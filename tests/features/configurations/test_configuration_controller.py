# tests/features/configurations/test_configuration_controller.py
from app.features.configurations.configuration_controller import ConfigurationController
from app.models.user import User

def test_on_save_success(mocker):
    """Test the successful save path."""
    mock_qmessagebox_info = mocker.patch('PySide6.QtWidgets.QMessageBox.information')
    mock_qmessagebox_warn = mocker.patch('PySide6.QtWidgets.QMessageBox.warning')
    mock_qapplication_instance = mocker.patch('PySide6.QtWidgets.QApplication.instance')
    mock_app = mocker.MagicMock()
    mock_qapplication_instance.return_value = mock_app

    mock_view = mocker.MagicMock()
    mock_user_service = mocker.MagicMock()
    mock_navigator = mocker.MagicMock()

    initial_user = User(id=1, name="Old Name", study_level="Beginner", description=None, created_at="", theme="Dark")
    updated_user = User(id=1, name="New Name", study_level="Advanced", description=None, created_at="", theme="Dark")
    mock_view.get_data.return_value = {"name": "New Name", "study_level": "Advanced", "theme": "Dark"}
    mock_user_service.update_user.return_value = updated_user

    controller = ConfigurationController(
        view=mock_view, user=initial_user, user_service=mock_user_service, navigator=mock_navigator
    )

    controller.on_save()

    mock_user_service.update_user.assert_called_once_with(1, "New Name", "Advanced", "Dark")
    mock_qmessagebox_info.assert_called_once()
    mock_qmessagebox_warn.assert_not_called()
    mock_navigator.show_overview.assert_called_once()


def test_on_save_validation_failure(mocker):
    """Test the save path when validation fails (e.g., empty name)."""
    mock_qmessagebox_info = mocker.patch('PySide6.QtWidgets.QMessageBox.information')
    mock_qmessagebox_warn = mocker.patch('PySide6.QtWidgets.QMessageBox.warning')

    mock_view = mocker.MagicMock()
    mock_user_service = mocker.MagicMock()
    mock_navigator = mocker.MagicMock()

    initial_user = User(id=1, name="Test", study_level="Beginner", description=None, created_at="", theme="Dark")
    mock_view.get_data.return_value = {"name": "  ", "study_level": "Advanced", "theme": "Dark"}

    controller = ConfigurationController(
        view=mock_view, user=initial_user, user_service=mock_user_service, navigator=mock_navigator
    )

    controller.on_save()

    mock_qmessagebox_warn.assert_called_once()
    mock_qmessagebox_info.assert_not_called()
    mock_user_service.update_user.assert_not_called()
    mock_navigator.show_overview.assert_not_called()