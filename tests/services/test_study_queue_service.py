import pytest
from unittest.mock import MagicMock, call
import json

from app.services.study_queue_service import SqliteStudyQueueService
from app.core.database import IDatabaseConnectionFactory
from app.models.subject import CycleSubject


@pytest.fixture
def mock_db_connection():
    """Fixture for a mock database connection."""
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = []  # Default to no rows
    conn.execute.return_value.fetchone.return_value = None  # Default to no row
    conn.cursor.return_value = conn # Mock cursor to be the connection itself for simplicity

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
def study_queue_service(mock_conn_factory):
    """Fixture for SqliteStudyQueueService with mocked dependencies."""
    return SqliteStudyQueueService(mock_conn_factory)


def test_save_queue(study_queue_service, mock_db_connection):
    """Test saving a study queue."""
    cycle_id = 1
    queue = [101, 102, 103]

    study_queue_service.save_queue(cycle_id, queue)

    # Verify DELETE call
    mock_db_connection.execute.assert_any_call(
        "DELETE FROM study_queue WHERE cycle_id = ?",
        (cycle_id,)
    )

    # Verify executemany call
    expected_queue_data = [
        (cycle_id, 101, 0),
        (cycle_id, 102, 1),
        (cycle_id, 103, 2),
    ]
    mock_db_connection.executemany.assert_called_once_with(
        "INSERT INTO study_queue (cycle_id, cycle_subject_id, queue_order) VALUES (?, ?, ?)",
        expected_queue_data
    )

    # Verify commit call
    mock_db_connection.commit.assert_called_once()


def test_get_next_in_queue_not_found(study_queue_service, mock_db_connection):
    """Test retrieving the next subject in queue when none is found."""
    cycle_id = 1
    position = 0
    mock_db_connection.execute.return_value.fetchone.return_value = None

    result = study_queue_service.get_next_in_queue(cycle_id, position)

    assert result is None
    mock_db_connection.execute.assert_called_once_with(
        "SELECT CS.*, S.name, S.color FROM study_queue AS Q JOIN cycle_subjects AS CS ON Q.cycle_subject_id = CS.id JOIN subjects AS S ON CS.subject_id = S.id WHERE Q.cycle_id = ? AND Q.queue_order = ?",
        (cycle_id, position)
    )


def test_get_next_in_queue_found(study_queue_service, mock_db_connection):
    """Test retrieving the next subject in queue when one is found."""
    cycle_id = 1
    position = 0
    mock_row = {
        'id': 101,
        'cycle_id': cycle_id,
        'subject_id': 1,
        'relevance_weight': 1,
        'volume_weight': 2,
        'difficulty_weight': 3,
        'is_active': True,
        'final_weight_calc': 2.5,
        'num_blocks_in_cycle': 5,
        'name': 'Math',
        'color': 'blue',
        'date_added': '2023-01-01',
        'current_strategic_state': 'DISCOVERY',
        'state_hysteresis_data': json.dumps({'consecutive_cycles_in_state': 0}),
        'work_units': []
    }
    mock_db_connection.execute.return_value.fetchone.return_value = mock_row

    result = study_queue_service.get_next_in_queue(cycle_id, position)

    assert result is not None
    assert result.id == 101
    assert result.name == 'Math'
    assert result.state_hysteresis_data == {'consecutive_cycles_in_state': 0}
    mock_db_connection.execute.assert_called_once_with(
        "SELECT CS.*, S.name, S.color FROM study_queue AS Q JOIN cycle_subjects AS CS ON Q.cycle_subject_id = CS.id JOIN subjects AS S ON CS.subject_id = S.id WHERE Q.cycle_id = ? AND Q.queue_order = ?",
        (cycle_id, position)
    )