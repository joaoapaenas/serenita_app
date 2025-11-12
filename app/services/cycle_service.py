# app/services/cycle_service.py
import json
import logging
from typing import List, Optional
from app.core.database import IDatabaseConnectionFactory
from app.models.cycle import Cycle
from app.services.interfaces import ICycleService

log = logging.getLogger(__name__)

class SqliteCycleService(ICycleService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def _set_all_inactive(self):
        with self._conn_factory.get_connection() as conn:
            conn.execute("UPDATE study_cycles SET is_active = 0")
            conn.commit()

    def set_all_inactive(self):
        self._set_all_inactive()

    def create(self, name: str, block_duration: int, is_continuous: bool, daily_goal: int, exam_id: int, timing_strategy: str) -> int:
        self._set_all_inactive()
        with self._conn_factory.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO study_cycles (exam_id, name, block_duration_min, is_active, is_continuous, daily_goal_blocks, timing_strategy) VALUES (?, ?, ?, 1, ?, ?, ?)", (exam_id, name, block_duration, is_continuous, daily_goal, timing_strategy))
            new_id = cursor.lastrowid
            conn.commit()
            return new_id

    def get_active(self) -> Optional[Cycle]:
        with self._conn_factory.get_connection() as conn:
            row = conn.execute("SELECT * FROM study_cycles WHERE is_active = 1 AND soft_delete = 0 LIMIT 1").fetchone()
            return Cycle(**dict(row)) if row else None

    def get_all_for_exam(self, exam_id: int) -> List[Cycle]:
        with self._conn_factory.get_connection() as conn:
            rows = conn.execute("SELECT * FROM study_cycles WHERE exam_id = ? AND soft_delete = 0 ORDER BY id DESC", (exam_id,)).fetchall()
            return [Cycle(**dict(row)) for row in rows]

    def set_active(self, cycle_id: int):
        self._set_all_inactive()
        with self._conn_factory.get_connection() as conn:
            conn.execute("UPDATE study_cycles SET is_active = 1 WHERE id = ?", (cycle_id,))
            conn.commit()

    def soft_delete(self, cycle_id: int):
        with self._conn_factory.get_connection() as conn:
            conn.execute("UPDATE study_cycles SET soft_delete = 1, deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (cycle_id,))
            conn.commit()

    def restore_soft_deleted(self, cycle_id: int):
        with self._conn_factory.get_connection() as conn:
            conn.execute("UPDATE study_cycles SET soft_delete = 0, deleted_at = NULL WHERE id = ?", (cycle_id,))
            conn.commit()

    def update_properties(self, cycle_id: int, name: str, block_duration: int, is_continuous: bool, daily_goal: int, is_active: bool, timing_strategy: str):
        with self._conn_factory.get_connection() as conn:
            conn.execute("UPDATE study_cycles SET name = ?, block_duration_min = ?, is_continuous = ?, daily_goal_blocks = ?, is_active = ?, timing_strategy = ? WHERE id = ?", (name, block_duration, is_continuous, daily_goal, 1 if is_active else 0, timing_strategy, cycle_id))
            conn.commit()

    def get_by_id(self, cycle_id: int) -> Optional[Cycle]:
        with self._conn_factory.get_connection() as conn:
            row = conn.execute("SELECT * FROM study_cycles WHERE id = ? AND soft_delete = 0", (cycle_id,)).fetchone()
            return Cycle(**dict(row)) if row else None

    def advance_queue_position(self, cycle_id: int):
        pass
    def save_plan_cache(self, cycle_id: int, plan_data: dict):
        """Saves a JSON snapshot of the plan to the database."""
        with self._conn_factory.get_connection() as conn:
            try:
                # Create a deep copy to avoid modifying the original plan_data object
                serializable_plan_data = json.loads(json.dumps(plan_data, default=lambda o: o.to_dict() if hasattr(o, 'to_dict') else o))

                plan_json = json.dumps(serializable_plan_data)
                conn.execute(
                    "UPDATE study_cycles SET plan_cache_json = ? WHERE id = ?",
                    (plan_json, cycle_id)
                )
                conn.commit()
                log.debug(f"Saved plan cache for cycle_id {cycle_id}.")
            except Exception as e:
                log.error(f"Failed to save plan cache for cycle {cycle_id}", exc_info=True)
                conn.rollback()

    def get_plan_cache(self, cycle_id: int) -> Optional[dict]:
        """Retrieves the JSON plan snapshot from the database."""
        with self._conn_factory.get_connection() as conn:
            try:
                row = conn.execute(
                    "SELECT plan_cache_json FROM study_cycles WHERE id = ?",
                    (cycle_id,)
                ).fetchone()

                if row and row["plan_cache_json"]:
                    log.debug(f"Retrieved plan cache for cycle_id {cycle_id}.")
                    return json.loads(row["plan_cache_json"])
            except Exception as e:
                log.error(f"Failed to retrieve or parse plan cache for cycle {cycle_id}", exc_info=True)
        return None