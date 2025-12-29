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
        
        # Table 1: source_concepts
        print("1. Creating source_concepts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_concepts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL UNIQUE,
                definition TEXT,
                category_id UUID REFERENCES categories(id),
                source_ids UUID[] DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_source_concepts_name ON source_concepts(name);
            CREATE INDEX IF NOT EXISTS idx_source_concepts_category ON source_concepts(category_id);
        """)
        print("   ✓ Complete\n")
        
        # Table 2: source_relationships
        print("2. Creating source_relationships table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_relationships (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                from_concept_id UUID NOT NULL REFERENCES source_concepts(id) ON DELETE CASCADE,
                to_concept_id UUID NOT NULL REFERENCES source_concepts(id) ON DELETE CASCADE,
                relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
                    'prerequisite', 'related', 'contradicts', 'extends', 'implements'
                )),
                strength DECIMAL(3,2) CHECK (strength >= 0.0 AND strength <= 1.0),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (from_concept_id, to_concept_id, relationship_type)
            );
            
            CREATE INDEX IF NOT EXISTS idx_source_relationships_from ON source_relationships(from_concept_id);
            CREATE INDEX IF NOT EXISTS idx_source_relationships_to ON source_relationships(to_concept_id);
            CREATE INDEX IF NOT EXISTS idx_source_relationships_type ON source_relationships(relationship_type);
        """)
        print("   ✓ Complete\n")
        
        # Table 3: source_use_cases
        print("3. Creating source_use_cases table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_use_cases (
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
            
            CREATE INDEX IF NOT EXISTS idx_source_use_cases_category ON source_use_cases(category_id);
            CREATE INDEX IF NOT EXISTS idx_source_use_cases_difficulty ON source_use_cases(difficulty_level);
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
