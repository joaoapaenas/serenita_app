-- Migration 001: Consolidated Initial Schema
-- This schema is re-ordered to respect all FOREIGN KEY dependencies
-- and represents the final state for the application.

-- The schema_version table is created and managed by the migration engine.

-- =============================================================================
-- SECTION 1: LOOKUP TABLES (No Dependencies)
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    study_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Seed the 'System' user required for templates
INSERT OR IGNORE INTO users (id, name, study_level) VALUES (1, 'System', 'Admin');

CREATE TABLE IF NOT EXISTS strategic_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
INSERT OR IGNORE INTO strategic_states (id, name) VALUES
    (1, 'DISCOVERY'), (2, 'DEEP_WORK'), (3, 'CONQUER'),
    (4, 'CEMENT'), (5, 'MAINTAIN');

CREATE TABLE IF NOT EXISTS activity_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
INSERT OR IGNORE INTO activity_types (id, name) VALUES (1, 'THEORY'), (2, 'PRACTICE'), (3, 'REVIEW');

CREATE TABLE IF NOT EXISTS review_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
INSERT OR IGNORE INTO review_types (id, name) VALUES (1, 'R24h'), (2, 'R7d'), (3, 'R30d');

CREATE TABLE IF NOT EXISTS review_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
INSERT OR IGNORE INTO review_statuses (id, name) VALUES (1, 'PENDING'), (2, 'COMPLETED'), (3, 'SKIPPED');


-- =============================================================================
-- SECTION 2: CORE ENTITIES
-- =============================================================================

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    institution TEXT,
    role TEXT,
    exam_board TEXT,
    area TEXT,
    status TEXT DEFAULT 'PREVISTO',
    has_edital INTEGER DEFAULT 0,
    predicted_exam_date TEXT,
    exam_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    soft_delete INTEGER DEFAULT 0,
    deleted_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT,
    strategic_state_id INTEGER DEFAULT 1, -- Default to 'DISCOVERY'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    soft_delete INTEGER DEFAULT 0,
    deleted_at TIMESTAMP,
    FOREIGN KEY (strategic_state_id) REFERENCES strategic_states (id)
);

CREATE TABLE IF NOT EXISTS study_cycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    block_duration_min INTEGER NOT NULL DEFAULT 60,
    current_queue_position INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 0,
    is_continuous INTEGER NOT NULL DEFAULT 0,
    daily_goal_blocks INTEGER NOT NULL DEFAULT 2,
    phase TEXT,
    plan_cache_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    soft_delete INTEGER DEFAULT 0,
    deleted_at TIMESTAMP,
    timing_strategy TEXT DEFAULT 'Adaptative',
    FOREIGN KEY (exam_id) REFERENCES exams (id)
);

-- =============================================================================
-- SECTION 3: JUNCTION AND DETAIL TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    soft_delete INTEGER DEFAULT 0,
    deleted_at TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

CREATE TABLE IF NOT EXISTS template_subjects (
    exam_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    relevance_weight INTEGER NOT NULL DEFAULT 3,
    volume_weight INTEGER NOT NULL DEFAULT 3,
    PRIMARY KEY (exam_id, subject_id),
    FOREIGN KEY (exam_id) REFERENCES exams (id),
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    user_id INTEGER,
    cycle_id INTEGER,
    topic_id INTEGER,
    end_time TIMESTAMP,
    total_duration_sec INTEGER NOT NULL DEFAULT 0,
    total_pause_duration_sec INTEGER NOT NULL DEFAULT 0,
    liquid_duration_sec INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    study_method TEXT,
    user_feedback_effectiveness INTEGER,
    soft_delete INTEGER DEFAULT 0,
    deleted_at TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (cycle_id) REFERENCES study_cycles (id),
    FOREIGN KEY (topic_id) REFERENCES topics (id)
);

CREATE TABLE IF NOT EXISTS study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    topic_id INTEGER,
    activity_type_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_sec INTEGER NOT NULL,
    questions_done INTEGER,
    questions_correct INTEGER,
    FOREIGN KEY (session_id) REFERENCES study_sessions (id),
    FOREIGN KEY (topic_id) REFERENCES topics (id),
    FOREIGN KEY (activity_type_id) REFERENCES activity_types (id)
);

CREATE TABLE IF NOT EXISTS review_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    original_study_activity_id INTEGER NOT NULL,
    scheduled_date TEXT NOT NULL,
    review_type_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL DEFAULT 1, -- Default to 'PENDING'
    completed_date TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics (id),
    FOREIGN KEY (original_study_activity_id) REFERENCES study_activities (id),
    FOREIGN KEY (review_type_id) REFERENCES review_types (id),
    FOREIGN KEY (status_id) REFERENCES review_statuses (id)
);

CREATE TABLE IF NOT EXISTS session_pauses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    pause_time TIMESTAMP NOT NULL,
    resume_time TIMESTAMP,
    duration_sec INTEGER,
    FOREIGN KEY (session_id) REFERENCES study_sessions (id)
);

CREATE TABLE IF NOT EXISTS cycle_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    relevance_weight INTEGER NOT NULL DEFAULT 3,
    volume_weight INTEGER NOT NULL DEFAULT 3,
    difficulty_weight INTEGER NOT NULL DEFAULT 3,
    is_active INTEGER NOT NULL DEFAULT 1,
    final_weight_calc REAL NOT NULL DEFAULT 0,
    num_blocks_in_cycle INTEGER NOT NULL DEFAULT 0,
    date_added TEXT,
    current_strategic_state TEXT DEFAULT 'DISCOVERY',
    state_hysteresis_data TEXT,
    FOREIGN KEY (cycle_id) REFERENCES study_cycles (id),
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

CREATE TABLE IF NOT EXISTS study_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id INTEGER NOT NULL,
    cycle_subject_id INTEGER NOT NULL,
    queue_order INTEGER NOT NULL,
    FOREIGN KEY (cycle_id) REFERENCES study_cycles (id),
    FOREIGN KEY (cycle_subject_id) REFERENCES cycle_subjects (id)
);

CREATE TABLE IF NOT EXISTS work_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    unit_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    estimated_time_minutes INTEGER NOT NULL,
    is_completed INTEGER NOT NULL DEFAULT 0,
    related_questions_topic TEXT,
    sequence_order INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

CREATE TABLE IF NOT EXISTS question_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    topic_name TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL,
    is_correct INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES study_sessions (id)
);

CREATE TABLE IF NOT EXISTS human_factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    energy_level TEXT NOT NULL,
    stress_level TEXT NOT NULL,
    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES users (id)
);


-- =============================================================================
-- SECTION 4: INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_exams_user_id ON exams(user_id);
CREATE INDEX IF NOT EXISTS idx_study_cycles_exam_id ON study_cycles(exam_id);
CREATE INDEX IF NOT EXISTS idx_topics_subject_id ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_cycle_subjects_cycle_id ON cycle_subjects(cycle_id);
CREATE INDEX IF NOT EXISTS idx_study_queue_cycle_id ON study_queue(cycle_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_cycle_id ON study_sessions(cycle_id);
CREATE INDEX IF NOT EXISTS idx_study_activities_session_id ON study_activities(session_id);
CREATE INDEX IF NOT EXISTS idx_review_tasks_status_id ON review_tasks(status_id);
CREATE INDEX IF NOT EXISTS idx_review_tasks_scheduled_date ON review_tasks(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_human_factors_user_id ON human_factors(user_id);


-- =============================================================================
-- SECTION 5: TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- =============================================================================

CREATE TRIGGER IF NOT EXISTS trg_update_subjects_updated_at
AFTER UPDATE ON subjects FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE subjects SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_update_topics_updated_at
AFTER UPDATE ON topics FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE topics SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_update_study_cycles_updated_at
AFTER UPDATE ON study_cycles FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE study_cycles SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_update_exams_updated_at
AFTER UPDATE ON exams FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE exams SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;