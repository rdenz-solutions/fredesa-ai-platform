-- Add missing columns to sources table for schema v2.1 completeness
-- Run date: 2025-12-29

ALTER TABLE sources ADD COLUMN IF NOT EXISTS quality_score DECIMAL(5,2) DEFAULT 50.00;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS citation_count INTEGER DEFAULT 0;

-- Create required index
CREATE INDEX IF NOT EXISTS idx_sources_quality_score ON sources(quality_score);

-- Verify columns exist
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'sources' 
AND column_name IN ('quality_score', 'citation_count');
