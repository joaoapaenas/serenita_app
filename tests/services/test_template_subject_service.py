import pytest
from unittest.mock import MagicMock
import sqlite3

from app.services.template_subject_service import SqliteTemplateSubjectService
from app.core.database import IDatabaseConnectionFactory


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
def template_subject_service(mock_conn_factory):
    """Fixture for SqliteTemplateSubjectService with mocked dependencies."""
    return SqliteTemplateSubjectService(mock_conn_factory)


def test_get_subjects_for_template_no_data(template_subject_service, mock_db_connection):
    """Test retrieving subjects for a template when no data is returned."""
    exam_id = 1
    template_subject_service._execute_query = MagicMock()
    template_subject_service._execute_query.return_value.fetchall.return_value = []

    result = template_subject_service.get_subjects_for_template(exam_id)

    template_subject_service._execute_query.assert_called_once_with(
        "SELECT S.name, TS.relevance_weight, TS.volume_weight FROM template_subjects AS TS JOIN subjects AS S ON TS.subject_id = S.id WHERE TS.exam_id = ?",
        (exam_id,)
    )


def test_get_subjects_for_template_with_data(template_subject_service, mock_db_connection):
    """Test retrieving subjects for a template with existing data."""
    exam_id = 1
    mock_rows = [
        {'name': 'Template Math', 'relevance_weight': 5, 'volume_weight': 3},
        {'name': 'Template Physics', 'relevance_weight': 4, 'volume_weight': 2},
    ]
    template_subject_service._execute_query = MagicMock()
    template_subject_service._execute_query.return_value.fetchall.return_value = mock_rows

    result = template_subject_service.get_subjects_for_template(exam_id)

    expected = [
        {'name': 'Template Math', 'relevance_weight': 5, 'volume_weight': 3},
        {'name': 'Template Physics', 'relevance_weight': 4, 'volume_weight': 2},
    ]
    assert result == expected
    template_subject_service._execute_query.assert_called_once_with(
        "SELECT S.name, TS.relevance_weight, TS.volume_weight FROM template_subjects AS TS JOIN subjects AS S ON TS.subject_id = S.id WHERE TS.exam_id = ?",
        (exam_id,)
    )