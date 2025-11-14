# app/services/master_subject_service.py
import logging
from typing import List, Optional

from app.core.database import IDatabaseConnectionFactory
from app.models.subject import Subject, Topic
from app.services import BaseService
from app.services.interfaces import IMasterSubjectService

log = logging.getLogger(__name__)


class SqliteMasterSubjectService(BaseService, IMasterSubjectService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        super().__init__(conn_factory)

    def get_master_subject_by_name(self, name: str) -> Optional[Subject]:
        row = self._execute_query("SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE name = ?", (name,)).fetchone()
        return self._map_row_to_model(row, Subject)

    def get_all_master_subjects(self) -> List[Subject]:
        rows = self._execute_query("SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE soft_delete = 0 ORDER BY name ASC").fetchall()
        return self._map_rows_to_model_list(rows, Subject)

    def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        row = self._execute_query("SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE id = ?", (subject_id,)).fetchone()
        return self._map_row_to_model(row, Subject)

    def create(self, name: str) -> int | None:
        try:
            cursor = self._execute_query("INSERT INTO subjects (name) VALUES (?)", (name,))
            new_id = cursor.lastrowid
            return new_id
        except Exception as e: # Catch all exceptions, including IntegrityError
            log.error(f"Error creating subject '{name}': {e}", exc_info=True)
            return None

    def update(self, subject_id: int, name: str):
        try:
            self._execute_query("UPDATE subjects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (name, subject_id))
        except Exception as e: # Catch all exceptions, including IntegrityError
            log.error(f"Error updating subject {subject_id} to name '{name}': {e}", exc_info=True)
            raise

    def delete(self, subject_id: int):
        try:
            with self._conn_factory.get_connection() as conn:
                # Delete associated topics first
                conn.execute("DELETE FROM topics WHERE subject_id = ?", (subject_id,))
                # Then delete the subject
                conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
                # The 'with' statement for the connection will handle the commit/rollback
        except Exception as e:
            log.error(f"Error deleting master subject {subject_id}: {e}", exc_info=True)
            raise

    def get_topics_for_subject(self, subject_id: int) -> List[Topic]:
        rows = self._execute_query("SELECT id, subject_id, name, description, created_at, updated_at, soft_delete, deleted_at FROM topics WHERE subject_id = ? ORDER BY name ASC", (subject_id,)).fetchall()
        return self._map_rows_to_model_list(rows, Topic)