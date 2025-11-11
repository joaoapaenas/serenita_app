# app/core/migrations.py

import logging
import os
import sqlite3
import re
from typing import Union

from sqlalchemy import Connection, text
from sqlalchemy.exc import OperationalError

from app.core.database import IDatabaseConnectionFactory
from app.core.seeder import seed_database_if_new

log = logging.getLogger(__name__)


def _get_current_db_version_sqlite3(cursor: sqlite3.Cursor) -> int:
    try:
        cursor.execute("SELECT version FROM schema_version;")
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO schema_version (version) VALUES (0);")
            cursor.connection.commit()
            return 0
        return result['version']
    except sqlite3.OperationalError:
        log.info("Schema version table not found. Creating it.")
        cursor.execute("CREATE TABLE schema_version (version INTEGER NOT NULL);")
        cursor.execute("INSERT INTO schema_version (version) VALUES (0);")
        cursor.connection.commit()
        return 0

def _set_db_version_sqlite3(cursor: sqlite3.Cursor, version: int):
    cursor.execute("UPDATE schema_version SET version = ?;", (version,))

def _get_current_db_version_sqlalchemy(conn: Connection) -> int:
    try:
        result = conn.execute(text("SELECT version FROM schema_version;")).scalar_one_or_none()
        if result is None:
            conn.execute(text("INSERT INTO schema_version (version) VALUES (0);"))
            return 0
        return result
    except OperationalError:
        log.info("Schema version table not found. Creating it.")
        conn.execute(text("CREATE TABLE schema_version (version INTEGER NOT NULL);"))
        conn.execute(text("INSERT INTO schema_version (version) VALUES (0);"))
        return 0

def _set_db_version_sqlalchemy(conn: Connection, version: int):
    conn.execute(text("UPDATE schema_version SET version = :version;"), {"version": version})


def run_migrations(conn_factory: IDatabaseConnectionFactory, base_path: str):
    """The main application's migration runner."""
    # The main app's connection factory returns sqlite3.Connection, so we keep this path.
    conn = conn_factory.get_connection()
    try:
        # Delegate the core logic to the connection-based runner
        run_migrations_on_connection(conn, base_path)
    finally:
        if conn:
            conn.close()


def run_migrations_on_connection(conn: Union[sqlite3.Connection, Connection], base_path: str):
    """
    Runs all migrations and seeding directly on a provided connection object.
    This function now handles both sqlite3.Connection (for the main app)
    and SQLAlchemy Connection (for tests).
    """
    migrations_dir = os.path.join(base_path, "migrations")
    log.info(f"Applying all migrations to connection in: {migrations_dir}")

    # Determine if it's a sqlite3.Connection or SQLAlchemy Connection
    is_sqlite3_conn = isinstance(conn, sqlite3.Connection)

    if is_sqlite3_conn:
        # For sqlite3.Connection, use cursor-based operations
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);")
        conn.commit()
        current_version = _get_current_db_version_sqlite3(cursor)
    else:
        # For SQLAlchemy Connection, use execute(text())
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);"))
        current_version = _get_current_db_version_sqlalchemy(conn)

    try:
        if not os.path.isdir(migrations_dir):
            log.error(f"Migrations directory not found at {migrations_dir}. Cannot proceed.")
            return
        migration_files = sorted(
            [f for f in os.listdir(migrations_dir) if f.endswith(".sql")],
            key=lambda x: int(x.split('_')[0])
        )
    except (ValueError, IndexError):
        log.error(f"Migration files in {migrations_dir} are not named correctly.")
        return

    applied_migrations = False
    for migration_file in migration_files:
        try:
            file_version = int(migration_file.split('_')[0])
            if file_version > current_version:
                with open(os.path.join(migrations_dir, migration_file), "r", encoding="utf-8") as f:
                    sql_script = f.read()
                    
                if is_sqlite3_conn:
                    cursor.executescript(sql_script)
                    _set_db_version_sqlite3(cursor, file_version)
                    conn.commit()
                else:
                    # For SQLAlchemy, access the underlying sqlite3.Connection and use executescript
                    # This is a workaround as SQLAlchemy's execute does not support multiple statements directly with sqlite
                    dbapi_connection = conn.connection.driver_connection
                    dbapi_connection.executescript(sql_script)
                    _set_db_version_sqlalchemy(conn, file_version)
                
                applied_migrations = True
        except Exception:
            log.error(f"Error applying migration: {migration_file}", exc_info=True)
            if is_sqlite3_conn:
                conn.rollback()
            else:
                # SQLAlchemy connections manage transactions differently,
                # but for a single connection, a rollback might be needed if not in a begin() block
                pass # The seeder uses engine.begin() which handles rollback on exception
            raise

    if current_version == 0 and applied_migrations:
        if is_sqlite3_conn:
            seed_database_if_new(conn, base_path)
        else:
            # For SQLAlchemy, seeding is handled by the seeder itself, or can be adapted here
            pass # The test seeder handles its own data population

    if is_sqlite3_conn:
        conn.commit()
    # SQLAlchemy connections commit implicitly if used with engine.begin() or explicitly if not.