# tests/features/cycle_editor/components/test_cycle_commands.py
import pytest
from app.features.cycle_editor.components.cycle_commands import (
    DeleteCycleCommand, CreateCycleCommand
)
from app.models.cycle import Cycle
from app.core.signals import app_signals


def test_delete_cycle_command(mocker, sample_cycle):
    mock_signal = mocker.patch('app.core.signals.app_signals.data_changed')
    mock_cycle_service = mocker.MagicMock()

    sample_cycle.id = 123
    sample_cycle.name = "Test Cycle to Delete"
    mock_cycle_service.get_by_id.return_value = sample_cycle

    command = DeleteCycleCommand(cycle_id=123, cycle_service=mock_cycle_service)

    command.redo()
    assert command.text() == "Delete Cycle 'Test Cycle to Delete'"
    mock_cycle_service.soft_delete.assert_called_once_with(123)

    command.undo()
    mock_cycle_service.restore_soft_deleted.assert_called_once_with(123)
    assert mock_signal.emit.call_count == 2


def test_create_cycle_command(mocker):
    mock_signal = mocker.patch('app.core.signals.app_signals.data_changed')

    # --- FIX: Patch CycleBuilder where it is imported and used ---
    mock_builder_class = mocker.patch('app.features.cycle_editor.components.cycle_commands.CycleBuilder')
    mock_builder_instance = mocker.MagicMock()
    mock_builder_class.return_value = mock_builder_instance

    # Configure the mock builder for chaining
    mock_builder_instance.for_exam.return_value = mock_builder_instance
    mock_builder_instance.with_properties.return_value = mock_builder_instance
    mock_builder_instance.with_subjects.return_value = mock_builder_instance
    mock_builder_instance.build.return_value = 1 # Simulate a new cycle ID

    # Mock the internal cycle_service used by the builder
    mock_builder_instance._cycle_service = mocker.MagicMock()

    cycle_data = {
        'name': 'New Cycle',
        'duration': 60,
        'is_continuous': True,
        'daily_goal': 2,
        'timing_strategy': 'Adaptive'
    }

    subjects_data = [
        {
            'name': 'Math',
            'relevance': 4,
            'volume': 3,
            'difficulty': 5,
            'is_active': True
        }
    ]

    command = CreateCycleCommand(
        exam_id=1,
        cycle_data=cycle_data,
        subjects_data=subjects_data,
        builder=mock_builder_instance # Pass the mocked builder
    )

    command.redo()

    mock_builder_instance._cycle_service.set_all_inactive.assert_called_once()
    # mock_builder_class.assert_called_once()  # Removed: The class itself is not called

    # Check that the builder was called with the correct, complete data
    mock_builder_instance.for_exam.assert_called_once_with(1)
    mock_builder_instance.with_properties.assert_called_once_with(cycle_data)
    mock_builder_instance.with_subjects.assert_called_once_with(subjects_data)
    mock_builder_instance.build.assert_called_once()

    mock_signal.emit.assert_called_once()