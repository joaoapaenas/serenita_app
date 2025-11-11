# tests/features/welcome/test_welcome_view.py
from PySide6.QtCore import Qt
from app.features.welcome.welcome_view import WelcomeView

def test_welcome_view_initial_state(qtbot):
    """Test the initial UI state of the welcome view."""
    # Arrange
    view = WelcomeView()
    qtbot.addWidget(view) # Add the widget to the qtbot to manage its lifecycle

    # Assert
    assert view.windowTitle() == "Welcome to Serenita!"
    assert not view.start_button.isEnabled()
    assert view.name_input.text() == ""
    assert view.experience_combo.currentText() == "Beginner"

def test_start_button_enables_on_text_entry(qtbot):
    """Test that the start button is enabled only when the name field has text."""
    # Arrange
    view = WelcomeView()
    qtbot.addWidget(view)

    # Act: Simulate user typing text into the QLineEdit
    qtbot.keyClicks(view.name_input, "Test User")

    # Assert
    assert view.start_button.isEnabled()

    # Act: Simulate user clearing the text
    view.name_input.clear()

    # Assert
    assert not view.start_button.isEnabled()

def test_start_requested_signal_emits_correct_data(qtbot):
    """Test that the start_requested signal is emitted with data from the UI."""
    # Arrange
    view = WelcomeView()
    qtbot.addWidget(view)

    # Act
    qtbot.keyClicks(view.name_input, "John Doe")
    view.experience_combo.setCurrentText("Advanced")

    # Use qtbot.waitSignal to safely capture the emitted signal
    with qtbot.waitSignal(view.start_requested, raising=True) as blocker:
        qtbot.mouseClick(view.start_button, Qt.LeftButton)

    # Assert that the arguments of the emitted signal are correct
    assert blocker.args == ["John Doe", "Advanced"]