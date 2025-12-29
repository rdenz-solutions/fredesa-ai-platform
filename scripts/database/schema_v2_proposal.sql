-- FreDeSa AI Platform - PostgreSQL Database Schema v2.0
-- Created: December 29, 2025
-- Purpose: Multi-tenant knowledge registry with epistemological completeness & federated architecture
-- Database: fredesa-db-dev.postgres.database.azure.com (PostgreSQL 15.15)
-- 
-- NEW FEATURES:
-- 1. Environment promotion workflow (dev → staging → prod)
-- 2. Epistemological dimension tracking (Theory, Practice, History, Current, Future)
-- 3. Quality validation and authority scoring
-- 4. Federated customer data connectors
-- 5. Fact-checking and source verification
-- 6. Audit trail for promotions and validations

-- Note: Using gen_random_uuid() instead of uuid-ossp extension for Azure compatibility

-- ============================================================================
-- TABLE: categories
-- Purpose: Knowledge categories and metadata
-- ============================================================================
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    source_count INTEGER DEFAULT 0,
    total_words BIGINT DEFAULT 0,
    parent_category UUID REFERENCES categories(id) ON DELETE SET NULL,
    
    -- NEW: Epistemological dimension stats
    theory_sources INTEGER DEFAULT 0,
    practice_sources INTEGER DEFAULT 0,
    history_sources INTEGER DEFAULT 0,
    current_sources INTEGER DEFAULT 0,
    future_sources INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT non_empty_category_name CHECK (LENGTH(TRIM(name)) > 0)
);

-- Index for category lookups and hierarchy
CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_categories_parent ON categories(parent_category);

-- ============================================================================
-- TABLE: sources
-- Purpose: Core knowledge registry with epistemological completeness tracking
-- ============================================================================
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    description TEXT,
    authority_level VARCHAR(50) DEFAULT 'Community',
    metadata JSONB DEFAULT '{}',
    
    -- Ingestion tracking (existing)
    ingestion_status VARCHAR(50) DEFAULT 'pending',
    ingestion_date TIMESTAMP,
    word_count INTEGER DEFAULT 0,
    file_count INTEGER DEFAULT 0,
    
    -- NEW: Environment promotion workflow
    environment_flags JSONB DEFAULT '{"dev": true, "staging": false, "production": false}'::jsonb,
    promoted_to_staging_at TIMESTAMP,
    promoted_to_production_at TIMESTAMP,
    promoted_by VARCHAR(255),
    approval_status VARCHAR(20) DEFAULT 'pending',
    
    -- NEW: Epistemological dimensions
    epistemological_dimension VARCHAR(20) CHECK (epistemological_dimension IN ('theory', 'practice', 'history', 'current', 'future')),
    publication_year INTEGER,
    
    -- NEW: Quality validation
    authority_score INTEGER CHECK (authority_score >= 0 AND authority_score <= 100),
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    validation_status VARCHAR(20) DEFAULT 'pending',
    fact_check_date TIMESTAMPTZ,
    fact_checked_by VARCHAR(255),
    
    -- NEW: Cross-reference tracking
    cross_reference_count INTEGER DEFAULT 0,
    superseded_by UUID REFERENCES sources(id),
    supersedes UUID REFERENCES sources(id),
    deprecation_reason TEXT,
    
    -- NEW: Federated source location
    source_location VARCHAR(50) DEFAULT 'rdenz_managed',
    
    -- Existing fields
    tenant_id UUID,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_url CHECK (url ~ '^https?://'),
    CONSTRAINT non_empty_name CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT valid_authority CHECK (authority_level IN ('Official', 'Expert', 'Community')),
    CONSTRAINT valid_status CHECK (ingestion_status IN ('pending', 'in_progress', 'complete', 'failed')),
    CONSTRAINT valid_approval CHECK (approval_status IN ('pending', 'approved_for_staging', 'approved_for_production', 'rejected')),
    CONSTRAINT valid_validation CHECK (validation_status IN ('pending', 'verified', 'disputed', 'stale', 'flagged', 'deprecated')),
    CONSTRAINT valid_location CHECK (source_location IN ('rdenz_managed', 'customer_sharepoint', 'customer_onedrive', 'customer_drive', 'customer_blob')),
    
    -- Foreign key to categories
    FOREIGN KEY (category) REFERENCES categories(name) ON UPDATE CASCADE
);

-- Existing indexes
CREATE INDEX idx_sources_category ON sources(category);
CREATE INDEX idx_sources_tenant ON sources(tenant_id);
CREATE INDEX idx_sources_status ON sources(ingestion_status);
CREATE INDEX idx_sources_active ON sources(is_active);
CREATE INDEX idx_sources_created ON sources(created_at DESC);
CREATE INDEX idx_sources_tenant_category ON sources(tenant_id, category);
CREATE INDEX idx_sources_search ON sources USING gin(
    to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(description, ''))
);

-- NEW: Epistemological indexes
CREATE INDEX idx_sources_dimension ON sources(epistemological_dimension);
CREATE INDEX idx_sources_category_dimension ON sources(category, epistemological_dimension);
CREATE INDEX idx_sources_publication_year ON sources(publication_year DESC);

-- NEW: Quality and validation indexes
CREATE INDEX idx_sources_authority_score ON sources(authority_score DESC);
CREATE INDEX idx_sources_quality_score ON sources(quality_score DESC);
CREATE INDEX idx_sources_validation_status ON sources(validation_status);
CREATE INDEX idx_sources_approval_status ON sources(approval_status);

-- NEW: Environment promotion indexes
CREATE INDEX idx_sources_environment_dev ON sources((environment_flags->>'dev')) WHERE (environment_flags->>'dev')::boolean = true;
CREATE INDEX idx_sources_environment_staging ON sources((environment_flags->>'staging')) WHERE (environment_flags->>'staging')::boolean = true;
CREATE INDEX idx_sources_environment_prod ON sources((environment_flags->>'production')) WHERE (environment_flags->>'production')::boolean = true;

-- NEW: Source location index (federated architecture)
CREATE INDEX idx_sources_location ON sources(source_location);

-- ============================================================================
-- TABLE: customers
-- Purpose: Multi-tenant customer accounts with scoped access
-- ============================================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    tenant_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free',
    allowed_categories JSONB DEFAULT '[]',
    allowed_sources UUID[] DEFAULT '{}',
    api_key_hash VARCHAR(255) UNIQUE,
    pinecone_namespace VARCHAR(100),
    max_api_calls_per_month INTEGER DEFAULT 5000,
    max_sources INTEGER DEFAULT 50,
    is_active BOOLEAN DEFAULT TRUE,
    trial_ends_at TIMESTAMP,
    subscription_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_tier CHECK (subscription_tier IN ('free', 'professional', 'enterprise', 'custom')),
    CONSTRAINT non_empty_customer_name CHECK (LENGTH(TRIM(name)) > 0)
);

-- Indexes for customer lookups
CREATE INDEX idx_customers_tenant ON customers(tenant_id);
CREATE INDEX idx_customers_api_key ON customers(api_key_hash);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_active ON customers(is_active);
CREATE INDEX idx_customers_tier ON customers(subscription_tier);

-- ============================================================================
-- TABLE: usage_tracking
-- Purpose: Track customer usage for billing and analytics
-- ============================================================================
CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    api_calls INTEGER DEFAULT 0,
    storage_gb DECIMAL(10, 2) DEFAULT 0,
    vector_searches INTEGER DEFAULT 0,
    sources_accessed INTEGER DEFAULT 0,
    total_tokens_used BIGINT DEFAULT 0,
    
    -- NEW: Federated query tracking
    federated_queries INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicate daily records
    UNIQUE(customer_id, date)
);

-- Indexes for usage queries
CREATE INDEX idx_usage_customer ON usage_tracking(customer_id);
CREATE INDEX idx_usage_date ON usage_tracking(date DESC);
CREATE INDEX idx_usage_customer_date ON usage_tracking(customer_id, date DESC);

-- ============================================================================
-- NEW TABLE: customer_connectors
-- Purpose: OAuth tokens and configuration for federated customer data
-- ============================================================================
CREATE TABLE customer_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_type VARCHAR(50) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    
    -- OAuth credentials (encrypted at application layer)
    oauth_access_token TEXT,
    oauth_refresh_token TEXT,
    oauth_token_expires_at TIMESTAMPTZ,
    
    -- Connector-specific configuration
    connector_config JSONB DEFAULT '{}',
    
    -- Status tracking
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMPTZ,
    last_sync_status VARCHAR(50),
    sync_error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_connector_type CHECK (connector_type IN ('sharepoint', 'onedrive', 'google_drive', 'azure_blob', 'file_upload')),
    CONSTRAINT valid_sync_status CHECK (last_sync_status IS NULL OR last_sync_status IN ('success', 'failed', 'in_progress'))
);

CREATE INDEX idx_connectors_customer ON customer_connectors(customer_id);
CREATE INDEX idx_connectors_type ON customer_connectors(connector_type);
CREATE INDEX idx_connectors_active ON customer_connectors(is_active);

-- ============================================================================
-- NEW TABLE: source_promotions
-- Purpose: Audit trail for environment promotions (dev → staging → prod)
-- ============================================================================
CREATE TABLE source_promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    from_environment VARCHAR(20) NOT NULL,
    to_environment VARCHAR(20) NOT NULL,
    promoted_by VARCHAR(255) NOT NULL,
    promotion_reason TEXT,
    approval_notes TEXT,
    
    -- Quality gates at promotion time
    authority_score_at_promotion INTEGER,
    quality_score_at_promotion INTEGER,
    validation_status_at_promotion VARCHAR(20),
    
    promoted_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_from_env CHECK (from_environment IN ('dev', 'staging')),
    CONSTRAINT valid_to_env CHECK (to_environment IN ('staging', 'production')),
    CONSTRAINT valid_promotion_flow CHECK (
        (from_environment = 'dev' AND to_environment = 'staging') OR
        (from_environment = 'staging' AND to_environment = 'production')
    )
);

CREATE INDEX idx_promotions_source ON source_promotions(source_id);
CREATE INDEX idx_promotions_promoted_at ON source_promotions(promoted_at DESC);
CREATE INDEX idx_promotions_promoted_by ON source_promotions(promoted_by);
CREATE INDEX idx_promotions_to_env ON source_promotions(to_environment);

-- ============================================================================
-- NEW TABLE: source_validations
-- Purpose: Track validation checks (authority, recency, cross-reference, customer feedback)
-- ============================================================================
CREATE TABLE source_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    validation_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB DEFAULT '{}',
    validated_by VARCHAR(255),
    validated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_validation_type CHECK (validation_type IN ('authority', 'cross_reference', 'recency', 'customer_feedback', 'contradiction_check', 'manual_review')),
    CONSTRAINT valid_validation_status CHECK (status IN ('pass', 'fail', 'warning', 'review_needed'))
);

CREATE INDEX idx_validations_source ON source_validations(source_id);
CREATE INDEX idx_validations_type ON source_validations(validation_type);
CREATE INDEX idx_validations_status ON source_validations(status);
CREATE INDEX idx_validations_date ON source_validations(validated_at DESC);

-- ============================================================================
-- NEW TABLE: source_feedback
-- Purpose: Customer-reported issues with sources
-- ============================================================================
CREATE TABLE source_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    issue_type VARCHAR(50) NOT NULL,
    evidence TEXT,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    resolution_notes TEXT,
    resolved_by VARCHAR(255),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_issue_type CHECK (issue_type IN ('outdated', 'inaccurate', 'disputed', 'missing_context', 'broken_link', 'duplicate', 'inappropriate')),
    CONSTRAINT valid_severity CHECK (severity IN ('critical', 'moderate', 'minor')),
    CONSTRAINT valid_feedback_status CHECK (status IN ('pending', 'reviewed', 'resolved', 'dismissed'))
);

CREATE INDEX idx_feedback_source ON source_feedback(source_id);
CREATE INDEX idx_feedback_customer ON source_feedback(customer_id);
CREATE INDEX idx_feedback_status ON source_feedback(status);
CREATE INDEX idx_feedback_severity ON source_feedback(severity);
CREATE INDEX idx_feedback_created ON source_feedback(created_at DESC);

-- ============================================================================
-- NEW TABLE: connector_query_log
-- Purpose: Track federated queries for billing and analytics
-- ============================================================================
CREATE TABLE connector_query_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_id UUID NOT NULL REFERENCES customer_connectors(id) ON DELETE CASCADE,
    query_type VARCHAR(50) NOT NULL,
    query_path TEXT,
    response_time_ms INTEGER,
    result_count INTEGER,
    error_message TEXT,
    queried_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_query_type CHECK (query_type IN ('list_files', 'search', 'get_content', 'get_metadata'))
);

CREATE INDEX idx_query_log_customer ON connector_query_log(customer_id);
CREATE INDEX idx_query_log_connector ON connector_query_log(connector_id);
CREATE INDEX idx_query_log_date ON connector_query_log(queried_at DESC);
CREATE INDEX idx_query_log_customer_date ON connector_query_log(customer_id, queried_at DESC);

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS)
-- Purpose: Enforce tenant isolation at database level
-- ============================================================================

-- Enable RLS on sources table
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see sources for their tenant or environment-appropriate sources
CREATE POLICY tenant_isolation_policy ON sources
    FOR ALL
    USING (
        tenant_id IS NULL OR  -- Allow access to shared/public sources
        tenant_id = current_setting('app.current_tenant_id', TRUE)::uuid
    );

-- Enable RLS on usage_tracking table
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own usage data
CREATE POLICY customer_usage_policy ON usage_tracking
    FOR ALL
    USING (
        customer_id = current_setting('app.current_customer_id', TRUE)::uuid
    );

-- Enable RLS on customer_connectors table
ALTER TABLE customer_connectors ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_connectors_policy ON customer_connectors
    FOR ALL
    USING (
        customer_id = current_setting('app.current_customer_id', TRUE)::uuid
    );

-- Enable RLS on source_feedback table
ALTER TABLE source_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_feedback_policy ON source_feedback
    FOR ALL
    USING (
        customer_id = current_setting('app.current_customer_id', TRUE)::uuid
    );

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- Purpose: Automated timestamp updates and statistics maintenance
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at on all tables
CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usage_updated_at BEFORE UPDATE ON usage_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_connectors_updated_at BEFORE UPDATE ON customer_connectors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- NEW: Function to update category statistics including epistemological dimensions
CREATE OR REPLACE FUNCTION update_category_statistics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update statistics for the affected category
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE categories
        SET 
            source_count = (SELECT COUNT(*) FROM sources WHERE category = NEW.category AND is_active = TRUE),
            theory_sources = (SELECT COUNT(*) FROM sources WHERE category = NEW.category AND epistemological_dimension = 'theory' AND is_active = TRUE),
            practice_sources = (SELECT COUNT(*) FROM sources WHERE category = NEW.category AND epistemological_dimension = 'practice' AND is_active = TRUE),
            history_sources = (SELECT COUNT(*) FROM sources WHERE category = NEW.category AND epistemological_dimension = 'history' AND is_active = TRUE),
            current_sources = (SELECT COUNT(*) FROM sources WHERE category = NEW.category AND epistemological_dimension = 'current' AND is_active = TRUE),
            future_sources = (SELECT COUNT(*) FROM sources WHERE category = NEW.category AND epistemological_dimension = 'future' AND is_active = TRUE)
        WHERE name = NEW.category;
    END IF;
    
    IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.category != NEW.category) THEN
        UPDATE categories
        SET 
            source_count = (SELECT COUNT(*) FROM sources WHERE category = OLD.category AND is_active = TRUE),
            theory_sources = (SELECT COUNT(*) FROM sources WHERE category = OLD.category AND epistemological_dimension = 'theory' AND is_active = TRUE),
            practice_sources = (SELECT COUNT(*) FROM sources WHERE category = OLD.category AND epistemological_dimension = 'practice' AND is_active = TRUE),
            history_sources = (SELECT COUNT(*) FROM sources WHERE category = OLD.category AND epistemological_dimension = 'history' AND is_active = TRUE),
            current_sources = (SELECT COUNT(*) FROM sources WHERE category = OLD.category AND epistemological_dimension = 'current' AND is_active = TRUE),
            future_sources = (SELECT COUNT(*) FROM sources WHERE category = OLD.category AND epistemological_dimension = 'future' AND is_active = TRUE)
        WHERE name = OLD.category;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger to maintain category statistics
CREATE TRIGGER maintain_category_statistics AFTER INSERT OR UPDATE OR DELETE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_category_statistics();

-- NEW: Function to automatically calculate authority score on source insert/update
CREATE OR REPLACE FUNCTION calculate_authority_score()
RETURNS TRIGGER AS $$
DECLARE
    score INTEGER := 0;
BEGIN
    -- Base score on authority level
    score := CASE NEW.authority_level
        WHEN 'Official' THEN 90
        WHEN 'Expert' THEN 70
        WHEN 'Community' THEN 50
        ELSE 30
    END;
    
    -- Adjust for publication recency (if applicable)
    IF NEW.publication_year IS NOT NULL THEN
        IF (EXTRACT(YEAR FROM CURRENT_DATE) - NEW.publication_year) <= 2 THEN
            score := score + 10;  -- Recent sources get bonus
        ELSIF (EXTRACT(YEAR FROM CURRENT_DATE) - NEW.publication_year) > 10 AND NEW.epistemological_dimension IN ('practice', 'current') THEN
            score := score - 20;  -- Old practice/current sources penalized
        END IF;
    END IF;
    
    -- Adjust for cross-references
    IF NEW.cross_reference_count > 3 THEN
        score := score + 10;  -- Well-referenced sources get bonus
    END IF;
    
    -- Cap at 100
    NEW.authority_score := LEAST(score, 100);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_calculate_authority_score BEFORE INSERT OR UPDATE ON sources
    FOR EACH ROW
    WHEN (NEW.authority_score IS NULL)
    EXECUTE FUNCTION calculate_authority_score();

-- ============================================================================
-- VIEWS
-- Purpose: Convenient queries for common use cases
-- ============================================================================

-- View: Active sources with category metadata and epistemological tracking
CREATE OR REPLACE VIEW active_sources AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.category,
    s.subcategory,
    s.description,
    s.authority_level,
    s.authority_score,
    s.quality_score,
    s.epistemological_dimension,
    s.publication_year,
    s.ingestion_status,
    s.validation_status,
    s.word_count,
    s.file_count,
    s.tenant_id,
    s.source_location,
    s.environment_flags,
    s.created_at,
    c.description AS category_description,
    c.source_count AS category_total_sources,
    c.theory_sources AS category_theory_count,
    c.practice_sources AS category_practice_count,
    c.history_sources AS category_history_count,
    c.current_sources AS category_current_count,
    c.future_sources AS category_future_count
FROM sources s
LEFT JOIN categories c ON s.category = c.name
WHERE s.is_active = TRUE;

-- NEW: View: Production-ready sources (for customer access)
CREATE OR REPLACE VIEW production_sources AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.category,
    s.subcategory,
    s.description,
    s.authority_level,
    s.authority_score,
    s.epistemological_dimension,
    s.publication_year,
    s.word_count,
    s.validation_status
FROM sources s
WHERE 
    s.is_active = TRUE 
    AND (s.environment_flags->>'production')::boolean = true
    AND s.validation_status = 'verified';

-- NEW: View: Epistemological completeness by vertical
CREATE OR REPLACE VIEW vertical_completeness AS
SELECT 
    category,
    COUNT(*) as total_sources,
    COUNT(*) FILTER (WHERE epistemological_dimension = 'theory') as theory_count,
    COUNT(*) FILTER (WHERE epistemological_dimension = 'practice') as practice_count,
    COUNT(*) FILTER (WHERE epistemological_dimension = 'history') as history_count,
    COUNT(*) FILTER (WHERE epistemological_dimension = 'current') as current_count,
    COUNT(*) FILTER (WHERE epistemological_dimension = 'future') as future_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE epistemological_dimension = 'theory') / NULLIF(COUNT(*), 0), 1) as theory_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE epistemological_dimension = 'practice') / NULLIF(COUNT(*), 0), 1) as practice_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE epistemological_dimension = 'history') / NULLIF(COUNT(*), 0), 1) as history_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE epistemological_dimension = 'current') / NULLIF(COUNT(*), 0), 1) as current_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE epistemological_dimension = 'future') / NULLIF(COUNT(*), 0), 1) as future_pct,
    AVG(authority_score) as avg_authority_score,
    AVG(quality_score) as avg_quality_score
FROM sources
WHERE is_active = TRUE
GROUP BY category
ORDER BY total_sources DESC;

-- View: Customer statistics
CREATE OR REPLACE VIEW customer_stats AS
SELECT 
    c.id,
    c.name,
    c.email,
    c.subscription_tier,
    c.is_active,
    COUNT(DISTINCT s.id) AS accessible_sources,
    COALESCE(SUM(u.api_calls), 0) AS total_api_calls,
    COALESCE(SUM(u.vector_searches), 0) AS total_vector_searches,
    COALESCE(SUM(u.federated_queries), 0) AS total_federated_queries,
    COUNT(DISTINCT conn.id) AS active_connectors,
    c.created_at
FROM customers c
LEFT JOIN sources s ON s.tenant_id = c.tenant_id
LEFT JOIN usage_tracking u ON u.customer_id = c.id
LEFT JOIN customer_connectors conn ON conn.customer_id = c.id AND conn.is_active = TRUE
GROUP BY c.id, c.name, c.email, c.subscription_tier, c.is_active, c.created_at;

-- NEW: View: Sources pending approval
CREATE OR REPLACE VIEW pending_approvals AS
SELECT 
    s.id,
    s.name,
    s.category,
    s.epistemological_dimension,
    s.authority_score,
    s.quality_score,
    s.validation_status,
    s.approval_status,
    s.created_at,
    COUNT(v.id) FILTER (WHERE v.status = 'fail') as failed_validations,
    COUNT(v.id) FILTER (WHERE v.status = 'warning') as validation_warnings
FROM sources s
LEFT JOIN source_validations v ON v.source_id = s.id
WHERE s.approval_status = 'pending' AND s.is_active = TRUE
GROUP BY s.id, s.name, s.category, s.epistemological_dimension, s.authority_score, s.quality_score, s.validation_status, s.approval_status, s.created_at
ORDER BY s.created_at ASC;

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample categories
INSERT INTO categories (name, description) VALUES
    ('Standards', 'Technical standards and specifications'),
    ('Federal_Contracting', 'Federal acquisition regulations and guidelines'),
    ('Program_Management', 'Project and program management methodologies'),
    ('Cybersecurity', 'Information security standards and best practices'),
    ('Intelligence', 'Intelligence analysis and OSINT methodologies')
ON CONFLICT (name) DO NOTHING;

-- Insert sample customer (for testing)
INSERT INTO customers (
    name, 
    email, 
    subscription_tier, 
    allowed_categories,
    pinecone_namespace
) VALUES (
    'Beta Test Customer',
    'test@fredesa.com',
    'professional',
    '["Standards", "Federal_Contracting"]'::jsonb,
    'customer_beta_test'
) ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- GRANT PERMISSIONS
-- Purpose: Set appropriate database permissions
-- ============================================================================

-- Grant all privileges on tables to application user (fredesaadmin)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fredesaadmin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fredesaadmin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO fredesaadmin;

-- ============================================================================
-- SCHEMA v2.0 COMPLETE
-- ============================================================================

-- Verify schema creation
SELECT 
    'Schema v2.0 - Tables created: ' || COUNT(*) AS status
FROM information_schema.tables
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN (
        'sources', 'categories', 'customers', 'usage_tracking',
        'customer_connectors', 'source_promotions', 'source_validations', 
        'source_feedback', 'connector_query_log'
    );
