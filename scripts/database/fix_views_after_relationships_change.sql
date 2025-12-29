-- Fix views after source_relationships schema change
-- source_relationships is now source-to-source (not concept-to-concept)

-- View 1: Knowledge Graph Summary (FIXED - no longer references relationships from concepts)
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
LEFT JOIN sources s ON s.category_id = c.id
LEFT JOIN source_relationships sr ON sr.source_id = s.id OR sr.related_source_id = s.id
LEFT JOIN source_use_cases suc ON suc.category_id = c.id
GROUP BY c.id, c.display_name;

-- Create aliases without _view suffix
CREATE OR REPLACE VIEW knowledge_graph_summary AS SELECT * FROM knowledge_graph_summary_view;
CREATE OR REPLACE VIEW customer_stats AS SELECT * FROM customer_stats_view;
CREATE OR REPLACE VIEW active_sources AS SELECT * FROM active_sources_view;
CREATE OR REPLACE VIEW production_sources AS SELECT * FROM production_sources_view;
CREATE OR REPLACE VIEW vertical_completeness AS SELECT * FROM vertical_completeness_view;
CREATE OR REPLACE VIEW pending_approvals AS SELECT * FROM pending_approvals_view;

-- Enable RLS on connector_query_log
ALTER TABLE connector_query_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_query_log ON connector_query_log
    USING (EXISTS (
        SELECT 1 FROM customer_connectors cc
        WHERE cc.id = connector_query_log.connector_id
        AND (cc.customer_id = (current_setting('app.current_customer_id', true))::uuid
             OR current_setting('app.current_customer_id', true) IS NULL)
    ));
