-- 004_add_questions_to_study_sessions.sql
ALTER TABLE study_sessions ADD COLUMN total_questions_done INTEGER DEFAULT 0;
ALTER TABLE study_sessions ADD COLUMN total_questions_correct INTEGER DEFAULT 0;