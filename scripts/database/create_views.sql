-- Create database views for schema v2.1
-- Run date: 2025-12-29

-- View 1: Knowledge Graph Summary
CREATE OR REPLACE VIEW knowledge_graph_summary_view AS
SELECT 
    c.id as category_id,
    c.display_name as category_name,
    COUNT(DISTINCT sc.id) as total_concepts,
    COUNT(DISTINCT sr.id) as total_relationships,
    COUNT(DISTINCT suc.id) as total_use_cases,
    COUNT(DISTINCT s.id) as total_sources
FROM categories c
LEFT JOIN source_concepts sc ON sc.category_id = c.id
LEFT JOIN source_relationships sr ON sr.from_concept_id IN (
    SELECT id FROM source_concepts WHERE category_id = c.id
)
LEFT JOIN source_use_cases suc ON suc.category_id = c.id
LEFT JOIN sources s ON s.category_id = c.id
GROUP BY c.id, c.display_name;

-- View 2: Customer Stats
CREATE OR REPLACE VIEW customer_stats_view AS
SELECT 
    cust.id as customer_id,
    cust.name as customer_name,
    COUNT(DISTINCT cc.id) as connector_count,
    COUNT(DISTINCT cql.id) as total_queries,
    COUNT(DISTINCT sf.id) as feedback_count,
    COUNT(DISTINCT s.id) as source_count
FROM customers cust
LEFT JOIN customer_connectors cc ON cc.customer_id = cust.id
LEFT JOIN connector_query_log cql ON cql.connector_id = cc.id
LEFT JOIN source_feedback sf ON sf.customer_id = cust.id
LEFT JOIN sources s ON s.customer_id = cust.id
GROUP BY cust.id, cust.name;

-- View 3: Active Sources
CREATE OR REPLACE VIEW active_sources_view AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.source_type,
    s.epistemological_dimension,
    s.difficulty_level,
    s.authority_score,
    s.quality_score,
    s.citation_count,
    c.display_name as category_name,
    s.created_at,
    s.updated_at
FROM sources s
LEFT JOIN categories c ON s.category_id = c.id
WHERE s.is_active = TRUE
AND s.validation_status = 'approved'
ORDER BY s.updated_at DESC;

-- View 4: Production Sources
CREATE OR REPLACE VIEW production_sources_view AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.environment,
    s.source_type,
    s.authority_score,
    s.quality_score,
    c.display_name as category_name,
    s.last_quality_check,
    s.times_accessed
FROM sources s
LEFT JOIN categories c ON s.category_id = c.id
WHERE s.environment = 'production'
AND s.is_active = TRUE
ORDER BY s.times_accessed DESC;

-- View 5: Vertical Completeness (Category Coverage)
CREATE OR REPLACE VIEW vertical_completeness_view AS
SELECT 
    c.id as category_id,
    c.display_name as category_name,
    c.theory_sources,
    c.practice_sources,
    c.history_sources,
    c.current_sources,
    c.future_sources,
    c.total_sources,
    CASE 
        WHEN c.theory_sources > 0 THEN 1 ELSE 0 END +
        CASE WHEN c.practice_sources > 0 THEN 1 ELSE 0 END +
        CASE WHEN c.history_sources > 0 THEN 1 ELSE 0 END +
        CASE WHEN c.current_sources > 0 THEN 1 ELSE 0 END +
        CASE WHEN c.future_sources > 0 THEN 1 ELSE 0 END
    as dimensions_covered,
    ROUND(
        (CASE WHEN c.theory_sources > 0 THEN 1.0 ELSE 0.0 END +
         CASE WHEN c.practice_sources > 0 THEN 1.0 ELSE 0.0 END +
         CASE WHEN c.history_sources > 0 THEN 1.0 ELSE 0.0 END +
         CASE WHEN c.current_sources > 0 THEN 1.0 ELSE 0.0 END +
         CASE WHEN c.future_sources > 0 THEN 1.0 ELSE 0.0 END) / 5.0 * 100, 2
    ) as completeness_percentage
FROM categories c
ORDER BY completeness_percentage DESC, c.total_sources DESC;

-- View 6: Curriculum Ready Sources
CREATE OR REPLACE VIEW curriculum_ready_sources_view AS
SELECT 
    s.id,
    s.name,
    s.url,
    s.difficulty_level,
    s.epistemological_dimension,
    s.authority_score,
    s.quality_score,
    c.display_name as category_name,
    COUNT(DISTINCT lp.id) as learning_path_count,
    s.prerequisites
FROM sources s
LEFT JOIN categories c ON s.category_id = c.id
LEFT JOIN learning_paths lp ON s.id = ANY(lp.source_sequence)
WHERE s.is_active = TRUE
AND s.validation_status = 'approved'
AND s.difficulty_level IS NOT NULL
GROUP BY s.id, s.name, s.url, s.difficulty_level, s.epistemological_dimension,
         s.authority_score, s.quality_score, c.display_name, s.prerequisites
ORDER BY s.difficulty_level, s.authority_score DESC;

-- View 7: Pending Approvals
CREATE OR REPLACE VIEW pending_approvals_view AS
SELECT 
    sp.id as promotion_id,
    s.name as source_name,
    sp.from_environment,
    sp.to_environment,
    sp.promotion_status,
    sp.promoted_by,
    sp.created_at,
    c.display_name as category_name
FROM source_promotions sp
JOIN sources s ON sp.source_id = s.id
LEFT JOIN categories c ON s.category_id = c.id
WHERE sp.promotion_status = 'pending'
ORDER BY sp.created_at ASC;

-- Verify views created
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'VIEW'
ORDER BY table_name;
