-- FreDeSa AI Platform - PostgreSQL Database Schema
-- Created: December 29, 2025
-- Purpose: Multi-tenant knowledge registry with customer isolation
-- Database: fredesa-db-dev.postgres.database.azure.com (PostgreSQL 15.15)

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT non_empty_category_name CHECK (LENGTH(TRIM(name)) > 0)
);

-- Index for category lookups and hierarchy
CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_categories_parent ON categories(parent_category);

-- ============================================================================
-- TABLE: sources
-- Purpose: Core knowledge registry - each source represents a document/URL
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
    ingestion_status VARCHAR(50) DEFAULT 'pending',
    ingestion_date TIMESTAMP,
    word_count INTEGER DEFAULT 0,
    file_count INTEGER DEFAULT 0,
    tenant_id UUID,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_url CHECK (url ~ '^https?://'),
    CONSTRAINT non_empty_name CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT valid_authority CHECK (authority_level IN ('Official', 'Expert', 'Community')),
    CONSTRAINT valid_status CHECK (ingestion_status IN ('pending', 'in_progress', 'complete', 'failed')),
    
    -- Foreign key to categories
    FOREIGN KEY (category) REFERENCES categories(name) ON UPDATE CASCADE
);

-- Indexes for common queries
CREATE INDEX idx_sources_category ON sources(category);
CREATE INDEX idx_sources_tenant ON sources(tenant_id);
CREATE INDEX idx_sources_status ON sources(ingestion_status);
CREATE INDEX idx_sources_active ON sources(is_active);
CREATE INDEX idx_sources_created ON sources(created_at DESC);

-- Full-text search index
CREATE INDEX idx_sources_search ON sources USING gin(
    to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(description, ''))
);

-- Composite index for tenant + category queries (common pattern)
CREATE INDEX idx_sources_tenant_category ON sources(tenant_id, category);

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
-- ROW-LEVEL SECURITY (RLS)
-- Purpose: Enforce tenant isolation at database level
-- ============================================================================

-- Enable RLS on sources table
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see sources for their tenant
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

-- Function to update category source count
CREATE OR REPLACE FUNCTION update_category_source_count()
RETURNS TRIGGER AS $$
BEGIN
    -- Update source count for the affected category
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE categories
        SET source_count = (
            SELECT COUNT(*) FROM sources WHERE category = NEW.category AND is_active = TRUE
        )
        WHERE name = NEW.category;
    END IF;
    
    IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.category != NEW.category) THEN
        UPDATE categories
        SET source_count = (
            SELECT COUNT(*) FROM sources WHERE category = OLD.category AND is_active = TRUE
        )
        WHERE name = OLD.category;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger to maintain category source counts
CREATE TRIGGER maintain_category_counts AFTER INSERT OR UPDATE OR DELETE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_category_source_count();

-- ============================================================================
-- VIEWS
-- Purpose: Convenient queries for common use cases
-- ============================================================================

-- View: Active sources with category metadata
CREATE OR REPLACE VIEW active_sources AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.category,
    s.subcategory,
    s.description,
    s.authority_level,
    s.ingestion_status,
    s.word_count,
    s.file_count,
    s.tenant_id,
    s.created_at,
    c.description AS category_description,
    c.source_count AS category_total_sources
FROM sources s
LEFT JOIN categories c ON s.category = c.name
WHERE s.is_active = TRUE;

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
    c.created_at
FROM customers c
LEFT JOIN sources s ON s.tenant_id = c.tenant_id
LEFT JOIN usage_tracking u ON u.customer_id = c.id
GROUP BY c.id, c.name, c.email, c.subscription_tier, c.is_active, c.created_at;

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
-- SCHEMA COMPLETE
-- ============================================================================

-- Verify schema creation
SELECT 
    'Tables created: ' || COUNT(*) AS status
FROM information_schema.tables
WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    AND table_name IN ('sources', 'categories', 'customers', 'usage_tracking');
