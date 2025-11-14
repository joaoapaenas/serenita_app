import pytest
from unittest.mock import MagicMock, call
from datetime import datetime, timedelta
import textwrap

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.services.analytics_service import SqliteAnalyticsService
from app.core.database import IDatabaseConnectionFactory
from app.services.interfaces import DailyPerformance, WeeklyPerformance


@pytest.fixture
def mock_db_connection():
    """Fixture for a mock database connection."""
    conn = MagicMock()
    conn.__class__ = Connection # Indicate it's a SQLAlchemy Connection for isinstance checks

    # Mock the execute method directly
    conn.execute.return_value.mappings.return_value.fetchall.return_value = [] # Default for fetchall
    conn.execute.return_value.mappings.return_value.fetchone.return_value = None # Default for fetchone

    # Mock context manager behavior
    conn.__enter__.return_value = conn
    conn.__exit__.return_value = None # __exit__ typically returns False or None to propagate exceptions

    return conn


@pytest.fixture
def mock_conn_factory(mock_db_connection):
    """Fixture for a mock database connection factory."""
    factory = MagicMock(spec=IDatabaseConnectionFactory)
    factory.get_connection.return_value = mock_db_connection
    return factory


@pytest.fixture
def analytics_service(mock_conn_factory):
    """Fixture for SqliteAnalyticsService with mocked dependencies."""
    return SqliteAnalyticsService(mock_conn_factory)


def test_get_daily_performance_no_data(analytics_service, mock_db_connection):
    """Test get_daily_performance when no data is returned from the database."""
    cycle_id = 1
    expected_query = """SELECT
                DATE(SS.start_time) as session_date,
                SUM(QP.is_correct) as total_correct,
                COUNT(QP.id) as total_questions
            FROM question_performance AS QP
            JOIN study_sessions AS SS ON QP.session_id = SS.id
            WHERE SS.cycle_id = :cycle_id GROUP BY session_date
                ORDER BY session_date ASC;"""
    
    result = analytics_service.get_daily_performance(cycle_id) # Define result
    mock_db_connection.execute.assert_called_once()
    actual_call_args, _ = mock_db_connection.execute.call_args
    assert "".join(str(actual_call_args[0]).split()) == "".join(str(text(expected_query)).split())
    assert actual_call_args[1] == {"cycle_id": cycle_id}
    assert result == []


def test_get_daily_performance_with_data(analytics_service, mock_db_connection):
    """Test get_daily_performance with some returned data."""
    cycle_id = 1
    mock_rows = [
        {'session_date': '2023-01-01', 'total_correct': 5, 'total_questions': 10},
        {'session_date': '2023-01-02', 'total_correct': 8, 'total_questions': 12},
    ]
    mock_db_connection.execute.return_value.mappings.return_value.fetchall.return_value = mock_rows

    result = analytics_service.get_daily_performance(cycle_id)

    expected = [
        DailyPerformance(date='2023-01-01', questions_done=10, questions_correct=5),
        DailyPerformance(date='2023-01-02', questions_done=12, questions_correct=8),
    ]
    expected_query = """SELECT
                DATE(SS.start_time) as session_date,
                SUM(QP.is_correct) as total_correct,
                COUNT(QP.id) as total_questions
            FROM question_performance AS QP
            JOIN study_sessions AS SS ON QP.session_id = SS.id
            WHERE SS.cycle_id = :cycle_id GROUP BY session_date
                ORDER BY session_date ASC;"""
    mock_db_connection.execute.assert_called_once()
    actual_call_args, _ = mock_db_connection.execute.call_args
    assert "".join(str(actual_call_args[0]).split()) == "".join(str(text(expected_query)).split())
    assert actual_call_args[1] == {"cycle_id": cycle_id}
    assert result == expected


def test_get_daily_performance_with_days_ago(analytics_service, mock_db_connection):
    """Test get_daily_performance with the days_ago parameter."""
    cycle_id = 1
    days_ago = 7
    mock_rows = [
        {'session_date': '2023-01-05', 'total_correct': 5, 'total_questions': 10},
    ]
    mock_db_connection.execute.return_value.mappings.return_value.fetchall.return_value = mock_rows

    result = analytics_service.get_daily_performance(cycle_id, days_ago)

    expected = [
        DailyPerformance(date='2023-01-05', questions_done=10, questions_correct=5),
    ]
    expected_query = """SELECT
                DATE(SS.start_time) as session_date,
                SUM(QP.is_correct) as total_correct,
                COUNT(QP.id) as total_questions
            FROM question_performance AS QP
            JOIN study_sessions AS SS ON QP.session_id = SS.id
            WHERE SS.cycle_id = :cycle_id AND DATE(SS.start_time) >= date('now', '-' || :days_ago || ' days') GROUP BY session_date
                ORDER BY session_date ASC;"""
    mock_db_connection.execute.assert_called_once()
    actual_call_args, _ = mock_db_connection.execute.call_args
    assert "".join(str(actual_call_args[0]).split()) == "".join(str(text(expected_query)).split())
    assert actual_call_args[1] == {"cycle_id": cycle_id, "days_ago": days_ago}
    assert result == expected

def test_get_weekly_summary_no_daily_data(analytics_service, mocker):
    """Test get_weekly_summary when get_daily_performance returns no data."""
    mocker.patch.object(analytics_service, 'get_daily_performance', return_value=[])
    result = analytics_service.get_weekly_summary(1)
    assert result == []


def test_get_weekly_summary_with_data(analytics_service, mocker):
    """Test get_weekly_summary with daily data spanning multiple weeks."""
    mocker.patch.object(analytics_service, 'get_daily_performance', return_value=[
        DailyPerformance(date='2023-01-01', questions_done=10, questions_correct=5),  # Sunday
        DailyPerformance(date='2023-01-02', questions_done=15, questions_correct=10), # Monday (Week 1)
        DailyPerformance(date='2023-01-03', questions_done=20, questions_correct=15), # Tuesday (Week 1)
        DailyPerformance(date='2023-01-08', questions_done=25, questions_correct=20), # Sunday (Week 2)
        DailyPerformance(date='2023-01-09', questions_done=30, questions_correct=25), # Monday (Week 2)
    ])

    result = analytics_service.get_weekly_summary(1)

    expected = [
        WeeklyPerformance(week_start_date='2022-12-26', questions_done=10, questions_correct=5, avg_per_day=10.0),
        WeeklyPerformance(week_start_date='2023-01-02', questions_done=60, questions_correct=45, avg_per_day=20.0),
        WeeklyPerformance(week_start_date='2023-01-09', questions_done=30, questions_correct=25, avg_per_day=30.0)
    ]
    # Sort both lists by week_start_date for consistent comparison
    result.sort(key=lambda x: x.week_start_date)
    expected.sort(key=lambda x: x.week_start_date)
    assert result == expected


def test_get_overall_summary_no_daily_data(analytics_service, mocker):
    """Test get_overall_summary when get_daily_performance returns no data."""
    mocker.patch.object(analytics_service, 'get_daily_performance', return_value=[])
    result = analytics_service.get_overall_summary(1)
    expected = {
        'start_date': None, 'end_date': None, 'days_in_period': 0,
        'total_questions': 0, 'total_correct': 0
    }
    assert result == expected


def test_get_overall_summary_with_data(analytics_service, mocker):
    """Test get_overall_summary with daily data."""
    mocker.patch.object(analytics_service, 'get_daily_performance', return_value=[
        DailyPerformance(date='2023-01-01', questions_done=10, questions_correct=5),
        DailyPerformance(date='2023-01-02', questions_done=15, questions_correct=10),
        DailyPerformance(date='2023-01-03', questions_done=20, questions_correct=15),
    ])
    result = analytics_service.get_overall_summary(1)
    expected = {
        'start_date': '2023-01-01',
        'end_date': '2023-01-03',
        'days_in_period': 3,
        'total_questions': 45,
        'total_correct': 30
    }
    assert result == expected