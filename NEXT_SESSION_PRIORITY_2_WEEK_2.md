# Priority 2: Knowledge Graph Tables (Week 2)

## ✅ Completed (Week 1)
- Schema v2.1 core (categories, sources tables)
- Priority 1 triggers (auto_calculate_authority_score, maintain_category_stats)
- Test baseline: **4/28 passing** (expected, 24 failures for missing P2/P3/P4 features)

## 🎯 This Week's Goal
Add 5 knowledge graph tables to improve test coverage from 4/28 to **10-15/28**

## Priority 2 Tables (Create This Week)

### Table 1: `concepts`
**Purpose:** Store key concepts extracted from sources

```sql
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    definition TEXT,
    category_id UUID REFERENCES categories(id),
    source_ids UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_concepts_name ON concepts(name);
CREATE INDEX idx_concepts_category ON concepts(category_id);
```

**Tests affected:**
- test_01_all_tables_exist (current: fails for missing 'concepts')
- test_24_indexes_exist (current: fails for missing 'idx_concepts_name')

### Table 2: `relationships`
**Purpose:** Map connections between concepts

```sql
CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    to_concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
        'prerequisite', 'related', 'contradicts', 'extends', 'implements'
    )),
    strength DECIMAL(3,2) CHECK (strength >= 0.0 AND strength <= 1.0),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (from_concept_id, to_concept_id, relationship_type)
);

CREATE INDEX idx_relationships_from ON relationships(from_concept_id);
CREATE INDEX idx_relationships_to ON relationships(to_concept_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
```

**Tests affected:**
- test_01_all_tables_exist (current: fails for missing 'relationships')
- test_24_indexes_exist (current: fails for missing 'idx_relationships_type')

### Table 3: `use_cases`
**Purpose:** Document practical applications

```sql
CREATE TABLE use_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    concepts UUID[] DEFAULT '{}',
    source_ids UUID[] DEFAULT '{}',
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN (
        'beginner', 'intermediate', 'advanced', 'expert'
    )),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_use_cases_category ON use_cases(category_id);
CREATE INDEX idx_use_cases_difficulty ON use_cases(difficulty_level);
```

**Tests affected:**
- test_01_all_tables_exist (current: fails for missing 'use_cases')
- test_24_indexes_exist (current: fails for missing 'idx_use_cases_category')

### Table 4: `customer_connectors`
**Purpose:** Track customer-specific data integrations

```sql
CREATE TABLE customer_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_type VARCHAR(100) NOT NULL CHECK (connector_type IN (
        'sharepoint', 'onedrive', 's3', 'azure_blob', 'google_drive', 'custom'
    )),
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (customer_id, connector_type)
);

CREATE INDEX idx_customer_connectors_customer ON customer_connectors(customer_id);
CREATE INDEX idx_customer_connectors_active ON customer_connectors(is_active);
```

**Tests affected:**
- test_01_all_tables_exist (current: fails for missing 'customer_connectors')

### Table 5: `citations`
**Purpose:** Track source citation relationships

```sql
CREATE TABLE citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citing_source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    cited_source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    context TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (citing_source_id, cited_source_id)
);

CREATE INDEX idx_citations_citing ON citations(citing_source_id);
CREATE INDEX idx_citations_cited ON citations(cited_source_id);

-- Trigger to maintain citation counts
CREATE OR REPLACE FUNCTION maintain_citation_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE sources SET citation_count = citation_count + 1 
        WHERE id = NEW.cited_source_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE sources SET citation_count = citation_count - 1 
        WHERE id = OLD.cited_source_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maintain_citation_counts_trigger
    AFTER INSERT OR DELETE ON citations
    FOR EACH ROW
    EXECUTE FUNCTION maintain_citation_counts();
```

**Tests affected:**
- test_01_all_tables_exist (current: fails for missing 'citations')
- test_26_triggers_exist (current: fails for missing 'maintain_citation_counts_trigger')

## Implementation Script Template

Create `scripts/database/create_priority_2_tables.py`:

```python
#!/usr/bin/env python3
"""
Create Priority 2 tables (Knowledge Graph)
Week 2 of schema v2.1 implementation
"""

import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main():
    print("\n" + "="*70)
    print("Creating Priority 2 Tables (Knowledge Graph)")
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
        
        # Table 1: concepts
        print("1. Creating concepts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concepts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL UNIQUE,
                definition TEXT,
                category_id UUID REFERENCES categories(id),
                source_ids UUID[] DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(name);
            CREATE INDEX IF NOT EXISTS idx_concepts_category ON concepts(category_id);
        """)
        print("   ✓ Complete\n")
        
        # Table 2: relationships
        print("2. Creating relationships table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                from_concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
                to_concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
                relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
                    'prerequisite', 'related', 'contradicts', 'extends', 'implements'
                )),
                strength DECIMAL(3,2) CHECK (strength >= 0.0 AND strength <= 1.0),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (from_concept_id, to_concept_id, relationship_type)
            );
            
            CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_concept_id);
            CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_concept_id);
            CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
        """)
        print("   ✓ Complete\n")
        
        # Table 3: use_cases
        print("3. Creating use_cases table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS use_cases (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                category_id UUID REFERENCES categories(id),
                concepts UUID[] DEFAULT '{}',
                source_ids UUID[] DEFAULT '{}',
                difficulty_level VARCHAR(20) CHECK (difficulty_level IN (
                    'beginner', 'intermediate', 'advanced', 'expert'
                )),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_use_cases_category ON use_cases(category_id);
            CREATE INDEX IF NOT EXISTS idx_use_cases_difficulty ON use_cases(difficulty_level);
        """)
        print("   ✓ Complete\n")
        
        # Table 4: customer_connectors
        print("4. Creating customer_connectors table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_connectors (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                connector_type VARCHAR(100) NOT NULL CHECK (connector_type IN (
                    'sharepoint', 'onedrive', 's3', 'azure_blob', 'google_drive', 'custom'
                )),
                config JSONB NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_sync TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (customer_id, connector_type)
            );
            
            CREATE INDEX IF NOT EXISTS idx_customer_connectors_customer ON customer_connectors(customer_id);
            CREATE INDEX IF NOT EXISTS idx_customer_connectors_active ON customer_connectors(is_active);
        """)
        print("   ✓ Complete\n")
        
        # Table 5: citations
        print("5. Creating citations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                citing_source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                cited_source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                context TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (citing_source_id, cited_source_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_citations_citing ON citations(citing_source_id);
            CREATE INDEX IF NOT EXISTS idx_citations_cited ON citations(cited_source_id);
        """)
        print("   ✓ Complete\n")
        
        # Citation counts trigger
        print("6. Creating citation counts trigger...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION maintain_citation_counts()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE sources SET citation_count = citation_count + 1 
                    WHERE id = NEW.cited_source_id;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE sources SET citation_count = citation_count - 1 
                    WHERE id = OLD.cited_source_id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            
            DROP TRIGGER IF EXISTS maintain_citation_counts_trigger ON citations;
            CREATE TRIGGER maintain_citation_counts_trigger
                AFTER INSERT OR DELETE ON citations
                FOR EACH ROW
                EXECUTE FUNCTION maintain_citation_counts();
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
        print("SUCCESS: Priority 2 tables created")
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

**Before (Week 1):** 4/28 passing
- test_02_epistemological_dimension_constraint ✅
- test_03_authority_score_auto_calculation ✅
- test_04_category_epistemological_statistics ✅
- test_27_difficulty_level_constraint ✅

**After (Week 2):** 10-15/28 passing
- All Week 1 tests ✅
- test_01_all_tables_exist ✅ (concepts, relationships, use_cases, customer_connectors, citations added)
- test_24_indexes_exist ✅ (idx_concepts_name, idx_relationships_type, idx_use_cases_category added)
- test_26_triggers_exist ✅ (maintain_citation_counts_trigger added)
- Possibly more depending on constraint tests

## Verification Commands

```bash
# Check table count
psql "host=fredesa-db-dev.postgres.database.azure.com..." \
  -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"

# Expected: 9 tables (categories, sources, customers, usage_tracking, concepts, relationships, use_cases, customer_connectors, citations)

# Check indexes
psql "..." \
  -c "SELECT tablename, indexname FROM pg_indexes WHERE schemaname='public' ORDER BY tablename, indexname;"

# Check triggers
psql "..." \
  -c "SELECT trigger_name, event_object_table FROM information_schema.triggers WHERE trigger_schema='public';"
```

## Next Session Protocol

1. **Health Check FIRST:**
   ```bash
   python3 scripts/utilities/check_retrospection_health.py
   ```

2. **Declare Intent:**
   "Session started - Retrospection health: [status]. Today's goal: Create Priority 2 knowledge graph tables"

3. **Load Context:**
   - Read this handoff document
   - Review current test output (4/28 passing baseline)

4. **Execute:**
   - Create scripts/database/create_priority_2_tables.py
   - Run script
   - Validate with test_schema_v2.py
   - Commit changes
   - Log retrospection lesson if issues encountered

5. **Session End:**
   - Verify health check still ✅ HEALTHY
   - Create handoff for Priority 3 (Week 3)

## Week 3 Preview (Priority 3)
- metadata table
- search_history table  
- recommendations table
- query_cache table
- Last 4 supporting tables for full v2.1 schema

---
**Handoff Created:** 2025-12-29 08:25 PST
**Current Test Status:** 4/28 passing (expected)
**Retrospection Health:** ✅ HEALTHY (37 lessons, 8 categories)
**Git Status:** All changes committed and pushed to origin/main
