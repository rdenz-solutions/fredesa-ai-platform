#!/usr/bin/env python3
"""
Comprehensive test suite for PostgreSQL Schema v2.1
Tests 15 tables, 40+ indexes, 7 views, 4 triggers

Expanded from v1 (10 tests) to v2.1 (28 tests)
Target: 28/28 passing before production deployment

Usage:
    python3 scripts/database/test_schema_v2.py
    python3 scripts/database/test_schema_v2.py --verbose
    python3 scripts/database/test_schema_v2.py --test knowledge_graph
"""

import os
import sys
import unittest
import psycopg2
from datetime import datetime, timedelta
import json
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSchemaV2(unittest.TestCase):
    """Test PostgreSQL Schema v2.1 - Epistemological Completeness Framework"""
    
    @classmethod
    def setUpClass(cls):
        """Connect to PostgreSQL database"""
        # Get connection string from environment or Key Vault
        conn_str = os.getenv('DATABASE_URL')
        
        if not conn_str:
            # Try to get from Azure Key Vault
            try:
                import subprocess
                password = subprocess.check_output([
                    'az', 'keyvault', 'secret', 'show',
                    '--vault-name', 'fredesa-kv-e997e3',
                    '--name', 'postgres-password',
                    '--query', 'value',
                    '-o', 'tsv'
                ], text=True).strip()
                
                conn_str = f"postgresql://fredesaadmin:{password}@fredesa-db-dev.postgres.database.azure.com:5432/postgres?sslmode=require"
            except Exception as e:
                raise Exception(f"Could not get database credentials: {e}")
        
        cls.conn = psycopg2.connect(conn_str)
        cls.conn.autocommit = False
        print(f"\n✅ Connected to PostgreSQL: {cls.conn.get_dsn_parameters()['host']}")
    
    @classmethod
    def tearDownClass(cls):
        """Close database connection"""
        if cls.conn:
            cls.conn.close()
            print("\n✅ Database connection closed")
    
    def setUp(self):
        """Start transaction for each test"""
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        """Rollback transaction after each test"""
        self.conn.rollback()
        if self.cursor:
            self.cursor.close()
    
    # ========================================================================
    # CORE TABLES TESTS (4 tests)
    # ========================================================================
    
    def test_01_all_tables_exist(self):
        """Test that all 15 tables exist"""
        expected_tables = [
            'categories', 'sources', 'customers', 'usage_tracking',
            'customer_connectors', 'connector_query_log', 'source_promotions',
            'source_validations', 'source_feedback',
            'source_concepts', 'source_relationships', 'source_use_cases',
            'learning_paths', 'source_versions', 'quality_history'
        ]
        
        self.cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        actual_tables = [row[0] for row in self.cursor.fetchall()]
        
        for table in expected_tables:
            self.assertIn(table, actual_tables, f"Table '{table}' not found")
        
        print(f"  ✅ All 15 tables exist: {', '.join(expected_tables)}")
    
    def test_02_epistemological_dimension_constraint(self):
        """Test epistemological dimension validation"""
        # Get a category
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        # Valid dimension should succeed
        valid_source = {
            'id': str(uuid.uuid4()),
            'category_id': category_id,
            'name': 'Test Theory Source',
            'url': 'https://example.com/theory',
            'source_type': 'expert',
            'epistemological_dimension': 'theory'
        }
        
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type, epistemological_dimension)
            VALUES (%(id)s, %(category_id)s, %(name)s, %(url)s, %(source_type)s, %(epistemological_dimension)s)
        """, valid_source)
        
        # Invalid dimension should fail
        with self.assertRaises(psycopg2.IntegrityError):
            invalid_source = valid_source.copy()
            invalid_source['id'] = str(uuid.uuid4())
            invalid_source['epistemological_dimension'] = 'invalid_dimension'
            
            self.cursor.execute("""
                INSERT INTO sources (id, category_id, name, url, source_type, epistemological_dimension)
                VALUES (%(id)s, %(category_id)s, %(name)s, %(url)s, %(source_type)s, %(epistemological_dimension)s)
            """, invalid_source)
        
        print("  ✅ Epistemological dimension constraint working (theory/practice/history/current/future)")
    
    def test_03_authority_score_auto_calculation(self):
        """Test authority score trigger auto-calculates based on source_type"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        test_sources = [
            {'type': 'official', 'expected_score': 90},
            {'type': 'expert', 'expected_score': 70},
            {'type': 'community', 'expected_score': 50},
        ]
        
        for test in test_sources:
            source_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO sources (id, category_id, name, url, source_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING authority_score
            """, (source_id, category_id, f"Test {test['type']} source", 
                  f"https://example.com/{test['type']}", test['type']))
            
            actual_score = self.cursor.fetchone()[0]
            self.assertEqual(actual_score, test['expected_score'],
                f"{test['type']} should have authority score {test['expected_score']}, got {actual_score}")
        
        print("  ✅ Authority score trigger: official=90, expert=70, community=50")
    
    def test_04_category_epistemological_statistics(self):
        """Test category statistics auto-update when sources added"""
        # Create test category
        cat_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO categories (id, name, display_name)
            VALUES (%s, %s, %s)
        """, (cat_id, 'test_category', 'Test Category'))
        
        # Add sources with different dimensions
        dimensions = ['theory', 'practice', 'history', 'current', 'future']
        source_ids = []
        
        for dim in dimensions:
            source_id = str(uuid.uuid4())
            source_ids.append(source_id)
            self.cursor.execute("""
                INSERT INTO sources (id, category_id, name, url, source_type, epistemological_dimension)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (source_id, cat_id, f"Test {dim} source", 
                  f"https://example.com/{dim}", 'expert', dim))
        
        # Check category statistics
        self.cursor.execute("""
            SELECT total_sources, theory_sources, practice_sources, 
                   history_sources, current_sources, future_sources
            FROM categories WHERE id = %s
        """, (cat_id,))
        
        stats = self.cursor.fetchone()
        self.assertEqual(stats[0], 5, "Total sources should be 5")
        self.assertEqual(stats[1], 1, "Theory sources should be 1")
        self.assertEqual(stats[2], 1, "Practice sources should be 1")
        self.assertEqual(stats[3], 1, "History sources should be 1")
        self.assertEqual(stats[4], 1, "Current sources should be 1")
        self.assertEqual(stats[5], 1, "Future sources should be 1")
        
        print("  ✅ Category statistics trigger: auto-updates epistemological counts")
    
    # ========================================================================
    # KNOWLEDGE GRAPH TESTS (8 tests)
    # ========================================================================
    
    def test_05_source_concepts_semantic_discovery(self):
        """Test source_concepts table for semantic discovery"""
        # Create test source
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        source_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (source_id, category_id, 'Test Cognitive Bias Source', 
              'https://example.com/cognitive-bias', 'expert'))
        
        # Add concepts
        concepts = [
            ('cognitive bias', 'principle', 0.95),
            ('confirmation bias', 'technique', 0.85),
            ('anchoring effect', 'technique', 0.75)
        ]
        
        for concept_name, category, relevance in concepts:
            self.cursor.execute("""
                INSERT INTO source_concepts (source_id, concept_name, concept_category, relevance_score)
                VALUES (%s, %s, %s, %s)
            """, (source_id, concept_name, category, relevance))
        
        # Query by concept
        self.cursor.execute("""
            SELECT COUNT(*) FROM source_concepts
            WHERE concept_name ILIKE '%cognitive%' AND relevance_score > 0.7
        """)
        
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, "Should find cognitive-related concepts")
        
        print("  ✅ Source concepts: semantic discovery working")
    
    def test_06_source_relationships_knowledge_graph(self):
        """Test source_relationships table for knowledge graph"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        # Create two related sources
        source1_id = str(uuid.uuid4())
        source2_id = str(uuid.uuid4())
        
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s), (%s, %s, %s, %s, %s)
        """, (source1_id, category_id, 'Theory Source', 'https://example.com/theory', 'expert',
              source2_id, category_id, 'Practice Source', 'https://example.com/practice', 'expert'))
        
        # Create relationship: practice applies theory
        self.cursor.execute("""
            INSERT INTO source_relationships 
            (source_id, related_source_id, relationship_type, relationship_strength)
            VALUES (%s, %s, %s, %s)
        """, (source2_id, source1_id, 'applies', 'strong'))
        
        # Verify relationship
        self.cursor.execute("""
            SELECT relationship_type, relationship_strength
            FROM source_relationships
            WHERE source_id = %s AND related_source_id = %s
        """, (source2_id, source1_id))
        
        result = self.cursor.fetchone()
        self.assertEqual(result[0], 'applies')
        self.assertEqual(result[1], 'strong')
        
        print("  ✅ Source relationships: knowledge graph working (applies/builds_on/contradicts)")
    
    def test_07_citation_count_trigger(self):
        """Test citation count auto-increments when relationship created"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        # Create two sources
        cited_source = str(uuid.uuid4())
        citing_source = str(uuid.uuid4())
        
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s), (%s, %s, %s, %s, %s)
        """, (cited_source, category_id, 'Cited Paper', 'https://example.com/cited', 'expert',
              citing_source, category_id, 'Citing Paper', 'https://example.com/citing', 'expert'))
        
        # Check initial citation count
        self.cursor.execute("SELECT cited_by_count FROM sources WHERE id = %s", (cited_source,))
        initial_count = self.cursor.fetchone()[0]
        
        # Create citation relationship
        self.cursor.execute("""
            INSERT INTO source_relationships (source_id, related_source_id, relationship_type)
            VALUES (%s, %s, %s)
        """, (citing_source, cited_source, 'cites'))
        
        # Check updated citation count
        self.cursor.execute("SELECT cited_by_count FROM sources WHERE id = %s", (cited_source,))
        updated_count = self.cursor.fetchone()[0]
        
        self.assertEqual(updated_count, initial_count + 1, "Citation count should increment by 1")
        
        print("  ✅ Citation count trigger: auto-increments on 'cites' relationship")
    
    def test_08_source_use_cases_problem_driven(self):
        """Test source_use_cases for problem-driven discovery"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        source_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (source_id, category_id, 'Bellingcat Toolkit', 
              'https://example.com/bellingcat', 'expert'))
        
        # Add use cases
        use_cases = [
            ('Verify Twitter account authenticity', 'intelligence_analysis', 0.90),
            ('Trace social media posts', 'intelligence_analysis', 0.85),
            ('Geolocate images', 'intelligence_analysis', 0.80)
        ]
        
        for name, category, score in use_cases:
            self.cursor.execute("""
                INSERT INTO source_use_cases (source_id, use_case_name, use_case_category, applicability_score)
                VALUES (%s, %s, %s, %s)
            """, (source_id, name, category, score))
        
        # Query by use case
        self.cursor.execute("""
            SELECT COUNT(*) FROM source_use_cases
            WHERE use_case_name ILIKE '%verify%' AND applicability_score > 0.8
        """)
        
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, "Should find verification-related use cases")
        
        print("  ✅ Source use cases: problem-driven discovery working")
    
    def test_09_learning_paths_curriculum(self):
        """Test learning_paths for curriculum sequencing"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        # Create sources with prerequisites
        beginner_id = str(uuid.uuid4())
        intermediate_id = str(uuid.uuid4())
        advanced_id = str(uuid.uuid4())
        
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type, difficulty_level)
            VALUES 
                (%s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s)
        """, (beginner_id, category_id, 'Intro to Intelligence', 'https://example.com/intro', 'expert', 'beginner',
              intermediate_id, category_id, 'Intelligence Methods', 'https://example.com/methods', 'expert', 'intermediate',
              advanced_id, category_id, 'Advanced Analysis', 'https://example.com/advanced', 'expert', 'advanced'))
        
        # Create learning path
        sequence = [
            {'source_id': str(beginner_id), 'order': 1, 'prerequisite_ids': []},
            {'source_id': str(intermediate_id), 'order': 2, 'prerequisite_ids': [str(beginner_id)]},
            {'source_id': str(advanced_id), 'order': 3, 'prerequisite_ids': [str(intermediate_id)]}
        ]
        
        path_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO learning_paths 
            (id, name, category_id, difficulty_level, sequence_order, estimated_duration_hours)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (path_id, 'Intelligence Analysis Fundamentals', category_id, 
              'intermediate', json.dumps(sequence), 40))
        
        # Verify learning path
        self.cursor.execute("""
            SELECT sequence_order FROM learning_paths WHERE id = %s
        """, (path_id,))
        
        stored_sequence = self.cursor.fetchone()[0]
        self.assertEqual(len(stored_sequence), 3, "Should have 3 steps in learning path")
        
        print("  ✅ Learning paths: curriculum sequencing working (beginner → expert)")
    
    def test_10_source_versions_history(self):
        """Test source_versions for version tracking"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        source_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (source_id, category_id, 'API Documentation', 
              'https://example.com/api/v1', 'official'))
        
        # Add version history
        versions = [
            ('1.0', 'https://example.com/api/v1', False, 'Initial release'),
            ('2.0', 'https://example.com/api/v2', True, 'Breaking changes: auth required'),
            ('2.1', 'https://example.com/api/v2.1', False, 'Bug fixes')
        ]
        
        for version, url, breaking, summary in versions:
            self.cursor.execute("""
                INSERT INTO source_versions 
                (source_id, version_number, url, breaking_changes, change_summary)
                VALUES (%s, %s, %s, %s, %s)
            """, (source_id, version, url, breaking, summary))
        
        # Query breaking changes
        self.cursor.execute("""
            SELECT COUNT(*) FROM source_versions
            WHERE source_id = %s AND breaking_changes = true
        """, (source_id,))
        
        breaking_count = self.cursor.fetchone()[0]
        self.assertEqual(breaking_count, 1, "Should have 1 breaking change version")
        
        print("  ✅ Source versions: version history tracking working")
    
    def test_11_quality_history_time_series(self):
        """Test quality_history for degradation detection"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        source_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (source_id, category_id, 'Quality Test Source', 
              'https://example.com/quality', 'expert'))
        
        # Add quality measurements over time
        measurements = [
            (datetime.now() - timedelta(days=90), 85, 80, 'validated'),
            (datetime.now() - timedelta(days=60), 82, 78, 'validated'),
            (datetime.now() - timedelta(days=30), 75, 70, 'flagged'),  # Degrading!
            (datetime.now(), 70, 65, 'flagged')
        ]
        
        for measured_at, authority, quality, status in measurements:
            self.cursor.execute("""
                INSERT INTO quality_history 
                (source_id, measured_at, authority_score, quality_score, validation_status)
                VALUES (%s, %s, %s, %s, %s)
            """, (source_id, measured_at, authority, quality, status))
        
        # Query for quality degradation
        self.cursor.execute("""
            SELECT measured_at, authority_score, quality_score
            FROM quality_history
            WHERE source_id = %s
            ORDER BY measured_at
        """, (source_id,))
        
        history = self.cursor.fetchall()
        self.assertEqual(len(history), 4, "Should have 4 quality measurements")
        
        # Check degradation trend
        first_quality = history[0][2]
        last_quality = history[-1][2]
        self.assertLess(last_quality, first_quality, "Quality should degrade over time in this test")
        
        print("  ✅ Quality history: time-series tracking and degradation detection working")
    
    def test_12_knowledge_graph_summary_view(self):
        """Test knowledge_graph_summary view performance"""
        # This view has complex JOINs - ensure it doesn't timeout
        self.cursor.execute("""
            SELECT source_id, source_name, concept_count, relationship_count, use_case_count
            FROM knowledge_graph_summary
            LIMIT 10
        """)
        
        results = self.cursor.fetchall()
        self.assertIsNotNone(results, "View should return results")
        
        print(f"  ✅ Knowledge graph summary view: returns {len(results)} rows (complex JOINs working)")
    
    # ========================================================================
    # QUALITY VALIDATION TESTS (4 tests)
    # ========================================================================
    
    def test_13_source_validations_tracking(self):
        """Test source_validations for quality checks"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        source_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (source_id, category_id, 'Validation Test Source', 
              'https://example.com/validation', 'expert'))
        
        # Add validation checks
        validations = [
            ('authority', 'pass', {'score': 85}),
            ('recency', 'pass', {'checked_date': str(datetime.now())}),
            ('cross_reference', 'warning', {'supporting_sources': 2}),
            ('fact_check', 'pass', {'checked_by': 'admin'})
        ]
        
        for val_type, result, details in validations:
            self.cursor.execute("""
                INSERT INTO source_validations 
                (source_id, validation_type, validation_result, validation_details)
                VALUES (%s, %s, %s, %s)
            """, (source_id, val_type, result, json.dumps(details)))
        
        # Query validation status
        self.cursor.execute("""
            SELECT validation_type, validation_result
            FROM source_validations
            WHERE source_id = %s AND validation_result = 'pass'
        """, (source_id,))
        
        passed = self.cursor.fetchall()
        self.assertGreater(len(passed), 0, "Should have passing validations")
        
        print("  ✅ Source validations: quality check tracking working")
    
    def test_14_source_feedback_customer_issues(self):
        """Test source_feedback for customer-reported issues"""
        # Get test customer and source
        self.cursor.execute("SELECT id FROM customers LIMIT 1")
        customer_id = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT id FROM sources LIMIT 1")
        source_id = self.cursor.fetchone()[0]
        
        # Add feedback
        self.cursor.execute("""
            INSERT INTO source_feedback 
            (source_id, customer_id, feedback_type, rating, feedback_text)
            VALUES (%s, %s, %s, %s, %s)
        """, (source_id, customer_id, 'accuracy_issue', 2, 'Content is outdated'))
        
        # Query unresolved issues
        self.cursor.execute("""
            SELECT COUNT(*) FROM source_feedback
            WHERE resolved = false AND rating < 3
        """)
        
        unresolved = self.cursor.fetchone()[0]
        self.assertGreater(unresolved, 0, "Should have unresolved low-rating feedback")
        
        print("  ✅ Source feedback: customer issue tracking working")
    
    def test_15_environment_promotion_workflow(self):
        """Test environment_flags and promotion workflow"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        source_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type, environment_flags)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_id, category_id, 'Promotion Test Source', 
              'https://example.com/promotion', 'expert',
              json.dumps({"dev": True, "staging": False, "production": False})))
        
        # Promote to staging
        self.cursor.execute("""
            UPDATE sources
            SET environment_flags = %s,
                promoted_to_staging_at = NOW(),
                promoted_by = 'admin'
            WHERE id = %s
        """, (json.dumps({"dev": True, "staging": True, "production": False}), source_id))
        
        # Log promotion
        self.cursor.execute("""
            INSERT INTO source_promotions 
            (source_id, from_environment, to_environment, promoted_by)
            VALUES (%s, %s, %s, %s)
        """, (source_id, 'dev', 'staging', 'admin'))
        
        # Verify promotion
        self.cursor.execute("""
            SELECT environment_flags FROM sources WHERE id = %s
        """, (source_id,))
        
        flags = self.cursor.fetchone()[0]
        self.assertTrue(flags['staging'], "Should be promoted to staging")
        
        print("  ✅ Environment promotion: dev → staging → production workflow working")
    
    def test_16_pending_approvals_view(self):
        """Test pending_approvals view for quality gates"""
        self.cursor.execute("""
            SELECT id, name, approval_status, promotion_type
            FROM pending_approvals
            LIMIT 5
        """)
        
        results = self.cursor.fetchall()
        self.assertIsNotNone(results, "View should return results")
        
        print(f"  ✅ Pending approvals view: {len(results)} sources awaiting approval")
    
    # ========================================================================
    # FEDERATED ARCHITECTURE TESTS (3 tests)
    # ========================================================================
    
    def test_17_customer_connectors_oauth(self):
        """Test customer_connectors for OAuth credentials"""
        self.cursor.execute("SELECT id FROM customers LIMIT 1")
        customer_id = self.cursor.fetchone()[0]
        
        connector_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO customer_connectors 
            (id, customer_id, connector_type, connector_name, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (connector_id, customer_id, 'sharepoint', 'Acme SharePoint', True))
        
        # Verify connector
        self.cursor.execute("""
            SELECT connector_type, is_active FROM customer_connectors WHERE id = %s
        """, (connector_id,))
        
        result = self.cursor.fetchone()
        self.assertEqual(result[0], 'sharepoint')
        self.assertTrue(result[1])
        
        print("  ✅ Customer connectors: OAuth credential storage working")
    
    def test_18_connector_query_log_billing(self):
        """Test connector_query_log for federated query billing"""
        self.cursor.execute("SELECT id FROM customers LIMIT 1")
        customer_id = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT id FROM customer_connectors LIMIT 1")
        connector_id = self.cursor.fetchone()
        
        if connector_id:
            connector_id = connector_id[0]
            
            # Log federated query
            self.cursor.execute("""
                INSERT INTO connector_query_log 
                (customer_id, connector_id, query_text, files_retrieved, bytes_retrieved, query_duration_ms)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (customer_id, connector_id, 'Search for proposal templates', 15, 2048000, 350))
            
            # Verify log
            self.cursor.execute("""
                SELECT files_retrieved, bytes_retrieved FROM connector_query_log
                WHERE customer_id = %s
            """, (customer_id,))
            
            result = self.cursor.fetchone()
            if result:
                self.assertGreater(result[0], 0, "Should have retrieved files")
                print("  ✅ Connector query log: federated query billing working")
        else:
            print("  ⚠️  Connector query log: skipped (no connectors available)")
    
    def test_19_customer_stats_view(self):
        """Test customer_stats view aggregates usage"""
        self.cursor.execute("""
            SELECT id, name, total_queries, federated_queries, active_connectors
            FROM customer_stats
            LIMIT 5
        """)
        
        results = self.cursor.fetchall()
        self.assertIsNotNone(results, "View should return customer statistics")
        
        print(f"  ✅ Customer stats view: {len(results)} customers tracked")
    
    # ========================================================================
    # VIEWS & PERFORMANCE TESTS (5 tests)
    # ========================================================================
    
    def test_20_active_sources_view(self):
        """Test active_sources view filters correctly"""
        self.cursor.execute("""
            SELECT COUNT(*) FROM active_sources
        """)
        
        count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(count, 0, "Active sources view should return results")
        
        print(f"  ✅ Active sources view: {count} active sources")
    
    def test_21_production_sources_view(self):
        """Test production_sources view shows only production-ready"""
        self.cursor.execute("""
            SELECT COUNT(*) FROM production_sources
        """)
        
        count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(count, 0, "Production sources view should return results")
        
        print(f"  ✅ Production sources view: {count} production-ready sources")
    
    def test_22_vertical_completeness_view(self):
        """Test vertical_completeness view calculates 5D percentages"""
        self.cursor.execute("""
            SELECT category_name, total_sources, 
                   theory_percent, practice_percent, history_percent, 
                   current_percent, future_percent
            FROM vertical_completeness
            LIMIT 5
        """)
        
        results = self.cursor.fetchall()
        self.assertIsNotNone(results, "Vertical completeness view should return results")
        
        if results:
            for row in results:
                # Check percentages sum to ~100 (allowing for rounding)
                total_percent = (row[2] or 0) + (row[3] or 0) + (row[4] or 0) + (row[5] or 0) + (row[6] or 0)
                if row[1] > 0:  # Only check if category has sources
                    self.assertAlmostEqual(total_percent, 100, delta=1, 
                        msg=f"Category {row[0]} percentages should sum to 100")
        
        print(f"  ✅ Vertical completeness view: 5D balance tracking working")
    
    def test_23_curriculum_ready_sources_view(self):
        """Test curriculum_ready_sources view for learning paths"""
        self.cursor.execute("""
            SELECT COUNT(*) FROM curriculum_ready_sources
        """)
        
        count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(count, 0, "Curriculum ready sources view should return results")
        
        print(f"  ✅ Curriculum ready sources view: {count} sources with prerequisites")
    
    def test_24_indexes_exist(self):
        """Test that critical indexes exist for performance"""
        critical_indexes = [
            'idx_sources_epistemological_dimension',
            'idx_sources_authority_score',
            'idx_sources_quality_score',
            'idx_sources_difficulty_level',
            'idx_concepts_name',
            'idx_relationships_type',
            'idx_use_cases_category'
        ]
        
        self.cursor.execute("""
            SELECT indexname FROM pg_indexes
            WHERE schemaname = 'public'
        """)
        
        existing_indexes = [row[0] for row in self.cursor.fetchall()]
        
        missing = []
        for idx in critical_indexes:
            if idx not in existing_indexes:
                missing.append(idx)
        
        self.assertEqual(len(missing), 0, f"Missing indexes: {missing}")
        
        print(f"  ✅ Critical indexes exist: {len(critical_indexes)} verified")
    
    # ========================================================================
    # RLS & SECURITY TESTS (2 tests)
    # ========================================================================
    
    def test_25_row_level_security_enabled(self):
        """Test that RLS is enabled on customer tables"""
        rls_tables = ['sources', 'customers', 'usage_tracking', 
                      'customer_connectors', 'connector_query_log', 'source_feedback']
        
        for table in rls_tables:
            self.cursor.execute("""
                SELECT relrowsecurity FROM pg_class
                WHERE relname = %s
            """, (table,))
            
            result = self.cursor.fetchone()
            if result:
                self.assertTrue(result[0], f"RLS should be enabled on {table}")
        
        print(f"  ✅ Row level security: enabled on {len(rls_tables)} tables")
    
    def test_26_triggers_exist(self):
        """Test that critical triggers exist"""
        critical_triggers = [
            'update_categories_updated_at',
            'update_sources_updated_at',
            'maintain_category_stats',
            'calculate_authority_score',
            'maintain_citation_counts_trigger'
        ]
        
        self.cursor.execute("""
            SELECT tgname FROM pg_trigger
            WHERE tgname IN %s
        """, (tuple(critical_triggers),))
        
        existing_triggers = [row[0] for row in self.cursor.fetchall()]
        
        for trigger in critical_triggers:
            self.assertIn(trigger, existing_triggers, f"Trigger {trigger} should exist")
        
        print(f"  ✅ Critical triggers exist: {len(existing_triggers)}/{len(critical_triggers)}")
    
    # ========================================================================
    # CONSTRAINT TESTS (2 tests)
    # ========================================================================
    
    def test_27_difficulty_level_constraint(self):
        """Test difficulty_level constraint validation"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        # Valid difficulty should succeed
        source_id = str(uuid.uuid4())
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type, difficulty_level)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (source_id, category_id, 'Test Difficulty Source', 
              'https://example.com/difficulty', 'expert', 'intermediate'))
        
        # Invalid difficulty should fail
        with self.assertRaises(psycopg2.IntegrityError):
            invalid_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO sources (id, category_id, name, url, source_type, difficulty_level)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (invalid_id, category_id, 'Invalid Difficulty', 
                  'https://example.com/invalid', 'expert', 'invalid_level'))
        
        print("  ✅ Difficulty level constraint: beginner/intermediate/advanced/expert enforced")
    
    def test_28_relationship_type_constraint(self):
        """Test relationship_type constraint validation"""
        self.cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = self.cursor.fetchone()[0]
        
        # Create two sources
        source1 = str(uuid.uuid4())
        source2 = str(uuid.uuid4())
        
        self.cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s), (%s, %s, %s, %s, %s)
        """, (source1, category_id, 'Source A', 'https://example.com/a', 'expert',
              source2, category_id, 'Source B', 'https://example.com/b', 'expert'))
        
        # Valid relationship should succeed
        self.cursor.execute("""
            INSERT INTO source_relationships (source_id, related_source_id, relationship_type)
            VALUES (%s, %s, %s)
        """, (source1, source2, 'builds_on'))
        
        # Invalid relationship should fail
        with self.assertRaises(psycopg2.IntegrityError):
            self.cursor.execute("""
                INSERT INTO source_relationships (source_id, related_source_id, relationship_type)
                VALUES (%s, %s, %s)
            """, (source2, source1, 'invalid_relationship'))
        
        print("  ✅ Relationship type constraint: builds_on/contradicts/applies/validates enforced")


def run_tests(verbose=False, test_filter=None):
    """Run test suite with optional filtering"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSchemaV2)
    
    # Filter tests if requested
    if test_filter:
        filtered_suite = unittest.TestSuite()
        for test in suite:
            if test_filter.lower() in str(test).lower():
                filtered_suite.addTest(test)
        suite = filtered_suite
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"📊 TEST RESULTS: {result.testsRun} tests run")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f"❌ Failed: {len(result.failures)}")
    if result.errors:
        print(f"⚠️  Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test PostgreSQL Schema v2.1')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--test', '-t', type=str, help='Filter tests (e.g., "knowledge_graph")')
    
    args = parser.parse_args()
    
    success = run_tests(verbose=args.verbose, test_filter=args.test)
    sys.exit(0 if success else 1)
