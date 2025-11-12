# app/core/seeder.py
import logging
import os
import sqlite3

from app.core.database import get_seed_file_path, get_templates_file_path

log = logging.getLogger(__name__)


def seed_database_if_new(conn: sqlite3.Connection, base_path: str):
    """
    Seeds the database with initial master data (subjects, templates) if the
    relevant tables are empty. This is typically called after the initial migration.
    """
    seeding_flag_path = os.path.join(base_path, ".serenita_seeding_in_progress")
    if os.path.exists(seeding_flag_path):
        log.info("Seeding is temporarily disabled because another seeding process is in progress.")
        return

    seed_file = get_seed_file_path(base_path)
    templates_file = get_templates_file_path(base_path)
    cursor = conn.cursor()

    try:
        # Seed Master Subjects
        log.info("Checking for master subjects to seed...")
        cursor.execute("SELECT COUNT(id) FROM Subjects")
        if cursor.fetchone()[0] == 0:
            log.info(f"Subjects table is empty. Seeding from {os.path.basename(seed_file)}...")
            with open(seed_file, "r", encoding="utf-8") as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
            log.info("Master subjects seeded successfully.")
        else:
            log.info("Subjects table already populated. Skipping master subject seed.")

        # Seed Exam Templates
        log.info("Checking for exam templates to seed...")
        cursor.execute("SELECT COUNT(id) FROM exams WHERE status = 'TEMPLATE'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT id FROM users WHERE name = 'System'")
            system_user = cursor.fetchone()
            # Default to 1 if the 'System' user (from initial seed) isn't found
            system_user_id = system_user['id'] if system_user else 1

            log.info(f"Templates table is empty. Seeding from {os.path.basename(templates_file)}...")
            with open(templates_file, "r", encoding="utf-8") as f:
                template_script = f.read()
                # Replace placeholder with the actual System User ID
                template_script = template_script.replace(':template_user_id', str(system_user_id))
                cursor.executescript(template_script)
            log.info("Exam templates seeded successfully.")
        else:
            log.info("Templates table already populated. Skipping template seed.")

        conn.commit()
    except Exception as e:
        log.error(f"An error occurred during database seeding: {e}", exc_info=True)
        conn.rollback()
