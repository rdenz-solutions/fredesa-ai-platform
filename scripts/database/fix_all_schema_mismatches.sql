-- Fix ALL schema mismatches to match test expectations
-- Run date: 2025-12-29
-- Goal: 28/28 tests passing

-- =========================================
-- SECTION 1: Fix source_relationships
-- =========================================
ALTER TABLE source_relationships 
    RENAME COLUMN strength TO relationship_strength;

-- =========================================
-- SECTION 2: Fix sources table
-- =========================================
ALTER TABLE sources 
    ADD COLUMN IF NOT EXISTS cited_by_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS environment_flags JSONB DEFAULT '{"dev": true, "staging": false, "production": false}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_sources_cited_by_count ON sources(cited_by_count);
CREATE INDEX IF NOT EXISTS idx_sources_environment_flags ON sources USING gin(environment_flags);

-- =========================================
-- SECTION 3: Fix source_concepts
-- =========================================
-- Change from source_ids[] to source_id UUID
ALTER TABLE source_concepts DROP COLUMN IF EXISTS source_ids;
ALTER TABLE source_concepts ADD COLUMN IF NOT EXISTS source_id UUID REFERENCES sources(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_source_concepts_source ON source_concepts(source_id);

-- =========================================
-- SECTION 4: Fix source_use_cases
-- =========================================
-- Change from source_ids[] to source_id UUID
ALTER TABLE source_use_cases DROP COLUMN IF EXISTS source_ids;
ALTER TABLE source_use_cases ADD COLUMN IF NOT EXISTS source_id UUID REFERENCES sources(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_source_use_cases_source ON source_use_cases(source_id);

-- =========================================
-- SECTION 5: Fix learning_paths
-- =========================================
-- Add explicit columns instead of path_data JSONB
ALTER TABLE learning_paths 
    ADD COLUMN IF NOT EXISTS name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS sequence INTEGER;

CREATE INDEX IF NOT EXISTS idx_learning_paths_sequence ON learning_paths(sequence);

-- =========================================
-- SECTION 6: Fix source_versions
-- =========================================
-- Add explicit columns
ALTER TABLE source_versions 
    ADD COLUMN IF NOT EXISTS url TEXT,
    ADD COLUMN IF NOT EXISTS breaking_changes BOOLEAN DEFAULT false;

-- =========================================
-- SECTION 7: Fix quality_history
-- =========================================
-- Add explicit validation_status column
ALTER TABLE quality_history 
    ADD COLUMN IF NOT EXISTS validation_status VARCHAR(50) CHECK (validation_status IN (
        'passed', 'failed', 'warning', 'skipped'
    ));

-- =========================================
-- SECTION 8: Fix source_validations
-- =========================================
-- Rename result to validation_result
ALTER TABLE source_validations 
    RENAME COLUMN result TO validation_result;

-- =========================================
-- SECTION 9: Fix source_feedback
-- =========================================
-- Add explicit columns instead of feedback_data JSONB
ALTER TABLE source_feedback 
    ADD COLUMN IF NOT EXISTS rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    ADD COLUMN IF NOT EXISTS feedback_text TEXT;

-- Enable RLS on source_feedback
ALTER TABLE source_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_feedback ON source_feedback
    USING (customer_id = (current_setting('app.current_customer_id', true))::uuid 
           OR current_setting('app.current_customer_id', true) IS NULL);

-- =========================================
-- SECTION 10: Fix customer_connectors
-- =========================================
-- Add explicit columns
ALTER TABLE customer_connectors 
    ADD COLUMN IF NOT EXISTS connector_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS credentials JSONB DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_customer_connectors_name ON customer_connectors(connector_name);

-- =========================================
-- SECTION 11: Fix Views - Correct Output Columns
-- =========================================

-- Fix knowledge_graph_summary view
DROP VIEW IF EXISTS knowledge_graph_summary CASCADE;
DROP VIEW IF EXISTS knowledge_graph_summary_view CASCADE;

CREATE OR REPLACE VIEW knowledge_graph_summary_view AS
SELECT 
    s.id as source_id,
    s.name as source_name,
    COUNT(DISTINCT sc.id) as concept_count,
    COUNT(DISTINCT sr.id) as relationship_count,
    COUNT(DISTINCT suc.id) as use_case_count
FROM sources s
LEFT JOIN source_concepts sc ON sc.source_id = s.id
LEFT JOIN source_relationships sr ON sr.source_id = s.id OR sr.related_source_id = s.id
LEFT JOIN source_use_cases suc ON suc.source_id = s.id
GROUP BY s.id, s.name;

CREATE OR REPLACE VIEW knowledge_graph_summary AS SELECT * FROM knowledge_graph_summary_view;

-- Fix customer_stats view
DROP VIEW IF EXISTS customer_stats CASCADE;
DROP VIEW IF EXISTS customer_stats_view CASCADE;

CREATE OR REPLACE VIEW customer_stats_view AS
SELECT 
    c.id,
    c.name,
    COUNT(DISTINCT cql.id) as total_queries,
    COUNT(DISTINCT CASE WHEN cql.query_type = 'federated' THEN cql.id END) as federated_queries,
    COUNT(DISTINCT cc.id) as connector_count,
    COUNT(DISTINCT sf.id) as feedback_count
FROM customers c
LEFT JOIN customer_connectors cc ON cc.customer_id = c.id
LEFT JOIN connector_query_log cql ON cql.connector_id = cc.id
LEFT JOIN source_feedback sf ON sf.customer_id = c.id
GROUP BY c.id, c.name;

CREATE OR REPLACE VIEW customer_stats AS SELECT * FROM customer_stats_view;

-- Fix vertical_completeness view
DROP VIEW IF EXISTS vertical_completeness CASCADE;
DROP VIEW IF EXISTS vertical_completeness_view CASCADE;

CREATE OR REPLACE VIEW vertical_completeness_view AS
SELECT 
    cat.id as category_id,
    cat.display_name as category_name,
    ROUND(100.0 * cat.theory_count / NULLIF(cat.total_sources, 0), 2) as theory_percent,
    ROUND(100.0 * cat.practice_count / NULLIF(cat.total_sources, 0), 2) as practice_percent,
    ROUND(100.0 * cat.history_count / NULLIF(cat.total_sources, 0), 2) as history_percent,
    ROUND(100.0 * cat.current_count / NULLIF(cat.total_sources, 0), 2) as current_percent,
    ROUND(100.0 * cat.future_count / NULLIF(cat.total_sources, 0), 2) as future_percent,
    cat.total_sources
FROM categories cat;

CREATE OR REPLACE VIEW vertical_completeness AS SELECT * FROM vertical_completeness_view;

-- Fix pending_approvals view
DROP VIEW IF EXISTS pending_approvals CASCADE;
DROP VIEW IF EXISTS pending_approvals_view CASCADE;

CREATE OR REPLACE VIEW pending_approvals_view AS
SELECT 
    sp.id,
    s.name,
    sp.approval_status,
    sp.promotion_type,
    sp.requested_by,
    sp.requested_at,
    sp.from_environment,
    sp.to_environment
FROM source_promotions sp
JOIN sources s ON s.id = sp.source_id
WHERE sp.approval_status = 'pending';

CREATE OR REPLACE VIEW pending_approvals AS SELECT * FROM pending_approvals_view;
