import pytest
from unittest.mock import MagicMock, call
from datetime import date

from app.core.tutor_engine.input_assembler import V20InputAssembler
from app.models.cycle import Cycle
from app.models.user import User, HumanFactor
from app.models.subject import CycleSubject, WorkUnit
from app.models.session import StudySession
from app.services.interfaces import (ICycleService, ICycleSubjectService, IWorkUnitService,
                                     ISessionService, IUserService)


@pytest.fixture
def mock_services():
    """Fixture to provide mocked service interfaces."""
    return {
        "cycle_service": MagicMock(spec=ICycleService),
        "cycle_subject_service": MagicMock(spec=ICycleSubjectService),
        "work_unit_service": MagicMock(spec=IWorkUnitService),
        "session_service": MagicMock(spec=ISessionService),
        "user_service": MagicMock(spec=IUserService),
    }


@pytest.fixture
def input_assembler(mock_services):
    """Fixture to provide a V20InputAssembler instance with mocked services."""
    return V20InputAssembler(
        cycle_service=mock_services["cycle_service"],
        cycle_subject_service=mock_services["cycle_subject_service"],
        work_unit_service=mock_services["work_unit_service"],
        session_service=mock_services["session_service"],
        user_service=mock_services["user_service"],
    )


@pytest.fixture
def mock_active_cycle():
    """Mock active Cycle object."""
    return Cycle(
        id=1, name="Test Cycle", block_duration_min=30, is_continuous=True,
        daily_goal_blocks=2, exam_id=101, is_active=True, timing_strategy="Adaptive",
        current_queue_position=0, phase="Discovery",
        created_at="2023-01-01", updated_at="2023-01-01", soft_delete=False, deleted_at=None
    )


@pytest.fixture
def mock_current_user():
    """Mock current User object."""
    return User(
        id=1, name="Test User", study_level="Beginner", theme="dark",
        created_at="2023-01-01", description="A test user" # Added description
    )


def test_assemble_basic_data(input_assembler, mock_services, mock_active_cycle, mock_current_user):
    """Test basic assembly of input data."""
    # Arrange
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = []
    mock_services["session_service"].get_history_for_cycle.return_value = []
    mock_services["user_service"].get_human_factor_history.return_value = []
    mock_services["cycle_service"].get_plan_cache.return_value = None

    # Act
    result = input_assembler.assemble(mock_active_cycle, mock_current_user)

    # Assert
    assert "subjects" in result
    assert result["subjects"] == []
    assert "study_history" in result
    assert result["study_history"] == []
    assert result["available_time_minutes"] == mock_active_cycle.daily_goal_blocks * mock_active_cycle.block_duration_min
    assert result["cycle_duration_days"] == 7
    assert "human_factor_input" in result
    assert result["human_factor_input"]["energy_level"] == 'Normal'
    assert result["human_factor_input"]["stress_level"] == 'Normal'
    assert "human_factor_history" in result
    assert result["human_factor_history"] == []
    assert "previous_cycle_config" in result
    assert result["previous_cycle_config"] == {}
    assert "meta" in result
    assert result["meta"]["human_factor_input"]["energy_level"] == 'Normal'


def test_assemble_subjects_with_work_units(input_assembler, mock_services, mock_active_cycle, mock_current_user):
    """Test assembly with subjects and their associated work units."""
    # Arrange
    mock_subject_1 = CycleSubject(
        id=1, cycle_id=mock_active_cycle.id, subject_id=101, relevance_weight=1,
        volume_weight=1, difficulty_weight=1, is_active=True, final_weight_calc=1.0,
        num_blocks_in_cycle=1, name="Math", color="blue", date_added="2023-01-01",
        current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[]
    )
    mock_subject_2 = CycleSubject(
        id=2, cycle_id=mock_active_cycle.id, subject_id=102, relevance_weight=1,
        volume_weight=1, difficulty_weight=1, is_active=True, final_weight_calc=1.0,
        num_blocks_in_cycle=1, name="Physics", color="red", date_added="2023-01-01",
        current_strategic_state="DISCOVERY", state_hysteresis_data={}, work_units=[]
    )
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = [mock_subject_1, mock_subject_2]

    mock_work_unit_1 = WorkUnit(
        id=1, subject_id=101, unit_id="wu_101_1", title="Algebra Basics", type="reading",
        estimated_time_minutes=60, is_completed=False, related_questions_topic="Algebra", sequence_order=1
    )
    mock_work_unit_2 = WorkUnit(
        id=2, subject_id=102, unit_id="wu_102_1", title="Newton's Laws", type="video",
        estimated_time_minutes=45, is_completed=True, related_questions_topic="Mechanics", sequence_order=1
    )
    mock_services["work_unit_service"].get_work_units_for_subject.side_effect = [
        [mock_work_unit_1],
        [mock_work_unit_2]
    ]
    mock_services["session_service"].get_history_for_cycle.return_value = []
    mock_services["user_service"].get_human_factor_history.return_value = []
    mock_services["cycle_service"].get_plan_cache.return_value = None

    # Act
    result = input_assembler.assemble(mock_active_cycle, mock_current_user)

    # Assert
    assert len(result["subjects"]) == 2
    assert result["subjects"][0].name == "Math"
    assert result["subjects"][0].work_units == [mock_work_unit_1]
    assert result["subjects"][1].name == "Physics"
    assert result["subjects"][1].work_units == [mock_work_unit_2]
    mock_services["work_unit_service"].get_work_units_for_subject.assert_has_calls([
        call(101), call(102)
    ])


def test_assemble_with_study_history(input_assembler, mock_services, mock_active_cycle, mock_current_user):
    """Test assembly with study history."""
    # Arrange
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = []
    mock_study_session = StudySession(
        id=1, user_id=mock_current_user.id, subject_id=101, cycle_id=mock_active_cycle.id,
        start_time="2023-01-01T10:00:00", end_time="2023-01-01T11:00:00",
        liquid_duration_sec=3600, description="Test session", topic_id=None,
        total_duration_sec=3600, total_pause_duration_sec=0, study_method="Pomodoro",
        soft_delete=False, deleted_at=None
    )
    mock_services["session_service"].get_history_for_cycle.return_value = [mock_study_session]
    mock_services["user_service"].get_human_factor_history.return_value = []
    mock_services["cycle_service"].get_plan_cache.return_value = None

    # Act
    result = input_assembler.assemble(mock_active_cycle, mock_current_user)

    # Assert
    assert result["study_history"] == [mock_study_session]
    mock_services["session_service"].get_history_for_cycle.assert_called_once_with(mock_active_cycle.id)


def test_assemble_human_factor_current_in_history(input_assembler, mock_services, mock_active_cycle, mock_current_user):
    """Test assembly when current human factor is found in history."""
    # Arrange
    today_str = date.today().isoformat()
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = []
    mock_services["session_service"].get_history_for_cycle.return_value = []
    mock_human_factor_today = HumanFactor(
        id=1, user_id=mock_current_user.id, date=today_str, energy_level="High", stress_level="Low"
    )
    mock_human_factor_yesterday = HumanFactor(
        id=2, user_id=mock_current_user.id, date="2023-11-07", energy_level="Normal", stress_level="Normal"
    )
    mock_services["user_service"].get_human_factor_history.return_value = [
        mock_human_factor_yesterday, mock_human_factor_today
    ]
    mock_services["cycle_service"].get_plan_cache.return_value = None

    # Act
    result = input_assembler.assemble(mock_active_cycle, mock_current_user)

    # Assert
    assert result["human_factor_input"]["date"] == today_str
    assert result["human_factor_input"]["energy_level"] == "High"
    assert result["human_factor_input"]["stress_level"] == "Low"
    assert result["human_factor_history"] == [mock_human_factor_yesterday, mock_human_factor_today]
    assert result["meta"]["human_factor_input"]["energy_level"] == "High"


def test_assemble_human_factor_current_not_in_history(input_assembler, mock_services, mock_active_cycle, mock_current_user):
    """Test assembly when current human factor is not found in history (defaults to Normal)."""
    # Arrange
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = []
    mock_services["session_service"].get_history_for_cycle.return_value = []
    mock_human_factor_yesterday = HumanFactor(
        id=1, user_id=mock_current_user.id, date="2023-11-07", energy_level="Low", stress_level="High"
    )
    mock_services["user_service"].get_human_factor_history.return_value = [mock_human_factor_yesterday]
    mock_services["cycle_service"].get_plan_cache.return_value = None

    # Act
    result = input_assembler.assemble(mock_active_cycle, mock_current_user)

    # Assert
    assert result["human_factor_input"]["energy_level"] == 'Normal'
    assert result["human_factor_input"]["stress_level"] == 'Normal'
    assert result["human_factor_history"] == [mock_human_factor_yesterday]
    assert result["meta"]["human_factor_input"]["energy_level"] == 'Normal'


def test_assemble_with_previous_cycle_config(input_assembler, mock_services, mock_active_cycle, mock_current_user):
    """Test assembly with a cached previous cycle configuration."""
    # Arrange
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = []
    mock_services["session_service"].get_history_for_cycle.return_value = []
    mock_services["user_service"].get_human_factor_history.return_value = []
    mock_cached_plan = {"meta": {"some_data": "value"}}
    mock_services["cycle_service"].get_plan_cache.return_value = mock_cached_plan

    # Act
    result = input_assembler.assemble(mock_active_cycle, mock_current_user)

    # Assert
    assert result["previous_cycle_config"] == mock_cached_plan
    mock_services["cycle_service"].get_plan_cache.assert_called_once_with(mock_active_cycle.id)