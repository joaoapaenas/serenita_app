from typing import List, Optional

from app.core.database import IDatabaseConnectionFactory
from app.models.cycle import Cycle
from app.services import BaseService
from app.services.interfaces import IAnalyticsService, DailyPerformance, WeeklyPerformance

log = logging.getLogger(__name__)


class SqliteAnalyticsService(BaseService, IAnalyticsService):
    """Concrete implementation for time-series performance analytics."""

    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        super().__init__(conn_factory)

    def get_daily_performance(self, cycle_id: int, days_ago: Optional[int] = None) -> List[DailyPerformance]:
        """Gets the total questions and correct answers grouped by day, with an optional date range."""
        query = """
            SELECT
                DATE(SS.start_time) as session_date,
                SUM(QP.is_correct) as total_correct,
                COUNT(QP.id) as total_questions
            FROM question_performance AS QP
            JOIN study_sessions AS SS ON QP.session_id = SS.id
            WHERE SS.cycle_id = ?
        """
        params = [cycle_id]

        if days_ago is not None:
            query += " AND DATE(SS.start_time) >= date('now', '-' || ? || ' days')"
            params.append(days_ago)
        query += " GROUP BY session_date ORDER BY session_date ASC;"
        rows = self._execute_query(query, tuple(params)).fetchall()

        return [
            DailyPerformance(
                date=row['session_date'],
                questions_done=row['total_questions'],
                questions_correct=row['total_correct']
            ) for row in rows
        ]

    def get_weekly_summary(self, cycle_id: int, days_ago: Optional[int] = None) -> List[WeeklyPerformance]:
        """Gets performance aggregated by week."""
        daily_data = self.get_daily_performance(cycle_id, days_ago)
        if not daily_data:
            return []

        weekly_agg = defaultdict(lambda: {'done': 0, 'correct': 0, 'days_studied': set(), 'start_date': None})

        for day in daily_data:
            date_obj = datetime.strptime(day.date, "%Y-%m-%d").date()
            # Group by ISO year and week number
            iso_year, iso_week, _ = date_obj.isocalendar()
            week_key = (iso_year, iso_week)

            if weekly_agg[week_key]['start_date'] is None:
                # Calculate the start of the week (Monday)
                start_of_week = date_obj - timedelta(days=date_obj.weekday())
                weekly_agg[week_key]['start_date'] = start_of_week.strftime("%Y-%m-%d")

            weekly_agg[week_key]['done'] += day.questions_done
            weekly_agg[week_key]['correct'] += day.questions_correct
            weekly_agg[week_key]['days_studied'].add(day.date)

        summary_list = []
        for week, data in sorted(weekly_agg.items()):
            days_in_week = len(data['days_studied'])
            avg = data['done'] / days_in_week if days_in_week > 0 else 0
            summary_list.append(WeeklyPerformance(
                week_start_date=data['start_date'],
                questions_done=data['done'],
                questions_correct=data['correct'],
                avg_per_day=avg
            ))
        return summary_list

    def get_overall_summary(self, cycle_id: int) -> dict:
        """Gets summary statistics for the entire cycle."""
        daily_data = self.get_daily_performance(cycle_id)
        if not daily_data:
            return {
                'start_date': None, 'end_date': None, 'days_in_period': 0,
                'total_questions': 0, 'total_correct': 0
            }

        start_date = daily_data[0].date
        end_date = daily_data[-1].date
        days_in_period = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days + 1
        total_questions = sum(d.questions_done for d in daily_data)
        total_correct = sum(d.questions_correct for d in daily_data)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'days_in_period': days_in_period,
            'total_questions': total_questions,
            'total_correct': total_correct
        }