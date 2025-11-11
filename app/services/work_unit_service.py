# app/services/work_unit_service.py
import logging
from typing import List, Optional

from app.core.database import IDatabaseConnectionFactory
from app.models.subject import WorkUnit
from app.services.interfaces import IWorkUnitService

log = logging.getLogger(__name__)


class SqliteWorkUnitService(IWorkUnitService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def get_work_units_for_subject(self, subject_id: int) -> List[WorkUnit]:
        conn = self._conn_factory.get_connection()
        rows = conn.execute("SELECT * FROM work_units WHERE subject_id = ? ORDER BY sequence_order ASC",
                         (subject_id,)).fetchall()
        return [WorkUnit(**dict(row)) for row in rows]

    def add_work_unit(self, subject_id: int, unit_data: dict) -> Optional[WorkUnit]:
        conn = self._conn_factory.get_connection()
        try:
            cursor = conn.cursor()
            placeholder_unit_id = 'pending_id_creation'
            cursor.execute(
                "INSERT INTO work_units (subject_id, unit_id, title, type, estimated_time_minutes, related_questions_topic, sequence_order) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (subject_id, placeholder_unit_id, unit_data['title'], unit_data['type'], unit_data['estimated_time'],
                 unit_data['topic'], 0))
            new_id = cursor.lastrowid
            if not new_id: raise conn.Error("Failed to get lastrowid after insert.")
            unit_id_str = f"wu_{subject_id}_{new_id}"
            cursor.execute("UPDATE work_units SET unit_id = ? WHERE id = ?", (unit_id_str, new_id))
            conn.commit()
            new_unit_row = cursor.execute("SELECT * FROM work_units WHERE id = ?", (new_id,)).fetchone()
            return WorkUnit(**dict(new_unit_row)) if new_unit_row else None
        except conn.Error as e:
            log.error(f"Database error adding work unit: {e}", exc_info=True)
            conn.rollback()
            return None

    def update_work_unit(self, unit_id: int, unit_data: dict) -> bool:
        conn = self._conn_factory.get_connection()
        try:
            conn.execute(
                "UPDATE work_units SET title = ?, type = ?, estimated_time_minutes = ?, related_questions_topic = ? WHERE id = ?",
                (unit_data['title'], unit_data['type'], unit_data['estimated_time'], unit_data['topic'], unit_id))
            conn.commit()
            return True
        except conn.Error as e:
            return False

    def delete_work_unit(self, unit_id: int):
        conn = self._conn_factory.get_connection()
        conn.execute("DELETE FROM work_units WHERE id = ?", (unit_id,))
        conn.commit()

    def update_work_unit_status(self, work_unit_id: int, is_completed: bool):
        conn = self._conn_factory.get_connection()
        conn.execute("UPDATE work_units SET is_completed = ? WHERE id = ?", (1 if is_completed else 0, work_unit_id))
        conn.commit()

    def add_topics_bulk(self, subject_id: int, topic_names: List[str]):
        if not topic_names: return
        conn = self._conn_factory.get_connection()
        data_to_insert = [(subject_id, name) for name in topic_names]
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO topics (subject_id, name) VALUES (?, ?)", data_to_insert)
        conn.commit()