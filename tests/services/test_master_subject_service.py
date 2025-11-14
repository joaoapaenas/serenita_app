import pytest
from unittest.mock import MagicMock, call
import sqlite3

from app.services.master_subject_service import SqliteMasterSubjectService
from app.core.database import IDatabaseConnectionFactory
from app.models.subject import Subject, Topic


@pytest.fixture
def mock_db_connection():
    """Fixture for a mock database connection."""
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = []  # Default to no rows
    conn.execute.return_value.fetchone.return_value = None  # Default to no row
    conn.cursor.return_value = conn  # Mock cursor to be the connection itself for simplicity
    conn.IntegrityError = sqlite3.IntegrityError # Attach a mock for the database IntegrityError

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
def master_subject_service(mock_conn_factory):
    """Fixture for SqliteMasterSubjectService with mocked dependencies."""
    return SqliteMasterSubjectService(mock_conn_factory)


def test_get_master_subject_by_name_found(master_subject_service, mock_db_connection):
    """Test retrieving a master subject by name when it exists."""
    subject_name = "Math"
    mock_row = {
        'id': 1, 'name': subject_name, 'color': 'blue',
        'created_at': '2023-01-01 00:00:00', 'updated_at': '2023-01-01 00:00:00',
        'soft_delete': False, 'deleted_at': None
    }
    mock_db_connection.execute.return_value.fetchone.return_value = mock_row

    result = master_subject_service.get_master_subject_by_name(subject_name)

    assert result is not None
    assert result.name == subject_name
    assert result.id == 1
    mock_db_connection.execute.assert_called_once_with(
        "SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE name = ?",
        (subject_name,)
    )


def test_get_master_subject_by_name_not_found(master_subject_service, mock_db_connection):
    """Test retrieving a master subject by name when it does not exist."""
    subject_name = "NonExistent"
    mock_db_connection.execute.return_value.fetchone.return_value = None

    result = master_subject_service.get_master_subject_by_name(subject_name)

    assert result is None
    mock_db_connection.execute.assert_called_once_with(
        "SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE name = ?",
        (subject_name,)
    )


def test_get_all_master_subjects_no_data(master_subject_service, mock_db_connection):
    """Test retrieving all master subjects when none exist."""
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = master_subject_service.get_all_master_subjects()

    mock_db_connection.execute.assert_called_once_with(
        "SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE soft_delete = 0 ORDER BY name ASC",
        ()
    )


def test_get_all_master_subjects_with_data(master_subject_service, mock_db_connection):
    """Test retrieving all master subjects with existing data."""
    mock_rows = [
        {
            'id': 1, 'name': 'Math', 'color': 'blue',
            'created_at': '2023-01-01 00:00:00', 'updated_at': '2023-01-01 00:00:00',
            'soft_delete': False, 'deleted_at': None
        },
        {
            'id': 2, 'name': 'Physics', 'color': 'red',
            'created_at': '2023-01-02 00:00:00', 'updated_at': '2023-01-02 00:00:00',
            'soft_delete': False, 'deleted_at': None
        },
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = master_subject_service.get_all_master_subjects()

    assert len(result) == 2
    assert result[0].name == 'Math'
    assert result[1].name == 'Physics'
    mock_db_connection.execute.assert_called_once_with(
        "SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE soft_delete = 0 ORDER BY name ASC",
        ()
    )


def test_create_master_subject_success(master_subject_service, mock_db_connection):
    """Test successfully creating a master subject."""
    subject_name = "Chemistry"
    mock_db_connection.execute.return_value.lastrowid = 3

    result = master_subject_service.create(subject_name)

    assert result == 3
    mock_db_connection.execute.assert_called_once_with(
        "INSERT INTO subjects (name) VALUES (?)",
        (subject_name,)
    )
    mock_db_connection.commit.assert_called_once()


def test_create_master_subject_duplicate_name(master_subject_service, mock_db_connection):
    """Test creating a master subject with a duplicate name."""
    subject_name = "Existing Subject"
    mock_db_connection.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: subjects.name")

    result = master_subject_service.create(subject_name)

    assert result is None
    mock_db_connection.execute.assert_called_once_with(
        "INSERT INTO subjects (name) VALUES (?)",
        (subject_name,)
    )
    mock_db_connection.rollback.assert_called_once()


def test_update_master_subject_success(master_subject_service, mock_db_connection):
    """Test successfully updating a master subject's name."""
    subject_id = 1
    old_name = "Old Name"
    new_name = "New Name"

    master_subject_service.update(subject_id, new_name)

    mock_db_connection.execute.assert_called_once_with(
        "UPDATE subjects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_name, subject_id)
    )
    mock_db_connection.commit.assert_called_once()


def test_delete_master_subject_success(master_subject_service, mock_db_connection):
    """Test successfully deleting a master subject and its topics."""
    subject_id = 1
    
    master_subject_service.delete(subject_id)

    # Verify that topics are deleted first, then the subject
    expected_calls = [
        call("DELETE FROM topics WHERE subject_id = ?", (subject_id,)),
        call("DELETE FROM subjects WHERE id = ?", (subject_id,))
    ]
    mock_db_connection.execute.assert_has_calls(expected_calls, any_order=False)
    mock_db_connection.commit.assert_called_once()


def test_get_topics_for_subject_no_data(master_subject_service, mock_db_connection):
    """Test retrieving topics for a subject when none exist."""
    subject_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = master_subject_service.get_topics_for_subject(subject_id)

    assert result == []
    mock_db_connection.execute.assert_called_once_with(
        "SELECT id, subject_id, name, description, created_at, updated_at, soft_delete, deleted_at FROM topics WHERE subject_id = ? ORDER BY name ASC",
        (subject_id,)
    )


def test_get_topics_for_subject_with_data(master_subject_service, mock_db_connection):
    """Test retrieving topics for a subject with existing data."""
    subject_id = 1
    mock_rows = [
        {
            'id': 1, 'subject_id': subject_id, 'name': 'Topic A', 'description': 'Desc A',
            'created_at': '2023-01-01 00:00:00', 'updated_at': '2023-01-01 00:00:00',
            'soft_delete': False, 'deleted_at': None
        },
        {
            'id': 2, 'subject_id': subject_id, 'name': 'Topic B', 'description': 'Desc B',
            'created_at': '2023-01-02 00:00:00', 'updated_at': '2023-01-02 00:00:00',
            'soft_delete': False, 'deleted_at': None
        },
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = master_subject_service.get_topics_for_subject(subject_id)

    assert len(result) == 2
    assert result[0].name == 'Topic A'
    assert result[1].name == 'Topic B'
    mock_db_connection.execute.assert_called_once_with(
        "SELECT id, subject_id, name, description, created_at, updated_at, soft_delete, deleted_at FROM topics WHERE subject_id = ? ORDER BY name ASC",
        (subject_id,)
    )