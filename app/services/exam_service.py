# app/services/exam_service.py
import logging
from typing import List, Optional
from app.core.database import IDatabaseConnectionFactory
from app.models.exam import Exam
from app.services import BaseService
from app.services.interfaces import IExamService
log = logging.getLogger(__name__)

class SqliteExamService(BaseService, IExamService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        super().__init__(conn_factory)

    def create(self, user_id: int, name: str, institution: str = "", role: str = "", exam_board: str = "", area: str = "", status: str = "PREVISTO", exam_date: str = None, has_edital: int = 0, predicted_exam_date: str = None) -> int:
        cursor = self._execute_query("INSERT INTO exams (user_id, name, institution, role, exam_board, area, status, exam_date, has_edital, predicted_exam_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, name, institution, role, exam_board, area, status, exam_date, has_edital, predicted_exam_date))
        new_id = cursor.lastrowid
        return new_id

    def get_by_id(self, exam_id: int) -> Optional[Exam]:
        row = self._execute_query("SELECT * FROM exams WHERE id = ? AND soft_delete = 0", (exam_id,)).fetchone()
        return self._map_row_to_model(row, Exam)

    def get_all_for_user(self, user_id: int) -> List[Exam]:
        rows = self._execute_query("SELECT * FROM exams WHERE user_id = ? AND status != 'TEMPLATE' AND soft_delete = 0 ORDER BY name ASC", (user_id,)).fetchall()
        return self._map_rows_to_model_list(rows, Exam)

    def update(self, exam_id: int, name: str, institution: str, role: str, exam_board: str, area: str, status: str, exam_date: str, has_edital: int, predicted_exam_date: str):
        self._execute_query("UPDATE exams SET name = ?, institution = ?, role = ?, exam_board = ?, area = ?, status = ?, exam_date = ?, has_edital = ?, predicted_exam_date = ? WHERE id = ?", (name, institution, role, exam_board, area, status, exam_date, has_edital, predicted_exam_date, exam_id))

    def soft_delete(self, exam_id: int):
        self._execute_query("UPDATE exams SET soft_delete = 1, deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (exam_id,))

    def get_available_templates(self) -> List[Exam]:
        rows = self._execute_query("SELECT * FROM exams WHERE status = 'TEMPLATE' ORDER BY name ASC").fetchall()
        return self._map_rows_to_model_list(rows, Exam)