import pytest
from unittest.mock import MagicMock, call
from datetime import date
import json

from app.services.cycle_subject_service import SqliteCycleSubjectService
from app.core.database import IDatabaseConnectionFactory
from app.models.subject import CycleSubject, Subject


@pytest.fixture
def mock_db_connection():
    """Fixture for a mock database connection."""
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = []  # Default to no rows
    conn.execute.return_value.fetchone.return_value = None  # Default to no row

    # Explicitly mock commit and rollback
    conn.commit = MagicMock()
    conn.rollback = MagicMock()

    # Mock context manager behavior
    conn.__enter__.return_value = conn
    # When __exit__ is called, ensure commit is called if no exception
    def mock_exit(exc_type, exc_val, exc_tb):
        if exc_type is None: # No exception, so commit
            conn.commit()
        else: # Exception occurred, so rollback
            conn.rollback()
        return False # Propagate exceptions

    conn.__exit__.side_effect = mock_exit

    return conn


@pytest.fixture
def mock_conn_factory(mock_db_connection):
    """Fixture for a mock database connection factory."""
    factory = MagicMock(spec=IDatabaseConnectionFactory)
    factory.get_connection.return_value = mock_db_connection
    return factory


@pytest.fixture
def cycle_subject_service(mock_conn_factory):
    """Fixture for SqliteCycleSubjectService with mocked dependencies."""
    return SqliteCycleSubjectService(mock_conn_factory)


def test_add_subject_to_cycle(cycle_subject_service, mock_db_connection):
    """Test adding a subject to a cycle."""
    cycle_id = 1
    subject_id = 101
    weights = {"relevance": 1, "volume": 2, "difficulty": 3, "is_active": True}
    calculated_data = {"final_weight": 2.5, "num_blocks": 5}
    today_str = date.today().isoformat()

    cycle_subject_service.add_subject_to_cycle(cycle_id, subject_id, weights, calculated_data)

    mock_db_connection.execute.assert_called_once_with(
        "INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight, is_active, final_weight_calc, num_blocks_in_cycle, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (cycle_id, subject_id, weights["relevance"], weights["volume"], weights["difficulty"], weights["is_active"],
         calculated_data["final_weight"], calculated_data["num_blocks"], today_str)
    )
    mock_db_connection.commit.assert_called_once()


def test_get_subjects_for_cycle_no_data(cycle_subject_service, mock_db_connection):
    """Test retrieving subjects for a cycle when none exist."""
    cycle_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = cycle_subject_service.get_subjects_for_cycle(cycle_id)

    assert result == []
    mock_db_connection.execute.assert_called_once_with(
        "SELECT CS.id, CS.cycle_id, CS.subject_id, CS.relevance_weight, CS.volume_weight, CS.difficulty_weight, CS.is_active, CS.final_weight_calc, CS.num_blocks_in_cycle, CS.date_added, CS.current_strategic_state, CS.state_hysteresis_data, S.name, S.color FROM cycle_subjects AS CS JOIN subjects AS S ON CS.subject_id = S.id WHERE CS.cycle_id = ?",
        (cycle_id,)
    )


def test_get_subjects_for_cycle_with_data(cycle_subject_service, mock_db_connection):
    """Test retrieving subjects for a cycle with existing data."""
    cycle_id = 1
    mock_rows = [
        {
            'id': 1, 'cycle_id': cycle_id, 'subject_id': 101, 'relevance_weight': 1,
            'volume_weight': 2, 'difficulty_weight': 3, 'is_active': True,
            'final_weight_calc': 2.5, 'num_blocks_in_cycle': 5, 'name': 'Math',
            'color': 'blue', 'date_added': '2023-01-01', 'current_strategic_state': 'DISCOVERY',
            'state_hysteresis_data': json.dumps({'consecutive_cycles_in_state': 0})
        },
        {
            'id': 2, 'cycle_id': cycle_id, 'subject_id': 102, 'relevance_weight': 2,
            'volume_weight': 3, 'difficulty_weight': 4, 'is_active': False,
            'final_weight_calc': 3.5, 'num_blocks_in_cycle': 7, 'name': 'Physics',
            'color': 'red', 'date_added': '2023-01-02', 'current_strategic_state': 'DEEP_WORK',
            'state_hysteresis_data': '{}'
        },
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = cycle_subject_service.get_subjects_for_cycle(cycle_id)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].name == 'Math'
    assert result[0].state_hysteresis_data == {'consecutive_cycles_in_state': 0}
    assert result[1].id == 2
    assert result[1].name == 'Physics'
    assert result[1].state_hysteresis_data == {}
    mock_db_connection.execute.assert_called_once_with(
        "SELECT CS.id, CS.cycle_id, CS.subject_id, CS.relevance_weight, CS.volume_weight, CS.difficulty_weight, CS.is_active, CS.final_weight_calc, CS.num_blocks_in_cycle, CS.date_added, CS.current_strategic_state, CS.state_hysteresis_data, S.name, S.color FROM cycle_subjects AS CS JOIN subjects AS S ON CS.subject_id = S.id WHERE CS.cycle_id = ?",
        (cycle_id,)
    )


def test_get_cycle_subject_not_found(cycle_subject_service, mock_db_connection):
    """Test retrieving a single cycle subject that does not exist."""
    cycle_subject_id = 999
    mock_db_connection.execute.return_value.fetchone.return_value = None

    result = cycle_subject_service.get_cycle_subject(cycle_subject_id)

    assert result is None
    mock_db_connection.execute.assert_called_once_with(
        "SELECT CS.id, CS.cycle_id, CS.subject_id, CS.relevance_weight, CS.volume_weight, CS.difficulty_weight, CS.is_active, CS.final_weight_calc, CS.num_blocks_in_cycle, CS.date_added, CS.current_strategic_state, CS.state_hysteresis_data, S.name, S.color FROM cycle_subjects AS CS JOIN subjects AS S ON CS.subject_id = S.id WHERE CS.id = ?",
        (cycle_subject_id,)
    )


def test_get_cycle_subject_found(cycle_subject_service, mock_db_connection):
    """Test retrieving a single cycle subject that exists."""
    cycle_subject_id = 1
    mock_row = {
        'id': cycle_subject_id, 'cycle_id': 1, 'subject_id': 101, 'relevance_weight': 1,
        'volume_weight': 2, 'difficulty_weight': 3, 'is_active': True,
        'final_weight_calc': 2.5, 'num_blocks_in_cycle': 5, 'name': 'Math',
        'color': 'blue', 'date_added': '2023-01-01', 'current_strategic_state': 'DISCOVERY',
        'state_hysteresis_data': json.dumps({'consecutive_cycles_in_state': 0})
    }
    mock_db_connection.execute.return_value.fetchone.return_value = mock_row

    result = cycle_subject_service.get_cycle_subject(cycle_subject_id)

    assert result is not None
    assert result.id == cycle_subject_id
    assert result.name == 'Math'
    assert result.state_hysteresis_data == {'consecutive_cycles_in_state': 0}
    mock_db_connection.execute.assert_called_once_with(
        "SELECT CS.id, CS.cycle_id, CS.subject_id, CS.relevance_weight, CS.volume_weight, CS.difficulty_weight, CS.is_active, CS.final_weight_calc, CS.num_blocks_in_cycle, CS.date_added, CS.current_strategic_state, CS.state_hysteresis_data, S.name, S.color FROM cycle_subjects AS CS JOIN subjects AS S ON CS.subject_id = S.id WHERE CS.id = ?",
        (cycle_subject_id,)
    )


def test_delete_subjects_for_cycle(cycle_subject_service, mock_db_connection):
    """Test deleting all subjects for a given cycle."""
    cycle_id = 1
    cycle_subject_service.delete_subjects_for_cycle(cycle_id)

    mock_db_connection.execute.assert_called_once_with(
        "DELETE FROM cycle_subjects WHERE cycle_id = ?",
        (cycle_id,)
    )
    mock_db_connection.commit.assert_called_once()


def test_update_cycle_subject_difficulty(cycle_subject_service, mock_db_connection):
    """Test updating the difficulty weight of a cycle subject."""
    cycle_subject_id = 1
    new_difficulty = 5
    cycle_subject_service.update_cycle_subject_difficulty(cycle_subject_id, new_difficulty)

    mock_db_connection.execute.assert_called_once_with(
        "UPDATE cycle_subjects SET difficulty_weight = ? WHERE id = ?",
        (new_difficulty, cycle_subject_id)
    )
    mock_db_connection.commit.assert_called_once()


def test_update_cycle_subject_calculated_fields(cycle_subject_service, mock_db_connection):
    """Test updating calculated fields of a cycle subject."""
    cycle_subject_id = 1
    final_weight = 3.0
    num_blocks = 6
    cycle_subject_service.update_cycle_subject_calculated_fields(cycle_subject_id, final_weight, num_blocks)

    mock_db_connection.execute.assert_called_once_with(
        "UPDATE cycle_subjects SET final_weight_calc = ?, num_blocks_in_cycle = ? WHERE id = ?",
        (final_weight, num_blocks, cycle_subject_id)
    )
    mock_db_connection.commit.assert_called_once()


def test_update_cycle_subject_state(cycle_subject_service, mock_db_connection):
    """Test updating the strategic state and hysteresis data of a cycle subject."""
    cycle_subject_id = 1
    state = "MAINTAIN"
    hysteresis_data = {'consecutive_cycles_in_state': 1, 'last_transition_date': '2023-01-01'}
    cycle_subject_service.update_cycle_subject_state(cycle_subject_id, state, hysteresis_data)

    mock_db_connection.execute.assert_called_once_with(
        "UPDATE cycle_subjects SET current_strategic_state = ?, state_hysteresis_data = ? WHERE id = ?",
        (state, json.dumps(hysteresis_data), cycle_subject_id)
    )
    mock_db_connection.commit.assert_called_once()