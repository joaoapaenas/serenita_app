# tests/features/cycle_editor/test_cycle_editor_flow.py
import uuid
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.core.context import AppContext
from app.features.cycle_editor.cycle_editor_view import CycleEditorView
from app.features.main_window.main_controller import MainWindowController
from app.features.main_window.main_window_view import MainWindow
from app.services.analytics_service import SqliteAnalyticsService
from app.services.cycle_service import SqliteCycleService
from app.services.cycle_subject_service import SqliteCycleSubjectService
from app.services.exam_service import SqliteExamService
from app.services.master_subject_service import SqliteMasterSubjectService
from app.services.performance_service import SqlitePerformanceService
from app.services.session_service import SqliteSessionService
from app.services.study_queue_service import SqliteStudyQueueService
from app.services.template_subject_service import SqliteTemplateSubjectService
from app.services.user_service import SqliteUserService
from app.services.work_unit_service import SqliteWorkUnitService


def test_cycle_editor_opens_for_existing_cycle(qtbot, session_mock_db_factory, mocker):
    """
    Test Case 2.1:
    Simulates opening the cycle editor for a new cycle when one already exists.
    1. App starts with a user and an active cycle.
    2. Main window opens.
    3. User requests to create a new cycle.
    4. CycleEditorView is shown.
    """
    # 1. Setup: Create AppContext and all services
    user_service = SqliteUserService(session_mock_db_factory)
    cycle_service = SqliteCycleService(session_mock_db_factory)
    exam_service = SqliteExamService(session_mock_db_factory)
    cycle_subject_service = SqliteCycleSubjectService(session_mock_db_factory)
    
    app_context = AppContext(
        user_service=user_service,
        cycle_service=cycle_service,
        exam_service=exam_service,
        cycle_subject_service=cycle_subject_service,
        session_service=SqliteSessionService(session_mock_db_factory),
        performance_service=SqlitePerformanceService(session_mock_db_factory),
        analytics_service=SqliteAnalyticsService(session_mock_db_factory),
        master_subject_service=SqliteMasterSubjectService(session_mock_db_factory),
        study_queue_service=SqliteStudyQueueService(session_mock_db_factory),
        work_unit_service=SqliteWorkUnitService(session_mock_db_factory),
        template_subject_service=SqliteTemplateSubjectService(session_mock_db_factory),
        conn_factory=session_mock_db_factory
    )    # 2. Pre-condition: Create a user, exam, and an active cycle
    user = user_service.create_user("Test User", "Intermediate")
    exam_id = exam_service.create(user_id=user.id, name="Test Exam", area="Test Area")
    exam = exam_service.get_by_id(exam_id)
    cycle_id = cycle_service.create(name="Test Cycle", exam_id=exam.id, block_duration=60, is_continuous=True, daily_goal=3, timing_strategy="Adaptive")
    cycle = cycle_service.get_by_id(cycle_id)
    
    assert user is not None
    assert cycle is not None
    assert cycle.is_active

    # 3. Instantiate and show the main window
    # Mock the plan regeneration to avoid background threads and DB issues in this UI test
    mocker.patch('app.features.main_window.plan_manager.PlanManager.regenerate_plan', return_value=None)

    main_window = MainWindow()
    main_controller = MainWindowController(
        view=main_window,
        current_user=user,
        app_context=app_context,
        is_dev_mode=False
    )
    
    main_window.show()
    qtbot.waitUntil(main_window.isVisible)

    # 4. Trigger the creation of a new cycle
    # This is normally triggered by a menu action. We can call the method directly.
    main_controller.launch_cycle_creator()

    # 5. Wait for the CycleEditorView to appear
    # We need to find the new view. The main controller will set it as the central widget.
    def cycle_editor_is_visible():
        current_widget = main_window.main_pane
        assert isinstance(current_widget, CycleEditorView)
        return current_widget.isVisible()
    
    qtbot.waitUntil(cycle_editor_is_visible)

    # 6. Final Assertion: The CycleEditorView is visible
    assert isinstance(main_window.main_pane, CycleEditorView)


def test_create_new_cycle(qtbot, session_mock_db_factory, mocker):
    """
    Test Case 2.1 (Create):
    Simulates creating a new cycle from the CycleEditorView.
    1. App starts with a user and master subjects.
    2. CycleEditorView is opened directly.
    3. User names the cycle and selects a subject.
    4. User clicks save.
    5. A new cycle and its subject link are created in the database.
    """
    # 1. Setup: Create AppContext and all services
    user_service = SqliteUserService(session_mock_db_factory)
    cycle_service = SqliteCycleService(session_mock_db_factory)
    exam_service = SqliteExamService(session_mock_db_factory)
    master_subject_service = SqliteMasterSubjectService(session_mock_db_factory)
    cycle_subject_service = SqliteCycleSubjectService(session_mock_db_factory)

    app_context = AppContext(
        user_service=user_service,
        cycle_service=cycle_service,
        exam_service=exam_service,
        cycle_subject_service=cycle_subject_service,
        master_subject_service=master_subject_service,
        session_service=SqliteSessionService(session_mock_db_factory),
        performance_service=SqlitePerformanceService(session_mock_db_factory),
        analytics_service=SqliteAnalyticsService(session_mock_db_factory),
        study_queue_service=SqliteStudyQueueService(session_mock_db_factory),
        work_unit_service=SqliteWorkUnitService(session_mock_db_factory),
        template_subject_service=SqliteTemplateSubjectService(session_mock_db_factory),
        conn_factory=session_mock_db_factory
    )
    # 2. Pre-condition: Create a user, exam, and master subjects
    unique_user_name = f"Test User {uuid.uuid4()}"
    user = user_service.create_user(unique_user_name, "Intermediate")
    exam_id = exam_service.create(user_id=user.id, name="Test Exam", area="Test Area")
    subject1_id = master_subject_service.create("Subject 1")
    subject2_id = master_subject_service.create("Subject 2")

    # 3. Instantiate and show the main window
    mocker.patch('app.features.main_window.plan_manager.PlanManager.regenerate_plan', return_value=None)
    main_window = MainWindow()
    main_controller = MainWindowController(
        view=main_window, current_user=user, app_context=app_context, is_dev_mode=False
    )
    main_window.show()
    qtbot.waitUntil(main_window.isVisible)

    # 4. Directly open the CycleEditorView
    main_controller.navigator.show_cycle_editor(exam_id=exam_id, cycle_id=None)

    def cycle_editor_is_visible():
        current_widget = main_window.main_pane
        return isinstance(current_widget, CycleEditorView) and current_widget.isVisible()
    qtbot.waitUntil(cycle_editor_is_visible)
    cycle_editor_view = main_window.main_pane

    # 5. Interact with the view
    new_cycle_name = "My New Cycle"
    qtbot.keyClicks(cycle_editor_view.settings_widget.cycle_name_input, new_cycle_name)

    # Select "Subject 1"
    available_list_widget = cycle_editor_view.subject_selector_widget.available_pane.available_list
    item = available_list_widget.findItems("Subject 1", Qt.MatchExactly)[0]
    item.setCheckState(Qt.Checked)

    # Click the save button
    qtbot.mouseClick(cycle_editor_view.save_cycle_button, Qt.MouseButton.LeftButton)

    # 6. Assertions
    # Find the new cycle in the database
    cycles = cycle_service.get_all_for_exam(exam_id)
    new_cycle = next((c for c in cycles if c.name == new_cycle_name), None)
    assert new_cycle is not None

    # Check that the subject was added to the cycle
    cycle_subjects = cycle_subject_service.get_subjects_for_cycle(new_cycle.id)
    assert len(cycle_subjects) == 1
    assert cycle_subjects[0].subject_id == subject1_id

