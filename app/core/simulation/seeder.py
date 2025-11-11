import json
import random
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from app.core.migrations import run_migrations_on_connection

# Define the base path relative to this file's location
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def seed_profile(profile_path: str, target: str = ":memory:"):
    """Seeds a complete user profile from a JSON file into a SQLite database."""
    if target != ":memory:" and os.path.exists(target):
        os.remove(target)
        
    engine = create_engine(f"sqlite:///{target}")
    # Best Practice: Run actual migrations on the test database to ensure schema parity.
    with engine.connect() as conn:
        run_migrations_on_connection(conn, BASE_PATH)

    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)

    with engine.begin() as conn:
        # 1. Create User
        user_res = conn.execute(text("INSERT INTO users (name, study_level) VALUES (:name, :level) RETURNING id"),
                                {"name": profile['user']['name'], "level": profile['user']['study_level']})
        user_id = user_res.scalar_one()

        # 2. Create Exam
        exam_res = conn.execute(text("INSERT INTO exams (user_id, name, area) VALUES (:uid, :name, :area) RETURNING id"),
                                {"uid": user_id, "name": profile['exam']['name'], "area": profile['exam']['area']})
        exam_id = exam_res.scalar_one()

        # 3. Create Cycle
        cycle_res = conn.execute(text("INSERT INTO study_cycles (exam_id, name, is_active, daily_goal_blocks) VALUES (:eid, :name, :active, :goal) RETURNING id"),
                                 {"eid": exam_id, "name": profile['cycle']['name'], "active": profile['cycle']['is_active'], "goal": profile['cycle']['daily_goal_blocks']})
        cycle_id = cycle_res.scalar_one()

        # 4. Create Subjects and CycleSubjects
        subject_map = {} # Cache subject name to master subject ID
        for s_prof in profile['cycle']['subjects']:
            # Get master subject ID (assumes subjects are pre-seeded by migrations)
            sub_res = conn.execute(text("SELECT id FROM subjects WHERE name = :name"), {"name": s_prof['name']}).scalar_one_or_none()
            if not sub_res:
                # If a subject isn't in the initial seed, create it for the test.
                sub_res = conn.execute(text("INSERT INTO subjects (name) VALUES (:name) RETURNING id"), {"name": s_prof['name']}).scalar_one()
            subject_id = sub_res
            subject_map[s_prof['name']] = subject_id

            # Insert into the junction table
            conn.execute(text("""
                INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight, current_strategic_state)
                VALUES (:cid, :sid, :r, :v, :d, :state)
            """), {"cid": cycle_id, "sid": subject_id, "r": s_prof['relevance_weight'], "v": s_prof['volume_weight'], "d": s_prof['difficulty_weight'], "state": s_prof['current_strategic_state']})

        # 5. Create Sessions and QuestionPerformance
        for sess_prof in profile['cycle']['sessions']:
            subject_id = subject_map[sess_prof['subject_name']]
            start_time = datetime.fromisoformat(sess_prof['start_time'])
            end_time = start_time + timedelta(seconds=sess_prof['liquid_duration_sec'])

            sess_res = conn.execute(text("""
                INSERT INTO study_sessions (user_id, cycle_id, subject_id, start_time, end_time, liquid_duration_sec)
                VALUES (:uid, :cid, :sid, :start, :end, :duration) RETURNING id
            """), {"uid": user_id, "cid": cycle_id, "sid": subject_id, "start": start_time.isoformat(), "end": end_time.isoformat(), "duration": sess_prof['liquid_duration_sec']})
            session_id = sess_res.scalar_one()
            for q_prof in sess_prof['questions']:
                conn.execute(text("""
                    INSERT INTO question_performance (session_id, topic_name, difficulty_level, is_correct)
                    VALUES (:sid, :topic, :diff, :correct)
                """), {"sid": session_id, "topic": q_prof['topic_name'], "diff": random.randint(1, 5), "correct": q_prof['is_correct']})
    return engine

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Seed a SQLite database with a user profile.")
    parser.add_argument("--profile", type=str, required=True, help="Name of the profile JSON file (e.g., 'alex').")
    parser.add_argument("--output", type=str, default=":memory:",
                        help="Output database file path (e.g., 'data/alex.db'). Defaults to in-memory.")

    args = parser.parse_args()

    profile_name = args.profile
    output_db_path = args.output
    profile_path = os.path.join(BASE_PATH, "tests", "fixtures", "profiles", f"{profile_name}.json")

    if not os.path.exists(profile_path):
        print(f"Error: Profile file not found at {profile_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Seeding profile '{profile_name}' into database '{output_db_path}'...")
    try:
        engine = seed_profile(profile_path, target=output_db_path)
        if output_db_path != ":memory:":
            print(f"Database '{output_db_path}' created successfully.")
        else:
            print("In-memory database seeded successfully.")
        engine.dispose()
    except Exception as e:
        print(f"Error seeding database: {e}", file=sys.stderr)
        sys.exit(1)