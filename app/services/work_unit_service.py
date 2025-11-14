# app/services/work_unit_service.py
import logging
from typing import List, Optional

from app.core.database import IDatabaseConnectionFactory
from app.models.subject import WorkUnit
from app.services import BaseService
from app.services.interfaces import IWorkUnitService

log = logging.getLogger(__name__)


class SqliteWorkUnitService(BaseService, IWorkUnitService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        super().__init__(conn_factory)

    def get_work_units_for_subject(self, subject_id: int) -> List[WorkUnit]:
        rows = self._execute_query("SELECT * FROM work_units WHERE subject_id = ? ORDER BY sequence_order ASC",
                                 (subject_id,)).fetchall()
        return self._map_rows_to_model_list(rows, WorkUnit)

    def add_work_unit(self, subject_id: int, unit_data: dict) -> Optional[WorkUnit]:
        conn = None
        try:
            conn = self._conn_factory.get_connection()
            placeholder_unit_id = 'pending_id_creation'
            cursor = conn.execute(
                "INSERT INTO work_units (subject_id, unit_id, title, type, estimated_time_minutes, related_questions_topic, sequence_order) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (subject_id, placeholder_unit_id, unit_data['title'], unit_data['type'], unit_data['estimated_time'],
                 unit_data['topic'], 0))
            new_id = cursor.lastrowid
            if not new_id:
                log.error("Failed to get lastrowid after insert for work unit.")
                conn.rollback()
                return None
            unit_id_str = f"wu_{subject_id}_{new_id}"
            conn.execute("UPDATE work_units SET unit_id = ? WHERE id = ?", (unit_id_str, new_id))
            new_unit_row = conn.execute("SELECT * FROM work_units WHERE id = ?", (new_id,)).fetchone()
            conn.commit()
            return self._map_row_to_model(new_unit_row, WorkUnit)
        except Exception as e:
            log.error(f"Database error adding work unit: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def update_work_unit(self, unit_id: int, unit_data: dict) -> bool:
        try:
            self._execute_query(
                "UPDATE work_units SET title = ?, type = ?, estimated_time_minutes = ?, related_questions_topic = ? WHERE id = ?",
                (unit_data['title'], unit_data['type'], unit_data['estimated_time'], unit_data['topic'], unit_id))
            return True
        except Exception as e:
            log.error(f"Database error updating work unit: {e}", exc_info=True)
            return False

    def delete_work_unit(self, unit_id: int):
        self._execute_query("DELETE FROM work_units WHERE id = ?", (unit_id,))

    def update_work_unit_status(self, work_unit_id: int, is_completed: bool):
        self._execute_query("UPDATE work_units SET is_completed = ? WHERE id = ?", (1 if is_completed else 0, work_unit_id))

    def add_topics_bulk(self, subject_id: int, topic_names: List[str]):
        if not topic_names: return
        data_to_insert = [(subject_id, name) for name in topic_names]
        self._executemany_query("INSERT OR IGNORE INTO topics (subject_id, name) VALUES (?, ?)", data_to_insert)