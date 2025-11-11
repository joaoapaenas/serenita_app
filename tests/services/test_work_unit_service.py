import pytest
from unittest.mock import MagicMock, call
import json
import sqlite3

from app.services.work_unit_service import SqliteWorkUnitService
from app.core.database import IDatabaseConnectionFactory
from app.models.subject import WorkUnit


@pytest.fixture
def mock_db_connection():
    """Fixture for a mock database connection."""
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = []  # Default to no rows
    conn.execute.return_value.fetchone.return_value = None  # Default to no row
    conn.cursor.return_value = conn  # Mock cursor to be the connection itself for simplicity
    conn.Error = sqlite3.Error # Attach a mock for the database error
    return conn


@pytest.fixture
def mock_conn_factory(mock_db_connection):
    """Fixture for a mock database connection factory."""
    factory = MagicMock(spec=IDatabaseConnectionFactory)
    factory.get_connection.return_value = mock_db_connection
    return factory


@pytest.fixture
def work_unit_service(mock_conn_factory):
    """Fixture for SqliteWorkUnitService with mocked dependencies."""
    return SqliteWorkUnitService(mock_conn_factory)


def test_get_work_units_for_subject_no_data(work_unit_service, mock_db_connection):
    """Test retrieving work units for a subject when none exist."""
    subject_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = work_unit_service.get_work_units_for_subject(subject_id)

    assert result == []
    mock_db_connection.execute.assert_called_once_with(
        "SELECT * FROM work_units WHERE subject_id = ? ORDER BY sequence_order ASC",
        (subject_id,)
    )


def test_get_work_units_for_subject_with_data(work_unit_service, mock_db_connection):
    """Test retrieving work units for a subject with existing data."""
    subject_id = 1
    mock_rows = [
        {
            'id': 1, 'subject_id': subject_id, 'unit_id': 'wu_1_1', 'title': 'Chapter 1',
            'type': 'reading', 'estimated_time_minutes': 60, 'is_completed': 0,
            'related_questions_topic': 'Topic A', 'sequence_order': 1
        },
        {
            'id': 2, 'subject_id': subject_id, 'unit_id': 'wu_1_2', 'title': 'Problem Set 1',
            'type': 'problem_set', 'estimated_time_minutes': 30, 'is_completed': 1,
            'related_questions_topic': 'Topic B', 'sequence_order': 2
        },
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = work_unit_service.get_work_units_for_subject(subject_id)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].title == 'Chapter 1'
    assert result[1].id == 2
    assert result[1].title == 'Problem Set 1'
    assert result[1].is_completed == True # SQLite stores bools as 0/1


def test_add_work_unit_success(work_unit_service, mock_db_connection):
    """Test adding a work unit successfully."""
    subject_id = 1
    unit_data = {
        'title': 'New Chapter', 'type': 'reading', 'estimated_time': 45, 'topic': 'New Topic'
    }
    mock_db_connection.lastrowid = 5
    mock_db_connection.execute.return_value.fetchone.return_value = {
        'id': 5, 'subject_id': subject_id, 'unit_id': 'wu_1_5', 'title': 'New Chapter',
        'type': 'reading', 'estimated_time_minutes': 45, 'is_completed': 0,
        'related_questions_topic': 'New Topic', 'sequence_order': 0
    }

    result = work_unit_service.add_work_unit(subject_id, unit_data)

    assert result is not None
    assert result.id == 5
    assert result.unit_id == 'wu_1_5'
    assert mock_db_connection.execute.call_count == 3 # INSERT, UPDATE, SELECT
    mock_db_connection.execute.assert_any_call(
        "INSERT INTO work_units (subject_id, unit_id, title, type, estimated_time_minutes, related_questions_topic, sequence_order) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (subject_id, 'pending_id_creation', unit_data['title'], unit_data['type'], unit_data['estimated_time'],
         unit_data['topic'], 0)
    )
    mock_db_connection.execute.assert_any_call(
        "UPDATE work_units SET unit_id = ? WHERE id = ?",
        ('wu_1_5', 5)
    )
    mock_db_connection.commit.assert_called_once()


def test_add_work_unit_db_error(work_unit_service, mock_db_connection):
    """Test adding a work unit when a database error occurs."""
    subject_id = 1
    unit_data = {
        'title': 'Failing Unit', 'type': 'reading', 'estimated_time': 30, 'topic': 'Error Topic'
    }
    mock_db_connection.execute.side_effect = sqlite3.Error("Mock DB Error")

    result = work_unit_service.add_work_unit(subject_id, unit_data)

    assert result is None
    mock_db_connection.rollback.assert_called_once()
    mock_db_connection.commit.assert_not_called()


def test_update_work_unit_success(work_unit_service, mock_db_connection):
    """Test updating a work unit successfully."""
    unit_id = 1
    unit_data = {
        'title': 'Updated Title', 'type': 'problem_set', 'estimated_time': 90, 'topic': 'Updated Topic'
    }

    result = work_unit_service.update_work_unit(unit_id, unit_data)

    assert result is True
    mock_db_connection.execute.assert_called_once_with(
        "UPDATE work_units SET title = ?, type = ?, estimated_time_minutes = ?, related_questions_topic = ? WHERE id = ?",
        (unit_data['title'], unit_data['type'], unit_data['estimated_time'], unit_data['topic'], unit_id)
    )
    mock_db_connection.commit.assert_called_once()


def test_update_work_unit_db_error(work_unit_service, mock_db_connection):
    """Test updating a work unit when a database error occurs."""
    unit_id = 1
    unit_data = {
        'title': 'Failing Update', 'type': 'reading', 'estimated_time': 10, 'topic': 'Error Topic'
    }
    mock_db_connection.execute.side_effect = sqlite3.Error("Mock DB Error")

    result = work_unit_service.update_work_unit(unit_id, unit_data)

    assert result is False
    mock_db_connection.commit.assert_not_called() # Rollback is not explicitly called in this method, just returns False


def test_delete_work_unit(work_unit_service, mock_db_connection):
    """Test deleting a work unit."""
    unit_id = 1
    work_unit_service.delete_work_unit(unit_id)

    mock_db_connection.execute.assert_called_once_with(
        "DELETE FROM work_units WHERE id = ?",
        (unit_id,)
    )
    mock_db_connection.commit.assert_called_once()


def test_update_work_unit_status(work_unit_service, mock_db_connection):
    """Test updating the completion status of a work unit."""
    work_unit_id = 1
    is_completed = True
    work_unit_service.update_work_unit_status(work_unit_id, is_completed)

    mock_db_connection.execute.assert_called_once_with(
        "UPDATE work_units SET is_completed = ? WHERE id = ?",
        (1, work_unit_id)
    )
    mock_db_connection.commit.assert_called_once()


def test_add_topics_bulk_empty_list(work_unit_service, mock_db_connection):
    """Test bulk adding topics with an empty list."""
    subject_id = 1
    topic_names = []
    work_unit_service.add_topics_bulk(subject_id, topic_names)

    mock_db_connection.executemany.assert_not_called()
    mock_db_connection.commit.assert_not_called()


def test_add_topics_bulk_with_data(work_unit_service, mock_db_connection):
    """Test bulk adding topics with a list of names."""
    subject_id = 1
    topic_names = ["Topic X", "Topic Y"]
    work_unit_service.add_topics_bulk(subject_id, topic_names)

    expected_data = [(subject_id, "Topic X"), (subject_id, "Topic Y")]
    mock_db_connection.executemany.assert_called_once_with(
        "INSERT OR IGNORE INTO topics (subject_id, name) VALUES (?, ?)",
        expected_data
    )
    mock_db_connection.commit.assert_called_once()