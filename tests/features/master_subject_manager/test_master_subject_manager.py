# tests/features/master_subject_manager/test_master_subject_manager.py

import pytest
from unittest.mock import MagicMock, call

from PySide6.QtWidgets import QDialog, QMessageBox

from app.features.master_subject_manager.master_subject_manager_controller import MasterSubjectManagerController
from app.features.master_subject_manager.master_subject_manager_view import MasterSubjectManagerView
from app.services.interfaces import IMasterSubjectService
from app.models.subject import Subject


@pytest.fixture
def mock_view():
    """Fixture for a mock MasterSubjectManagerView."""
    return MagicMock(spec=MasterSubjectManagerView)


@pytest.fixture
def mock_master_subject_service():
    """Fixture for a mock IMasterSubjectService."""
    return MagicMock(spec=IMasterSubjectService)


@pytest.fixture
def mock_navigator():
    """Fixture for a mock Navigator."""
    return MagicMock()


@pytest.fixture
def controller(mock_view, mock_master_subject_service, mock_navigator):
    """Fixture for MasterSubjectManagerController with mocked dependencies."""
    # Reset mocks before each test
    mock_view.reset_mock()
    mock_master_subject_service.reset_mock()
    mock_navigator.reset_mock()
    
    # Instantiate the controller
    # The controller's __init__ calls load_data() once.
    return MasterSubjectManagerController(
        view=mock_view,
        master_subject_service=mock_master_subject_service,
        navigator=mock_navigator
    )


def test_load_data_on_init(controller, mock_master_subject_service, mock_view):
    """Test that load_data is called on controller initialization."""
    # Assert that __init__ called load_data
    mock_master_subject_service.get_all_master_subjects.assert_called_once()
    mock_view.populate_subjects.assert_called_once()


def test_on_add_success(controller, mock_master_subject_service, mocker):
    """Test the add functionality with a successful dialog."""
    # Arrange
    mocker.patch(
        'app.features.master_subject_manager.master_subject_manager_controller.MasterSubjectEditorDialog',
        return_value=MagicMock(
            exec=lambda: QDialog.DialogCode.Accepted,
            get_subject_name=lambda: "New Subject"
        )
    )
    mock_signal = mocker.patch('app.features.master_subject_manager.master_subject_manager_controller.app_signals.data_changed')

    # Act
    controller._on_add()

    # Assert
    mock_master_subject_service.create.assert_called_once_with("New Subject")
    mock_signal.emit.assert_called_once()


def test_on_add_cancel(controller, mock_master_subject_service, mocker):
    """Test the add functionality when the dialog is cancelled."""
    # Arrange
    mocker.patch(
        'app.features.master_subject_manager.master_subject_manager_controller.MasterSubjectEditorDialog',
        return_value=MagicMock(exec=lambda: QDialog.DialogCode.Rejected)
    )

    # Act
    controller._on_add()

    # Assert
    mock_master_subject_service.create.assert_not_called()


def test_on_edit_success(controller, mock_master_subject_service, mocker):
    """Test the edit functionality with a successful dialog."""
    # Arrange
    subject_to_edit = Subject(id=1, name="Old Name", color=None, created_at="", updated_at="", soft_delete=False, deleted_at=None)
    mocker.patch(
        'app.features.master_subject_manager.master_subject_manager_controller.MasterSubjectEditorDialog',
        return_value=MagicMock(
            exec=lambda: QDialog.DialogCode.Accepted,
            get_subject_name=lambda: "New Name"
        )
    )
    mock_signal = mocker.patch('app.features.master_subject_manager.master_subject_manager_controller.app_signals.data_changed')

    # Act
    controller._on_edit(subject_to_edit)

    # Assert
    mock_master_subject_service.update.assert_called_once_with(1, "New Name")
    mock_signal.emit.assert_called_once()


def test_on_delete_confirm(controller, mock_master_subject_service, mocker):
    """Test the delete functionality when the user confirms."""
    # Arrange
    subject_to_delete = Subject(id=1, name="To Delete", color=None, created_at="", updated_at="", soft_delete=False, deleted_at=None)
    mocker.patch('PySide6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Yes)
    mock_signal = mocker.patch('app.features.master_subject_manager.master_subject_manager_controller.app_signals.data_changed')

    # Act
    controller._on_delete(subject_to_delete)

    # Assert
    mock_master_subject_service.delete.assert_called_once_with(1)
    mock_signal.emit.assert_called_once()


def test_on_delete_cancel(controller, mock_master_subject_service, mocker):
    """Test the delete functionality when the user cancels."""
    # Arrange
    subject_to_delete = Subject(id=1, name="To Delete", color=None, created_at="", updated_at="", soft_delete=False, deleted_at=None)
    mocker.patch('PySide6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Cancel)

    # Act
    controller._on_delete(subject_to_delete)

    # Assert
    mock_master_subject_service.delete.assert_not_called()


def test_back_requested(controller, mock_navigator):
    """Test that the back requested signal calls the navigator."""
    # This test relies on the connection made in the controller's __init__
    # We can trigger the signal on the mock view to test the connection
    controller._view.back_requested.connect.assert_called_with(mock_navigator.show_configurations_landing)
