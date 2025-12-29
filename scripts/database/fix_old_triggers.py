#!/usr/bin/env python3
"""
Fix/drop old triggers that reference dropped columns
"""

import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main():
    print("\n" + "="*70)
    print("Fixing old triggers")
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
        
        # Drop old trigger function
        print("Dropping old trigger function update_category_source_count...")
        cursor.execute("DROP FUNCTION IF EXISTS update_category_source_count() CASCADE")
        print("  ✓ Complete\n")
        
        conn.commit()
        
        print("="*70)
        print("SUCCESS: Old triggers cleaned up")
        print("="*70)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
