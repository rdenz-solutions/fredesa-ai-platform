-- Migration: v1 → v2.1
-- Safe migration that preserves existing data while adding new schema

-- Backup reminder
\echo '⚠️  REMINDER: Backup created with pg_dump before migration'

-- Start transaction
BEGIN;

-- ============================================================================
-- STEP 1: Enhance existing CATEGORIES table
-- ============================================================================

\echo 'Step 1: Enhancing categories table...'

-- Add new epistemological dimension columns
ALTER TABLE categories ADD COLUMN IF NOT EXISTS parent_category_id UUID REFERENCES categories(id) ON DELETE CASCADE;
ALTER TABLE categories ADD COLUMN IF NOT EXISTS icon_name VARCHAR(100);
ALTER TABLE categories ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;
ALTER TABLE categories ADD COLUMN IF NOT EXISTS theory_sources INTEGER DEFAULT 0;
ALTER TABLE categories ADD COLUMN IF NOT EXISTS practice_sources INTEGER DEFAULT 0;
ALTER TABLE categories ADD COLUMN IF NOT EXISTS history_sources INTEGER DEFAULT 0;
ALTER TABLE categories ADD COLUMN IF NOT EXISTS current_sources INTEGER DEFAULT 0;
ALTER TABLE categories ADD COLUMN IF NOT EXISTS future_sources INTEGER DEFAULT 0;

-- Add constraint
ALTER TABLE categories DROP CONSTRAINT IF EXISTS check_epistemological_sum;
ALTER TABLE categories ADD CONSTRAINT check_epistemological_sum 
    CHECK (total_sources = theory_sources + practice_sources + history_sources + current_sources + future_sources);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_categories_sort_order ON categories(sort_order);

-- ============================================================================
-- STEP 2: Enhance existing SOURCES table (25+ new fields)
-- ============================================================================

\echo 'Step 2: Enhancing sources table...'

-- Epistemological framework
ALTER TABLE sources ADD COLUMN IF NOT EXISTS epistemological_dimension VARCHAR(50);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS theory_completeness DECIMAL(3,2) DEFAULT 0.00;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS practice_completeness DECIMAL(3,2) DEFAULT 0.00;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS difficulty_level VARCHAR(20);

-- Authority and credibility
ALTER TABLE sources ADD COLUMN IF NOT EXISTS source_type VARCHAR(50);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS authority_score INTEGER DEFAULT 50;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS author VARCHAR(500);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS publisher VARCHAR(500);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS publication_year INTEGER;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_verified TIMESTAMPTZ;

-- Content metadata
ALTER TABLE sources ADD COLUMN IF NOT EXISTS content_format VARCHAR(50);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en';
ALTER TABLE sources ADD COLUMN IF NOT EXISTS target_audience VARCHAR(100);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS prerequisites TEXT[];

-- Quality validation
ALTER TABLE sources ADD COLUMN IF NOT EXISTS validation_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE sources ADD COLUMN IF NOT EXISTS validation_notes TEXT;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_quality_check TIMESTAMPTZ;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS deprecation_reason TEXT;

-- Multi-tenant fields
ALTER TABLE sources ADD COLUMN IF NOT EXISTS customer_id UUID REFERENCES customers(id) ON DELETE CASCADE;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT true;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS access_level VARCHAR(50) DEFAULT 'public';
ALTER TABLE sources ADD COLUMN IF NOT EXISTS environment VARCHAR(20) DEFAULT 'dev';

-- Usage tracking
ALTER TABLE sources ADD COLUMN IF NOT EXISTS times_accessed INTEGER DEFAULT 0;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS times_cited INTEGER DEFAULT 0;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS avg_usefulness_rating DECIMAL(3,2);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_accessed TIMESTAMPTZ;

-- Add constraints
ALTER TABLE sources DROP CONSTRAINT IF EXISTS check_epistemological_dimension;
ALTER TABLE sources ADD CONSTRAINT check_epistemological_dimension 
    CHECK (epistemological_dimension IN ('theory', 'practice', 'history', 'current', 'future'));

ALTER TABLE sources DROP CONSTRAINT IF EXISTS check_difficulty_level;
ALTER TABLE sources ADD CONSTRAINT check_difficulty_level 
    CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'expert'));

ALTER TABLE sources DROP CONSTRAINT IF EXISTS check_authority_score;
ALTER TABLE sources ADD CONSTRAINT check_authority_score 
    CHECK (authority_score BETWEEN 0 AND 100);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_sources_epistemological_dimension ON sources(epistemological_dimension);
CREATE INDEX IF NOT EXISTS idx_sources_difficulty_level ON sources(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_sources_source_type ON sources(source_type);
CREATE INDEX IF NOT EXISTS idx_sources_authority_score ON sources(authority_score DESC);
CREATE INDEX IF NOT EXISTS idx_sources_validation_status ON sources(validation_status);
CREATE INDEX IF NOT EXISTS idx_sources_customer_id ON sources(customer_id);
CREATE INDEX IF NOT EXISTS idx_sources_environment ON sources(environment);
CREATE INDEX IF NOT EXISTS idx_sources_publication_year ON sources(publication_year);

-- ============================================================================
-- STEP 3: Create new KNOWLEDGE GRAPH tables
-- ============================================================================

\echo 'Step 3: Creating knowledge graph tables...'

CREATE TABLE IF NOT EXISTS source_concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    concept_name VARCHAR(255) NOT NULL,
    concept_type VARCHAR(100),
    definition TEXT,
    importance_score INTEGER DEFAULT 50,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(source_id, concept_name),
    CHECK (importance_score BETWEEN 0 AND 100)
);

CREATE INDEX idx_source_concepts_source ON source_concepts(source_id);
CREATE INDEX idx_source_concepts_name ON source_concepts(concept_name);
CREATE INDEX idx_source_concepts_type ON source_concepts(concept_type);

CREATE TABLE IF NOT EXISTS source_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    related_source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    relationship_strength DECIMAL(3,2) DEFAULT 0.50,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (source_id != related_source_id),
    CHECK (relationship_type IN ('prerequisite', 'cites', 'contradicts', 'validates', 'extends', 'implements', 'related', 'supersedes')),
    CHECK (relationship_strength BETWEEN 0.00 AND 1.00),
    UNIQUE(source_id, related_source_id, relationship_type)
);

CREATE INDEX idx_source_relationships_source ON source_relationships(source_id);
CREATE INDEX idx_source_relationships_related ON source_relationships(related_source_id);
CREATE INDEX idx_source_relationships_type ON source_relationships(relationship_type);

CREATE TABLE IF NOT EXISTS source_use_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    use_case_title VARCHAR(255) NOT NULL,
    use_case_description TEXT,
    industry VARCHAR(100),
    role VARCHAR(100),
    problem_solved TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_source_use_cases_source ON source_use_cases(source_id);
CREATE INDEX idx_source_use_cases_industry ON source_use_cases(industry);

CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_name VARCHAR(255) NOT NULL UNIQUE,
    path_description TEXT,
    target_role VARCHAR(100),
    estimated_hours INTEGER,
    difficulty_level VARCHAR(20),
    sequence_order JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- STEP 4: Create QUALITY VALIDATION tables
-- ============================================================================

\echo 'Step 4: Creating quality validation tables...'

CREATE TABLE IF NOT EXISTS source_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    validation_type VARCHAR(100) NOT NULL,
    validation_result VARCHAR(50) NOT NULL,
    validation_details JSONB,
    validated_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_source_validations_source ON source_validations(source_id);
CREATE INDEX idx_source_validations_type ON source_validations(validation_type);
CREATE INDEX idx_source_validations_result ON source_validations(validation_result);

CREATE TABLE IF NOT EXISTS source_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    feedback_type VARCHAR(100) NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_source_feedback_source ON source_feedback(source_id);
CREATE INDEX idx_source_feedback_customer ON source_feedback(customer_id);
CREATE INDEX idx_source_feedback_type ON source_feedback(feedback_type);

CREATE TABLE IF NOT EXISTS environment_promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    from_environment VARCHAR(20) NOT NULL,
    to_environment VARCHAR(20) NOT NULL,
    promoted_by VARCHAR(255),
    promotion_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (from_environment IN ('dev', 'staging', 'production')),
    CHECK (to_environment IN ('dev', 'staging', 'production'))
);

CREATE INDEX idx_environment_promotions_source ON environment_promotions(source_id);

-- ============================================================================
-- STEP 5: Create FEDERATED ARCHITECTURE tables
-- ============================================================================

\echo 'Step 5: Creating federated architecture tables...'

CREATE TABLE IF NOT EXISTS customer_source_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_type VARCHAR(100) NOT NULL,
    connector_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_customer_connectors_customer ON customer_source_connectors(customer_id);
CREATE INDEX idx_customer_connectors_type ON customer_source_connectors(connector_type);

CREATE TABLE IF NOT EXISTS customer_query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    query_type VARCHAR(100),
    sources_accessed UUID[],
    execution_time_ms INTEGER,
    result_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_customer_query_logs_customer ON customer_query_logs(customer_id);
CREATE INDEX idx_customer_query_logs_created ON customer_query_logs(created_at DESC);

-- ============================================================================
-- STEP 6: Create VERSIONING tables
-- ============================================================================

\echo 'Step 6: Creating versioning tables...'

CREATE TABLE IF NOT EXISTS source_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content_snapshot JSONB NOT NULL,
    change_summary TEXT,
    changed_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(source_id, version_number)
);

CREATE INDEX idx_source_versions_source ON source_versions(source_id);
CREATE INDEX idx_source_versions_created ON source_versions(created_at DESC);

CREATE TABLE IF NOT EXISTS source_quality_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    authority_score INTEGER,
    validation_status VARCHAR(50),
    times_accessed INTEGER,
    avg_usefulness_rating DECIMAL(3,2),
    snapshot_date TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_source_quality_history_source ON source_quality_history(source_id);
CREATE INDEX idx_source_quality_history_date ON source_quality_history(snapshot_date DESC);

-- ============================================================================
-- STEP 7: Create TRIGGERS
-- ============================================================================

\echo 'Step 7: Creating triggers...'

-- Authority score auto-calculation
CREATE OR REPLACE FUNCTION calculate_authority_score()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.source_type = 'official' THEN
        NEW.authority_score := 90;
    ELSIF NEW.source_type = 'expert' THEN
        NEW.authority_score := 70;
    ELSIF NEW.source_type = 'community' THEN
        NEW.authority_score := 50;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_calculate_authority_score ON sources;
CREATE TRIGGER trg_calculate_authority_score
    BEFORE INSERT OR UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION calculate_authority_score();

-- Category statistics auto-update
CREATE OR REPLACE FUNCTION update_category_epistemological_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE categories SET
            total_sources = total_sources + 1,
            theory_sources = theory_sources + CASE WHEN NEW.epistemological_dimension = 'theory' THEN 1 ELSE 0 END,
            practice_sources = practice_sources + CASE WHEN NEW.epistemological_dimension = 'practice' THEN 1 ELSE 0 END,
            history_sources = history_sources + CASE WHEN NEW.epistemological_dimension = 'history' THEN 1 ELSE 0 END,
            current_sources = current_sources + CASE WHEN NEW.epistemological_dimension = 'current' THEN 1 ELSE 0 END,
            future_sources = future_sources + CASE WHEN NEW.epistemological_dimension = 'future' THEN 1 ELSE 0 END
        WHERE id = NEW.category_id;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.category_id != NEW.category_id OR OLD.epistemological_dimension != NEW.epistemological_dimension THEN
            -- Decrement old category
            UPDATE categories SET
                total_sources = total_sources - 1,
                theory_sources = theory_sources - CASE WHEN OLD.epistemological_dimension = 'theory' THEN 1 ELSE 0 END,
                practice_sources = practice_sources - CASE WHEN OLD.epistemological_dimension = 'practice' THEN 1 ELSE 0 END,
                history_sources = history_sources - CASE WHEN OLD.epistemological_dimension = 'history' THEN 1 ELSE 0 END,
                current_sources = current_sources - CASE WHEN OLD.epistemological_dimension = 'current' THEN 1 ELSE 0 END,
                future_sources = future_sources - CASE WHEN OLD.epistemological_dimension = 'future' THEN 1 ELSE 0 END
            WHERE id = OLD.category_id;
            
            -- Increment new category
            UPDATE categories SET
                total_sources = total_sources + 1,
                theory_sources = theory_sources + CASE WHEN NEW.epistemological_dimension = 'theory' THEN 1 ELSE 0 END,
                practice_sources = practice_sources + CASE WHEN NEW.epistemological_dimension = 'practice' THEN 1 ELSE 0 END,
                history_sources = history_sources + CASE WHEN NEW.epistemological_dimension = 'history' THEN 1 ELSE 0 END,
                current_sources = current_sources + CASE WHEN NEW.epistemological_dimension = 'current' THEN 1 ELSE 0 END,
                future_sources = future_sources + CASE WHEN NEW.epistemological_dimension = 'future' THEN 1 ELSE 0 END
            WHERE id = NEW.category_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE categories SET
            total_sources = total_sources - 1,
            theory_sources = theory_sources - CASE WHEN OLD.epistemological_dimension = 'theory' THEN 1 ELSE 0 END,
            practice_sources = practice_sources - CASE WHEN OLD.epistemological_dimension = 'practice' THEN 1 ELSE 0 END,
            history_sources = history_sources - CASE WHEN OLD.epistemological_dimension = 'history' THEN 1 ELSE 0 END,
            current_sources = current_sources - CASE WHEN OLD.epistemological_dimension = 'current' THEN 1 ELSE 0 END,
            future_sources = future_sources - CASE WHEN OLD.epistemological_dimension = 'future' THEN 1 ELSE 0 END
        WHERE id = OLD.category_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_category_epistemological_stats ON sources;
CREATE TRIGGER trg_update_category_epistemological_stats
    AFTER INSERT OR UPDATE OR DELETE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_category_epistemological_stats();

-- Citation count auto-update
CREATE OR REPLACE FUNCTION update_citation_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE sources SET times_cited = times_cited + 1 WHERE id = NEW.related_source_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE sources SET times_cited = GREATEST(times_cited - 1, 0) WHERE id = OLD.related_source_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_citation_count ON source_relationships;
CREATE TRIGGER trg_update_citation_count
    AFTER INSERT OR DELETE ON source_relationships
    FOR EACH ROW
    EXECUTE FUNCTION update_citation_count();

-- ============================================================================
-- STEP 8: Create VIEWS
-- ============================================================================

\echo 'Step 8: Creating views...'

CREATE OR REPLACE VIEW active_sources_view AS
SELECT 
    s.id,
    s.name,
    s.category_id,
    c.display_name as category_name,
    s.epistemological_dimension,
    s.difficulty_level,
    s.authority_score,
    s.validation_status,
    s.environment,
    s.times_accessed,
    s.times_cited,
    s.avg_usefulness_rating,
    s.last_accessed,
    s.created_at
FROM sources s
JOIN categories c ON s.category_id = c.id
WHERE s.validation_status NOT IN ('deprecated', 'flagged');

CREATE OR REPLACE VIEW production_ready_sources AS
SELECT *
FROM active_sources_view
WHERE environment = 'production'
  AND validation_status = 'verified'
  AND authority_score >= 75;

CREATE OR REPLACE VIEW vertical_completeness_view AS
SELECT 
    c.id as category_id,
    c.display_name as category_name,
    c.total_sources,
    ROUND((c.theory_sources::DECIMAL / NULLIF(c.total_sources, 0)) * 100, 2) as theory_percent,
    ROUND((c.practice_sources::DECIMAL / NULLIF(c.total_sources, 0)) * 100, 2) as practice_percent,
    ROUND((c.history_sources::DECIMAL / NULLIF(c.total_sources, 0)) * 100, 2) as history_percent,
    ROUND((c.current_sources::DECIMAL / NULLIF(c.total_sources, 0)) * 100, 2) as current_percent,
    ROUND((c.future_sources::DECIMAL / NULLIF(c.total_sources, 0)) * 100, 2) as future_percent
FROM categories c
WHERE c.total_sources > 0
ORDER BY c.total_sources DESC;

CREATE OR REPLACE VIEW curriculum_ready_sources AS
SELECT 
    s.id,
    s.name,
    s.category_id,
    s.epistemological_dimension,
    s.difficulty_level,
    s.prerequisites,
    s.authority_score,
    COUNT(DISTINCT sc.id) as concept_count,
    COUNT(DISTINCT sr.id) as relationship_count
FROM sources s
LEFT JOIN source_concepts sc ON s.id = sc.source_id
LEFT JOIN source_relationships sr ON s.id = sr.source_id
WHERE s.difficulty_level IS NOT NULL
  AND s.epistemological_dimension IS NOT NULL
  AND s.validation_status = 'verified'
GROUP BY s.id, s.name, s.category_id, s.epistemological_dimension, 
         s.difficulty_level, s.prerequisites, s.authority_score
HAVING COUNT(DISTINCT sc.id) > 0;

CREATE OR REPLACE VIEW knowledge_graph_summary AS
SELECT 
    s.id as source_id,
    s.name as source_name,
    s.category_id,
    COUNT(DISTINCT sc.id) as concept_count,
    COUNT(DISTINCT sr.id) as relationship_count,
    COUNT(DISTINCT suc.id) as use_case_count,
    AVG(sc.importance_score) as avg_concept_importance
FROM sources s
LEFT JOIN source_concepts sc ON s.id = sc.source_id
LEFT JOIN source_relationships sr ON s.id = sr.source_id
LEFT JOIN source_use_cases suc ON s.id = suc.source_id
GROUP BY s.id, s.name, s.category_id;

CREATE OR REPLACE VIEW pending_validations_view AS
SELECT 
    s.id,
    s.name,
    s.validation_status,
    s.epistemological_dimension,
    s.authority_score,
    s.last_quality_check,
    COUNT(DISTINCT sf.id) as feedback_count,
    AVG(sf.rating) as avg_feedback_rating
FROM sources s
LEFT JOIN source_feedback sf ON s.id = sf.source_id AND sf.resolved = false
WHERE s.validation_status IN ('pending', 'flagged')
GROUP BY s.id, s.name, s.validation_status, s.epistemological_dimension, 
         s.authority_score, s.last_quality_check;

CREATE OR REPLACE VIEW customer_stats_view AS
SELECT 
    c.id as customer_id,
    c.name as customer_name,
    COUNT(DISTINCT s.id) as total_sources,
    COUNT(DISTINCT CASE WHEN s.environment = 'production' THEN s.id END) as production_sources,
    COUNT(DISTINCT csc.id) as active_connectors,
    COUNT(DISTINCT cql.id) as total_queries,
    AVG(cql.execution_time_ms) as avg_query_time_ms
FROM customers c
LEFT JOIN sources s ON c.id = s.customer_id
LEFT JOIN customer_source_connectors csc ON c.id = csc.customer_id AND csc.is_active = true
LEFT JOIN customer_query_logs cql ON c.id = cql.customer_id
GROUP BY c.id, c.name;

-- ============================================================================
-- STEP 9: Enable Row Level Security (RLS)
-- ============================================================================

\echo 'Step 9: Enabling row level security...'

ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_source_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_query_logs ENABLE ROW LEVEL SECURITY;

-- Policies will be created per-customer at runtime
-- Example: CREATE POLICY customer_isolation ON sources FOR ALL TO app_user USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMIT;

\echo '✅ Migration v1 → v2.1 complete!'
\echo ''
\echo 'Schema summary:'
\echo '  - 4 enhanced tables (categories, sources, customers, usage_tracking)'
\echo '  - 11 new tables (knowledge graph, quality validation, federated architecture)'
\echo '  - 3 triggers (authority score, category stats, citation count)'
\echo '  - 7 views (active sources, production ready, completeness, curriculum, etc.)'
\echo '  - Row level security enabled'
\echo ''
\echo 'Next steps:'
\echo '  1. Run test suite: python3 scripts/database/test_schema_v2.py'
\echo '  2. Run benchmarks: python3 scripts/database/benchmark_schema.py'
\echo '  3. Classify existing sources (LLM-assisted)'
