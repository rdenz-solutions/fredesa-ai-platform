-- FreDeSa AI Platform - Complete PostgreSQL Schema v2.1
-- Multi-tenant knowledge registry with epistemological completeness framework
-- 15 Tables: Core + Federated Architecture + Quality Validation + Knowledge Graph

-- ============================================================================
-- CATEGORIES TABLE
-- Hierarchical organization of knowledge sources with epistemological stats
-- ============================================================================

CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    icon_name VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    
    -- Epistemological dimension statistics (auto-calculated)
    total_sources INTEGER DEFAULT 0,
    theory_sources INTEGER DEFAULT 0,
    practice_sources INTEGER DEFAULT 0,
    history_sources INTEGER DEFAULT 0,
    current_sources INTEGER DEFAULT 0,
    future_sources INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(name),
    CHECK (theory_sources >= 0),
    CHECK (practice_sources >= 0),
    CHECK (history_sources >= 0),
    CHECK (current_sources >= 0),
    CHECK (future_sources >= 0),
    CHECK (total_sources = theory_sources + practice_sources + history_sources + current_sources + future_sources)
);

CREATE INDEX idx_categories_parent ON categories(parent_category_id);
CREATE INDEX idx_categories_sort_order ON categories(sort_order);

-- ============================================================================
-- SOURCES TABLE (Enhanced with Epistemological Framework)
-- Complete cognitive foundation for AI agents - 25+ new fields
-- ============================================================================

CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    name VARCHAR(500) NOT NULL,
    url TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Environment & Promotion Workflow
    environment_flags JSONB DEFAULT '{"dev": true, "staging": false, "production": false}'::jsonb,
    promoted_to_staging_at TIMESTAMPTZ,
    promoted_to_production_at TIMESTAMPTZ,
    promoted_by VARCHAR(255),
    approval_status VARCHAR(20) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    rejection_reason TEXT,
    
    -- Epistemological Dimension Classification
    epistemological_dimension VARCHAR(20) CHECK (epistemological_dimension IN ('theory', 'practice', 'history', 'current', 'future')),
    publication_year INTEGER,
    
    -- Quality & Validation
    authority_score INTEGER CHECK (authority_score >= 0 AND authority_score <= 100),
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    validation_status VARCHAR(20) DEFAULT 'unvalidated' CHECK (validation_status IN ('unvalidated', 'validated', 'flagged', 'deprecated')),
    fact_check_date TIMESTAMPTZ,
    fact_checked_by VARCHAR(255),
    
    -- Cross-Reference & Deprecation
    cross_reference_count INTEGER DEFAULT 0,
    superseded_by UUID REFERENCES sources(id) ON DELETE SET NULL,
    supersedes UUID REFERENCES sources(id) ON DELETE SET NULL,
    deprecation_reason TEXT,
    
    -- Citation Tracking
    cited_by_count INTEGER DEFAULT 0,
    external_citations TEXT[],
    
    -- Curriculum & Learning Sequencing
    prerequisite_sources UUID[],
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_read_time_minutes INTEGER,
    
    -- Geographic & Jurisdictional Scope
    geographic_scope VARCHAR(50)[],
    jurisdiction VARCHAR(100)[],
    applicable_industries VARCHAR(100)[],
    
    -- Language Support
    primary_language VARCHAR(10) DEFAULT 'en',
    available_translations VARCHAR(10)[],
    
    -- Federated Customer Sources
    source_location VARCHAR(50) DEFAULT 'rdenz' CHECK (source_location IN ('rdenz', 'customer_sharepoint', 'customer_onedrive', 'customer_drive', 'customer_blob')),
    
    -- Metadata
    tags TEXT[],
    file_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    last_ingested_at TIMESTAMPTZ,
    last_updated_at TIMESTAMPTZ,
    ingestion_status VARCHAR(50) DEFAULT 'pending',
    cost_estimate DECIMAL(10, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(url, category_id),
    CHECK (authority_score IS NULL OR (authority_score >= 0 AND authority_score <= 100)),
    CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 100)),
    CHECK (cited_by_count >= 0),
    CHECK (cross_reference_count >= 0),
    CHECK (estimated_read_time_minutes IS NULL OR estimated_read_time_minutes > 0)
);

-- Core indexes
CREATE INDEX idx_sources_category ON sources(category_id);
CREATE INDEX idx_sources_type ON sources(source_type);
CREATE INDEX idx_sources_status ON sources(ingestion_status);
CREATE INDEX idx_sources_tags ON sources USING GIN(tags);
CREATE INDEX idx_sources_created_at ON sources(created_at);

-- Epistemological indexes
CREATE INDEX idx_sources_epistemological_dimension ON sources(epistemological_dimension);
CREATE INDEX idx_sources_publication_year ON sources(publication_year);
CREATE INDEX idx_sources_difficulty_level ON sources(difficulty_level);

-- Quality indexes
CREATE INDEX idx_sources_authority_score ON sources(authority_score);
CREATE INDEX idx_sources_quality_score ON sources(quality_score);
CREATE INDEX idx_sources_validation_status ON sources(validation_status);

-- Environment indexes
CREATE INDEX idx_sources_environment_flags ON sources USING GIN(environment_flags);
CREATE INDEX idx_sources_approval_status ON sources(approval_status);

-- Curriculum indexes
CREATE INDEX idx_sources_prerequisite_sources ON sources USING GIN(prerequisite_sources);

-- Citation indexes
CREATE INDEX idx_sources_cited_by_count ON sources(cited_by_count);
CREATE INDEX idx_sources_external_citations ON sources USING GIN(external_citations);

-- Geographic indexes
CREATE INDEX idx_sources_geographic_scope ON sources USING GIN(geographic_scope);
CREATE INDEX idx_sources_jurisdiction ON sources USING GIN(jurisdiction);
CREATE INDEX idx_sources_applicable_industries ON sources USING GIN(applicable_industries);

-- Language indexes
CREATE INDEX idx_sources_primary_language ON sources(primary_language);
CREATE INDEX idx_sources_available_translations ON sources USING GIN(available_translations);

-- Federated indexes
CREATE INDEX idx_sources_location ON sources(source_location);

-- ============================================================================
-- CUSTOMERS TABLE
-- Multi-tenant customer accounts with subscription tiers
-- ============================================================================

CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    tier VARCHAR(50) NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'basic', 'professional', 'enterprise')),
    subscription_start_date TIMESTAMPTZ DEFAULT NOW(),
    subscription_end_date TIMESTAMPTZ,
    max_federated_sources INTEGER DEFAULT 0,
    max_custom_agents INTEGER DEFAULT 0,
    api_key_hash VARCHAR(255),
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (subscription_end_date IS NULL OR subscription_end_date > subscription_start_date)
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_tier ON customers(tier);
CREATE INDEX idx_customers_api_key ON customers(api_key_hash);

-- ============================================================================
-- USAGE TRACKING TABLE
-- Track customer usage of knowledge registry and federated sources
-- ============================================================================

CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    agent_id VARCHAR(255),
    query_type VARCHAR(50) NOT NULL CHECK (query_type IN ('semantic_search', 'source_access', 'federated_query', 'injection', 'synthesis')),
    query_metadata JSONB,
    response_time_ms INTEGER,
    tokens_used INTEGER,
    cost_incurred DECIMAL(10, 4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (response_time_ms IS NULL OR response_time_ms >= 0),
    CHECK (tokens_used IS NULL OR tokens_used >= 0),
    CHECK (cost_incurred IS NULL OR cost_incurred >= 0)
);

CREATE INDEX idx_usage_customer ON usage_tracking(customer_id);
CREATE INDEX idx_usage_source ON usage_tracking(source_id);
CREATE INDEX idx_usage_query_type ON usage_tracking(query_type);
CREATE INDEX idx_usage_created_at ON usage_tracking(created_at);
CREATE INDEX idx_usage_customer_created ON usage_tracking(customer_id, created_at);

-- ============================================================================
-- CUSTOMER CONNECTORS TABLE
-- OAuth credentials for federated data sources (SharePoint, OneDrive, Drive)
-- ============================================================================

CREATE TABLE IF NOT EXISTS customer_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_type VARCHAR(50) NOT NULL CHECK (connector_type IN ('sharepoint', 'onedrive', 'google_drive', 'azure_blob', 's3')),
    connector_name VARCHAR(255) NOT NULL,
    oauth_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMPTZ,
    connection_metadata JSONB,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(customer_id, connector_name)
);

CREATE INDEX idx_connectors_customer ON customer_connectors(customer_id);
CREATE INDEX idx_connectors_type ON customer_connectors(connector_type);
CREATE INDEX idx_connectors_active ON customer_connectors(is_active);

-- ============================================================================
-- CONNECTOR QUERY LOG TABLE
-- Track federated queries for billing and analytics
-- ============================================================================

CREATE TABLE IF NOT EXISTS connector_query_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_id UUID NOT NULL REFERENCES customer_connectors(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    files_retrieved INTEGER DEFAULT 0,
    bytes_retrieved BIGINT DEFAULT 0,
    query_duration_ms INTEGER,
    cost_incurred DECIMAL(10, 4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (files_retrieved >= 0),
    CHECK (bytes_retrieved >= 0),
    CHECK (query_duration_ms IS NULL OR query_duration_ms >= 0)
);

CREATE INDEX idx_connector_log_customer ON connector_query_log(customer_id);
CREATE INDEX idx_connector_log_connector ON connector_query_log(connector_id);
CREATE INDEX idx_connector_log_created_at ON connector_query_log(created_at);

-- ============================================================================
-- SOURCE PROMOTIONS TABLE
-- Audit trail for environment promotions (dev → staging → production)
-- ============================================================================

CREATE TABLE IF NOT EXISTS source_promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    from_environment VARCHAR(20) NOT NULL CHECK (from_environment IN ('dev', 'staging', 'production')),
    to_environment VARCHAR(20) NOT NULL CHECK (to_environment IN ('dev', 'staging', 'production')),
    promoted_by VARCHAR(255) NOT NULL,
    approval_notes TEXT,
    quality_score_at_promotion INTEGER,
    authority_score_at_promotion INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CHECK (from_environment != to_environment)
);

CREATE INDEX idx_promotions_source ON source_promotions(source_id);
CREATE INDEX idx_promotions_from_env ON source_promotions(from_environment);
CREATE INDEX idx_promotions_to_env ON source_promotions(to_environment);
CREATE INDEX idx_promotions_created_at ON source_promotions(created_at);

-- ============================================================================
-- SOURCE VALIDATIONS TABLE
-- Track all quality checks performed on sources
-- ============================================================================

CREATE TABLE IF NOT EXISTS source_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    validation_type VARCHAR(50) NOT NULL CHECK (validation_type IN ('authority', 'recency', 'cross_reference', 'fact_check', 'customer_feedback')),
    validation_result VARCHAR(20) NOT NULL CHECK (validation_result IN ('pass', 'fail', 'warning')),
    validation_details JSONB,
    validated_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_validations_source ON source_validations(source_id);
CREATE INDEX idx_validations_type ON source_validations(validation_type);
CREATE INDEX idx_validations_result ON source_validations(validation_result);
CREATE INDEX idx_validations_created_at ON source_validations(created_at);

-- ============================================================================
-- SOURCE FEEDBACK TABLE
-- Customer-reported issues, ratings, and suggestions
-- ============================================================================

CREATE TABLE IF NOT EXISTS source_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL CHECK (feedback_type IN ('accuracy_issue', 'outdated', 'missing_content', 'positive', 'suggestion')),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    resolved BOOLEAN DEFAULT false,
    resolved_by VARCHAR(255),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_source ON source_feedback(source_id);
CREATE INDEX idx_feedback_customer ON source_feedback(customer_id);
CREATE INDEX idx_feedback_type ON source_feedback(feedback_type);
CREATE INDEX idx_feedback_resolved ON source_feedback(resolved);
CREATE INDEX idx_feedback_created_at ON source_feedback(created_at);

-- ============================================================================
-- SOURCE CONCEPTS TABLE
-- Semantic discovery - map concepts to sources for intelligent search
-- Example: "cognitive bias" → Sherman Kent, Heuer, Bellingcat
-- ============================================================================

CREATE TABLE IF NOT EXISTS source_concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    concept_name VARCHAR(255) NOT NULL,
    concept_category VARCHAR(100) CHECK (concept_category IN ('technique', 'principle', 'tool', 'framework', 'methodology', 'theory', 'practice_area')),
    relevance_score DECIMAL(3,2) CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    context_snippet TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(source_id, concept_name)
);

CREATE INDEX idx_concepts_source ON source_concepts(source_id);
CREATE INDEX idx_concepts_name ON source_concepts(concept_name);
CREATE INDEX idx_concepts_category ON source_concepts(concept_category);
CREATE INDEX idx_concepts_relevance ON source_concepts(relevance_score);

-- ============================================================================
-- SOURCE RELATIONSHIPS TABLE
-- Knowledge graph - how sources relate to each other
-- ============================================================================

CREATE TABLE IF NOT EXISTS source_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    related_source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
        'builds_on',        -- Theory builds on earlier theory
        'contradicts',      -- Opposing viewpoints
        'applies',          -- Practice applies theory
        'validates',        -- Current research validates theory
        'supersedes',       -- Newer version replaces older
        'extends',          -- Expands on concepts
        'critiques',        -- Critical analysis
        'cites'             -- Academic citation
    )),
    relationship_strength VARCHAR(20) CHECK (relationship_strength IN ('strong', 'moderate', 'weak')),
    relationship_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(source_id, related_source_id, relationship_type),
    CHECK (source_id != related_source_id)
);

CREATE INDEX idx_relationships_source ON source_relationships(source_id);
CREATE INDEX idx_relationships_related ON source_relationships(related_source_id);
CREATE INDEX idx_relationships_type ON source_relationships(relationship_type);
CREATE INDEX idx_relationships_strength ON source_relationships(relationship_strength);

-- ============================================================================
-- SOURCE USE CASES TABLE
-- Problem-driven discovery - map real-world problems to relevant sources
-- Example: "Verify Twitter account authenticity" → Bellingcat, RAND, platform guides
-- ============================================================================

CREATE TABLE IF NOT EXISTS source_use_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    use_case_name VARCHAR(255) NOT NULL,
    use_case_category VARCHAR(100) CHECK (use_case_category IN (
        'intelligence_analysis', 'proposal_writing', 'threat_detection', 
        'compliance_verification', 'research', 'training', 'decision_making'
    )),
    applicability_score DECIMAL(3,2) CHECK (applicability_score >= 0.0 AND applicability_score <= 1.0),
    example TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(source_id, use_case_name)
);

CREATE INDEX idx_use_cases_source ON source_use_cases(source_id);
CREATE INDEX idx_use_cases_name ON source_use_cases(use_case_name);
CREATE INDEX idx_use_cases_category ON source_use_cases(use_case_category);
CREATE INDEX idx_use_cases_applicability ON source_use_cases(applicability_score);

-- ============================================================================
-- LEARNING PATHS TABLE
-- Structured curriculum sequencing (beginner → intermediate → advanced → expert)
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_role VARCHAR(100),
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_duration_hours INTEGER,
    sequence_order JSONB NOT NULL, -- [{source_id: UUID, order: 1, prerequisite_ids: [UUID]}]
    created_by VARCHAR(255),
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(name)
);

CREATE INDEX idx_learning_paths_category ON learning_paths(category_id);
CREATE INDEX idx_learning_paths_difficulty ON learning_paths(difficulty_level);
CREATE INDEX idx_learning_paths_role ON learning_paths(target_role);
CREATE INDEX idx_learning_paths_published ON learning_paths(is_published);

-- ============================================================================
-- SOURCE VERSIONS TABLE
-- Version history tracking for sources that change over time
-- ============================================================================

CREATE TABLE IF NOT EXISTS source_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    version_number VARCHAR(20) NOT NULL,
    url TEXT NOT NULL,
    breaking_changes BOOLEAN DEFAULT false,
    change_summary TEXT,
    migration_notes TEXT,
    archived_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(source_id, version_number)
);

CREATE INDEX idx_versions_source ON source_versions(source_id);
CREATE INDEX idx_versions_archived ON source_versions(archived_at);
CREATE INDEX idx_versions_breaking ON source_versions(breaking_changes);

-- ============================================================================
-- QUALITY HISTORY TABLE
-- Track quality metrics over time for proactive degradation detection
-- ============================================================================

CREATE TABLE IF NOT EXISTS quality_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    authority_score INTEGER CHECK (authority_score >= 0 AND authority_score <= 100),
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    validation_status VARCHAR(20) CHECK (validation_status IN ('unvalidated', 'validated', 'flagged', 'deprecated')),
    customer_feedback_count INTEGER DEFAULT 0,
    average_customer_rating DECIMAL(2,1),
    usage_count INTEGER DEFAULT 0,
    citation_count INTEGER DEFAULT 0,
    measurement_notes TEXT
);

CREATE INDEX idx_quality_history_source ON quality_history(source_id);
CREATE INDEX idx_quality_history_measured_at ON quality_history(measured_at);
CREATE INDEX idx_quality_history_authority ON quality_history(authority_score);
CREATE INDEX idx_quality_history_quality ON quality_history(quality_score);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Multi-tenant isolation
-- ============================================================================

ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE connector_query_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_feedback ENABLE ROW LEVEL SECURITY;

-- Sources: All customers can read, only admins can write
CREATE POLICY sources_read_policy ON sources FOR SELECT USING (true);
CREATE POLICY sources_write_policy ON sources FOR ALL USING (current_user = 'fredesa_admin');

-- Customers: Users can only see their own data
CREATE POLICY customers_isolation_policy ON customers FOR ALL 
    USING (id::text = current_setting('app.current_customer_id', TRUE));

-- Usage tracking: Users can only see their own usage
CREATE POLICY usage_tracking_isolation_policy ON usage_tracking FOR ALL 
    USING (customer_id::text = current_setting('app.current_customer_id', TRUE));

-- Customer connectors: Users can only see their own connectors
CREATE POLICY connectors_isolation_policy ON customer_connectors FOR ALL 
    USING (customer_id::text = current_setting('app.current_customer_id', TRUE));

-- Connector query log: Users can only see their own queries
CREATE POLICY connector_log_isolation_policy ON connector_query_log FOR ALL 
    USING (customer_id::text = current_setting('app.current_customer_id', TRUE));

-- Source feedback: Users can only see their own feedback
CREATE POLICY feedback_isolation_policy ON source_feedback FOR ALL 
    USING (customer_id::text = current_setting('app.current_customer_id', TRUE));

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_connectors_updated_at BEFORE UPDATE ON customer_connectors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_learning_paths_updated_at BEFORE UPDATE ON learning_paths
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Auto-update category epistemological statistics
CREATE OR REPLACE FUNCTION maintain_category_statistics()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE categories SET
            total_sources = (SELECT COUNT(*) FROM sources WHERE category_id = NEW.category_id),
            theory_sources = (SELECT COUNT(*) FROM sources WHERE category_id = NEW.category_id AND epistemological_dimension = 'theory'),
            practice_sources = (SELECT COUNT(*) FROM sources WHERE category_id = NEW.category_id AND epistemological_dimension = 'practice'),
            history_sources = (SELECT COUNT(*) FROM sources WHERE category_id = NEW.category_id AND epistemological_dimension = 'history'),
            current_sources = (SELECT COUNT(*) FROM sources WHERE category_id = NEW.category_id AND epistemological_dimension = 'current'),
            future_sources = (SELECT COUNT(*) FROM sources WHERE category_id = NEW.category_id AND epistemological_dimension = 'future')
        WHERE id = NEW.category_id;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        UPDATE categories SET
            total_sources = (SELECT COUNT(*) FROM sources WHERE category_id = OLD.category_id),
            theory_sources = (SELECT COUNT(*) FROM sources WHERE category_id = OLD.category_id AND epistemological_dimension = 'theory'),
            practice_sources = (SELECT COUNT(*) FROM sources WHERE category_id = OLD.category_id AND epistemological_dimension = 'practice'),
            history_sources = (SELECT COUNT(*) FROM sources WHERE category_id = OLD.category_id AND epistemological_dimension = 'history'),
            current_sources = (SELECT COUNT(*) FROM sources WHERE category_id = OLD.category_id AND epistemological_dimension = 'current'),
            future_sources = (SELECT COUNT(*) FROM sources WHERE category_id = OLD.category_id AND epistemological_dimension = 'future')
        WHERE id = OLD.category_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maintain_category_stats AFTER INSERT OR UPDATE OR DELETE ON sources
    FOR EACH ROW EXECUTE FUNCTION maintain_category_statistics();

-- Auto-calculate authority score based on source type
CREATE OR REPLACE FUNCTION auto_calculate_authority_score()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.authority_score IS NULL THEN
        NEW.authority_score = CASE NEW.source_type
            WHEN 'official' THEN 90
            WHEN 'expert' THEN 70
            WHEN 'community' THEN 50
            ELSE 40
        END;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_authority_score BEFORE INSERT OR UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION auto_calculate_authority_score();

-- Auto-maintain citation counts
CREATE OR REPLACE FUNCTION maintain_citation_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE sources SET cited_by_count = cited_by_count + 1 WHERE id = NEW.related_source_id;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        UPDATE sources SET cited_by_count = GREATEST(cited_by_count - 1, 0) WHERE id = OLD.related_source_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maintain_citation_counts_trigger AFTER INSERT OR DELETE ON source_relationships
    FOR EACH ROW EXECUTE FUNCTION maintain_citation_counts();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active sources (currently ingested and not deprecated)
CREATE OR REPLACE VIEW active_sources AS
SELECT 
    s.*,
    c.name as category_name,
    c.display_name as category_display_name,
    CASE 
        WHEN s.environment_flags->>'production' = 'true' THEN 'production'
        WHEN s.environment_flags->>'staging' = 'true' THEN 'staging'
        WHEN s.environment_flags->>'dev' = 'true' THEN 'dev'
        ELSE 'unknown'
    END as current_environment
FROM sources s
JOIN categories c ON s.category_id = c.id
WHERE s.ingestion_status = 'completed' 
  AND s.validation_status != 'deprecated';

-- Production-ready sources only
CREATE OR REPLACE VIEW production_sources AS
SELECT 
    s.*,
    c.name as category_name,
    c.display_name as category_display_name
FROM sources s
JOIN categories c ON s.category_id = c.id
WHERE s.environment_flags->>'production' = 'true'
  AND s.validation_status = 'validated'
  AND s.approval_status = 'approved';

-- Vertical completeness tracking
CREATE OR REPLACE VIEW vertical_completeness AS
SELECT 
    c.name as category_name,
    c.display_name,
    c.total_sources,
    c.theory_sources,
    c.practice_sources,
    c.history_sources,
    c.current_sources,
    c.future_sources,
    ROUND(100.0 * c.theory_sources / NULLIF(c.total_sources, 0), 1) as theory_percent,
    ROUND(100.0 * c.practice_sources / NULLIF(c.total_sources, 0), 1) as practice_percent,
    ROUND(100.0 * c.history_sources / NULLIF(c.total_sources, 0), 1) as history_percent,
    ROUND(100.0 * c.current_sources / NULLIF(c.total_sources, 0), 1) as current_percent,
    ROUND(100.0 * c.future_sources / NULLIF(c.total_sources, 0), 1) as future_percent
FROM categories c
WHERE c.total_sources > 0
ORDER BY c.total_sources DESC;

-- Knowledge graph summary
CREATE OR REPLACE VIEW knowledge_graph_summary AS
SELECT 
    s.id as source_id,
    s.name as source_name,
    s.category_id,
    COUNT(DISTINCT sc.id) as concept_count,
    COUNT(DISTINCT sr.id) as relationship_count,
    COUNT(DISTINCT suc.id) as use_case_count,
    AVG(sc.relevance_score) as avg_concept_relevance,
    s.cited_by_count,
    s.difficulty_level,
    ARRAY_AGG(DISTINCT sc.concept_name) FILTER (WHERE sc.relevance_score > 0.7) as key_concepts
FROM sources s
LEFT JOIN source_concepts sc ON s.id = sc.source_id
LEFT JOIN source_relationships sr ON s.id = sr.source_id
LEFT JOIN source_use_cases suc ON s.id = suc.source_id
GROUP BY s.id, s.name, s.category_id, s.cited_by_count, s.difficulty_level;

-- Curriculum-ready sources (have prerequisites and difficulty level)
CREATE OR REPLACE VIEW curriculum_ready_sources AS
SELECT 
    s.id,
    s.name,
    s.difficulty_level,
    s.prerequisite_sources,
    s.estimated_read_time_minutes,
    c.name as category_name,
    COUNT(lp.id) as learning_path_count
FROM sources s
JOIN categories c ON s.category_id = c.id
LEFT JOIN learning_paths lp ON s.category_id = lp.category_id
WHERE s.difficulty_level IS NOT NULL
GROUP BY s.id, s.name, s.difficulty_level, s.prerequisite_sources, s.estimated_read_time_minutes, c.name;

-- Customer stats
CREATE OR REPLACE VIEW customer_stats AS
SELECT 
    c.id,
    c.name,
    c.tier,
    COUNT(DISTINCT ut.id) as total_queries,
    COUNT(DISTINCT CASE WHEN ut.query_type = 'federated_query' THEN ut.id END) as federated_queries,
    SUM(ut.cost_incurred) as total_cost,
    COUNT(DISTINCT cc.id) as active_connectors,
    COUNT(DISTINCT sf.id) as feedback_count
FROM customers c
LEFT JOIN usage_tracking ut ON c.id = ut.customer_id
LEFT JOIN customer_connectors cc ON c.id = cc.customer_id AND cc.is_active = true
LEFT JOIN source_feedback sf ON c.id = sf.customer_id
GROUP BY c.id, c.name, c.tier;

-- Pending approvals
CREATE OR REPLACE VIEW pending_approvals AS
SELECT 
    s.id,
    s.name,
    s.category_id,
    c.name as category_name,
    s.authority_score,
    s.quality_score,
    s.approval_status,
    s.created_at,
    CASE 
        WHEN s.environment_flags->>'staging' = 'true' THEN 'staging → production'
        WHEN s.environment_flags->>'dev' = 'true' THEN 'dev → staging'
        ELSE 'new source'
    END as promotion_type
FROM sources s
JOIN categories c ON s.category_id = c.id
WHERE s.approval_status = 'pending'
ORDER BY s.created_at;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Sample categories
INSERT INTO categories (name, display_name, description, icon_name, sort_order) VALUES
('federal_contracting', 'Federal Contracting', 'FAR, DFARS, proposal development, capture planning', 'description', 1),
('intelligence', 'Intelligence Community', 'OSINT, HUMINT, competitive intelligence, analysis frameworks', 'shield', 2),
('cybersecurity', 'Cybersecurity', 'NIST frameworks, zero trust, threat intelligence, compliance', 'security', 3),
('ai_platforms', 'AI/LLM Platforms', 'Airia, OpenAI, Anthropic, platform documentation', 'smart_toy', 4),
('standards', 'Standards & Protocols', 'OpenAPI, REST, HTTP/2, YAML, API specifications', 'code', 5)
ON CONFLICT (name) DO NOTHING;

-- Sample test customer
INSERT INTO customers (name, email, tier, max_federated_sources, max_custom_agents) VALUES
('Test Customer', 'test@fredesa.ai', 'enterprise', 100, 50)
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================

COMMENT ON SCHEMA public IS 'FreDeSa AI Platform Schema v2.1 - Complete Epistemological Framework with Knowledge Graph';
