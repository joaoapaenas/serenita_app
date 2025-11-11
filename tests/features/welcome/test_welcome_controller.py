# tests/features/welcome/test_welcome_controller.py
from PySide6.QtCore import Qt
from app.features.welcome.welcome_view import WelcomeView
from app.features.welcome.welcome_controller import WelcomeController


def test_welcome_view_initial_state(qtbot):
    """Test the initial state of the welcome view."""
    view = WelcomeView()
    qtbot.addWidget(view)
    assert view.windowTitle() == "Welcome to Serenita!"
    assert not view.start_button.isEnabled()


def test_start_button_enablement(qtbot):
    """Test that the start button is enabled only when a name is entered."""
    view = WelcomeView()
    qtbot.addWidget(view)

    assert not view.start_button.isEnabled()
    qtbot.keyClicks(view.name_input, "Test User")
    assert view.start_button.isEnabled()
    view.name_input.setText("   ")
    assert not view.start_button.isEnabled()


def test_start_requested_signal_emitted(qtbot):
    """Test that the start_requested signal is emitted with correct data on click."""
    view = WelcomeView()
    qtbot.addWidget(view)

    qtbot.keyClicks(view.name_input, "Test User")
    view.experience_combo.setCurrentText("Intermediate")

    with qtbot.waitSignal(view.start_requested, raising=True) as blocker:
        qtbot.mouseClick(view.start_button, Qt.LeftButton)

    assert blocker.args == ["Test User", "Intermediate"]


def test_welcome_controller_create_user(mocker):
    """Test that the controller calls the user service on start_requested."""
    mock_view = mocker.MagicMock()
    mock_user_service = mocker.MagicMock()

    controller = WelcomeController(view=mock_view, user_service=mock_user_service)

    controller.create_user("Test User", "Beginner")

    mock_user_service.create_user.assert_called_once_with("Test User", "Beginner")
    mock_view.accept.assert_called_once()