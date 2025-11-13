# app/services/user_service.py
import logging
from typing import Optional, List
from app.core.database import IDatabaseConnectionFactory
from app.models.user import User, HumanFactor
from app.services.interfaces import IUserService

log = logging.getLogger(__name__)

class SqliteUserService(IUserService):
    def __init__(self, conn_factory: IDatabaseConnectionFactory):
        self._conn_factory = conn_factory

    def create_user(self, name: str, study_level: str) -> Optional[User]:
        conn = self._conn_factory.get_connection()
        try:
            cursor = conn.cursor()
            # The 'theme' column will use its default value 'Dark'
            cursor.execute("INSERT INTO users (name, study_level) VALUES (?, ?)", (name, study_level))
            new_id = cursor.lastrowid
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE id = ?", (new_id,)).fetchone()
            return User(**dict(row)) if row else None
        except conn.Error as e:
            log.error(f"Failed to create user '{name}'.", exc_info=True)
            conn.rollback()
            return None

    def get_user(self, user_id: int) -> Optional[User]:
        conn = self._conn_factory.get_connection()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return User(**dict(row)) if row else None

    def get_first_user(self) -> Optional[User]:
        conn = self._conn_factory.get_connection()
        row = conn.execute("SELECT * FROM users WHERE name != 'System' ORDER BY id ASC LIMIT 1").fetchone()
        return User(**dict(row)) if row else None

    def save_human_factor(self, user_id: int, date: str, energy: str, stress: str) -> int:
        conn = self._conn_factory.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO human_factors (user_id, date, energy_level, stress_level) VALUES (?, ?, ?, ?)", (user_id, date, energy, stress))
        new_id = cursor.lastrowid
        conn.commit()
        return new_id

    def get_human_factor_history(self, user_id: int, limit: int = 20) -> List[HumanFactor]:
        conn = self._conn_factory.get_connection()
        rows = conn.execute("SELECT * FROM human_factors WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit)).fetchall()
        return [HumanFactor(**dict(row)) for row in rows]

    def update_user(self, user_id: int, name: str, study_level: str, theme: str) -> Optional[User]:
        conn = self._conn_factory.get_connection()
        try:
            conn.execute("UPDATE users SET name = ?, study_level = ?, theme = ? WHERE id = ?", (name, study_level, theme, user_id))
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return User(**dict(row)) if row else None
        except conn.Error as e:
            log.error(f"Failed to update user {user_id}", exc_info=True)
            conn.rollback()
            return None