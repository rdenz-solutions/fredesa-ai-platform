# Priority 3: Supporting Tables (Week 3)

## ✅ Completed (Weeks 1-2)
- **Week 1:** Schema v2.1 core + Priority 1 triggers (4/28 tests passing)
- **Week 2:** Knowledge graph tables (6/28 tests passing)

## 🎯 This Week's Goal
Add 6 supporting tables to complete schema structure and improve test coverage to **15-20/28**

## Current Status

**Existing Tables (9):**
- ✅ categories
- ✅ sources  
- ✅ customers
- ✅ usage_tracking
- ✅ source_concepts (renamed from concepts)
- ✅ source_relationships (renamed from relationships)
- ✅ source_use_cases (renamed from use_cases)
- ✅ customer_connectors
- ✅ citations

**Missing Tables (6) - Priority 3:**
1. connector_query_log
2. source_promotions
3. source_validations
4. source_feedback
5. learning_paths
6. source_versions
7. quality_history

## Priority 3 Tables (Create This Week)

### Table 1: `connector_query_log`
**Purpose:** Track customer connector queries and performance

```sql
CREATE TABLE connector_query_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES customer_connectors(id) ON DELETE CASCADE,
    query_text TEXT,
    query_type VARCHAR(50),
    results_count INTEGER,
    execution_time_ms INTEGER,
    status VARCHAR(20) CHECK (status IN ('success', 'error', 'timeout')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_connector_query_log_connector ON connector_query_log(connector_id);
CREATE INDEX idx_connector_query_log_status ON connector_query_log(status);
CREATE INDEX idx_connector_query_log_created ON connector_query_log(created_at);
```

**Tests affected:**
- test_01_all_tables_exist
- test_17_customer_connectors_oauth

### Table 2: `source_promotions`
**Purpose:** Track source promotions through environments (dev → staging → prod)

```sql
CREATE TABLE source_promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    from_environment VARCHAR(20) CHECK (from_environment IN ('development', 'staging', 'production')),
    to_environment VARCHAR(20) CHECK (to_environment IN ('development', 'staging', 'production')),
    promoted_by VARCHAR(255),
    promotion_status VARCHAR(20) DEFAULT 'pending' CHECK (promotion_status IN (
        'pending', 'approved', 'rejected', 'completed'
    )),
    approval_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_source_promotions_source ON source_promotions(source_id);
CREATE INDEX idx_source_promotions_status ON source_promotions(promotion_status);
```

**Tests affected:**
- test_01_all_tables_exist
- test_15_environment_promotion_workflow
- test_16_pending_approvals_view

### Table 3: `source_validations`
**Purpose:** Track validation checks and quality scores

```sql
CREATE TABLE source_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    validation_type VARCHAR(50) NOT NULL,
    validation_status VARCHAR(20) CHECK (validation_status IN ('pass', 'fail', 'warning')),
    validation_score DECIMAL(5,2),
    validation_details JSONB,
    validated_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source_validations_source ON source_validations(source_id);
CREATE INDEX idx_source_validations_status ON source_validations(validation_status);
```

**Tests affected:**
- test_01_all_tables_exist
- test_13_source_validations_tracking

### Table 4: `source_feedback`
**Purpose:** Customer feedback and issue tracking for sources

```sql
CREATE TABLE source_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) CHECK (feedback_type IN (
        'bug', 'feature_request', 'improvement', 'question', 'compliment'
    )),
    feedback_text TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_source_feedback_source ON source_feedback(source_id);
CREATE INDEX idx_source_feedback_customer ON source_feedback(customer_id);
CREATE INDEX idx_source_feedback_status ON source_feedback(status);
```

**Tests affected:**
- test_01_all_tables_exist
- test_14_source_feedback_customer_issues

### Table 5: `learning_paths`
**Purpose:** Define structured learning curricula using sources

```sql
CREATE TABLE learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN (
        'beginner', 'intermediate', 'advanced', 'expert'
    )),
    estimated_hours INTEGER,
    source_sequence UUID[] DEFAULT '{}',  -- Ordered array of source IDs
    prerequisites UUID[] DEFAULT '{}',    -- Array of prerequisite path IDs
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learning_paths_category ON learning_paths(category_id);
CREATE INDEX idx_learning_paths_difficulty ON learning_paths(difficulty_level);
CREATE INDEX idx_learning_paths_published ON learning_paths(is_published);
```

**Tests affected:**
- test_01_all_tables_exist
- test_09_learning_paths_curriculum
- test_23_curriculum_ready_sources_view

### Table 6: `source_versions`
**Purpose:** Version history and change tracking for sources

```sql
CREATE TABLE source_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    change_summary TEXT,
    changed_by VARCHAR(255),
    source_snapshot JSONB,  -- Full source data at this version
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_id, version_number)
);

CREATE INDEX idx_source_versions_source ON source_versions(source_id);
CREATE INDEX idx_source_versions_created ON source_versions(created_at);
```

**Tests affected:**
- test_01_all_tables_exist
- test_10_source_versions_history

### Table 7: `quality_history`
**Purpose:** Time-series tracking of source quality metrics

```sql
CREATE TABLE quality_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    quality_score DECIMAL(5,2) NOT NULL,
    authority_score INTEGER,
    validation_count INTEGER,
    feedback_count INTEGER,
    usage_count INTEGER,
    measured_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quality_history_source ON quality_history(source_id);
CREATE INDEX idx_quality_history_measured ON quality_history(measured_at);
CREATE INDEX idx_quality_history_score ON quality_history(quality_score);
```

**Tests affected:**
- test_01_all_tables_exist
- test_11_quality_history_time_series

## Implementation Script

Create `scripts/database/create_priority_3_tables.py`:

```python
#!/usr/bin/env python3
"""
Create Priority 3 tables (Supporting Infrastructure)
Week 3 of schema v2.1 implementation
"""

import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main():
    print("\n" + "="*70)
    print("Creating Priority 3 Tables (Supporting Infrastructure)")
    print("="*70 + "\n")
    
    # Get database password
    credential = DefaultAzureCredential()
    vault_url = "https://fredesa-kv-e997e3.vault.azure.net/"
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    password = secret_client.get_secret('postgres-password').value
    
    # Connect
    conn = psycopg2.connect(
        host='fredesa-db-dev.postgres.database.azure.com',
        port=5432,
        database='postgres',
        user='fredesaadmin',
        password=password,
        sslmode='require'
    )
    
    try:
        cursor = conn.cursor()
        
        # Table 1: connector_query_log
        print("1. Creating connector_query_log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connector_query_log (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                connector_id UUID NOT NULL REFERENCES customer_connectors(id) ON DELETE CASCADE,
                query_text TEXT,
                query_type VARCHAR(50),
                results_count INTEGER,
                execution_time_ms INTEGER,
                status VARCHAR(20) CHECK (status IN ('success', 'error', 'timeout')),
                error_message TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_connector_query_log_connector ON connector_query_log(connector_id);
            CREATE INDEX IF NOT EXISTS idx_connector_query_log_status ON connector_query_log(status);
            CREATE INDEX IF NOT EXISTS idx_connector_query_log_created ON connector_query_log(created_at);
        """)
        print("   ✓ Complete\n")
        
        # Table 2: source_promotions
        print("2. Creating source_promotions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_promotions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                from_environment VARCHAR(20) CHECK (from_environment IN ('development', 'staging', 'production')),
                to_environment VARCHAR(20) CHECK (to_environment IN ('development', 'staging', 'production')),
                promoted_by VARCHAR(255),
                promotion_status VARCHAR(20) DEFAULT 'pending' CHECK (promotion_status IN (
                    'pending', 'approved', 'rejected', 'completed'
                )),
                approval_notes TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMPTZ
            );
            
            CREATE INDEX IF NOT EXISTS idx_source_promotions_source ON source_promotions(source_id);
            CREATE INDEX IF NOT EXISTS idx_source_promotions_status ON source_promotions(promotion_status);
        """)
        print("   ✓ Complete\n")
        
        # Table 3: source_validations
        print("3. Creating source_validations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_validations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                validation_type VARCHAR(50) NOT NULL,
                validation_status VARCHAR(20) CHECK (validation_status IN ('pass', 'fail', 'warning')),
                validation_score DECIMAL(5,2),
                validation_details JSONB,
                validated_by VARCHAR(255),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_source_validations_source ON source_validations(source_id);
            CREATE INDEX IF NOT EXISTS idx_source_validations_status ON source_validations(validation_status);
        """)
        print("   ✓ Complete\n")
        
        # Table 4: source_feedback
        print("4. Creating source_feedback table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_feedback (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
                feedback_type VARCHAR(50) CHECK (feedback_type IN (
                    'bug', 'feature_request', 'improvement', 'question', 'compliment'
                )),
                feedback_text TEXT NOT NULL,
                priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMPTZ
            );
            
            CREATE INDEX IF NOT EXISTS idx_source_feedback_source ON source_feedback(source_id);
            CREATE INDEX IF NOT EXISTS idx_source_feedback_customer ON source_feedback(customer_id);
            CREATE INDEX IF NOT EXISTS idx_source_feedback_status ON source_feedback(status);
        """)
        print("   ✓ Complete\n")
        
        # Table 5: learning_paths
        print("5. Creating learning_paths table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                category_id UUID REFERENCES categories(id),
                difficulty_level VARCHAR(20) CHECK (difficulty_level IN (
                    'beginner', 'intermediate', 'advanced', 'expert'
                )),
                estimated_hours INTEGER,
                source_sequence UUID[] DEFAULT '{}',
                prerequisites UUID[] DEFAULT '{}',
                is_published BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_learning_paths_category ON learning_paths(category_id);
            CREATE INDEX IF NOT EXISTS idx_learning_paths_difficulty ON learning_paths(difficulty_level);
            CREATE INDEX IF NOT EXISTS idx_learning_paths_published ON learning_paths(is_published);
        """)
        print("   ✓ Complete\n")
        
        # Table 6: source_versions
        print("6. Creating source_versions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_versions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                version_number INTEGER NOT NULL,
                change_summary TEXT,
                changed_by VARCHAR(255),
                source_snapshot JSONB,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (source_id, version_number)
            );
            
            CREATE INDEX IF NOT EXISTS idx_source_versions_source ON source_versions(source_id);
            CREATE INDEX IF NOT EXISTS idx_source_versions_created ON source_versions(created_at);
        """)
        print("   ✓ Complete\n")
        
        # Table 7: quality_history
        print("7. Creating quality_history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                quality_score DECIMAL(5,2) NOT NULL,
                authority_score INTEGER,
                validation_count INTEGER,
                feedback_count INTEGER,
                usage_count INTEGER,
                measured_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_quality_history_source ON quality_history(source_id);
            CREATE INDEX IF NOT EXISTS idx_quality_history_measured ON quality_history(measured_at);
            CREATE INDEX IF NOT EXISTS idx_quality_history_score ON quality_history(quality_score);
        """)
        print("   ✓ Complete\n")
        
        conn.commit()
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [r[0] for r in cursor.fetchall()]
        
        print("="*70)
        print("SUCCESS: Priority 3 tables created")
        print("="*70)
        print(f"\nAll tables ({len(tables)}):")
        for t in tables:
            print(f"  • {t}")
        print("\nRun tests to validate:")
        print("  python3 scripts/database/test_schema_v2.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
```

## Expected Test Improvements

**Before (Week 2):** 6/28 passing

**After (Week 3):** 15-20/28 passing

**New passing tests expected:**
- test_01_all_tables_exist ✅ (all 15 tables present)
- test_09_learning_paths_curriculum ✅
- test_10_source_versions_history ✅
- test_11_quality_history_time_series ✅
- test_13_source_validations_tracking ✅
- test_14_source_feedback_customer_issues ✅
- test_15_environment_promotion_workflow ✅
- test_16_pending_approvals_view ✅
- test_17_customer_connectors_oauth ✅

Plus potentially more depending on view/constraint tests.

## Still Missing (Week 4 - Priority 4)

**Database Views:** (test errors, not table failures)
- knowledge_graph_summary_view
- customer_stats_view
- active_sources_view
- production_sources_view
- vertical_completeness_view
- curriculum_ready_sources_view

**Advanced Features:**
- Row Level Security (RLS) policies
- Additional indexes (idx_sources_quality_score)
- Materialized views for performance

## Verification Commands

```bash
# Check table count (should be 16 total)
psql "host=fredesa-db-dev.postgres.database.azure.com..." \
  -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"

# List all tables
psql "..." \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name;"

# Check indexes count
psql "..." \
  -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public';"
```

## Next Session Protocol

1. **Health Check FIRST:**
   ```bash
   python3 scripts/utilities/check_retrospection_health.py
   ```

2. **Declare Intent:**
   "Session started - Retrospection health: [status]. Today's goal: Create Priority 3 supporting tables"

3. **Execute:**
   - Create scripts/database/create_priority_3_tables.py
   - Run script
   - Validate with test_schema_v2.py
   - Target: 15-20/28 passing tests
   - Commit changes
   - Log retrospection lesson if issues encountered

4. **Session End:**
   - Verify health check still ✅ HEALTHY
   - Create handoff for Priority 4 (Week 4 - Views & RLS)

---
**Handoff Created:** 2025-12-29 08:45 PST
**Current Test Status:** 6/28 passing (expected)
**Retrospection Health:** ✅ HEALTHY (38 lessons, 8 categories)
**Git Status:** All changes committed and pushed to origin/main
**Tables Created:** 9/16 (56% complete)
