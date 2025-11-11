-- Serenita Study App - Initial Database Seed v2.0
-- This script populates the database with a realistic set of subjects and topics
-- based on the structure of common high-complexity Brazilian public service exams (e.g., QConcursos).

-- The color palette is chosen for good visual distinction.
-- A "System" user is needed for associating with templates.
INSERT OR IGNORE INTO users (id, name, description, study_level) VALUES
(1, 'System', 'Internal system user for templates', 'N/A');

-- =============================================================================
-- SECTION 1: Subjects (Disciplinas)
-- =============================================================================
INSERT OR IGNORE INTO subjects (name, color) VALUES
-- Grupo Básico
('Língua Portuguesa', '#4ECDC4'),
('Língua Inglesa', '#A2D2FF'),
('Raciocínio Lógico-Matemático', '#FF6B6B'),
('Direito Constitucional', '#45B7D1'),
('Direito Administrativo', '#F7B733'),
('Controle Externo', '#0096C7'),
('Análise de Informações', '#48CAE4'),
('Tecnologia da Informação', '#0077B6'),
('Atualidades', '#F3722C'),

-- Área Fiscal / Controle
('Contabilidade Geral', '#9B5DE5'),
('Contabilidade Avançada', '#F4A261'),
('Auditoria', '#E76F51'),
('Direito Tributário', '#2A9D8F'),
('Legislação Tributária', '#264653'),
('Administração Financeira e Orçamentária (AFO)', '#CDB4DB'),
('Economia e Finanças Públicas', '#FF8FAB'),
('Contabilidade Pública', '#83C5BE'),

-- Área Policial / Outras
('Contabilidade de Custos', '#F9C74F'),
('Direito Penal', '#E57373'),
('Direito Processual Penal', '#BA68C8'),
('Legislação Especial Penal', '#7986CB'),
('Criminalística', '#64B5F6'),
('Medicina Legal', '#4DB6AC'),
('Física', '#FFD54F'),
('Química', '#B39DDB'),
('Biologia', '#81C784'),
('Estatística', '#90A4AE');


-- =============================================================================
-- SECTION 2: Topics (Assuntos)
-- This section populates the topics for the most common subjects.
-- =============================================================================

-- Topics for: Direito Administrativo
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estado, Governo e Administração Pública' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Princípios da Administração Pública' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Organização Administrativa' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Atos Administrativos' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Poderes Administrativos' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Licitações (Leis 8.666/93 e 14.133/21)' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Contratos Administrativos' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Serviços Públicos' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Controle da Administração Pública' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Agentes Públicos (Lei 8.112/90)' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Responsabilidade Civil do Estado' FROM Subjects WHERE name = 'Direito Administrativo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Intervenção do Estado na Propriedade' FROM Subjects WHERE name = 'Direito Administrativo';

-- Topics for: Direito Constitucional
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Teoria da Constituição' FROM Subjects WHERE name = 'Direito Constitucional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Direitos e Garantias Fundamentais' FROM Subjects WHERE name = 'Direito Constitucional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Organização do Estado' FROM Subjects WHERE name = 'Direito Constitucional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Organização dos Poderes' FROM Subjects WHERE name = 'Direito Constitucional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Controle de Constitucionalidade' FROM Subjects WHERE name = 'Direito Constitucional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Processo Legislativo' FROM Subjects WHERE name = 'Direito Constitucional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Defesa do Estado e das Instituições Democráticas' FROM Subjects WHERE name = 'Direito Constitucional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Ordem Social' FROM Subjects WHERE name = 'Direito Constitucional';

-- Topics for: Língua Portuguesa
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Interpretação de Textos' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Tipologia e Gêneros Textuais' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Ortografia Oficial e Acentuação Gráfica' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Morfologia (Classes de Palavras)' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Sintaxe da Oração e do Período' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Concordância Verbal e Nominal' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Regência Verbal e Nominal' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Crase' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Pontuação' FROM Subjects WHERE name = 'Língua Portuguesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Redação Oficial' FROM Subjects WHERE name = 'Língua Portuguesa';

-- Topics for: Raciocínio Lógico-Matemático
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estruturas Lógicas e Proposições' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Tabelas-Verdade' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Equivalências e Negações Lógicas' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lógica de Argumentação' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Análise Combinatória' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Probabilidade' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Conjuntos' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Porcentagem e Proporções' FROM Subjects WHERE name = 'Raciocínio Lógico-Matemático';

-- Topics for: Administração Financeira e Orçamentária (AFO)
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Orçamento Público: Conceitos e Princípios' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Instrumentos de Planejamento (PPA, LDO, LOA)' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Ciclo Orçamentário' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Receita Pública' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Despesa Pública' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Créditos Adicionais' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei de Responsabilidade Fiscal (LRF - LC 101/2000)' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Suprimento de Fundos' FROM Subjects WHERE name = 'Administração Financeira e Orçamentária (AFO)';

-- Topics for: Contabilidade Geral
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estrutura Conceitual Básica (CPC 00)' FROM Subjects WHERE name = 'Contabilidade Geral';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Escrituração e Lançamentos Contábeis' FROM Subjects WHERE name = 'Contabilidade Geral';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Balanço Patrimonial' FROM Subjects WHERE name = 'Contabilidade Geral';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Demonstração do Resultado (DRE)' FROM Subjects WHERE name = 'Contabilidade Geral';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Demonstração dos Fluxos de Caixa (DFC)' FROM Subjects WHERE name = 'Contabilidade Geral';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Demonstração das Mutações do Patrimônio Líquido (DMPL)' FROM Subjects WHERE name = 'Contabilidade Geral';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Operações com Mercadorias' FROM Subjects WHERE name = 'Contabilidade Geral';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Análise das Demonstrações Contábeis' FROM Subjects WHERE name = 'Contabilidade Geral';

-- Topics for: Tecnologia da Informação
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Redes de Computadores' FROM Subjects WHERE name = 'Tecnologia da Informação';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Segurança da Informação' FROM Subjects WHERE name = 'Tecnologia da Informação';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Bancos de Dados' FROM Subjects WHERE name = 'Tecnologia da Informação';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Engenharia e Arquitetura de Software' FROM Subjects WHERE name = 'Tecnologia da Informação';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Governança de TI (COBIT, ITIL)' FROM Subjects WHERE name = 'Tecnologia da Informação';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Análise de Dados e Business Intelligence' FROM Subjects WHERE name = 'Tecnologia da Informação';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Sistemas Operacionais' FROM Subjects WHERE name = 'Tecnologia da Informação';

-- =============================================================================
-- SECTION 2: Topics (Assuntos) - CONTINUATION
-- This section populates the topics for additional high-value subjects.
-- =============================================================================

-- Topics for: Controle Externo
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Natureza, Tipos e Formas de Controle' FROM Subjects WHERE name = 'Controle Externo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Controle Externo na Constituição Federal (Art. 70 a 75)' FROM Subjects WHERE name = 'Controle Externo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Tribunais de Contas: Natureza, Competência e Jurisdição' FROM Subjects WHERE name = 'Controle Externo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei Orgânica do TCU (Lei nº 8.443/1992)' FROM Subjects WHERE name = 'Controle Externo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Processos no TCU: Tomada e Prestação de Contas' FROM Subjects WHERE name = 'Controle Externo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Processos no TCU: Fiscalização (Auditorias e Inspeções)' FROM Subjects WHERE name = 'Controle Externo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Processos no TCU: Representações e Denúncias' FROM Subjects WHERE name = 'Controle Externo';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Responsabilização e Sanções' FROM Subjects WHERE name = 'Controle Externo';

-- Topics for: Auditoria
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Auditoria Interna vs. Externa (Independente)' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Normas de Auditoria (NBC TA e NBC TI)' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Planejamento da Auditoria' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Risco de Auditoria e Materialidade' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Controles Internos (Relatório COSO)' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Testes de Auditoria (Controle e Substantivos)' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Evidências e Procedimentos de Auditoria' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Relatório (Parecer) de Auditoria' FROM Subjects WHERE name = 'Auditoria';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Auditoria Governamental' FROM Subjects WHERE name = 'Auditoria';

-- Topics for: Direito Tributário
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Sistema Tributário Nacional (CF/88)' FROM Subjects WHERE name = 'Direito Tributário';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Princípios Constitucionais Tributários' FROM Subjects WHERE name = 'Direito Tributário';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Competência Tributária e Limitações ao Poder de Tributar' FROM Subjects WHERE name = 'Direito Tributário';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Legislação Tributária (Código Tributário Nacional - CTN)' FROM Subjects WHERE name = 'Direito Tributário';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Obrigação Tributária' FROM Subjects WHERE name = 'Direito Tributário';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Crédito Tributário (Lançamento, Suspensão, Extinção, Exclusão)' FROM Subjects WHERE name = 'Direito Tributário';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Impostos da União, dos Estados e dos Municípios' FROM Subjects WHERE name = 'Direito Tributário';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Administração Tributária' FROM Subjects WHERE name = 'Direito Tributário';

-- Topics for: Contabilidade Pública (CASP)
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estrutura Conceitual da Contabilidade do Setor Público' FROM Subjects WHERE name = 'Contabilidade Pública';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Plano de Contas Aplicado ao Setor Público (PCASP)' FROM Subjects WHERE name = 'Contabilidade Pública';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Subsistemas de Informação Contábil (Orçamentário, Patrimonial, etc.)' FROM Subjects WHERE name = 'Contabilidade Pública';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Variações Patrimoniais (Qualitativas e Quantitativas)' FROM Subjects WHERE name = 'Contabilidade Pública';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Demonstrações Contábeis Aplicadas ao Setor Público (DCASP)' FROM Subjects WHERE name = 'Contabilidade Pública';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei nº 4.320/1964' FROM Subjects WHERE name = 'Contabilidade Pública';

-- Topics for: Análise de Informações
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Coleta, Tratamento e Análise de Dados' FROM Subjects WHERE name = 'Análise de Informações';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Bancos de Dados Relacionais e Linguagem SQL' FROM Subjects WHERE name = 'Análise de Informações';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Modelagem de Dados' FROM Subjects WHERE name = 'Análise de Informações';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Bancos de Dados NoSQL' FROM Subjects WHERE name = 'Análise de Informações';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Business Intelligence e Data Warehousing' FROM Subjects WHERE name = 'Análise de Informações';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Mineração de Dados (Data Mining)' FROM Subjects WHERE name = 'Análise de Informações';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei de Acesso à Informação (LAI)' FROM Subjects WHERE name = 'Análise de Informações';

-- Topics for: Direito Penal
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Aplicação da Lei Penal no Tempo e no Espaço' FROM Subjects WHERE name = 'Direito Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Teoria do Crime (Fato Típico, Ilicitude, Culpabilidade)' FROM Subjects WHERE name = 'Direito Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Concurso de Pessoas' FROM Subjects WHERE name = 'Direito Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Penas e Medidas de Segurança' FROM Subjects WHERE name = 'Direito Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Extinção da Punibilidade' FROM Subjects WHERE name = 'Direito Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Crimes contra a Pessoa' FROM Subjects WHERE name = 'Direito Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Crimes contra o Patrimônio' FROM Subjects WHERE name = 'Direito Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Crimes contra a Administração Pública' FROM Subjects WHERE name = 'Direito Penal';

-- Topics for: Direito Processual Penal
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Inquérito Policial' FROM Subjects WHERE name = 'Direito Processual Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Ação Penal' FROM Subjects WHERE name = 'Direito Processual Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Jurisdição e Competência' FROM Subjects WHERE name = 'Direito Processual Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Provas no Processo Penal' FROM Subjects WHERE name = 'Direito Processual Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Prisão e Liberdade Provisória' FROM Subjects WHERE name = 'Direito Processual Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Nulidades' FROM Subjects WHERE name = 'Direito Processual Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Recursos no Processo Penal' FROM Subjects WHERE name = 'Direito Processual Penal';

-- Topics for: Estatística
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estatística Descritiva (Medidas de Posição e Dispersão)' FROM Subjects WHERE name = 'Estatística';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Probabilidade' FROM Subjects WHERE name = 'Estatística';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Distribuições de Probabilidade (Binomial, Poisson, Normal)' FROM Subjects WHERE name = 'Estatística';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Amostragem' FROM Subjects WHERE name = 'Estatística';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estimação (Intervalos de Confiança)' FROM Subjects WHERE name = 'Estatística';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Testes de Hipóteses' FROM Subjects WHERE name = 'Estatística';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Correlação e Regressão Linear Simples' FROM Subjects WHERE name = 'Estatística';

-- =============================================================================
-- SECTION 2: Topics (Assuntos) - FINAL CONTINUATION
-- This section populates the topics for the remaining specialized subjects.
-- =============================================================================

-- Topics for: Contabilidade Avançada
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Investimentos (MEP, Custo, Valor Justo)' FROM Subjects WHERE name = 'Contabilidade Avançada';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Demonstrações Consolidadas' FROM Subjects WHERE name = 'Contabilidade Avançada';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Arrendamento Mercantil (CPC 06 / IFRS 16)' FROM Subjects WHERE name = 'Contabilidade Avançada';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Instrumentos Financeiros (CPC 48 / IFRS 9)' FROM Subjects WHERE name = 'Contabilidade Avançada';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Reavaliação e Redução ao Valor Recuperável (Impairment - CPC 01)' FROM Subjects WHERE name = 'Contabilidade Avançada';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Ativo Intangível (CPC 04)' FROM Subjects WHERE name = 'Contabilidade Avançada';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Reorganização Societária (Fusão, Cisão, Incorporação)' FROM Subjects WHERE name = 'Contabilidade Avançada';

-- Topics for: Economia e Finanças Públicas
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Microeconomia: Teoria do Consumidor e da Demanda' FROM Subjects WHERE name = 'Economia e Finanças Públicas';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Microeconomia: Teoria da Produção e da Oferta' FROM Subjects WHERE name = 'Economia e Finanças Públicas';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estruturas de Mercado (Concorrência Perfeita, Monopólio, etc.)' FROM Subjects WHERE name = 'Economia e Finanças Públicas';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Macroeconomia: Contas Nacionais (PIB, Renda, etc.)' FROM Subjects WHERE name = 'Economia e Finanças Públicas';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Macroeconomia: Modelos Clássico e Keynesiano' FROM Subjects WHERE name = 'Economia e Finanças Públicas';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Políticas Monetária, Fiscal e Cambial' FROM Subjects WHERE name = 'Economia e Finanças Públicas';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Finanças Públicas: Funções do Governo e Falhas de Mercado' FROM Subjects WHERE name = 'Economia e Finanças Públicas';

-- Topics for: Legislação Tributária
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Imposto sobre Produtos Industrializados (IPI)' FROM Subjects WHERE name = 'Legislação Tributária';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Imposto sobre a Renda (IRPF e IRPJ)' FROM Subjects WHERE name = 'Legislação Tributária';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Imposto sobre Circulação de Mercadorias e Serviços (ICMS)' FROM Subjects WHERE name = 'Legislação Tributária';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Imposto Sobre Serviços (ISS)' FROM Subjects WHERE name = 'Legislação Tributária';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'PIS/COFINS' FROM Subjects WHERE name = 'Legislação Tributária';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Simples Nacional (LC 123/2006)' FROM Subjects WHERE name = 'Legislação Tributária';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Processo Administrativo Fiscal (PAF)' FROM Subjects WHERE name = 'Legislação Tributária';

-- Topics for: Legislação Especial Penal
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei de Drogas (Lei nº 11.343/2006)' FROM Subjects WHERE name = 'Legislação Especial Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei de Abuso de Autoridade (Lei nº 13.869/2019)' FROM Subjects WHERE name = 'Legislação Especial Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei de Tortura (Lei nº 9.455/1997)' FROM Subjects WHERE name = 'Legislação Especial Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei de Crimes Hediondos (Lei nº 8.072/1990)' FROM Subjects WHERE name = 'Legislação Especial Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Estatuto do Desarmamento (Lei nº 10.826/2003)' FROM Subjects WHERE name = 'Legislação Especial Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei Maria da Penha (Lei nº 11.340/2006)' FROM Subjects WHERE name = 'Legislação Especial Penal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Lei de Lavagem de Dinheiro (Lei nº 9.613/1998)' FROM Subjects WHERE name = 'Legislação Especial Penal';

-- Topics for: Língua Inglesa
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Reading Comprehension (Interpretação de Textos)' FROM Subjects WHERE name = 'Língua Inglesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Vocabulary (Vocabulário e Sinônimos)' FROM Subjects WHERE name = 'Língua Inglesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Grammar: Verb Tenses (Tempos Verbais)' FROM Subjects WHERE name = 'Língua Inglesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Grammar: Modal Verbs (Verbos Modais)' FROM Subjects WHERE name = 'Língua Inglesa';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Grammar: Prepositions and Conjunctions' FROM Subjects WHERE name = 'Língua Inglesa';

-- Topics for: Atualidades
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Tópicos Relevantes e Atuais de Política Nacional' FROM Subjects WHERE name = 'Atualidades';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Tópicos Relevantes e Atuais de Economia' FROM Subjects WHERE name = 'Atualidades';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Tópicos Relevantes e Atuais de Sociedade e Cultura' FROM Subjects WHERE name = 'Atualidades';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Geopolítica e Relações Internacionais' FROM Subjects WHERE name = 'Atualidades';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Desenvolvimento Sustentável e Meio Ambiente' FROM Subjects WHERE name = 'Atualidades';

-- Topics for: Contabilidade de Custos
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Terminologia e Classificação dos Custos' FROM Subjects WHERE name = 'Contabilidade de Custos';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Métodos de Custeio (Absorção, Variável, ABC)' FROM Subjects WHERE name = 'Contabilidade de Custos';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Análise Custo-Volume-Lucro' FROM Subjects WHERE name = 'Contabilidade de Custos';

-- Topics for other specialized subjects (basic entries)
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Noções Gerais de Comércio Internacional' FROM Subjects WHERE name = 'Comércio Internacional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Legislação Aduaneira' FROM Subjects WHERE name = 'Comércio Internacional';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Locais e Vestígios' FROM Subjects WHERE name = 'Criminalística';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Traumatologia Forense' FROM Subjects WHERE name = 'Medicina Legal';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Mecânica e Cinemática' FROM Subjects WHERE name = 'Física';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Química Orgânica e Inorgânica' FROM Subjects WHERE name = 'Química';
INSERT OR IGNORE INTO Topics (subject_id, name) SELECT id, 'Citologia e Genética' FROM Subjects WHERE name = 'Biologia';