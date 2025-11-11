# tests/features/onboarding/test_onboarding_controller.py
import pytest
from unittest.mock import MagicMock
from app.features.onboarding.onboarding_controller import OnboardingController
from app.features.onboarding.components.define_exam_page import DefineExamPage
from app.features.onboarding.components.goal_page import GoalPage
from app.features.onboarding.components.import_topics_page import ImportTopicsPage
from app.features.onboarding.components.subjects_config_page import SubjectsConfigPage
from app.features.onboarding.components.cycle_settings_page import CycleSettingsPage
from app.models.exam import Exam


# Mock pages to avoid creating real Qt Widgets
@pytest.fixture
def mock_onboarding_pages(mocker):
    pages = {
        "goal": mocker.MagicMock(spec=GoalPage),
        "define_exam": mocker.MagicMock(spec=DefineExamPage),
        "subjects_config": mocker.MagicMock(spec=SubjectsConfigPage),
        "import_topics": mocker.MagicMock(spec=ImportTopicsPage),
        "cycle_settings": mocker.MagicMock(spec=CycleSettingsPage)
    }
    # Mock the presenter within the subjects_config page
    pages["subjects_config"].presenter = mocker.MagicMock()
    return pages


@pytest.fixture
def onboarding_fixture(mocker, mock_onboarding_pages):
    mock_view = mocker.MagicMock()
    mock_exam_service = mocker.MagicMock()
    mock_master_subject_service = mocker.MagicMock()
    mock_template_subject_service = mocker.MagicMock()
    mock_cycle_service = mocker.MagicMock()
    mock_cycle_subject_service = mocker.MagicMock()
    mock_study_queue_service = mocker.MagicMock()
    mock_work_unit_service = mocker.MagicMock()

    # We need to make the view return our mock pages
    mock_view.create_page_goal.return_value = mock_onboarding_pages["goal"]
    mock_view.create_page_define_exam.return_value = mock_onboarding_pages["define_exam"]
    mock_view.create_page_subjects_config.return_value = mock_onboarding_pages["subjects_config"]
    mock_view.create_page_import_topics.return_value = mock_onboarding_pages["import_topics"]
    mock_view.create_page_cycle_settings.return_value = mock_onboarding_pages["cycle_settings"]

    controller = OnboardingController(
        view=mock_view,
        user_id=1,
        exam_service=mock_exam_service,
        master_subject_service=mock_master_subject_service,
        template_subject_service=mock_template_subject_service,
        cycle_service=mock_cycle_service,
        cycle_subject_service=mock_cycle_subject_service,
        study_queue_service=mock_study_queue_service,
        work_unit_service=mock_work_unit_service
    )
    return {
        "controller": controller,
        "mock_exam_service": mock_exam_service,
        "mock_master_subject_service": mock_master_subject_service,
        "mock_template_subject_service": mock_template_subject_service,
        "mock_cycle_service": mock_cycle_service,
        "mock_cycle_subject_service": mock_cycle_subject_service,
        "mock_study_queue_service": mock_study_queue_service,
        "mock_work_unit_service": mock_work_unit_service
    }


def test_onboarding_initial_state(onboarding_fixture):
    """Test the controller's state when it's first created."""
    controller = onboarding_fixture["controller"]
    # Act
    controller.start()

    # Assert
    # The initial flow should only contain the goal page
    assert len(controller.flow_manager.active_flow) == 1
    assert controller.flow_manager.current_page() == controller.pages["goal"]

    # Check that the view was instructed to show the first page
    controller._view.go_to_page.assert_called_once_with(controller.pages["goal"])

    # Check that navigation buttons are in the correct initial state
    controller._view.update_navigation.assert_called_with(0, 1, False)


def test_onboarding_flow_custom_selection(onboarding_fixture):
    """Test that the flow is correctly updated when the user selects a custom exam."""
    # Arrange
    controller = onboarding_fixture["controller"]
    controller.start()

    # Act: Simulate the user selecting "custom" on the goal page
    controller._on_goal_selection_changed("custom")

    # Assert
    # The flow should now have 5 pages
    assert len(controller.flow_manager.active_flow) == 5
    assert controller.pages["define_exam"] in controller.flow_manager.active_flow

    # Navigation should be updated to reflect the new flow
    # can_proceed is now True
    controller._view.update_navigation.assert_called_with(0, 5, True)


def test_onboarding_flow_template_selection(onboarding_fixture, mocker):
    """Test that the flow is correctly updated when the user selects a template."""
    # Arrange
    controller = onboarding_fixture["controller"]
    mock_template_subject_service = onboarding_fixture["mock_template_subject_service"]
    controller.start()
    mock_template_exam = mocker.MagicMock(spec=Exam)
    mock_template_exam.id = 101  # Give it an ID

    # Mock the return value of get_subjects_for_template
    mock_template_subject_service.get_subjects_for_template.return_value = []

    # Act: Simulate the user selecting a template Exam object
    controller._on_goal_selection_changed(mock_template_exam)

    # Assert
    # The flow for a template is shorter (4 pages), skipping define_exam
    assert len(controller.flow_manager.active_flow) == 4
    assert controller.pages["define_exam"] not in controller.flow_manager.active_flow
    assert controller.pages["subjects_config"] in controller.flow_manager.active_flow

    controller._view.update_navigation.assert_called_with(0, 4, True)


def test_onboarding_next_step_populates_next_page(onboarding_fixture, mock_onboarding_pages, mocker):
    """Test that moving to the next step correctly prepares the upcoming page."""
    # Arrange
    controller = onboarding_fixture["controller"]
    mock_master_subject_service = onboarding_fixture["mock_master_subject_service"]
    controller.start()
    controller._on_goal_selection_changed("custom")  # Set up a multi-page flow

    # Mock the return value of get_all_master_subjects
    mock_master_subject_service.get_all_master_subjects.return_value = [mocker.MagicMock()]

    # Act: Simulate clicking "Next" from the 'define_exam' page
    controller.flow_manager.current_page_index = 1  # Manually set the page to define_exam
    controller._on_next_step()

    # Assert
    # The next page is subjects_config, it should be populated
    mock_master_subject_service.get_all_master_subjects.assert_called_once()

    # The presenter on the mock subjects_config page should have been told to load the subjects
    mock_onboarding_pages["subjects_config"].presenter.load_master_subjects.assert_called_once()

    # The view should be told to navigate to the subjects_config page
    controller._view.go_to_page.assert_called_with(mock_onboarding_pages["subjects_config"])