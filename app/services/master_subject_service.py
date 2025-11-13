# app/services/master_subject_service.py
import logging
from typing import List, Optional

from app.core.database import IDatabaseConnectionFactory
from app.models.subject import Subject, Topic
from app.services.interfaces import IMasterSubjectService

log = logging.getLogger(__name__)


class SqliteMasterSubjectService(IMasterSubjectService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def get_master_subject_by_name(self, name: str) -> Optional[Subject]:
        conn = self._conn_factory.get_connection()
        row = conn.execute("SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE name = ?", (name,)).fetchone()
        return Subject(**dict(row)) if row else None

    def get_all_master_subjects(self) -> List[Subject]:
        conn = self._conn_factory.get_connection()
        rows = conn.execute("SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE soft_delete = 0 ORDER BY name ASC").fetchall()
        return [Subject(**dict(row)) for row in rows]

    def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        conn = self._conn_factory.get_connection()
        row = conn.execute("SELECT id, name, color, created_at, updated_at, soft_delete, deleted_at FROM subjects WHERE id = ?", (subject_id,)).fetchone()
        return Subject(**dict(row)) if row else None

    def create(self, name: str) -> int | None:
        conn = self._conn_factory.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            new_id = cursor.lastrowid
            conn.commit()
            return new_id
        except conn.IntegrityError:
            log.error(f"Integrity error while creating subject '{name}'. It might already exist.")
            return None

    def update(self, subject_id: int, name: str):
        conn = self._conn_factory.get_connection()
        try:
            conn.execute("UPDATE subjects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (name, subject_id))
            conn.commit()
        except conn.IntegrityError:
            log.error(f"Integrity error while updating subject {subject_id} to name '{name}'.")
            raise

    def delete(self, subject_id: int):
        conn = self._conn_factory.get_connection()
        # Also delete related topics to maintain database integrity.
        # This assumes no foreign key cascade is set up.
        conn.execute("DELETE FROM topics WHERE subject_id = ?", (subject_id,))
        conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()

    def get_topics_for_subject(self, subject_id: int) -> List[Topic]:
        conn = self._conn_factory.get_connection()
        rows = conn.execute("SELECT id, subject_id, name, description, created_at, updated_at, soft_delete, deleted_at FROM topics WHERE subject_id = ? ORDER BY name ASC", (subject_id,)).fetchall()
        return [Topic(**dict(row)) for row in rows]