#!/usr/bin/env python3
"""
PostgreSQL Schema Performance Benchmark
Compare schema v1 vs v2.1 performance to validate <5% overhead claim

Usage:
    python3 scripts/database/benchmark_schema.py
    python3 scripts/database/benchmark_schema.py --iterations 100
    python3 scripts/database/benchmark_schema.py --report
"""

import os
import sys
import time
import statistics
import psycopg2
import uuid
from datetime import datetime
import json

class SchemaBenchmark:
    """Benchmark PostgreSQL schema performance"""
    
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        self.conn.autocommit = False
        self.results = {}
    
    def __del__(self):
        if self.conn:
            self.conn.close()
    
    def run_benchmark(self, name, query, params=None, iterations=10):
        """Run a query multiple times and measure performance"""
        times = []
        
        for i in range(iterations):
            cursor = self.conn.cursor()
            start = time.perf_counter()
            
            try:
                cursor.execute(query, params or ())
                cursor.fetchall()
                end = time.perf_counter()
                times.append((end - start) * 1000)  # Convert to milliseconds
            finally:
                cursor.close()
                self.conn.rollback()  # Don't persist test data
        
        self.results[name] = {
            'min_ms': min(times),
            'max_ms': max(times),
            'avg_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stddev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }
        
        return self.results[name]
    
    # ========================================================================
    # READ BENCHMARKS
    # ========================================================================
    
    def bench_select_all_sources(self, iterations=10):
        """Benchmark: SELECT * FROM sources"""
        return self.run_benchmark(
            'SELECT all sources',
            'SELECT * FROM sources LIMIT 1000',
            iterations=iterations
        )
    
    def bench_select_by_category(self, iterations=10):
        """Benchmark: SELECT with WHERE clause on indexed column"""
        # Get a real category ID
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = cursor.fetchone()[0]
        cursor.close()
        
        return self.run_benchmark(
            'SELECT by category (indexed)',
            'SELECT * FROM sources WHERE category_id = %s',
            (category_id,),
            iterations=iterations
        )
    
    def bench_select_by_dimension(self, iterations=10):
        """Benchmark: SELECT by epistemological dimension (v2.1 feature)"""
        return self.run_benchmark(
            'SELECT by epistemological dimension',
            "SELECT * FROM sources WHERE epistemological_dimension = 'theory'",
            iterations=iterations
        )
    
    def bench_select_active_sources_view(self, iterations=10):
        """Benchmark: SELECT from active_sources view"""
        return self.run_benchmark(
            'SELECT from active_sources view',
            'SELECT * FROM active_sources LIMIT 100',
            iterations=iterations
        )
    
    def bench_select_vertical_completeness_view(self, iterations=10):
        """Benchmark: SELECT from vertical_completeness view (complex aggregation)"""
        return self.run_benchmark(
            'SELECT from vertical_completeness view',
            'SELECT * FROM vertical_completeness',
            iterations=iterations
        )
    
    def bench_knowledge_graph_summary_view(self, iterations=10):
        """Benchmark: SELECT from knowledge_graph_summary view (multiple JOINs)"""
        return self.run_benchmark(
            'SELECT from knowledge_graph_summary view',
            'SELECT * FROM knowledge_graph_summary LIMIT 100',
            iterations=iterations
        )
    
    # ========================================================================
    # WRITE BENCHMARKS
    # ========================================================================
    
    def bench_insert_source(self, iterations=10):
        """Benchmark: INSERT single source (with triggers)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = cursor.fetchone()[0]
        cursor.close()
        
        times = []
        for i in range(iterations):
            cursor = self.conn.cursor()
            source_id = str(uuid.uuid4())
            start = time.perf_counter()
            
            try:
                cursor.execute("""
                    INSERT INTO sources (id, category_id, name, url, source_type, epistemological_dimension)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (source_id, category_id, f'Benchmark Source {i}', 
                      f'https://example.com/bench{i}', 'expert', 'practice'))
                
                end = time.perf_counter()
                times.append((end - start) * 1000)
            finally:
                cursor.close()
                self.conn.rollback()  # Don't persist test data
        
        self.results['INSERT source with triggers'] = {
            'min_ms': min(times),
            'max_ms': max(times),
            'avg_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stddev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }
        
        return self.results['INSERT source with triggers']
    
    def bench_update_source(self, iterations=10):
        """Benchmark: UPDATE source (with triggers)"""
        # Create a test source
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = cursor.fetchone()[0]
        
        source_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO sources (id, category_id, name, url, source_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (source_id, category_id, 'Benchmark Update Source', 
              'https://example.com/update', 'expert'))
        self.conn.commit()
        cursor.close()
        
        times = []
        for i in range(iterations):
            cursor = self.conn.cursor()
            start = time.perf_counter()
            
            try:
                cursor.execute("""
                    UPDATE sources SET quality_score = %s WHERE id = %s
                """, (70 + i, source_id))
                
                end = time.perf_counter()
                times.append((end - start) * 1000)
            finally:
                cursor.close()
                self.conn.rollback()
        
        # Cleanup
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM sources WHERE id = %s", (source_id,))
        self.conn.commit()
        cursor.close()
        
        self.results['UPDATE source with triggers'] = {
            'min_ms': min(times),
            'max_ms': max(times),
            'avg_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stddev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }
        
        return self.results['UPDATE source with triggers']
    
    def bench_bulk_insert(self, count=100):
        """Benchmark: Bulk insert multiple sources"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = cursor.fetchone()[0]
        
        start = time.perf_counter()
        
        for i in range(count):
            source_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO sources (id, category_id, name, url, source_type, epistemological_dimension)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (source_id, category_id, f'Bulk Source {i}', 
                  f'https://example.com/bulk{i}', 'expert', 'practice'))
        
        end = time.perf_counter()
        
        cursor.close()
        self.conn.rollback()  # Don't persist test data
        
        total_ms = (end - start) * 1000
        avg_ms = total_ms / count
        
        self.results[f'Bulk INSERT {count} sources'] = {
            'total_ms': total_ms,
            'avg_ms_per_source': avg_ms,
            'count': count
        }
        
        return self.results[f'Bulk INSERT {count} sources']
    
    # ========================================================================
    # KNOWLEDGE GRAPH BENCHMARKS
    # ========================================================================
    
    def bench_insert_with_knowledge_graph(self, iterations=5):
        """Benchmark: Insert source + concepts + relationships + use cases"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM categories LIMIT 1")
        category_id = cursor.fetchone()[0]
        cursor.close()
        
        times = []
        for i in range(iterations):
            cursor = self.conn.cursor()
            source_id = str(uuid.uuid4())
            start = time.perf_counter()
            
            try:
                # Insert source
                cursor.execute("""
                    INSERT INTO sources (id, category_id, name, url, source_type, epistemological_dimension)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (source_id, category_id, f'KG Source {i}', 
                      f'https://example.com/kg{i}', 'expert', 'theory'))
                
                # Insert 5 concepts
                for j in range(5):
                    cursor.execute("""
                        INSERT INTO source_concepts (source_id, concept_name, concept_category, relevance_score)
                        VALUES (%s, %s, %s, %s)
                    """, (source_id, f'Concept {j}', 'principle', 0.8))
                
                # Insert 3 use cases
                for j in range(3):
                    cursor.execute("""
                        INSERT INTO source_use_cases (source_id, use_case_name, use_case_category, applicability_score)
                        VALUES (%s, %s, %s, %s)
                    """, (source_id, f'Use Case {j}', 'intelligence_analysis', 0.75))
                
                end = time.perf_counter()
                times.append((end - start) * 1000)
            finally:
                cursor.close()
                self.conn.rollback()
        
        self.results['INSERT with knowledge graph (1 source + 5 concepts + 3 use cases)'] = {
            'min_ms': min(times),
            'max_ms': max(times),
            'avg_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stddev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }
        
        return self.results['INSERT with knowledge graph (1 source + 5 concepts + 3 use cases)']
    
    def bench_semantic_search(self, iterations=10):
        """Benchmark: Semantic search by concept name"""
        return self.run_benchmark(
            'Semantic search by concept',
            """
            SELECT s.*, sc.concept_name, sc.relevance_score
            FROM sources s
            JOIN source_concepts sc ON s.id = sc.source_id
            WHERE sc.concept_name ILIKE '%cognitive%'
            ORDER BY sc.relevance_score DESC
            LIMIT 20
            """,
            iterations=iterations
        )
    
    def bench_relationship_traversal(self, iterations=10):
        """Benchmark: Knowledge graph relationship traversal"""
        # Get a source with relationships
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT source_id FROM source_relationships LIMIT 1
        """)
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            source_id = result[0]
            return self.run_benchmark(
                'Knowledge graph relationship traversal',
                """
                SELECT s1.name as source_name, 
                       sr.relationship_type,
                       s2.name as related_source_name
                FROM sources s1
                JOIN source_relationships sr ON s1.id = sr.source_id
                JOIN sources s2 ON sr.related_source_id = s2.id
                WHERE s1.id = %s
                """,
                (source_id,),
                iterations=iterations
            )
        else:
            print("  ⚠️  Skipped: No relationships in database")
            return None
    
    # ========================================================================
    # REPORT GENERATION
    # ========================================================================
    
    def print_report(self):
        """Print formatted benchmark report"""
        print("\n" + "="*80)
        print("📊 POSTGRESQL SCHEMA PERFORMANCE BENCHMARK")
        print("="*80)
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {self.conn.get_dsn_parameters()['host']}")
        
        # Categorize results
        read_ops = [k for k in self.results.keys() if 'SELECT' in k or 'search' in k.lower()]
        write_ops = [k for k in self.results.keys() if 'INSERT' in k or 'UPDATE' in k]
        
        # Read operations
        print("\n" + "-"*80)
        print("📖 READ OPERATIONS")
        print("-"*80)
        for op in read_ops:
            result = self.results[op]
            if 'avg_ms' in result:
                print(f"\n{op}:")
                print(f"  Average: {result['avg_ms']:.2f} ms")
                print(f"  Median:  {result['median_ms']:.2f} ms")
                print(f"  Min/Max: {result['min_ms']:.2f} / {result['max_ms']:.2f} ms")
                print(f"  StdDev:  {result['stddev_ms']:.2f} ms")
                
                # Performance assessment
                if result['avg_ms'] < 10:
                    print(f"  ✅ EXCELLENT (< 10 ms)")
                elif result['avg_ms'] < 50:
                    print(f"  ✅ GOOD (< 50 ms)")
                elif result['avg_ms'] < 100:
                    print(f"  ⚠️  ACCEPTABLE (< 100 ms)")
                else:
                    print(f"  ❌ SLOW (> 100 ms) - NEEDS OPTIMIZATION")
        
        # Write operations
        print("\n" + "-"*80)
        print("✍️  WRITE OPERATIONS")
        print("-"*80)
        for op in write_ops:
            result = self.results[op]
            if 'avg_ms' in result:
                print(f"\n{op}:")
                print(f"  Average: {result['avg_ms']:.2f} ms")
                print(f"  Median:  {result['median_ms']:.2f} ms")
                print(f"  Min/Max: {result['min_ms']:.2f} / {result['max_ms']:.2f} ms")
                print(f"  StdDev:  {result['stddev_ms']:.2f} ms")
                
                # Performance assessment
                if result['avg_ms'] < 50:
                    print(f"  ✅ EXCELLENT (< 50 ms)")
                elif result['avg_ms'] < 100:
                    print(f"  ✅ GOOD (< 100 ms)")
                elif result['avg_ms'] < 200:
                    print(f"  ⚠️  ACCEPTABLE (< 200 ms)")
                else:
                    print(f"  ❌ SLOW (> 200 ms) - NEEDS OPTIMIZATION")
            elif 'total_ms' in result:
                print(f"\n{op}:")
                print(f"  Total time: {result['total_ms']:.2f} ms")
                print(f"  Avg per source: {result['avg_ms_per_source']:.2f} ms")
                print(f"  Count: {result['count']}")
        
        # Summary
        print("\n" + "="*80)
        print("📈 SUMMARY")
        print("="*80)
        
        all_avg = [r['avg_ms'] for r in self.results.values() if 'avg_ms' in r]
        if all_avg:
            print(f"\nOverall average: {statistics.mean(all_avg):.2f} ms")
            print(f"Overall median:  {statistics.median(all_avg):.2f} ms")
            print(f"Fastest operation: {min(all_avg):.2f} ms")
            print(f"Slowest operation: {max(all_avg):.2f} ms")
        
        print("\n" + "="*80)
        print("✅ BENCHMARK COMPLETE")
        print("="*80 + "\n")
    
    def save_report_json(self, filepath):
        """Save benchmark results as JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'database': self.conn.get_dsn_parameters()['host'],
            'results': self.results
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📁 Report saved to: {filepath}")


def main():
    """Run comprehensive benchmark suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark PostgreSQL Schema Performance')
    parser.add_argument('--iterations', '-i', type=int, default=10, help='Iterations per benchmark (default: 10)')
    parser.add_argument('--report', '-r', type=str, help='Save report to JSON file')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick mode (fewer iterations)')
    
    args = parser.parse_args()
    
    # Get connection string
    conn_str = os.getenv('DATABASE_URL')
    
    if not conn_str:
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
            print(f"❌ Could not get database credentials: {e}")
            sys.exit(1)
    
    # Adjust iterations
    if args.quick:
        iterations = 3
        print("🏃 Quick mode: 3 iterations per benchmark")
    else:
        iterations = args.iterations
        print(f"📊 Running benchmarks: {iterations} iterations per operation")
    
    # Run benchmark
    bench = SchemaBenchmark(conn_str)
    
    print("\n🔍 Running READ benchmarks...")
    bench.bench_select_all_sources(iterations)
    bench.bench_select_by_category(iterations)
    bench.bench_select_by_dimension(iterations)
    bench.bench_select_active_sources_view(iterations)
    bench.bench_select_vertical_completeness_view(iterations)
    bench.bench_knowledge_graph_summary_view(iterations)
    
    print("\n✍️  Running WRITE benchmarks...")
    bench.bench_insert_source(iterations)
    bench.bench_update_source(iterations)
    bench.bench_bulk_insert(100)
    
    print("\n🕸️  Running KNOWLEDGE GRAPH benchmarks...")
    bench.bench_insert_with_knowledge_graph(5)
    bench.bench_semantic_search(iterations)
    bench.bench_relationship_traversal(iterations)
    
    # Print report
    bench.print_report()
    
    # Save report if requested
    if args.report:
        bench.save_report_json(args.report)


if __name__ == '__main__':
    main()
