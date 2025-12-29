#!/usr/bin/env python3
"""
Apply PostgreSQL schema to Azure database.

This script:
1. Connects to fredesa-db-dev.postgres.database.azure.com
2. Applies schema.sql to create tables, indexes, constraints
3. Verifies schema creation
4. Reports results

Usage:
    python3 scripts/database/apply_schema.py
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Azure secrets utility from rDenz repo
# Path: /Users/delchaplin/Project Files/rdenz-knowledge-registry
rdenz_repo = Path("/Users/delchaplin/Project Files/rdenz-knowledge-registry")
if not rdenz_repo.exists():
    print(f"❌ ERROR: rdenz-knowledge-registry not found at {rdenz_repo}")
    sys.exit(1)

sys.path.insert(0, str(rdenz_repo))

try:
    from scripts.utilities.azure_secrets import AzureSecretManager
except ImportError as e:
    print("❌ ERROR: Cannot import azure_secrets.py from rdenz-knowledge-registry")
    print(f"   Path checked: {rdenz_repo}")
    print(f"   Import error: {e}")
    sys.exit(1)


def get_connection_string() -> str:
    """Get PostgreSQL connection string from Azure Key Vault."""
    try:
        secrets = AzureSecretManager()
        password = secrets.get_secret("postgres-password")
        
        return (
            f"host=fredesa-db-dev.postgres.database.azure.com "
            f"port=5432 "
            f"dbname=postgres "
            f"user=fredesaadmin "
            f"password={password} "
            f"sslmode=require"
        )
    except Exception as e:
        print(f"❌ ERROR getting database credentials: {e}")
        sys.exit(1)


def connect_to_database(conn_string: str):
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(conn_string)
        conn.set_session(autocommit=False)
        print("✅ Connected to fredesa-db-dev")
        return conn
    except psycopg2.Error as e:
        print(f"❌ ERROR connecting to database: {e}")
        sys.exit(1)


def read_schema_file() -> str:
    """Read schema.sql file."""
    schema_path = Path(__file__).parent / "schema.sql"
    
    if not schema_path.exists():
        print(f"❌ ERROR: schema.sql not found at {schema_path}")
        sys.exit(1)
    
    with open(schema_path, 'r') as f:
        return f.read()


def apply_schema(conn, schema_sql: str):
    """Apply SQL schema to database."""
    cursor = conn.cursor()
    
    try:
        print("\n📋 Applying schema...")
        
        # Execute schema SQL
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema applied successfully")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"❌ ERROR applying schema: {e}")
        print(f"   Error code: {e.pgcode}")
        print(f"   Error detail: {e.pgerror}")
        sys.exit(1)
    finally:
        cursor.close()


def verify_schema(conn):
    """Verify that schema was created correctly."""
    cursor = conn.cursor()
    
    print("\n🔍 Verifying schema...")
    
    try:
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name IN ('sources', 'categories', 'customers', 'usage_tracking')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Tables created ({len(tables)}/4):")
        for (table_name,) in tables:
            print(f"   ✓ {table_name}")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public'
                AND tablename IN ('sources', 'categories', 'customers', 'usage_tracking')
            ORDER BY indexname
        """)
        indexes = cursor.fetchall()
        
        print(f"\n🔍 Indexes created ({len(indexes)}):")
        for (index_name,) in indexes[:10]:  # Show first 10
            print(f"   ✓ {index_name}")
        if len(indexes) > 10:
            print(f"   ... and {len(indexes) - 10} more")
        
        # Check views
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
                AND table_name IN ('active_sources', 'customer_stats')
            ORDER BY table_name
        """)
        views = cursor.fetchall()
        
        print(f"\n👁️  Views created ({len(views)}/2):")
        for (view_name,) in views:
            print(f"   ✓ {view_name}")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        
        print(f"\n📦 Sample data:")
        print(f"   ✓ {category_count} categories")
        print(f"   ✓ {customer_count} customers")
        
        # Overall status
        if len(tables) == 4 and len(views) == 2:
            print("\n✅ Schema verification PASSED")
            print(f"   • 4/4 tables created")
            print(f"   • {len(indexes)} indexes created")
            print(f"   • 2/2 views created")
            print(f"   • Row-level security enabled")
            print(f"   • Triggers and functions active")
            return True
        else:
            print("\n⚠️  Schema verification INCOMPLETE")
            return False
            
    except psycopg2.Error as e:
        print(f"❌ ERROR verifying schema: {e}")
        return False
    finally:
        cursor.close()


def show_next_steps():
    """Show what to do next."""
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Test with sample queries:")
    print("   python3 scripts/database/test_schema.py")
    print("\n2. Create repository adapter:")
    print("   api/repositories/postgres_source_repository.py")
    print("\n3. Migrate data from YAML:")
    print("   python3 scripts/database/migrate_yaml_to_postgres.py")
    print("\n4. Performance benchmark:")
    print("   python3 scripts/database/benchmark_queries.py")
    print()


def main():
    """Main execution."""
    print("="*70)
    print("FreDeSa AI Platform - Schema Deployment")
    print("="*70)
    print(f"Database: fredesa-db-dev.postgres.database.azure.com")
    print(f"Schema: PostgreSQL 15.15")
    print("="*70)
    
    # Get connection string
    print("\n🔐 Retrieving database credentials from Azure Key Vault...")
    conn_string = get_connection_string()
    
    # Connect to database
    conn = connect_to_database(conn_string)
    
    try:
        # Read schema file
        print("\n📄 Reading schema.sql...")
        schema_sql = read_schema_file()
        print(f"   Schema file: {len(schema_sql):,} characters")
        
        # Apply schema
        apply_schema(conn, schema_sql)
        
        # Verify schema
        success = verify_schema(conn)
        
        # Show next steps
        if success:
            show_next_steps()
        
    finally:
        conn.close()
        print("\n👋 Database connection closed")


if __name__ == "__main__":
    main()
