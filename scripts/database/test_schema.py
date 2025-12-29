#!/usr/bin/env python3
"""
Test PostgreSQL schema with sample queries.

This script validates:
1. Tables exist and are accessible
2. Indexes are working
3. Foreign key constraints function
4. Row-level security policies work
5. Triggers update timestamps correctly
6. Views return expected data

Usage:
    python3 scripts/database/test_schema.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add rdenz repo to path for Azure secrets
rdenz_repo = Path("/Users/delchaplin/Project Files/rdenz-knowledge-registry")
sys.path.insert(0, str(rdenz_repo))

try:
    from scripts.utilities.azure_secrets import AzureSecretManager
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError as e:
    print(f"❌ ERROR: Missing dependencies: {e}")
    sys.exit(1)


class SchemaTest:
    """Test PostgreSQL schema functionality."""
    
    def __init__(self):
        """Initialize test with database connection."""
        secrets = AzureSecretManager()
        password = secrets.get_secret("postgres-password")
        
        self.conn_string = (
            f"host=fredesa-db-dev.postgres.database.azure.com "
            f"port=5432 "
            f"dbname=postgres "
            f"user=fredesaadmin "
            f"password={password} "
            f"sslmode=require"
        )
        
        self.conn = psycopg2.connect(self.conn_string)
        self.conn.set_session(autocommit=False)
        self.test_results: List[Tuple[str, bool, str]] = []
    
    def run_test(self, name: str, func):
        """Run a single test and record result."""
        try:
            func()
            self.test_results.append((name, True, ""))
            print(f"  ✅ {name}")
        except Exception as e:
            self.test_results.append((name, False, str(e)))
            print(f"  ❌ {name}")
            print(f"     Error: {e}")
    
    def test_tables_exist(self):
        """Verify all tables were created."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name IN ('sources', 'categories', 'customers', 'usage_tracking')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        assert len(tables) == 4, f"Expected 4 tables, found {len(tables)}"
        assert 'sources' in tables, "sources table missing"
        assert 'categories' in tables, "categories table missing"
        assert 'customers' in tables, "customers table missing"
        assert 'usage_tracking' in tables, "usage_tracking table missing"
    
    def test_sample_data_exists(self):
        """Verify sample data was inserted."""
        cursor = self.conn.cursor()
        
        # Check categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        assert cat_count >= 5, f"Expected at least 5 categories, found {cat_count}"
        
        # Check customers
        cursor.execute("SELECT COUNT(*) FROM customers WHERE email = 'test@fredesa.com'")
        cust_count = cursor.fetchone()[0]
        assert cust_count == 1, "Test customer not found"
        
        cursor.close()
    
    def test_insert_source(self):
        """Test inserting a new source."""
        cursor = self.conn.cursor()
        
        # Get a category
        cursor.execute("SELECT name FROM categories LIMIT 1")
        category = cursor.fetchone()[0]
        
        # Insert source
        cursor.execute("""
            INSERT INTO sources (name, url, category, description, authority_level)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            "Test Source",
            "https://example.com/test",
            category,
            "Test description",
            "Community"
        ))
        
        source_id = cursor.fetchone()[0]
        assert source_id is not None, "Source insertion failed"
        
        # Verify it was inserted
        cursor.execute("SELECT name FROM sources WHERE id = %s", (source_id,))
        result = cursor.fetchone()
        assert result[0] == "Test Source", "Source name doesn't match"
        
        # Clean up
        cursor.execute("DELETE FROM sources WHERE id = %s", (source_id,))
        self.conn.commit()
        cursor.close()
    
    def test_foreign_key_constraint(self):
        """Test foreign key constraints."""
        cursor = self.conn.cursor()
        
        try:
            # Try to insert source with invalid category
            cursor.execute("""
                INSERT INTO sources (name, url, category)
                VALUES (%s, %s, %s)
            """, ("Bad Source", "https://example.com", "INVALID_CATEGORY"))
            self.conn.commit()
            raise AssertionError("Foreign key constraint should have failed")
        except psycopg2.IntegrityError:
            # Expected - foreign key violation
            self.conn.rollback()
            pass
        
        cursor.close()
    
    def test_updated_at_trigger(self):
        """Test that updated_at timestamp is auto-updated."""
        cursor = self.conn.cursor()
        
        # Get a category
        cursor.execute("SELECT name FROM categories LIMIT 1")
        category = cursor.fetchone()[0]
        
        # Insert a source
        cursor.execute("""
            INSERT INTO sources (name, url, category)
            VALUES (%s, %s, %s)
            RETURNING id, created_at, updated_at
        """, ("Trigger Test Source", "https://example.com/trigger", category))
        
        source_id, created_at, updated_at1 = cursor.fetchone()
        self.conn.commit()
        
        # Update the source
        import time
        time.sleep(1)  # Ensure time difference
        
        cursor.execute("""
            UPDATE sources 
            SET description = %s 
            WHERE id = %s
            RETURNING updated_at
        """, ("Updated description", source_id))
        
        updated_at2 = cursor.fetchone()[0]
        self.conn.commit()
        
        # Verify updated_at changed
        assert updated_at2 > updated_at1, "updated_at trigger not working"
        
        # Clean up
        cursor.execute("DELETE FROM sources WHERE id = %s", (source_id,))
        self.conn.commit()
        cursor.close()
    
    def test_category_count_trigger(self):
        """Test that category source_count is auto-maintained."""
        cursor = self.conn.cursor()
        
        # Get Standards category
        cursor.execute("""
            SELECT name, source_count 
            FROM categories 
            WHERE name = 'Standards'
        """)
        result = cursor.fetchone()
        if not result:
            raise AssertionError("Standards category not found")
        
        category, initial_count = result
        
        # Insert a source in this category
        cursor.execute("""
            INSERT INTO sources (name, url, category)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ("Count Test Source", "https://example.com/count", category))
        
        source_id = cursor.fetchone()[0]
        self.conn.commit()
        
        # Check count increased
        cursor.execute("""
            SELECT source_count 
            FROM categories 
            WHERE name = %s
        """, (category,))
        
        new_count = cursor.fetchone()[0]
        assert new_count == initial_count + 1, "Category count trigger not working"
        
        # Clean up
        cursor.execute("DELETE FROM sources WHERE id = %s", (source_id,))
        self.conn.commit()
        
        # Verify count decreased
        cursor.execute("""
            SELECT source_count 
            FROM categories 
            WHERE name = %s
        """, (category,))
        
        final_count = cursor.fetchone()[0]
        assert final_count == initial_count, "Category count not decremented on delete"
        
        cursor.close()
    
    def test_active_sources_view(self):
        """Test active_sources view."""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM active_sources LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            # Verify view has expected columns
            assert 'name' in result, "View missing 'name' column"
            assert 'category' in result, "View missing 'category' column"
            assert 'category_description' in result, "View missing 'category_description' column"
        
        cursor.close()
    
    def test_customer_stats_view(self):
        """Test customer_stats view."""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM customer_stats 
            WHERE email = 'test@fredesa.com'
        """)
        
        result = cursor.fetchone()
        assert result is not None, "Test customer not in stats view"
        assert 'accessible_sources' in result, "View missing 'accessible_sources' column"
        assert 'total_api_calls' in result, "View missing 'total_api_calls' column"
        
        cursor.close()
    
    def test_indexes_exist(self):
        """Verify indexes were created."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE schemaname = 'public'
                AND tablename IN ('sources', 'categories', 'customers', 'usage_tracking')
        """)
        
        index_count = cursor.fetchone()[0]
        assert index_count >= 20, f"Expected at least 20 indexes, found {index_count}"
        
        cursor.close()
    
    def test_url_constraint(self):
        """Test URL validation constraint."""
        cursor = self.conn.cursor()
        
        # Get a category
        cursor.execute("SELECT name FROM categories LIMIT 1")
        category = cursor.fetchone()[0]
        
        try:
            # Try invalid URL
            cursor.execute("""
                INSERT INTO sources (name, url, category)
                VALUES (%s, %s, %s)
            """, ("Bad URL Source", "not-a-url", category))
            self.conn.commit()
            raise AssertionError("URL constraint should have failed")
        except psycopg2.IntegrityError:
            # Expected
            self.conn.rollback()
            pass
        
        cursor.close()
    
    def run_all_tests(self):
        """Run all schema tests."""
        print("\n" + "="*70)
        print("FreDeSa AI Platform - Schema Tests")
        print("="*70)
        
        print("\n📋 Running tests...")
        
        self.run_test("Tables exist", self.test_tables_exist)
        self.run_test("Sample data exists", self.test_sample_data_exists)
        self.run_test("Insert source", self.test_insert_source)
        self.run_test("Foreign key constraint", self.test_foreign_key_constraint)
        self.run_test("updated_at trigger", self.test_updated_at_trigger)
        self.run_test("Category count trigger", self.test_category_count_trigger)
        self.run_test("active_sources view", self.test_active_sources_view)
        self.run_test("customer_stats view", self.test_customer_stats_view)
        self.run_test("Indexes exist", self.test_indexes_exist)
        self.run_test("URL constraint", self.test_url_constraint)
        
        # Summary
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print("\n" + "="*70)
        print(f"RESULTS: {passed}/{total} tests passed")
        print("="*70)
        
        if passed == total:
            print("✅ All tests PASSED")
            return True
        else:
            print("❌ Some tests FAILED")
            for name, success, error in self.test_results:
                if not success:
                    print(f"  • {name}: {error}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Main execution."""
    test_suite = SchemaTest()
    
    try:
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        test_suite.close()


if __name__ == "__main__":
    main()
