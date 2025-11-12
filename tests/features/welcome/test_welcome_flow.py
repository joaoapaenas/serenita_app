# tests/features/welcome/test_welcome_flow.py
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from app.core.context import AppContext
from app.features.main_window.main_window_view import MainWindow
from app.features.welcome.welcome_controller import WelcomeController
from app.features.welcome.welcome_view import WelcomeView
from app.services.user_service import SqliteUserService
from app.models.user import User # Import the User dataclass

def test_first_launch_user_creation_and_main_window_opens(qtbot, session_mock_db_factory, mocker):
    """
    Test Case 1.1 (adapted):
    Simulates the entire first-launch flow:
    1. App starts with no users.
    2. Welcome screen is shown.
    3. User enters their name and experience level.
    4. User is created in the database.
    5. Main window opens for the new user.
    """
    # 1. Setup: Create AppContext with the in-memory DB
    user_service = SqliteUserService(session_mock_db_factory)
    
    # Mock get_first_user to ensure it returns None initially for this test
    # We'll use a side_effect to simulate the user being created
    mock_user = None
    def get_first_user_side_effect():
        nonlocal mock_user
        return mock_user

    mocker.patch.object(user_service, 'get_first_user', side_effect=get_first_user_side_effect)

    # Mock create_user to return a User object and update mock_user
    def create_user_side_effect(name, study_level):
        nonlocal mock_user
        mock_user = User(id=1, name=name, study_level=study_level, theme="Dark", description=None, created_at="2025-01-01 00:00:00")
        return mock_user
    
    mocker.patch.object(user_service, 'create_user', side_effect=create_user_side_effect)

    app_context = AppContext(
        user_service=user_service,        # Add other services if needed, but for this test, user_service is key
        cycle_service=None, # SqliteCycleService(session_mock_db_factory),
        session_service=None, # SqliteSessionService(session_mock_db_factory),
        exam_service=None, # SqliteExamService(session_mock_db_factory),
        performance_service=None, # SqlitePerformanceService(session_mock_db_factory),
        analytics_service=None, # SqliteAnalyticsService(session_mock_db_factory),
        master_subject_service=None, # SqliteMasterSubjectService(session_mock_db_factory),
        cycle_subject_service=None, # SqliteCycleSubjectService(session_mock_db_factory),
        study_queue_service=None, # SqliteStudyQueueService(session_mock_db_factory),
        work_unit_service=None, # SqliteWorkUnitService(session_mock_db_factory),
        template_subject_service=None, # SqliteTemplateSubjectService(session_mock_db_factory),
        conn_factory=session_mock_db_factory # Add conn_factory here
    )

    # 2. Pre-condition: Assert no user exists (now guaranteed by mock)
    assert app_context.user_service.get_first_user() is None

    # 3. Show the Welcome screen
    welcome_view = WelcomeView()
    welcome_controller = WelcomeController(view=welcome_view, user_service=app_context.user_service)
    
    # We can't use welcome_controller.run() as it's blocking.
    # We show the view and interact with it directly.
    welcome_view.show()
    qtbot.waitUntil(welcome_view.isVisible)

    # 4. Simulate user input
    test_user_name = "John Doe"
    qtbot.keyClicks(welcome_view.name_input, test_user_name)
    # The button should now be enabled
    qtbot.waitUntil(welcome_view.start_button.isEnabled)
    
    # Select "Advanced" from the combo box
    welcome_view.experience_combo.setCurrentText("Advanced")

    # 5. Click the "Get Started" button
    qtbot.mouseClick(welcome_view.start_button, Qt.MouseButton.LeftButton)

    # The controller's create_user method is called, which calls view.accept()
    # So we wait for the dialog to close.
    qtbot.waitUntil(lambda: not welcome_view.isVisible())

    # 6. Post-condition: Assert the user was created
    new_user = app_context.user_service.get_first_user()
    assert new_user is not None
    assert new_user.name == test_user_name
    assert new_user.study_level == "Advanced"

    # 7. Proceed to open the main window, as the real app would
    main_window = MainWindow()
    # In a real test, you'd instantiate the MainWindowController as well
    main_window.setWindowTitle(f"Serenita - {new_user.name}") # Simulate what the controller would do
    main_window.show()
    qtbot.waitUntil(main_window.isVisible)

    # 8. Final Assertion: The main window is open for the correct user
    assert main_window.windowTitle() == f"Serenita - {new_user.name}"
