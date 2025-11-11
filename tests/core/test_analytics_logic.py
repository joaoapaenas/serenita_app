import pytest
from app.core.analytics_logic import calculate_moving_average, calculate_streak_stats
from app.services.interfaces import DailyPerformance
from datetime import date


# Tests for calculate_moving_average
def test_calculate_moving_average_empty_data():
    assert calculate_moving_average([]) == []


def test_calculate_moving_average_single_element():
    assert calculate_moving_average([10]) == [10.0]


def test_calculate_moving_average_small_list_default_window():
    assert calculate_moving_average([10, 20, 30]) == [10.0, 15.0, 20.0]


def test_calculate_moving_average_larger_list_specified_window():
    data = [10, 20, 30, 40, 50]
    window_size = 3
    expected = [10.0, 15.0, 20.0, 30.0, 40.0]
    assert calculate_moving_average(data, window_size) == expected


def test_calculate_moving_average_window_larger_than_data():
    data = [10, 20]
    window_size = 5
    expected = [10.0, 15.0]
    assert calculate_moving_average(data, window_size) == expected


# Tests for calculate_streak_stats
def test_calculate_streak_stats_empty_data():
    expected = {
        'current_streak': 0, 'max_streak': 0, 'days_goal_met': 0,
        'total_days_studied': 0
    }
    assert calculate_streak_stats([], 5) == expected


def test_calculate_streak_stats_no_streak():
    daily_data = [
        DailyPerformance(date=date(2023, 1, 1), questions_done=3, questions_correct=2),
        DailyPerformance(date=date(2023, 1, 2), questions_done=4, questions_correct=3),
        DailyPerformance(date=date(2023, 1, 3), questions_done=2, questions_correct=1),
    ]
    daily_goal = 5
    expected = {
        'current_streak': 0, 'max_streak': 0, 'days_goal_met': 0,
        'total_days_studied': 3
    }
    assert calculate_streak_stats(daily_data, daily_goal) == expected


def test_calculate_streak_stats_current_streak():
    daily_data = [
        DailyPerformance(date=date(2023, 1, 1), questions_done=3, questions_correct=2),
        DailyPerformance(date=date(2023, 1, 2), questions_done=6, questions_correct=5),
        DailyPerformance(date=date(2023, 1, 3), questions_done=7, questions_correct=6),
    ]
    daily_goal = 5
    expected = {
        'current_streak': 2, 'max_streak': 2, 'days_goal_met': 2,
        'total_days_studied': 3
    }
    assert calculate_streak_stats(daily_data, daily_goal) == expected


def test_calculate_streak_stats_max_streak_not_current():
    daily_data = [
        DailyPerformance(date=date(2023, 1, 1), questions_done=6, questions_correct=5),
        DailyPerformance(date=date(2023, 1, 2), questions_done=7, questions_correct=6),
        DailyPerformance(date=date(2023, 1, 3), questions_done=3, questions_correct=2),
        DailyPerformance(date=date(2023, 1, 4), questions_done=8, questions_correct=7),
    ]
    daily_goal = 5
    expected = {
        'current_streak': 1, 'max_streak': 2, 'days_goal_met': 3,
        'total_days_studied': 4
    }
    assert calculate_streak_stats(daily_data, daily_goal) == expected


def test_calculate_streak_stats_all_days_meet_goal():
    daily_data = [
        DailyPerformance(date=date(2023, 1, 1), questions_done=6, questions_correct=5),
        DailyPerformance(date=date(2023, 1, 2), questions_done=7, questions_correct=6),
        DailyPerformance(date=date(2023, 1, 3), questions_done=8, questions_correct=7),
    ]
    daily_goal = 5
    expected = {
        'current_streak': 3, 'max_streak': 3, 'days_goal_met': 3,
        'total_days_studied': 3
    }
    assert calculate_streak_stats(daily_data, daily_goal) == expected


def test_calculate_streak_stats_mixed_results():
    daily_data = [
        DailyPerformance(date=date(2023, 1, 1), questions_done=6, questions_correct=5),  # Goal
        DailyPerformance(date=date(2023, 1, 2), questions_done=7, questions_correct=6),  # Goal
        DailyPerformance(date=date(2023, 1, 3), questions_done=3, questions_correct=2),  # No Goal
        DailyPerformance(date=date(2023, 1, 4), questions_done=8, questions_correct=7),  # Goal
        DailyPerformance(date=date(2023, 1, 5), questions_done=9, questions_correct=8),  # Goal
        DailyPerformance(date=date(2023, 1, 6), questions_done=4, questions_correct=3),  # No Goal
    ]
    daily_goal = 5
    expected = {
        'current_streak': 0, 'max_streak': 2, 'days_goal_met': 4,
        'total_days_studied': 6
    }
    assert calculate_streak_stats(daily_data, daily_goal) == expected