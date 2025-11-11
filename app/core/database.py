# app/core/database.py

import logging
import os
import sqlite3
from typing import Protocol

log = logging.getLogger(__name__)



# Define paths relative to a passed-in base path for robustness.
def get_db_file_path(base_path: str) -> str:
    """Constructs the full path to the database file."""
    # The database file is located in the root of the base_path
    return os.path.join(base_path, "study_app.db")


def get_seed_file_path(base_path: str) -> str:
    """Constructs the full path to the main seed data SQL file."""
    return os.path.join(base_path, "app", "assets", "sql", "seed.sql")


def get_templates_file_path(base_path: str) -> str:
    """Constructs the full path to the templates data SQL file."""
    return os.path.join(base_path, "app", "assets", "sql", "templates.sql")


class IDatabaseConnectionFactory(Protocol):
    """
    An abstraction for a component that provides database connections.
    This allows services to depend on an interface, not a concrete implementation,
    improving testability and flexibility.
    """

    def get_connection(self) -> sqlite3.Connection: ...


class SqliteConnectionFactory(IDatabaseConnectionFactory):
    """The concrete implementation for creating SQLite database connections."""

    def __init__(self, db_path: str):
        self._db_path = db_path

        if self._db_path != ":memory:" and not self._db_path.startswith("file:"):
            db_dir = os.path.dirname(self._db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

        log.info(f"Database connection factory initialized for path: {self._db_path}")

    def get_connection(self) -> sqlite3.Connection:
        is_uri = self._db_path.startswith("file:")
        if is_uri:
            conn = sqlite3.connect(self._db_path, uri=True)
        else:
            conn = sqlite3.connect(self._db_path)


        conn.row_factory = sqlite3.Row
        return conn