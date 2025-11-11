# app/core/analytics_logic.py
from typing import List

from app.services.interfaces import DailyPerformance


def calculate_moving_average(data: List[float], window_size: int = 7) -> List[float]:
    """Calculates a simple moving average."""
    if not data or window_size <= 0:
        return []

    averages = []
    for i in range(len(data)):
        start_index = max(0, i - window_size + 1)
        window = data[start_index:i + 1]
        averages.append(sum(window) / len(window))
    return averages


def calculate_streak_stats(daily_data: List[DailyPerformance], daily_goal: int) -> dict:
    """Calculates current streak, max streak, and success rates."""
    if not daily_data:
        return {
            'current_streak': 0, 'max_streak': 0, 'days_goal_met': 0,
            'total_days_studied': 0
        }

    current_streak = 0
    max_streak = 0
    days_goal_met = 0

    # Check today's streak
    if daily_data[-1].questions_done >= daily_goal:
        current_streak = 1
        for day in reversed(daily_data[:-1]):
            if day.questions_done >= daily_goal:
                current_streak += 1
            else:
                break

    # Calculate max streak
    temp_streak = 0
    for day in daily_data:
        if day.questions_done >= daily_goal:
            temp_streak += 1
            days_goal_met += 1
        else:
            max_streak = max(max_streak, temp_streak)
            temp_streak = 0
    max_streak = max(max_streak, temp_streak)

    return {
        'current_streak': current_streak,
        'max_streak': max_streak,
        'days_goal_met': days_goal_met,
        'total_days_studied': len(daily_data)
    }