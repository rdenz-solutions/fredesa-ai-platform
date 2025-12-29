-- Fix source_relationships table to match test expectations
-- Current: concept-to-concept relationships
-- Expected: source-to-source relationships

DROP TABLE IF EXISTS source_relationships CASCADE;

CREATE TABLE source_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    related_source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
        'builds_on', 'contradicts', 'applies', 'validates'
    )),
    strength DECIMAL(3,2) CHECK (strength >= 0.0 AND strength <= 1.0) DEFAULT 0.80,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_id, related_source_id, relationship_type),
    CHECK (source_id != related_source_id)  -- Prevent self-referential relationships
);

CREATE INDEX IF NOT EXISTS idx_source_relationships_source ON source_relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_source_relationships_related ON source_relationships(related_source_id);
CREATE INDEX IF NOT EXISTS idx_source_relationships_type ON source_relationships(relationship_type);

-- Verify structure
\d source_relationships
