#!/usr/bin/env python3
"""
Drop old category and subcategory VARCHAR columns after v2.1 migration.
Run this AFTER migrate_v1_to_v2_complete.py has successfully executed.
"""

import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main():
    print("\n" + "="*70)
    print("Dropping old category/subcategory columns")
    print("="*70 + "\n")
    
    # Get database password from Azure Key Vault
    credential = DefaultAzureCredential()
    vault_url = "https://fredesa-kv-e997e3.vault.azure.net/"
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    password = secret_client.get_secret('postgres-password').value
    
    # Connect to database
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
        
        # Check if columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sources' 
            AND column_name IN ('category', 'subcategory')
        """)
        existing_cols = [row[0] for row in cursor.fetchall()]
        
        if not existing_cols:
            print("✓ Old columns already dropped - nothing to do\n")
            print("="*70)
            print("SUCCESS: Schema is clean")
            print("="*70)
            return
        
        print(f"Found old columns to drop: {', '.join(existing_cols)}\n")
        
        # Drop the columns
        if 'category' in existing_cols:
            print("Dropping 'category' column...")
            cursor.execute("ALTER TABLE sources DROP COLUMN category")
            print("  ✓ Complete\n")
        
        if 'subcategory' in existing_cols:
            print("Dropping 'subcategory' column...")
            cursor.execute("ALTER TABLE sources DROP COLUMN subcategory")
            print("  ✓ Complete\n")
        
        conn.commit()
        
        # Verify
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sources' 
            AND column_name IN ('category', 'subcategory')
        """)
        remaining = cursor.fetchall()
        
        if not remaining:
            print("="*70)
            print("SUCCESS: Old category columns dropped")
            print("="*70)
        else:
            print(f"⚠️  WARNING: Columns still exist: {remaining}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
