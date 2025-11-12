# app/services/performance_service.py

import logging
from typing import List, Dict

from app.core.database import IDatabaseConnectionFactory
from app.models.session import SubjectPerformance
from app.services.interfaces import IPerformanceService

log = logging.getLogger(__name__)


class SqlitePerformanceService(IPerformanceService):
    """The concrete SQLite implementation of the IPerformanceService interface."""

    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def get_summary(self, cycle_id: int) -> List[SubjectPerformance]:
        log.debug(f"Getting performance summary for cycle_id: {cycle_id}")
        conn = self._conn_factory.get_connection()
        try:
            # This query has a bug, it relies on study_activities which is not being populated.
            # We will query question_performance directly for a more reliable result.
            rows = conn.execute(
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
                (cycle_id,),
            ).fetchall()

            summary_list = [
                SubjectPerformance(
                    subject_name=row["subject_name"],
                    total_questions=row["total_questions"] or 0,
                    total_correct=row["total_correct"] or 0,
                )
                for row in rows
            ]
            log.debug(f"Found performance data for {len(summary_list)} subjects.")
            return summary_list
        finally:
            conn.close()

    def get_performance_over_time(self, user_id: int, subject_id: int | None = None) -> List[dict]:
        log.debug(f"Getting performance over time for user_id: {user_id}, subject_id: {subject_id}")
        conn = self._conn_factory.get_connection()
        try:
            query = """
                    SELECT strftime('%Y-%m-%d', SS.start_time) as date,
                           COUNT(QP.id)                        as total_questions,
                           SUM(QP.is_correct)                  as total_correct
                    FROM question_performance AS QP
                             JOIN study_sessions AS SS ON QP.session_id = SS.id
                    WHERE SS.user_id = ?
                    """
            params = [user_id]

            if subject_id is not None:
                query += " AND SS.subject_id = ?"
                params.append(subject_id)

            query += """
                GROUP BY date
                ORDER BY date ASC;
            """

            rows = conn.execute(query, tuple(params)).fetchall()

            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_subjects_with_performance_data(self, user_id: int) -> List[dict]:
        log.debug(f"Getting subjects with performance data for user_id: {user_id}")
        conn = self._conn_factory.get_connection()
        try:
            query = """
                SELECT DISTINCT
                    S.id,
                    S.name
                FROM subjects AS S
                JOIN study_sessions AS SS ON S.id = SS.subject_id
                WHERE SS.user_id = ?
                  -- This subquery ensures we only list subjects that actually have questions logged
                  AND SS.id IN (SELECT DISTINCT session_id FROM question_performance)
                ORDER BY S.name ASC;
            """
            rows = conn.execute(query, (user_id,)).fetchall()
            return [{'id': row['id'], 'name': row['name']} for row in rows]
        finally:
            conn.close()

    def get_topic_performance(self, user_id: int, subject_id: int, days_ago: int | None = None) -> List[Dict[str, any]]:
        log.debug(f"Getting topic performance for user:{user_id}, subject:{subject_id}, last {days_ago} days.")
        conn = self._conn_factory.get_connection()
        try:
            query = """
                SELECT
                    QP.topic_name,
                    COUNT(QP.id) AS total_questions,
                    SUM(QP.is_correct) AS total_correct
                FROM question_performance AS QP
                JOIN study_sessions SS ON QP.session_id = SS.id
                WHERE SS.user_id = ? AND SS.subject_id = ? AND QP.topic_name != 'general'
            """
            params = [user_id, subject_id]

            if days_ago is not None:
                query += " AND date(SS.start_time) >= date('now', '-' || ? || ' days')"
                params.append(days_ago)

            query += """
                GROUP BY QP.topic_name
                ORDER BY total_correct * 1.0 / total_questions ASC;
            """

            rows = conn.execute(query, tuple(params)).fetchall()

            results = []
            for row in rows:
                total = row['total_questions']
                correct = row['total_correct'] if row['total_correct'] is not None else 0
                accuracy = (correct / total * 100) if total > 0 else 0
                results.append({**dict(row), 'total_correct': correct, 'accuracy': accuracy})
            return results
        finally:
            conn.close()

    def get_work_unit_summary(self, user_id: int, subject_id: int | None = None) -> dict:
        log.debug(f"Getting work unit summary for user_id: {user_id}, subject_id: {subject_id}")
        conn = self._conn_factory.get_connection()
        try:
            query = "SELECT COUNT(id) AS total_units, SUM(is_completed) AS completed_units FROM work_units"
            params = []

            if subject_id is not None:
                query += " WHERE subject_id = ?"
                params.append(subject_id)

            # Note: This query doesn't filter by user, assuming subjects are user-specific via exams.
            # A more complex join would be needed in a multi-user context beyond the current scope.

            row = conn.execute(query, tuple(params)).fetchone()
            if row:
                return {'total_units': row['total_units'] or 0, 'completed_units': row['completed_units'] or 0}
            return {'total_units': 0, 'completed_units': 0}
        finally:
            conn.close()

    def get_study_time_summary(self, user_id: int, days_ago: int) -> dict[int, int]:
        log.debug(f"Getting study time summary for user {user_id} for the last {days_ago} days.")
        conn = self._conn_factory.get_connection()
        try:
            rows = conn.execute(
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
            ).fetchall()

            return {row['subject_id']: row['total_seconds'] for row in rows}
        finally:
            conn.close()

    def get_study_session_summary(self, user_id: int, days_ago: int | None = None) -> dict[int, int]:
        log.debug(f"Getting study session summary for user {user_id} for the last {days_ago} days.")
        conn = self._conn_factory.get_connection()
        try:
            query = """
                SELECT
                    subject_id,
                    COUNT(id) as session_count
                FROM study_sessions
                WHERE
                    user_id = ? AND
                    end_time IS NOT NULL
            """
            params = [user_id]

            if days_ago is not None:
                query += " AND date(start_time) >= date('now', '-' || ? || ' days')"
                params.append(days_ago)

            query += " GROUP BY subject_id;"

            rows = conn.execute(query, tuple(params)).fetchall()
            return {row['subject_id']: row['session_count'] for row in rows}
        finally:
            conn.close()

    def get_subject_summary_for_analytics(self, user_id: int, cycle_id: int, days_ago: int | None = None) -> List[dict]:
        """
        Retrieves a comprehensive summary for each subject within a specific cycle.
        """
        log.debug(f"Getting comprehensive subject summary for user {user_id} and cycle {cycle_id}")
        conn = self._conn_factory.get_connection()
        try:
            query = """
                WITH TimeAndSessions AS (
                    SELECT
                        subject_id,
                        SUM(liquid_duration_sec) / 60 AS total_minutes,
                        COUNT(id) AS session_count
                    FROM study_sessions
                    WHERE user_id = ? AND cycle_id = ? AND end_time IS NOT NULL
                    {date_filter_clause}
                    GROUP BY subject_id
                ),
                QuestionPerf AS (
                    SELECT
                        ss.subject_id,
                        COUNT(qp.id) AS total_questions,
                        SUM(qp.is_correct) AS total_correct
                    FROM question_performance qp
                    JOIN study_sessions ss ON qp.session_id = ss.id
                    WHERE ss.user_id = ? AND ss.cycle_id = ?
                    {date_filter_clause}
                    GROUP BY ss.subject_id
                )
                SELECT
                    s.name AS subject_name,
                    s.id as subject_id,
                    COALESCE(ts.total_minutes, 0) AS total_study_minutes,
                    COALESCE(ts.session_count, 0) AS session_count,
                    COALESCE(qp.total_questions, 0) AS total_questions,
                    COALESCE(qp.total_correct, 0) AS total_correct
                FROM cycle_subjects cs
                JOIN subjects s ON cs.subject_id = s.id
                LEFT JOIN TimeAndSessions ts ON cs.subject_id = ts.subject_id
                LEFT JOIN QuestionPerf qp ON cs.subject_id = qp.subject_id
                WHERE cs.cycle_id = ?
                ORDER BY s.name;
            """

            date_clause = ""
            # Base params for CTEs and final WHERE
            params = [user_id, cycle_id, user_id, cycle_id, cycle_id]
            if days_ago is not None:
                date_clause = "AND date(start_time) >= date('now', '-' || ? || ' days')"
                # Insert the days_ago param for each CTE
                params.insert(2, days_ago)
                params.insert(5, days_ago)

            final_query = query.format(date_filter_clause=date_clause)
            rows = conn.execute(final_query, tuple(params)).fetchall()

            results = []
            for row in rows:
                data = dict(row)
                total_q = data['total_questions']
                total_c = data['total_correct']
                data['accuracy'] = (total_c / total_q * 100) if total_q > 0 else 0.0
                results.append(data)

            return results
        finally:
            conn.close()