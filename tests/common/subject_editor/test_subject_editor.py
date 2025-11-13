# tests/common/subject_editor/test_subject_editor.py

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

from app.common.subject_editor.subject_editor_controller import SubjectEditorController
from app.common.subject_editor.subject_editor_view import SubjectEditorView


@pytest.fixture
def controller_and_view(qtbot, mocker):
    """Fixture to provide a controller and its view."""
    # Patch the exec() method to prevent the dialog from blocking tests
    mocker.patch.object(
        SubjectEditorView, "exec", return_value=QDialog.DialogCode.Accepted
    )

    view = SubjectEditorView()
    # FIX: Instantiate the controller by passing the view instance directly.
    controller = SubjectEditorController(view)
    qtbot.addWidget(view)
    return controller, view


def test_controller_show_dialog(qtbot, controller_and_view, mocker):
    """Verify that calling show() on the controller calls exec() on the view."""
    controller, view = controller_and_view
    # Use spy to observe calls to the already patched exec method
    mock_exec = mocker.spy(view, "exec")
    controller.show()
    mock_exec.assert_called_once()


def test_controller_save_valid_subject(qtbot, controller_and_view, mocker):
    """Verify controller handles valid subject data, emits its signal, and accepts the view."""
    controller, view = controller_and_view
    mock_accept = mocker.spy(view, "accept")

    test_data = {"name": "Valid Subject", "relevance": 4, "volume": 3, "difficulty": 2}

    # Simulate user input
    view.subject_name_input.setText(test_data["name"])
    view.relevance_input.setValue(test_data["relevance"])
    view.volume_input.setValue(test_data["volume"])
    view.difficulty_input.setValue(test_data["difficulty"])

    # The controller listens for view.subject_saved, validates, and then emits its own signal.
    with qtbot.waitSignal(controller.subject_saved, timeout=1000) as blocker:
        qtbot.mouseClick(view.save_button, Qt.MouseButton.LeftButton)

    # Assert that the controller emitted the correct data
    assert blocker.args[0] == test_data
    # Assert that the controller accepted the view after successful validation
    mock_accept.assert_called_once()


def test_controller_save_empty_name_shows_warning(qtbot, controller_and_view, mocker):
    """Verify controller shows warning for empty name and does not close the dialog."""
    controller, view = controller_and_view

    mock_warning = mocker.patch("PySide6.QtWidgets.QMessageBox.warning")
    mock_accept = mocker.spy(view, "accept")

    # Simulate clicking save with an empty name
    qtbot.mouseClick(view.save_button, Qt.MouseButton.LeftButton)

    # Allow Qt's event loop to process the signals
    QApplication.processEvents()

    # Verify the warning was shown and the dialog was not closed
    mock_warning.assert_called_once_with(
        view, "Validation Error", "Subject name cannot be empty."
    )
    mock_accept.assert_not_called()


def test_controller_view_rejected_closes_controller(qtbot, controller_and_view, mocker):
    """Verify controller's close method is called when view is rejected."""
    controller, view = controller_and_view
    mock_controller_close = mocker.spy(controller, "close")

    # Simulate the view being rejected (e.g., by clicking Cancel or the 'X' button)
    # This emits the view's `rejected` signal.
    view.reject()

    # The controller's `close` slot should be called in response.
    mock_controller_close.assert_called_once()
