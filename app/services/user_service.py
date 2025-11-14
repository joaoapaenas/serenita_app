# app/services/user_service.py
import logging
from typing import Optional, List
from app.core.database import IDatabaseConnectionFactory
from app.models.user import User, HumanFactor
from app.services import BaseService
from app.services.interfaces import IUserService

log = logging.getLogger(__name__)

class SqliteUserService(BaseService, IUserService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        super().__init__(conn_factory)

    def create_user(self, name: str, study_level: str) -> Optional[User]:
        try:
            cursor = self._execute_query("INSERT INTO users (name, study_level) VALUES (?, ?)", (name, study_level))
            new_id = cursor.lastrowid
            row = self._execute_query("SELECT * FROM users WHERE id = ?", (new_id,)).fetchone()
            return self._map_row_to_model(row, User)
        except Exception as e:
            log.error(f"Failed to create user '{name}'.", exc_info=True)
            return None

    def get_user(self, user_id: int) -> Optional[User]:
        row = self._execute_query("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._map_row_to_model(row, User)

    def get_first_user(self) -> Optional[User]:
        row = self._execute_query("SELECT * FROM users WHERE name != 'System' ORDER BY id ASC LIMIT 1").fetchone()
        return self._map_row_to_model(row, User)

    def save_human_factor(self, user_id: int, date: str, energy: str, stress: str) -> int:
        cursor = self._execute_query("INSERT OR REPLACE INTO human_factors (user_id, date, energy_level, stress_level) VALUES (?, ?, ?, ?)", (user_id, date, energy, stress))
        new_id = cursor.lastrowid
        return new_id

    def get_human_factor_history(self, user_id: int, limit: int = 20) -> List[HumanFactor]:
        rows = self._execute_query("SELECT * FROM human_factors WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit)).fetchall()
        return self._map_rows_to_model_list(rows, HumanFactor)

    def update_user(self, user_id: int, name: str, study_level: str, theme: str) -> Optional[User]:
        try:
            self._execute_query("UPDATE users SET name = ?, study_level = ?, theme = ? WHERE id = ?", (name, study_level, theme, user_id))
            row = self._execute_query("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return self._map_row_to_model(row, User)
        except Exception as e:
            log.error(f"Failed to update user {user_id}", exc_info=True)
            return None