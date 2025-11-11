-- app/assets/sql/templates.sql


-- Serenita Study App - Exam Templates
-- This script populates the 'exams' and 'template_subjects' tables with
-- realistic, high-quality templates for common Brazilian public service exams.
-- The :template_user_id placeholder is replaced by the migration runner.

-- =============================================================================
-- TEMPLATE 1: Receita Federal - Auditor-Fiscal (Área Fiscal)
-- =============================================================================

-- 1. Create the Exam Template record
INSERT INTO exams (user_id, name, institution, role, area, exam_board, status)
SELECT :template_user_id, 'Receita Federal - Auditor-Fiscal (Template)', 'Receita Federal do Brasil', 'Auditor-Fiscal', 'Fiscal', 'FGV', 'TEMPLATE'
WHERE NOT EXISTS (SELECT 1 FROM exams WHERE name = 'Receita Federal - Auditor-Fiscal (Template)');

-- 2. Link Subjects to the Template with realistic weights
INSERT OR IGNORE INTO template_subjects (exam_id, subject_id, relevance_weight, volume_weight)
SELECT
    (SELECT id FROM exams WHERE name = 'Receita Federal - Auditor-Fiscal (Template)'),
    s.id,
    CASE s.name
        WHEN 'Direito Tributário' THEN 5
        WHEN 'Legislação Tributária' THEN 5
        WHEN 'Contabilidade Geral' THEN 5
        WHEN 'Língua Portuguesa' THEN 5
        WHEN 'Auditoria' THEN 4
        WHEN 'Direito Administrativo' THEN 4
        WHEN 'Direito Constitucional' THEN 4
        WHEN 'Comércio Internacional' THEN 3
        WHEN 'Raciocínio Lógico-Matemático' THEN 3
        WHEN 'Língua Inglesa' THEN 2
        ELSE 3
    END, -- relevance_weight
    CASE s.name
        WHEN 'Direito Tributário' THEN 5
        WHEN 'Legislação Tributária' THEN 5
        WHEN 'Contabilidade Geral' THEN 5
        WHEN 'Auditoria' THEN 4
        ELSE 4
    END -- volume_weight
FROM subjects s
WHERE s.name IN (
    'Língua Portuguesa',
    'Língua Inglesa',
    'Raciocínio Lógico-Matemático',
    'Direito Constitucional',
    'Direito Administrativo',
    'Direito Tributário',
    'Legislação Tributária',
    'Contabilidade Geral',
    'Auditoria',
    'Comércio Internacional'
);


-- =============================================================================
-- TEMPLATE 2: Polícia Federal - Agente (Área Policial)
-- =============================================================================

-- 1. Create the Exam Template record
INSERT INTO exams (user_id, name, institution, role, area, exam_board, status)
SELECT :template_user_id, 'Polícia Federal - Agente (Template)', 'Polícia Federal', 'Agente de Polícia Federal', 'Policial', 'Cebraspe', 'TEMPLATE'
WHERE NOT EXISTS (SELECT 1 FROM exams WHERE name = 'Polícia Federal - Agente (Template)');

-- 2. Link Subjects to the Template
INSERT OR IGNORE INTO template_subjects (exam_id, subject_id, relevance_weight, volume_weight)
SELECT
    (SELECT id FROM exams WHERE name = 'Polícia Federal - Agente (Template)'),
    s.id,
    CASE s.name
        WHEN 'Língua Portuguesa' THEN 5
        WHEN 'Contabilidade Geral' THEN 5
        WHEN 'Tecnologia da Informação' THEN 5
        WHEN 'Direito Administrativo' THEN 4
        WHEN 'Direito Constitucional' THEN 4
        WHEN 'Direito Penal' THEN 4
        WHEN 'Direito Processual Penal' THEN 4
        WHEN 'Raciocínio Lógico-Matemático' THEN 3
        WHEN 'Estatística' THEN 3
        ELSE 3
    END, -- relevance_weight
    CASE s.name
        WHEN 'Tecnologia da Informação' THEN 5
        WHEN 'Contabilidade Geral' THEN 5
        ELSE 4
    END -- volume_weight
FROM subjects s
WHERE s.name IN (
    'Língua Portuguesa',
    'Direito Administrativo',
    'Direito Constitucional',
    'Direito Penal',
    'Direito Processual Penal',
    'Legislação Especial Penal',
    'Contabilidade Geral',
    'Tecnologia da Informação',
    'Raciocínio Lógico-Matemático',
    'Estatística'
);


-- =============================================================================
-- TEMPLATE 3: Concurso Nacional Unificado - Analista (Área Administrativa)
-- =============================================================================

-- 1. Create the Exam Template record
INSERT INTO exams (user_id, name, institution, role, area, exam_board, status)
SELECT :template_user_id, 'CNU - Analista Administrativo (Template)', 'Governo Federal (Bloco 7)', 'Analista Técnico-Administrativo', 'Administrativa / Geral', 'Cesgranrio', 'TEMPLATE'
WHERE NOT EXISTS (SELECT 1 FROM exams WHERE name = 'CNU - Analista Administrativo (Template)');

-- 2. Link Subjects to the Template
INSERT OR IGNORE INTO template_subjects (exam_id, subject_id, relevance_weight, volume_weight)
SELECT
    (SELECT id FROM exams WHERE name = 'CNU - Analista Administrativo (Template)'),
    s.id,
    CASE s.name
        WHEN 'Administração Financeira e Orçamentária (AFO)' THEN 5
        WHEN 'Direito Administrativo' THEN 5
        WHEN 'Língua Portuguesa' THEN 5
        WHEN 'Direito Constitucional' THEN 4
        WHEN 'Contabilidade Pública' THEN 4
        WHEN 'Raciocínio Lógico-Matemático' THEN 3
        ELSE 3
    END, -- relevance_weight
    CASE s.name
        WHEN 'Administração Financeira e Orçamentária (AFO)' THEN 5
        WHEN 'Direito Administrativo' THEN 5
        ELSE 4
    END -- volume_weight
FROM subjects s
WHERE s.name IN (
    'Língua Portuguesa',
    'Direito Constitucional',
    'Direito Administrativo',
    'Raciocínio Lógico-Matemático',
    'Administração Financeira e Orçamentária (AFO)',
    'Contabilidade Pública',
    'Atualidades'
);




