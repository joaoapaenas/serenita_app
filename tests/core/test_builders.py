import pytest
from unittest.mock import MagicMock, patch

from app.core.builders import CycleBuilder
from app.models.subject import Subject, CycleSubject
from app.services.interfaces import ICycleService, ICycleSubjectService, IStudyQueueService, IMasterSubjectService


@pytest.fixture
def mock_services():
    """Fixture to provide mocked service interfaces."""
    return {
        "cycle_service": MagicMock(spec=ICycleService),
        "cycle_subject_service": MagicMock(spec=ICycleSubjectService),
        "master_subject_service": MagicMock(spec=IMasterSubjectService),
        "queue_service": MagicMock(spec=IStudyQueueService),
    }


@pytest.fixture
def cycle_builder(mock_services):
    """Fixture to provide a CycleBuilder instance with mocked services."""
    return CycleBuilder(
        cycle_service=mock_services["cycle_service"],
        cycle_subject_service=mock_services["cycle_subject_service"],
        master_subject_service=mock_services["master_subject_service"],
        queue_service=mock_services["queue_service"],
    )


def test_build_new_cycle_creation(cycle_builder, mock_services):
    """Test the creation of a new cycle with subjects and queue generation."""
    # Arrange
    exam_id = 101
    cycle_data = {
        'name': 'Test Cycle', 'duration': 60, 'is_continuous': True,
        'daily_goal': 5, 'timing_strategy': 'Adaptive'
    }
    subjects_data = [
        {'name': 'Math', 'relevance': 1, 'volume': 1, 'difficulty': 1, 'is_active': True},
        {'name': 'Physics', 'relevance': 2, 'volume': 2, 'difficulty': 2, 'is_active': True},
    ]

    # Mock service return values
    mock_services["cycle_service"].create.return_value = 1
    mock_services["master_subject_service"].get_master_subject_by_name.side_effect = [
        Subject(id=1, name='Math', color='blue', created_at='2023-01-01 00:00:00', updated_at='2023-01-01 00:00:00', soft_delete=False, deleted_at=None),
        Subject(id=2, name='Physics', color='red', created_at='2023-01-01 00:00:00', updated_at='2023-01-01 00:00:00', soft_delete=False, deleted_at=None),
    ]
    # Mock the return of get_subjects_for_cycle for queue generation
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = [
        CycleSubject(id=1, cycle_id=1, subject_id=1, name="Math", relevance_weight=1, volume_weight=1, difficulty_weight=1, is_active=True, final_weight_calc=1.0, num_blocks_in_cycle=1, current_strategic_state="DISCOVERY"),
        CycleSubject(id=2, cycle_id=1, subject_id=2, name="Physics", relevance_weight=2, volume_weight=2, difficulty_weight=2, is_active=True, final_weight_calc=2.0, num_blocks_in_cycle=2, current_strategic_state="DEEP_WORK"),
    ]

    # Patch business_logic.calculate_final_weight and business_logic.calculate_num_blocks
    with patch('app.core.business_logic.calculate_final_weight', side_effect=[1.0, 2.0]), \
         patch('app.core.business_logic.calculate_num_blocks', side_effect=[1, 2]), \
         patch('app.core.business_logic.generate_study_queue', return_value=[1, 2, 2]):
        # Act
        result_cycle_id = cycle_builder.for_exam(exam_id).with_properties(cycle_data).with_subjects(subjects_data).build()

        # Assert
        assert result_cycle_id == 1
        mock_services["cycle_service"].create.assert_called_once_with(
            cycle_data['name'], cycle_data['duration'], cycle_data['is_continuous'],
            cycle_data['daily_goal'], exam_id, cycle_data['timing_strategy']
        )
        assert mock_services["master_subject_service"].get_master_subject_by_name.call_count == len(subjects_data)
        assert mock_services["cycle_subject_service"].add_subject_to_cycle.call_count == len(subjects_data)
        mock_services["queue_service"].save_queue.assert_called_once_with(1, [1, 2, 2])


def test_build_existing_cycle_update(cycle_builder, mock_services):
    """Test the update of an existing cycle with new subjects and queue generation."""
    # Arrange
    existing_cycle_id = 1
    cycle_data = {
        'name': 'Updated Cycle', 'duration': 70, 'is_continuous': False,
        'daily_goal': 7, 'is_active': True, 'timing_strategy': 'Spaced Repetition'
    }
    subjects_data = [
        {'name': 'Chemistry', 'relevance': 3, 'volume': 3, 'difficulty': 3, 'is_active': True},
    ]

    # Mock service return values
    mock_services["master_subject_service"].get_master_subject_by_name.return_value = \
        Subject(id=3, name='Chemistry', color='green', created_at='2023-01-01 00:00:00', updated_at='2023-01-01 00:00:00', soft_delete=False, deleted_at=None)
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = [
        CycleSubject(id=3, cycle_id=1, subject_id=3, name="Chemistry", relevance_weight=3, volume_weight=3, difficulty_weight=3, is_active=True, final_weight_calc=3.0, num_blocks_in_cycle=3, current_strategic_state="CONQUER"),
    ]

    with patch('app.core.business_logic.calculate_final_weight', return_value=3.0), \
         patch('app.core.business_logic.calculate_num_blocks', return_value=3), \
         patch('app.core.business_logic.generate_study_queue', return_value=[3, 3, 3]):
        # Act
        result_cycle_id = cycle_builder.from_existing(existing_cycle_id).with_properties(cycle_data).with_subjects(subjects_data).build()

        # Assert
        assert result_cycle_id == existing_cycle_id
        mock_services["cycle_service"].update_properties.assert_called_once_with(
            existing_cycle_id, cycle_data['name'], cycle_data['duration'],
            cycle_data['is_continuous'], cycle_data['daily_goal'],
            cycle_data['is_active'], cycle_data['timing_strategy']
        )
        mock_services["cycle_subject_service"].delete_subjects_for_cycle.assert_called_once_with(existing_cycle_id)
        mock_services["cycle_subject_service"].add_subject_to_cycle.assert_called_once()
        mock_services["queue_service"].save_queue.assert_called_once_with(existing_cycle_id, [3, 3, 3])


def test_build_no_exam_or_cycle_id_raises_error(cycle_builder):
    """Test that building without exam_id or cycle_id raises a ValueError."""
    with pytest.raises(ValueError, match="CycleBuilder requires either an exam_id"):
        cycle_builder.with_properties({}).with_subjects([]).build()


def test_build_with_subject_order(cycle_builder, mock_services):
    """Test that the queue is generated respecting the provided subject order."""
    # Arrange
    exam_id = 101
    cycle_data = {
        'name': 'Ordered Cycle', 'duration': 60, 'is_continuous': True,
        'daily_goal': 5, 'timing_strategy': 'Adaptive'
    }
    subjects_data = [
        {'name': 'Physics', 'relevance': 2, 'volume': 2, 'difficulty': 2, 'is_active': True},
        {'name': 'Math', 'relevance': 1, 'volume': 1, 'difficulty': 1, 'is_active': True},
    ]
    subject_order = ['Math', 'Physics']

    mock_services["cycle_service"].create.return_value = 1
    mock_services["master_subject_service"].get_master_subject_by_name.side_effect = [
        Subject(id=2, name='Physics', color='red', created_at='2023-01-01 00:00:00', updated_at='2023-01-01 00:00:00', soft_delete=False, deleted_at=None),
        Subject(id=1, name='Math', color='blue', created_at='2023-01-01 00:00:00', updated_at='2023-01-01 00:00:00', soft_delete=False, deleted_at=None),
    ]
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = [
        CycleSubject(id=1, cycle_id=1, subject_id=1, name="Math", relevance_weight=1, volume_weight=1, difficulty_weight=1, is_active=True, final_weight_calc=1.0, num_blocks_in_cycle=1, current_strategic_state="DISCOVERY"),
        CycleSubject(id=2, cycle_id=1, subject_id=2, name="Physics", relevance_weight=2, volume_weight=2, difficulty_weight=2, is_active=True, final_weight_calc=2.0, num_blocks_in_cycle=2, current_strategic_state="DEEP_WORK"),
    ]

    with patch('app.core.business_logic.calculate_final_weight', side_effect=[2.0, 1.0]), \
         patch('app.core.business_logic.calculate_num_blocks', side_effect=[2, 1]), \
         patch('app.core.business_logic.generate_study_queue', return_value=[]) as mock_generate_study_queue:
        # Act
        result_cycle_id = cycle_builder.for_exam(exam_id).with_properties(cycle_data).with_subjects(subjects_data).with_subject_order(subject_order).build()

        # Assert
        assert result_cycle_id == 1
        # The expected queue should be [Math, Physics, Physics] based on num_blocks_in_cycle
        mock_services["queue_service"].save_queue.assert_called_once_with(1, [1, 2, 2])
        # generate_study_queue should be called with an empty list as all subjects are ordered
        mock_generate_study_queue.assert_called_once_with([])


def test_build_subject_not_found(cycle_builder, mock_services):
    """Test that subjects not found in master_subject_service are skipped."""
    # Arrange
    exam_id = 101
    cycle_data = {
        'name': 'Test Cycle', 'duration': 60, 'is_continuous': True,
        'daily_goal': 5, 'timing_strategy': 'Adaptive'
    }
    subjects_data = [
        {'name': 'NonExistentSubject', 'relevance': 1, 'volume': 1, 'difficulty': 1, 'is_active': True},
    ]

    mock_services["cycle_service"].create.return_value = 1
    mock_services["master_subject_service"].get_master_subject_by_name.return_value = None # No subject found
    mock_services["cycle_subject_service"].get_subjects_for_cycle.return_value = []

    with patch('app.core.business_logic.calculate_final_weight'), \
         patch('app.core.business_logic.calculate_num_blocks'), \
         patch('app.core.business_logic.generate_study_queue', return_value=[]):
        # Act
        result_cycle_id = cycle_builder.for_exam(exam_id).with_properties(cycle_data).with_subjects(subjects_data).build()

        # Assert
        assert result_cycle_id == 1
        mock_services["master_subject_service"].get_master_subject_by_name.assert_called_once_with('NonExistentSubject')
        mock_services["cycle_subject_service"].add_subject_to_cycle.assert_not_called()
        mock_services["queue_service"].save_queue.assert_called_once_with(1, [])
