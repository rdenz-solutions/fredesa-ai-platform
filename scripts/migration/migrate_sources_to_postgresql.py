#!/usr/bin/env python3
"""
Migrate sources from rdenz-knowledge-registry to FreDeSa PostgreSQL
Maps sources.yaml structure to schema v2.1 epistemological framework
"""

import sys
import yaml
import psycopg2
import psycopg2.extras
import json
from pathlib import Path
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Configuration
KR_PATH = Path("/Users/delchaplin/Project Files/rdenz-knowledge-registry")
SOURCES_FILE = KR_PATH / "config" / "sources.yaml"
BATCH_SIZE = 50

# Epistemological dimension mapping
DIMENSION_MAPPING = {
    'Standards': 'theory',              # Standards define theoretical frameworks
    'Federal_Contracting': 'practice',  # FAR/DFARS are practice-oriented
    'Cybersecurity': 'current',         # Security threats are current concerns
    'Intelligence': 'current',          # Intelligence is current/operational
    'Cloud_Platforms': 'practice',      # Cloud platforms are applied technology
    'LLM_Frameworks': 'practice',       # Frameworks are applied tools
    'Methodologies': 'theory',          # Methodologies are theoretical approaches
    'Programming_Languages': 'practice',# Languages are practical tools
    'AI/LLM_Platforms': 'practice',     # Platforms are practical implementations
    'Data_Engineering': 'practice',     # Engineering is applied practice
}

# Authority type mapping based on source characteristics
def determine_authority_type(source: dict) -> str:
    """Determine if source is official, expert, or community"""
    name = source.get('name', '').lower()
    tags = source.get('metadata_tags', []) + source.get('tags', [])
    
    # Official sources
    official_keywords = ['dod', 'nist', 'iso', 'far', 'dfars', 'fedramp', 'government', 'federal']
    if any(kw in name or kw in str(tags).lower() for kw in official_keywords):
        return 'official'
    
    # Expert sources
    expert_keywords = ['documentation', 'reference', 'specification', 'standard']
    source_type = source.get('type', '')
    if source_type == 'documentation' or any(kw in name for kw in expert_keywords):
        return 'expert'
    
    # Default to community
    return 'community'

# Difficulty mapping
def determine_difficulty(source: dict) -> str:
    """Determine difficulty level based on audience and content"""
    scope = source.get('scope', {})
    audience = scope.get('audience', [])
    
    if 'beginners' in str(audience).lower() or 'getting-started' in source.get('name', '').lower():
        return 'beginner'
    elif 'advanced' in str(audience).lower() or 'expert' in str(audience).lower():
        return 'advanced'
    elif 'technical professionals' in str(audience).lower():
        return 'intermediate'
    else:
        return 'intermediate'  # Default

def get_db_connection():
    """Connect to PostgreSQL using Azure Key Vault credentials"""
    print("🔐 Retrieving database credentials from Azure Key Vault...")
    credential = DefaultAzureCredential()
    vault_url = "https://fredesa-kv-e997e3.vault.azure.net/"
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    password = secret_client.get_secret('postgres-password').value
    
    print("📡 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host='fredesa-db-dev.postgres.database.azure.com',
        port=5432,
        database='postgres',
        user='fredesaadmin',
        password=password,
        sslmode='require'
    )
    return conn

def ensure_categories_exist(cursor, sources: list):
    """Ensure all categories from sources.yaml exist in categories table"""
    print("\n📊 Creating categories...")
    
    # Get unique categories
    categories = set(s.get('category', 'Uncategorized') for s in sources)
    
    for category in sorted(categories):
        # Check if exists
        cursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
        if cursor.fetchone():
            print(f"   ⏭️  {category} (already exists)")
            continue
        
        # Create category
        display_name = category.replace('_', ' ')
        description = f"Knowledge sources related to {display_name.lower()}"
        
        cursor.execute("""
            INSERT INTO categories (name, display_name, description, sort_order)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, (category, display_name, description, 0))
        
        print(f"   ✅ {category}")

def migrate_source(cursor, source: dict, category_map: dict) -> bool:
    """Migrate a single source to PostgreSQL"""
    try:
        # Get category ID
        category_name = source.get('category', 'Uncategorized')
        category_id = category_map.get(category_name)
        
        if not category_id:
            print(f"   ⚠️  {source['id']}: Category '{category_name}' not found")
            return False
        
        # Determine epistemological dimension
        dimension = DIMENSION_MAPPING.get(category_name, 'current')
        
        # Determine authority type
        authority_type = determine_authority_type(source)
        
        # Determine difficulty
        difficulty = determine_difficulty(source)
        
        # Get ingestion data
        ingestion = source.get('ingestion', {})
        words = ingestion.get('words', 0)
        
        # Get primary URL
        urls = source.get('canonical_urls', [])
        url = urls[0] if urls else 'https://example.com/unknown'
        
        # Quality score estimation (based on trust_score if available)
        metadata = source.get('metadata', {})
        quality_score = metadata.get('trust_score', 50.0)
        
        # Determine active status
        is_active = source.get('status', 'active') == 'active'
        
        # Check if URL already exists
        cursor.execute("SELECT id FROM sources WHERE url = %s", (url,))
        if cursor.fetchone():
            return None  # Already exists
        
        # Insert source
        cursor.execute("""
            INSERT INTO sources (
                name, url, source_type, category_id,
                epistemological_dimension, difficulty_level,
                description, metadata, quality_score,
                is_active, environment_flags,
                word_count, file_count
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s
            )
            RETURNING id
        """, (
            source['name'],
            url,
            authority_type,  # Maps to source_type (official/expert/community)
            category_id,
            dimension,
            difficulty,
            source.get('description', ''),
            psycopg2.extras.Json({
                'original_id': source['id'],
                'tags': source.get('metadata_tags', []),
                'ingestion_status': ingestion.get('status'),
                'last_update': ingestion.get('last_update')
            }),
            quality_score,
            is_active,
            psycopg2.extras.Json({
                'dev': True,
                'staging': False,
                'production': False
            }),
            words,
            ingestion.get('files_count', 0)
        ))
        
        result = cursor.fetchone()
        return True if result else False
            
    except Exception as e:
        print(f"   ❌ {source.get('id', 'unknown')}: {str(e)[:100]}")
        # Rollback this individual transaction
        cursor.connection.rollback()
        return False

def migrate_sources(limit: int = None):
    """Main migration function"""
    print("="*70)
    print("📦 FreDeSa Knowledge Migration")
    print("="*70)
    print(f"Source: {SOURCES_FILE}")
    print(f"Target: fredesa-db-dev.postgres.database.azure.com")
    
    # Load sources
    print(f"\n📖 Loading sources from {SOURCES_FILE.name}...")
    with open(SOURCES_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    sources = data.get('sources', [])
    if limit:
        sources = sources[:limit]
    
    print(f"   Found {len(sources)} sources to migrate")
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Ensure categories exist
        ensure_categories_exist(cursor, sources)
        conn.commit()
        
        # Build category map
        cursor.execute("SELECT name, id FROM categories")
        category_map = dict(cursor.fetchall())
        
        # Migrate sources
        print(f"\n🚀 Migrating sources...")
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for i, source in enumerate(sources, 1):
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(sources)}")
            
            result = migrate_source(cursor, source, category_map)
            if result:
                success_count += 1
                conn.commit()  # Commit each success immediately
            elif result is None:
                skip_count += 1
            else:
                error_count += 1
        
        # Final commit
        conn.commit()
        
        # Print summary
        print("\n" + "="*70)
        print("📊 MIGRATION SUMMARY")
        print("="*70)
        print(f"✅ Successfully migrated: {success_count}")
        print(f"⏭️  Skipped (already exist): {skip_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📈 Total processed: {len(sources)}")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM sources")
        total_sources = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = cursor.fetchone()[0]
        
        print(f"\n📦 Database State:")
        print(f"   Categories: {total_categories}")
        print(f"   Sources: {total_sources}")
        
        # Show epistemological breakdown
        cursor.execute("""
            SELECT epistemological_dimension, COUNT(*)
            FROM sources
            GROUP BY epistemological_dimension
            ORDER BY COUNT(*) DESC
        """)
        print(f"\n📐 Epistemological Dimensions:")
        for dim, count in cursor.fetchall():
            print(f"   {dim}: {count}")
        
        # Show authority breakdown
        cursor.execute("""
            SELECT source_type, COUNT(*)
            FROM sources
            GROUP BY source_type
            ORDER BY COUNT(*) DESC
        """)
        print(f"\n🏆 Authority Types:")
        for auth_type, count in cursor.fetchall():
            cursor.execute("SELECT authority_score FROM sources WHERE source_type = %s LIMIT 1", (auth_type,))
            score = cursor.fetchone()[0]
            print(f"   {auth_type}: {count} (score={score})")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed")

if __name__ == '__main__':
    # Parse command line arguments
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            print(f"⚠️  LIMIT MODE: Migrating only first {limit} sources\n")
        except ValueError:
            print("Usage: python3 migrate_sources_to_postgresql.py [limit]")
            sys.exit(1)
    
    migrate_sources(limit=limit)
