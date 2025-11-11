-- ===================================================================================
-- Long-Term User Simulation Seed File
-- ===================================================================================
-- This script populates the database to simulate a user ("Alex Concurseiro")
-- who has been studying for the "Concurso Nacional Unificado" for about 6 months.
--
-- Instructions:
-- 1. Run the application once to create a fresh, migrated database.
-- 2. Close the application.
-- 3. Open the `study_app.db` file with a SQLite browser.
-- 4. Execute this entire script.
-- 5. Relaunch the application.
-- ===================================================================================

BEGIN TRANSACTION;

-- ===================================================================================
-- STEP 1: CLEANUP & USER SETUP
-- ===================================================================================
-- Delete any user created during the initial app run to avoid conflicts.
DELETE FROM users WHERE name != 'System';

-- Create our long-term user, Alex. (ID will be 2)
INSERT INTO users (id, name, study_level, created_at) VALUES
(2, 'Alex Concurseiro', 'Intermediate', '2024-01-01 10:00:00');

-- ===================================================================================
-- STEP 2: EXAM & MASTER SUBJECTS
-- ===================================================================================
-- Create the primary exam goal for Alex.
INSERT INTO exams (id, user_id, name, institution, role, area, predicted_exam_date, created_at) VALUES
(1, 2, 'Concurso Nacional Unificado - Bloco 4', 'Governo Federal', 'Auditor-Fiscal do Trabalho', 'Trabalho e Previdência', '2024-08-25', '2024-01-01 10:01:00');

-- Create the master subjects for this exam area.
INSERT INTO subjects (id, name, created_at) VALUES
(1, 'Políticas Públicas', '2024-01-01 10:02:00'),
(2, 'Direito Constitucional', '2024-01-01 10:02:00'),
(3, 'Direito Administrativo', '2024-01-01 10:02:00'),
(4, 'Administração Financeira e Orçamentária (AFO)', '2024-01-01 10:02:00'),
(5, 'Gestão Governamental e Governança Pública', '2024-01-01 10:02:00'),
(6, 'Sociologia e Psicologia Aplicadas ao Trabalho', '2024-01-01 10:02:00');


-- ===================================================================================
-- STEP 3: HISTORICAL STUDY CYCLES (5 months)
-- ===================================================================================
-- We create 5 inactive cycles representing past months of study.
INSERT INTO study_cycles (id, exam_id, name, is_active, is_continuous, daily_goal_blocks, created_at) VALUES
(1, 1, 'Janeiro - Fundamentos', 0, 1, 3, '2024-01-01 11:00:00'),
(2, 1, 'Fevereiro - Aprofundamento', 0, 1, 3, '2024-02-01 11:00:00'),
(3, 1, 'Março - Resolução de Questões', 0, 1, 4, '2024-03-01 11:00:00'),
(4, 1, 'Abril - Revisão Intensiva', 0, 1, 4, '2024-04-01 11:00:00'),
(5, 1, 'Maio - Pré-Edital', 0, 1, 4, '2024-05-01 11:00:00');

-- Associate subjects with past cycles, showing some progression in difficulty.
-- Cycle 1: Janeiro
INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight) VALUES
(1, 1, 4, 4, 3), (1, 2, 5, 4, 3), (1, 3, 5, 5, 3), (1, 4, 4, 5, 4), (1, 5, 3, 3, 3), (1, 6, 2, 3, 4);
-- Cycle 2: Fevereiro
INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight) VALUES
(2, 1, 4, 4, 3), (2, 2, 5, 4, 2), (2, 3, 5, 5, 3), (2, 4, 4, 5, 4), (2, 5, 3, 3, 3), (2, 6, 2, 3, 4);
-- Cycle 3: Março (Difficulty for Constitucional lowered, AFO still high)
INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight) VALUES
(3, 1, 4, 4, 3), (3, 2, 5, 4, 2), (3, 3, 5, 5, 2), (3, 4, 4, 5, 5), (3, 5, 3, 3, 3), (3, 6, 2, 3, 3);
-- Cycle 4: Abril
INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight) VALUES
(4, 1, 4, 4, 3), (4, 2, 5, 4, 1), (4, 3, 5, 5, 2), (4, 4, 4, 5, 5), (4, 5, 3, 3, 2), (4, 6, 2, 3, 3);
-- Cycle 5: Maio
INSERT INTO cycle_subjects (cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight) VALUES
(5, 1, 4, 4, 2), (5, 2, 5, 4, 1), (5, 3, 5, 5, 2), (5, 4, 4, 5, 4), (5, 5, 3, 3, 2), (5, 6, 2, 3, 2);


-- ===================================================================================
-- STEP 4: CURRENT ACTIVE CYCLE & TACTICAL PLAN
-- ===================================================================================
-- Create the currently active cycle.
INSERT INTO study_cycles (id, exam_id, name, is_active, is_continuous, daily_goal_blocks, timing_strategy, created_at) VALUES
(6, 1, 'Junho - Reta Final', 1, 1, 4, 'Adaptive', '2024-06-01 09:00:00');

-- Associate subjects with the ACTIVE cycle, simulating the tutor's current diagnosis.
-- Note the `current_strategic_state` and `state_hysteresis_data` JSON.
INSERT INTO cycle_subjects (id, cycle_id, subject_id, relevance_weight, volume_weight, difficulty_weight, final_weight_calc, num_blocks_in_cycle, current_strategic_state, state_hysteresis_data) VALUES
(31, 6, 1, 4, 4, 2, 3.4, 3, 'CONQUER',   '{"consecutive_cycles_in_state": 1, "last_mastery_score": 0.82}'),
(32, 6, 2, 5, 4, 1, 3.2, 3, 'MAINTAIN',  '{"consecutive_cycles_in_state": 2, "last_mastery_score": 0.93}'),
(33, 6, 3, 5, 5, 2, 3.6, 4, 'CEMENT',    '{"consecutive_cycles_in_state": 1, "last_mastery_score": 0.88}'),
(34, 6, 4, 4, 5, 4, 4.2, 4, 'DEEP_WORK', '{"consecutive_cycles_in_state": 3, "last_mastery_score": 0.71}'),
(35, 6, 5, 3, 3, 2, 2.7, 3, 'CEMENT',    '{"consecutive_cycles_in_state": 1, "last_mastery_score": 0.85}'),
(36, 6, 6, 2, 3, 2, 2.2, 2, 'DEEP_WORK', '{"consecutive_cycles_in_state": 1, "last_mastery_score": 0.75}');

-- Create a study queue for the active cycle based on the num_blocks above (Total 19 blocks).
-- This simulates the output of business_logic.generate_study_queue.
INSERT INTO study_queue (cycle_id, cycle_subject_id, queue_order) VALUES
(6, 34, 0), (6, 33, 1), (6, 31, 2), (6, 34, 3), (6, 32, 4), (6, 35, 5), (6, 33, 6),
(6, 36, 7), (6, 34, 8), (6, 31, 9), (6, 33, 10), (6, 35, 11), (6, 32, 12), (6, 34, 13),
(6, 36, 14), (6, 33, 15), (6, 31, 16), (6, 35, 17), (6, 32, 18);


-- Create some tactical work units for a few subjects to populate that view.
INSERT INTO work_units (subject_id, unit_id, title, type, estimated_time_minutes, is_completed, related_questions_topic) VALUES
(3, 'wu_3_1', 'Revisar Lei 8.112/90', 'Reading', 90, 1, 'lei_8112'),
(3, 'wu_3_2', 'Resolver Questões - Licitações (Lei 14.133)', 'Problem Set', 120, 1, 'licitacoes'),
(3, 'wu_3_3', 'Mapa Mental - Atos Administrativos', 'Review', 45, 0, 'atos_administrativos'),
(4, 'wu_4_1', 'Estudar LRF - Lei de Responsabilidade Fiscal', 'Reading', 120, 1, 'lrf'),
(4, 'wu_4_2', 'Resolver Questões - Créditos Adicionais', 'Problem Set', 90, 0, 'creditos_adicionais'),
(4, 'wu_4_3', 'Assistir Videoaula - PPA, LDO e LOA', 'Video Lecture', 75, 0, 'ciclo_orcamentario');


-- ===================================================================================
-- STEP 5: HISTORICAL STUDY SESSIONS & PERFORMANCE DATA (~100 sessions)
-- ===================================================================================
-- This is a sample of sessions. A full script would have many more.
-- We will show progression: low accuracy in Jan, higher in May.
-- We are focusing on generating data for Direito Constitucional (subject_id=2, high perf)
-- and AFO (subject_id=4, lower perf).

-- JANUARY SESSIONS (Lower performance)
INSERT INTO study_sessions (id, user_id, cycle_id, subject_id, start_time, end_time, liquid_duration_sec) VALUES
(1, 2, 1, 2, '2024-01-05 19:00:00', '2024-01-05 20:30:00', 5400),
(2, 2, 1, 4, '2024-01-06 14:00:00', '2024-01-06 15:45:00', 6300),
(3, 2, 1, 3, '2024-01-08 20:00:00', '2024-01-08 21:30:00', 5400);

INSERT INTO question_performance (session_id, topic_name, difficulty_level, is_correct) VALUES
-- Session 1 (Constitucional - Good start)
(1, 'direitos_fundamentais', 3, 1), (1, 'direitos_fundamentais', 4, 1), (1, 'direitos_fundamentais', 2, 0), (1, 'direitos_fundamentais', 3, 1), (1, 'direitos_fundamentais', 5, 1),
(1, 'direitos_fundamentais', 3, 1), (1, 'direitos_fundamentais', 4, 1), (1, 'direitos_fundamentais', 4, 1), (1, 'direitos_fundamentais', 2, 1), (1, 'direitos_fundamentais', 3, 1), -- 9/10 correct (90%)
-- Session 2 (AFO - Rocky start)
(2, 'principios_orcamentarios', 3, 0), (2, 'principios_orcamentarios', 4, 1), (2, 'principios_orcamentarios', 2, 0), (2, 'principios_orcamentarios', 3, 1), (2, 'principios_orcamentarios', 5, 0),
(2, 'principios_orcamentarios', 4, 0), (2, 'principios_orcamentarios', 3, 1), (2, 'principios_orcamentarios', 2, 1), (2, 'principios_orcamentarios', 4, 0), (2, 'principios_orcamentarios', 3, 1); -- 5/10 correct (50%)

-- MARCH SESSIONS (Performance improving)
INSERT INTO study_sessions (id, user_id, cycle_id, subject_id, start_time, end_time, liquid_duration_sec) VALUES
(21, 2, 3, 2, '2024-03-10 10:00:00', '2024-03-10 11:30:00', 5400),
(22, 2, 3, 4, '2024-03-11 19:30:00', '2024-03-11 21:15:00', 6300),
(23, 2, 3, 1, '2024-03-12 20:00:00', '2024-03-12 21:30:00', 5400);

INSERT INTO question_performance (session_id, topic_name, difficulty_level, is_correct) VALUES
-- Session 21 (Constitucional - Consistent)
(21, 'controle_constitucionalidade', 4, 1), (21, 'controle_constitucionalidade', 5, 1), (21, 'controle_constitucionalidade', 3, 1), (21, 'controle_constitucionalidade', 4, 0), (21, 'controle_constitucionalidade', 5, 1),
(21, 'controle_constitucionalidade', 4, 1), (21, 'controle_constitucionalidade', 5, 1), (21, 'controle_constitucionalidade', 4, 1), (21, 'controle_constitucionalidade', 3, 1), (21, 'controle_constitucionalidade', 5, 1), -- 9/10 correct (90%)
-- Session 22 (AFO - Getting better)
(22, 'lrf', 4, 1), (22, 'lrf', 3, 0), (22, 'lrf', 4, 1), (22, 'lrf', 5, 1), (22, 'lrf', 3, 1),
(22, 'lrf', 4, 0), (22, 'lrf', 5, 1), (22, 'lrf', 3, 1), (22, 'lrf', 4, 1), (22, 'lrf', 5, 0); -- 7/10 correct (70%)


-- MAY SESSIONS (Strong performance)
INSERT INTO study_sessions (id, user_id, cycle_id, subject_id, start_time, end_time, liquid_duration_sec) VALUES
(41, 2, 5, 2, '2024-05-15 20:00:00', '2024-05-15 21:40:00', 6000),
(42, 2, 5, 4, '2024-05-16 08:00:00', '2024-05-16 09:45:00', 6300),
(43, 2, 5, 3, '2024-05-18 15:00:00', '2024-05-18 16:30:00', 5400);

INSERT INTO question_performance (session_id, topic_name, difficulty_level, is_correct) VALUES
-- Session 41 (Constitucional - Mastery)
(41, 'poder_judiciario', 5, 1), (41, 'poder_judiciario', 4, 1), (41, 'poder_judiciario', 5, 1), (41, 'poder_judiciario', 4, 1), (41, 'poder_judiciario', 5, 1),
(41, 'poder_judiciario', 4, 1), (41, 'poder_judiciario', 5, 0), (41, 'poder_judiciario', 4, 1), (41, 'poder_judiciario', 5, 1), (41, 'poder_judiciario', 4, 1), -- 9/10 correct (90%)
-- Session 42 (AFO - Solid)
(42, 'receita_publica', 4, 1), (42, 'receita_publica', 3, 1), (42, 'receita_publica', 4, 1), (42, 'receita_publica', 5, 0), (42, 'receita_publica', 3, 1),
(42, 'receita_publica', 4, 0), (42, 'receita_publica', 5, 1), (42, 'receita_publica', 3, 1), (42, 'receita_publica', 4, 1), (42, 'receita_publica', 5, 1); -- 8/10 correct (80%)


-- ===================================================================================
-- STEP 6: HUMAN FACTOR HISTORY
-- ===================================================================================
-- Simulate daily check-ins for the last few months. This is a small sample.
INSERT INTO human_factors (user_id, date, energy_level, stress_level) VALUES
(2, '2024-05-01', 'Normal', 'Normal'), (2, '2024-05-02', 'High', 'Low'), (2, '2024-05-03', 'Normal', 'Low'), (2, '2024-05-04', 'Normal', 'Normal'),
(2, '2024-05-05', 'Low', 'Normal'), (2, '2024-05-06', 'Normal', 'High'), (2, '2024-05-07', 'High', 'Normal'), (2, '2024-05-08', 'Normal', 'Low'),
(2, '2024-05-09', 'Normal', 'Normal'), (2, '2024-05-10', 'High', 'Low'), (2, '2024-05-11', 'Normal', 'Normal'), (2, '2024-05-12', 'Low', 'High'),
(2, '2024-05-13', 'Normal', 'Normal'), (2, '2024-05-14', 'High', 'Low'), (2, '2024-05-15', 'Normal', 'Normal'), (2, '2024-05-16', 'Normal', 'Normal'),
(2, '2024-05-17', 'Low', 'High'), (2, '2024-05-18', 'High', 'Low'), (2, '2024-05-19', 'Normal', 'Normal'), (2, '2024-05-20', 'Normal', 'Low'),
(2, '2024-05-21', 'High', 'Normal'), (2, '2024-05-22', 'Normal', 'Normal'), (2, '2024-05-23', 'Low', 'Normal'), (2, '2024-05-24', 'Normal', 'High'),
(2, '2024-05-25', 'High', 'Low'), (2, '2024-05-26', 'Normal', 'Normal'), (2, '2024-05-27', 'Normal', 'Low'), (2, '2024-05-28', 'High', 'Normal'),
(2, '2024-05-29', 'Normal', 'Normal'), (2, '2024-05-30', 'Low', 'High'), (2, '2024-05-31', 'Normal', 'Normal'), (2, '2024-06-01', 'High', 'Low');


COMMIT;