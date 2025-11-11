import pytest
from unittest.mock import MagicMock, call
import sqlite3

from app.services.performance_service import SqlitePerformanceService
from app.core.database import IDatabaseConnectionFactory
from app.models.session import SubjectPerformance


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
def performance_service(mock_conn_factory):
    """Fixture for SqlitePerformanceService with mocked dependencies."""
    return SqlitePerformanceService(mock_conn_factory)


def test_get_summary_no_data(performance_service, mock_db_connection):
    """Test get_summary when no data is returned from the database."""
    cycle_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = performance_service.get_summary(cycle_id)

    assert result == []
    mock_db_connection.execute.assert_called_once_with(
        """
                SELECT
                    S.name AS subject_name,
                    COUNT(QP.id) AS total_questions,
                    SUM(QP.is_correct) AS total_correct
                FROM question_performance AS QP
                JOIN study_sessions AS SS ON QP.session_id = SS.id
                JOIN subjects AS S ON SS.subject_id = S.id
                WHERE SS.cycle_id = ?
                GROUP BY S.name
                ORDER BY S.name;
                """,
        (cycle_id,)
    )


def test_get_summary_with_data(performance_service, mock_db_connection):
    """Test get_summary with some returned data."""
    cycle_id = 1
    mock_rows = [
        {'subject_name': 'Math', 'total_questions': 10, 'total_correct': 7},
        {'subject_name': 'Physics', 'total_questions': 15, 'total_correct': 10},
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = performance_service.get_summary(cycle_id)

    expected = [
        SubjectPerformance(subject_name='Math', total_questions=10, total_correct=7),
        SubjectPerformance(subject_name='Physics', total_questions=15, total_correct=10),
    ]
    assert result == expected
    mock_db_connection.execute.assert_called_once_with(
        """
                SELECT
                    S.name AS subject_name,
                    COUNT(QP.id) AS total_questions,
                    SUM(QP.is_correct) AS total_correct
                FROM question_performance AS QP
                JOIN study_sessions AS SS ON QP.session_id = SS.id
                JOIN subjects AS S ON SS.subject_id = S.id
                WHERE SS.cycle_id = ?
                GROUP BY S.name
                ORDER BY S.name;
                """,
        (cycle_id,)
    )


def test_get_performance_over_time_no_data(performance_service, mock_db_connection):
    """Test get_performance_over_time when no data is returned."""
    user_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = performance_service.get_performance_over_time(user_id)

    assert result == []
    mock_db_connection.execute.assert_called_once()
    args, kwargs = mock_db_connection.execute.call_args
    assert "WHERE SS.user_id = ?" in args[0]
    assert "AND SS.subject_id = ?" not in args[0]
    assert args[1] == (user_id,)


def test_get_performance_over_time_with_data(performance_service, mock_db_connection):
    """Test get_performance_over_time with some data and subject_id."""
    user_id = 1
    subject_id = 101
    mock_rows = [
        {'date': '2023-01-01', 'total_questions': 10, 'total_correct': 5},
        {'date': '2023-01-02', 'total_questions': 12, 'total_correct': 8},
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = performance_service.get_performance_over_time(user_id, subject_id)

    expected = [
        {'date': '2023-01-01', 'total_questions': 10, 'total_correct': 5},
        {'date': '2023-01-02', 'total_questions': 12, 'total_correct': 8},
    ]
    assert result == expected
    mock_db_connection.execute.assert_called_once()
    args, kwargs = mock_db_connection.execute.call_args
    assert "SELECT strftime('%Y-%m-%d', SS.start_time) as date" in args[0]
    assert "FROM question_performance AS QP" in args[0]
    assert "JOIN study_sessions AS SS ON QP.session_id = SS.id" in args[0]
    assert "WHERE SS.user_id = ?" in args[0]
    assert "AND SS.subject_id = ?" in args[0]
    assert "GROUP BY date" in args[0]
    assert "ORDER BY date ASC;" in args[0]
    assert args[1] == (user_id, subject_id)


def test_get_subjects_with_performance_data_no_data(performance_service, mock_db_connection):
    """Test get_subjects_with_performance_data when no data is returned."""
    user_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = performance_service.get_subjects_with_performance_data(user_id)

    assert result == []
    mock_db_connection.execute.assert_called_once_with(
        """
                SELECT DISTINCT
                    S.id,
                    S.name
                FROM subjects AS S
                JOIN study_sessions AS SS ON S.id = SS.subject_id
                WHERE SS.user_id = ?
                  -- This subquery ensures we only list subjects that actually have questions logged
                  AND SS.id IN (SELECT DISTINCT session_id FROM question_performance)
                ORDER BY S.name ASC;
            """,
        (user_id,)
    )


def test_get_subjects_with_performance_data_with_data(performance_service, mock_db_connection):
    """Test get_subjects_with_performance_data with some data."""
    user_id = 1
    mock_rows = [
        {'id': 1, 'name': 'Math'},
        {'id': 2, 'name': 'Physics'},
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = performance_service.get_subjects_with_performance_data(user_id)

    expected = [{'id': 1, 'name': 'Math'}, {'id': 2, 'name': 'Physics'}]
    assert result == expected
    mock_db_connection.execute.assert_called_once_with(
        """
                SELECT DISTINCT
                    S.id,
                    S.name
                FROM subjects AS S
                JOIN study_sessions AS SS ON S.id = SS.subject_id
                WHERE SS.user_id = ?
                  -- This subquery ensures we only list subjects that actually have questions logged
                  AND SS.id IN (SELECT DISTINCT session_id FROM question_performance)
                ORDER BY S.name ASC;
            """,
        (user_id,)
    )


def test_get_topic_performance_no_data(performance_service, mock_db_connection):
    """Test get_topic_performance when no data is returned."""
    user_id = 1
    subject_id = 101
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = performance_service.get_topic_performance(user_id, subject_id)

    assert result == []
    mock_db_connection.execute.assert_called_once()
    args, kwargs = mock_db_connection.execute.call_args
    assert "WHERE SS.user_id = ? AND SS.subject_id = ? AND QP.topic_name != 'general'" in args[0]
    assert "AND date(SS.start_time) >= date('now', '-' || ? || ' days')" not in args[0]
    assert args[1] == (user_id, subject_id)


def test_get_topic_performance_with_data(performance_service, mock_db_connection):
    """Test get_topic_performance with some data and days_ago."""
    user_id = 1
    subject_id = 101
    days_ago = 7
    mock_rows = [
        {'topic_name': 'Algebra', 'total_questions': 20, 'total_correct': 15},
        {'topic_name': 'Geometry', 'total_questions': 10, 'total_correct': 5},
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = performance_service.get_topic_performance(user_id, subject_id, days_ago)

    expected = [
        {'topic_name': 'Algebra', 'total_questions': 20, 'total_correct': 15, 'accuracy': 75.0},
        {'topic_name': 'Geometry', 'total_questions': 10, 'total_correct': 5, 'accuracy': 50.0},
    ]
    assert result == expected
    mock_db_connection.execute.assert_called_once_with(
        """
                SELECT
                    QP.topic_name,
                    COUNT(QP.id) AS total_questions,
                    SUM(QP.is_correct) AS total_correct
                FROM question_performance AS QP
                JOIN study_sessions SS ON QP.session_id = SS.id
                WHERE SS.user_id = ? AND SS.subject_id = ? AND QP.topic_name != 'general'
             AND date(SS.start_time) >= date('now', '-' || ? || ' days')
                GROUP BY QP.topic_name
                ORDER BY total_correct * 1.0 / total_questions ASC;
            """,
        (user_id, subject_id, days_ago)
    )


def test_get_work_unit_summary_no_data(performance_service, mock_db_connection):
    """Test get_work_unit_summary when no data is returned."""
    user_id = 1
    mock_db_connection.execute.return_value.fetchone.return_value = {'total_units': None, 'completed_units': None}

    result = performance_service.get_work_unit_summary(user_id)

    expected = {'total_units': 0, 'completed_units': 0}
    assert result == expected
    mock_db_connection.execute.assert_called_once_with(
        "SELECT COUNT(id) AS total_units, SUM(is_completed) AS completed_units FROM work_units",
        ()
    )


def test_get_work_unit_summary_with_data(performance_service, mock_db_connection):
    """Test get_work_unit_summary with some data and subject_id."""
    user_id = 1
    subject_id = 101
    mock_db_connection.execute.return_value.fetchone.return_value = {'total_units': 5, 'completed_units': 3}

    result = performance_service.get_work_unit_summary(user_id, subject_id)

    expected = {'total_units': 5, 'completed_units': 3}
    assert result == expected
    mock_db_connection.execute.assert_called_once_with(
        "SELECT COUNT(id) AS total_units, SUM(is_completed) AS completed_units FROM work_units WHERE subject_id = ?",
        (subject_id,)
    )


def test_get_study_time_summary_no_data(performance_service, mock_db_connection):
    """Test get_study_time_summary when no data is returned."""
    user_id = 1
    days_ago = 30
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = performance_service.get_study_time_summary(user_id, days_ago)

    assert result == {}
    mock_db_connection.execute.assert_called_once_with(
        """
                SELECT
                    subject_id,
                    SUM(liquid_duration_sec) as total_seconds
                FROM study_sessions
                WHERE
                    user_id = ? AND
                    end_time IS NOT NULL AND
                    date(start_time) >= date('now', '-' || ? || ' days')
                GROUP BY subject_id;
                """,
        (user_id, days_ago)
    )

def test_get_study_time_summary_with_data(performance_service, mock_db_connection):
    """Test get_study_time_summary with some data."""
    user_id = 1
    days_ago = 30
    mock_rows = [
        {'subject_id': 101, 'total_seconds': 3600},
        {'subject_id': 102, 'total_seconds': 1800},
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = performance_service.get_study_time_summary(user_id, days_ago)

    expected = {101: 3600, 102: 1800}
    assert result == expected
    mock_db_connection.execute.assert_called_once_with(
        """
                SELECT
                    subject_id,
                    SUM(liquid_duration_sec) as total_seconds
                FROM study_sessions
                WHERE
                    user_id = ? AND
                    end_time IS NOT NULL AND
                    date(start_time) >= date('now', '-' || ? || ' days')
                GROUP BY subject_id;
                """,
        (user_id, days_ago)
    )

def test_get_study_session_summary_no_data(performance_service, mock_db_connection):
    """Test get_study_session_summary when no data is returned."""
    user_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = performance_service.get_study_session_summary(user_id)

    assert result == {}
    mock_db_connection.execute.assert_called_once()
    args, kwargs = mock_db_connection.execute.call_args
    assert """
                SELECT
                    subject_id,
                    COUNT(id) as session_count
                FROM study_sessions
                WHERE
                    user_id = ? AND
                    end_time IS NOT NULL
             GROUP BY subject_id;""" in args[0]
    assert args[1] == (user_id,)
def test_get_study_session_summary_with_data(performance_service, mock_db_connection):
    """Test get_study_session_summary with some data and days_ago."""
    user_id = 1
    days_ago = 7
    mock_rows = [
        {'subject_id': 101, 'session_count': 5},
        {'subject_id': 102, 'session_count': 3},
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = performance_service.get_study_session_summary(user_id, days_ago)

    expected = {101: 5, 102: 3}
    assert result == expected
    mock_db_connection.execute.assert_called_once()
    args, kwargs = mock_db_connection.execute.call_args
    assert """
                SELECT
                    subject_id,
                    COUNT(id) as session_count
                FROM study_sessions
                WHERE
                    user_id = ? AND
                    end_time IS NOT NULL
             AND date(start_time) >= date('now', '-' || ? || ' days') GROUP BY subject_id;""" in args[0]
    assert args[1] == (user_id, days_ago)

def test_get_subject_summary_for_analytics_no_data(performance_service, mock_db_connection):
    """Test get_subject_summary_for_analytics when no data is returned."""
    user_id = 1
    cycle_id = 1
    mock_db_connection.execute.return_value.fetchall.return_value = []

    result = performance_service.get_subject_summary_for_analytics(user_id, cycle_id)

    assert result == []
    mock_db_connection.execute.assert_called_once()
    args, kwargs = mock_db_connection.execute.call_args
    assert "FROM cycle_subjects cs" in args[0]
    assert "WHERE cs.cycle_id = ?" in args[0]
    assert "date_filter_clause" not in args[0] # Ensure no date filter
    assert args[1] == (user_id, cycle_id, user_id, cycle_id, cycle_id)


def test_get_subject_summary_for_analytics_with_data(performance_service, mock_db_connection):
    """Test get_subject_summary_for_analytics with some data and days_ago."""
    user_id = 1
    cycle_id = 1
    days_ago = 30
    mock_rows = [
        {
            'subject_name': 'Math', 'subject_id': 101, 'total_study_minutes': 60,
            'session_count': 2, 'total_questions': 20, 'total_correct': 15
        },
        {
            'subject_name': 'Physics', 'subject_id': 102, 'total_study_minutes': 30,
            'session_count': 1, 'total_questions': 10, 'total_correct': 5
        },
    ]
    mock_db_connection.execute.return_value.fetchall.return_value = mock_rows

    result = performance_service.get_subject_summary_for_analytics(user_id, cycle_id, days_ago)

    expected = [
        {
            'subject_name': 'Math', 'subject_id': 101, 'total_study_minutes': 60,
            'session_count': 2, 'total_questions': 20, 'total_correct': 15, 'accuracy': 75.0
        },
        {
            'subject_name': 'Physics', 'subject_id': 102, 'total_study_minutes': 30,
            'session_count': 1, 'total_questions': 10, 'total_correct': 5, 'accuracy': 50.0
        },
    ]
    assert result == expected
    mock_db_connection.execute.assert_called_once()
    args, kwargs = mock_db_connection.execute.call_args
    assert "date(start_time) >= date('now', '-' || ? || ' days')" in args[0] # Ensure date filter is present
    assert args[1] == (user_id, cycle_id, days_ago, user_id, cycle_id, days_ago, cycle_id)