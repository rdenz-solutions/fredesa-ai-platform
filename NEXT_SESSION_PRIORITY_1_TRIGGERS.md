# Next Session: Priority 1 Triggers
**Status**: Schema v2.1 migration complete, ready for trigger creation  
**Goal**: Create missing triggers to get 4-6 tests passing

## Quick Start

```bash
cd "/Users/delchaplin/Project Files/fredesa-ai-platform"
python3 scripts/database/create_priority_1_triggers.py
python3 scripts/database/test_schema_v2.py
```

## What You Need to Create

### Trigger 1: Auto-Calculate Authority Score

**Purpose**: Automatically set authority_score based on source_type when inserting/updating sources

**SQL** (ready to execute):
```sql
CREATE OR REPLACE FUNCTION auto_calculate_authority_score()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.source_type = 'official' THEN
        NEW.authority_score := 90;
    ELSIF NEW.source_type = 'expert' THEN
        NEW.authority_score := 70;
    ELSIF NEW.source_type = 'community' THEN
        NEW.authority_score := 50;
    ELSE
        NEW.authority_score := 50;  -- Default
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_authority_score
    BEFORE INSERT OR UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION auto_calculate_authority_score();
```

**Test it validates**: `test_03_authority_score_auto_calculation`

### Trigger 2: Maintain Category Statistics

**Purpose**: Keep theory_sources, practice_sources, and total_sources counts accurate in categories table

**SQL** (ready to execute):
```sql
CREATE OR REPLACE FUNCTION maintain_category_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- Update theory/practice/total counts for affected category
        UPDATE categories
        SET 
            theory_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = NEW.category_id 
                AND epistemological_dimension = 'theory'
                AND is_active = TRUE),
            practice_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = NEW.category_id 
                AND epistemological_dimension = 'practice'
                AND is_active = TRUE),
            history_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = NEW.category_id 
                AND epistemological_dimension = 'history'
                AND is_active = TRUE),
            current_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = NEW.category_id 
                AND epistemological_dimension = 'current'
                AND is_active = TRUE),
            future_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = NEW.category_id 
                AND epistemological_dimension = 'future'
                AND is_active = TRUE),
            total_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = NEW.category_id
                AND is_active = TRUE)
        WHERE id = NEW.category_id;
    ELSIF TG_OP = 'DELETE' THEN
        -- Update counts after deletion
        UPDATE categories
        SET 
            theory_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = OLD.category_id 
                AND epistemological_dimension = 'theory'
                AND is_active = TRUE),
            practice_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = OLD.category_id 
                AND epistemological_dimension = 'practice'
                AND is_active = TRUE),
            history_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = OLD.category_id 
                AND epistemological_dimension = 'history'
                AND is_active = TRUE),
            current_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = OLD.category_id 
                AND epistemological_dimension = 'current'
                AND is_active = TRUE),
            future_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = OLD.category_id 
                AND epistemological_dimension = 'future'
                AND is_active = TRUE),
            total_sources = (SELECT COUNT(*) FROM sources 
                WHERE category_id = OLD.category_id
                AND is_active = TRUE)
        WHERE id = OLD.category_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_category_stats
    AFTER INSERT OR UPDATE OR DELETE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION maintain_category_stats();
```

**Test it validates**: `test_04_category_epistemological_statistics`

## Implementation Script Template

Create `scripts/database/create_priority_1_triggers.py`:

```python
#!/usr/bin/env python3
"""
Create Priority 1 triggers for schema v2.1
Adds auto-calculation and statistics maintenance
"""

import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main():
    print("\n" + "="*70)
    print("Creating Priority 1 Triggers")
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
        
        # Trigger 1: Auto-calculate authority score
        print("1. Creating auto_calculate_authority_score trigger...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION auto_calculate_authority_score()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.source_type = 'official' THEN
                    NEW.authority_score := 90;
                ELSIF NEW.source_type = 'expert' THEN
                    NEW.authority_score := 70;
                ELSIF NEW.source_type = 'community' THEN
                    NEW.authority_score := 50;
                ELSE
                    NEW.authority_score := 50;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS calculate_authority_score ON sources;
            CREATE TRIGGER calculate_authority_score
                BEFORE INSERT OR UPDATE ON sources
                FOR EACH ROW
                EXECUTE FUNCTION auto_calculate_authority_score();
        """)
        print("   ✓ Complete\n")
        
        # Trigger 2: Maintain category statistics
        print("2. Creating maintain_category_stats trigger...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION maintain_category_stats()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                    UPDATE categories
                    SET 
                        theory_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = NEW.category_id 
                            AND epistemological_dimension = 'theory'
                            AND is_active = TRUE),
                        practice_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = NEW.category_id 
                            AND epistemological_dimension = 'practice'
                            AND is_active = TRUE),
                        history_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = NEW.category_id 
                            AND epistemological_dimension = 'history'
                            AND is_active = TRUE),
                        current_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = NEW.category_id 
                            AND epistemological_dimension = 'current'
                            AND is_active = TRUE),
                        future_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = NEW.category_id 
                            AND epistemological_dimension = 'future'
                            AND is_active = TRUE),
                        total_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = NEW.category_id
                            AND is_active = TRUE)
                    WHERE id = NEW.category_id;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE categories
                    SET 
                        theory_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = OLD.category_id 
                            AND epistemological_dimension = 'theory'
                            AND is_active = TRUE),
                        practice_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = OLD.category_id 
                            AND epistemological_dimension = 'practice'
                            AND is_active = TRUE),
                        history_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = OLD.category_id 
                            AND epistemological_dimension = 'history'
                            AND is_active = TRUE),
                        current_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = OLD.category_id 
                            AND epistemological_dimension = 'current'
                            AND is_active = TRUE),
                        future_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = OLD.category_id 
                            AND epistemological_dimension = 'future'
                            AND is_active = TRUE),
                        total_sources = (SELECT COUNT(*) FROM sources 
                            WHERE category_id = OLD.category_id
                            AND is_active = TRUE)
                    WHERE id = OLD.category_id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_category_stats ON sources;
            CREATE TRIGGER update_category_stats
                AFTER INSERT OR UPDATE OR DELETE ON sources
                FOR EACH ROW
                EXECUTE FUNCTION maintain_category_stats();
        """)
        print("   ✓ Complete\n")
        
        conn.commit()
        
        # Verify triggers exist
        cursor.execute("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE event_object_table = 'sources'
            ORDER BY trigger_name
        """)
        triggers = [r[0] for r in cursor.fetchall()]
        
        print("="*70)
        print("SUCCESS: Priority 1 triggers created")
        print("="*70)
        print(f"\nActive triggers on 'sources' table:")
        for t in triggers:
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

## Expected Results

After creating these triggers, re-run tests:
```bash
python3 scripts/database/test_schema_v2.py
```

**Expected improvement**:
- From: 2/28 tests passing
- To: 4-6/28 tests passing

**New passing tests**:
- `test_03_authority_score_auto_calculation` ✅
- `test_04_category_epistemological_statistics` ✅

## Verification Commands

**Check if triggers exist**:
```bash
python3 -c "
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import psycopg2

credential = DefaultAzureCredential()
secret_client = SecretClient(
    vault_url='https://fredesa-kv-e997e3.vault.azure.net/', 
    credential=credential
)
password = secret_client.get_secret('postgres-password').value

conn = psycopg2.connect(
    host='fredesa-db-dev.postgres.database.azure.com',
    port=5432,
    database='postgres',
    user='fredesaadmin',
    password=password,
    sslmode='require'
)
cursor = conn.cursor()
cursor.execute(\"\"\"
    SELECT trigger_name, event_manipulation 
    FROM information_schema.triggers 
    WHERE event_object_table = 'sources'
    ORDER BY trigger_name
\"\"\")
print('Triggers on sources table:')
for row in cursor.fetchall():
    print(f'  {row[0]:30} {row[1]}')
conn.close()
"
```

## After Completion

1. Commit to git: `git commit -m "✅ Added Priority 1 triggers (authority_score, category_stats)"`
2. Push: `git push origin main`
3. Update MIGRATION_SESSION_HANDOFF.md with progress
4. Move to Priority 2: Knowledge Graph Tables (Week 2)

---

**Current Status**: Schema v2.1 core complete, awaiting trigger creation  
**Next Action**: Create `scripts/database/create_priority_1_triggers.py` and execute
