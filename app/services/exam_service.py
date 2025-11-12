# app/services/exam_service.py
import logging
from typing import List, Optional
from app.core.database import IDatabaseConnectionFactory
from app.models.exam import Exam
from app.services.interfaces import IExamService
log = logging.getLogger(__name__)

class SqliteExamService(IExamService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def create(self, user_id: int, name: str, institution: str = "", role: str = "", exam_board: str = "", area: str = "", status: str = "PREVISTO", exam_date: str = None, has_edital: int = 0, predicted_exam_date: str = None) -> int:
        with self._conn_factory.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO exams (user_id, name, institution, role, exam_board, area, status, exam_date, has_edital, predicted_exam_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, name, institution, role, exam_board, area, status, exam_date, has_edital, predicted_exam_date))
            new_id = cursor.lastrowid
            conn.commit()
            return new_id

    def get_by_id(self, exam_id: int) -> Optional[Exam]:
        with self._conn_factory.get_connection() as conn:
            row = conn.execute("SELECT * FROM exams WHERE id = ? AND soft_delete = 0", (exam_id,)).fetchone()
            return Exam(**dict(row)) if row else None

    def get_all_for_user(self, user_id: int) -> List[Exam]:
        with self._conn_factory.get_connection() as conn:
            rows = conn.execute("SELECT * FROM exams WHERE user_id = ? AND status != 'TEMPLATE' AND soft_delete = 0 ORDER BY name ASC", (user_id,)).fetchall()
            return [Exam(**dict(row)) for row in rows]

    def update(self, exam_id: int, name: str, institution: str, role: str, exam_board: str, area: str, status: str, exam_date: str, has_edital: int, predicted_exam_date: str):
        with self._conn_factory.get_connection() as conn:
            conn.execute("UPDATE exams SET name = ?, institution = ?, role = ?, exam_board = ?, area = ?, status = ?, exam_date = ?, has_edital = ?, predicted_exam_date = ? WHERE id = ?", (name, institution, role, exam_board, area, status, exam_date, has_edital, predicted_exam_date, exam_id))
            conn.commit()

    def soft_delete(self, exam_id: int):
        with self._conn_factory.get_connection() as conn:
            conn.execute("UPDATE exams SET soft_delete = 1, deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (exam_id,))
            conn.commit()

    def get_available_templates(self) -> List[Exam]:
        with self._conn_factory.get_connection() as conn:
            rows = conn.execute("SELECT * FROM exams WHERE status = 'TEMPLATE' ORDER BY name ASC").fetchall()
            return [Exam(**dict(row)) for row in rows]