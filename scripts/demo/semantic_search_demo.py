#!/usr/bin/env python3
"""
Semantic Search Demo for FreDeSa Knowledge Platform
Demonstrates querying 1,043 sources with natural language
"""

import sys
import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from typing import List, Dict, Optional

def get_db_connection():
    """Connect to PostgreSQL"""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url='https://fredesa-kv-e997e3.vault.azure.net/', credential=credential)
    password = client.get_secret('postgres-password').value
    
    return psycopg2.connect(
        host='fredesa-db-dev.postgres.database.azure.com',
        port=5432,
        dbname='postgres',
        user='fredesaadmin',
        password=password,
        sslmode='require'
    )

def search_by_keywords(
    cursor,
    keywords: List[str],
    dimension: Optional[str] = None,
    category: Optional[str] = None,
    min_authority: Optional[int] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Search sources by keywords with optional filters
    
    Args:
        keywords: Words to search in name, description, metadata
        dimension: Filter by epistemological dimension (theory/practice/current)
        category: Filter by category name
        min_authority: Minimum authority score (50, 70, 90)
        limit: Max results to return
    """
    
    # Build WHERE clauses
    where_clauses = []
    params = []
    
    # Keyword search (name, description, metadata tags)
    if keywords:
        keyword_conditions = []
        for kw in keywords:
            keyword_conditions.append(
                "(LOWER(s.name) LIKE %s OR LOWER(s.description) LIKE %s OR LOWER(s.metadata::text) LIKE %s)"
            )
            search_pattern = f"%{kw.lower()}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        where_clauses.append(f"({' OR '.join(keyword_conditions)})")
    
    # Dimension filter
    if dimension:
        where_clauses.append("s.epistemological_dimension = %s")
        params.append(dimension)
    
    # Category filter
    if category:
        where_clauses.append("c.name = %s")
        params.append(category)
    
    # Authority filter
    if min_authority:
        where_clauses.append("s.authority_score >= %s")
        params.append(min_authority)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Execute query
    query = f"""
        SELECT 
            s.id,
            s.name,
            s.url,
            s.description,
            s.epistemological_dimension,
            s.difficulty_level,
            s.source_type,
            s.authority_score,
            s.quality_score,
            c.display_name as category,
            s.word_count,
            s.metadata
        FROM sources s
        JOIN categories c ON c.id = s.category_id
        WHERE {where_sql}
        ORDER BY s.authority_score DESC, s.quality_score DESC
        LIMIT %s
    """
    
    params.append(limit)
    cursor.execute(query, params)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row[0],
            'name': row[1],
            'url': row[2],
            'description': row[3],
            'dimension': row[4],
            'difficulty': row[5],
            'source_type': row[6],
            'authority_score': row[7],
            'quality_score': row[8],
            'category': row[9],
            'word_count': row[10],
            'metadata': row[11]
        })
    
    return results

def display_results(results: List[Dict], query_description: str):
    """Pretty print search results"""
    print("\n" + "="*80)
    print(f"🔍 QUERY: {query_description}")
    print("="*80)
    
    if not results:
        print("❌ No results found")
        return
    
    print(f"✅ Found {len(results)} sources:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}")
        print(f"   📂 Category: {result['category']}")
        print(f"   📐 Dimension: {result['dimension']} | Difficulty: {result['difficulty']}")
        print(f"   ⭐ Authority: {result['authority_score']} ({result['source_type']}) | Quality: {result['quality_score']}")
        
        if result['word_count']:
            print(f"   📊 Content: {result['word_count']:,} words")
        
        # Show description preview
        if result['description']:
            desc = result['description'][:120] + "..." if len(result['description']) > 120 else result['description']
            print(f"   💡 {desc}")
        
        print(f"   🔗 {result['url']}\n")

def run_demo_queries(cursor):
    """Run a series of demonstration queries"""
    
    print("\n" + "🎯"*40)
    print("FreDeSa Knowledge Platform - Semantic Search Demo")
    print("Testing queries against 1,043 knowledge sources")
    print("🎯"*40)
    
    # Query 1: Federal contracting practice
    print("\n" + "─"*80)
    results = search_by_keywords(
        cursor,
        keywords=['FAR', 'subcontract', 'proposal'],
        dimension='practice',
        min_authority=70,
        limit=5
    )
    display_results(results, "Federal contracting guidance (Practice-oriented, Authority 70+)")
    
    # Query 2: AI governance frameworks
    print("\n" + "─"*80)
    results = search_by_keywords(
        cursor,
        keywords=['AI', 'governance', 'framework', 'ethics'],
        dimension='theory',
        limit=5
    )
    display_results(results, "AI governance frameworks (Theory dimension)")
    
    # Query 3: Current cybersecurity threats
    print("\n" + "─"*80)
    results = search_by_keywords(
        cursor,
        keywords=['cybersecurity', 'security', 'vulnerability'],
        dimension='current',
        category='Cybersecurity',
        limit=5
    )
    display_results(results, "Current cybersecurity knowledge (Cybersecurity category)")
    
    # Query 4: Official government sources only
    print("\n" + "─"*80)
    results = search_by_keywords(
        cursor,
        keywords=['DOD', 'NIST', 'federal'],
        min_authority=90,
        limit=5
    )
    display_results(results, "Official government sources (Authority Score 90)")
    
    # Query 5: LLM frameworks for practice
    print("\n" + "─"*80)
    results = search_by_keywords(
        cursor,
        keywords=['LLM', 'agent', 'framework', 'MCP'],
        dimension='practice',
        limit=5
    )
    display_results(results, "LLM frameworks and tools (Practice implementations)")
    
    # Query 6: Intelligence gathering methods
    print("\n" + "─"*80)
    results = search_by_keywords(
        cursor,
        keywords=['intelligence', 'OSINT', 'collection'],
        category='Intelligence',
        limit=5
    )
    display_results(results, "Intelligence gathering resources")
    
    # Show query statistics
    print("\n" + "="*80)
    print("📊 QUERY PERFORMANCE STATS")
    print("="*80)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_sources,
            COUNT(DISTINCT category_id) as total_categories,
            COUNT(CASE WHEN authority_score = 90 THEN 1 END) as official_sources,
            COUNT(CASE WHEN authority_score = 70 THEN 1 END) as expert_sources,
            COUNT(CASE WHEN authority_score = 50 THEN 1 END) as community_sources,
            ROUND(AVG(quality_score), 1) as avg_quality,
            SUM(word_count) as total_words
        FROM sources
    """)
    
    stats = cursor.fetchone()
    print(f"\n📦 Total Sources: {stats[0]:,}")
    print(f"📂 Categories: {stats[1]}")
    print(f"\n🏆 Authority Distribution:")
    print(f"   Official (90):   {stats[2]:3} sources")
    print(f"   Expert (70):     {stats[3]:3} sources")
    print(f"   Community (50):  {stats[4]:3} sources")
    print(f"\n⭐ Average Quality Score: {stats[5]}")
    print(f"📝 Total Content: {stats[6]:,} words")

def custom_query(cursor, query_text: str):
    """Run a custom query provided by user"""
    print("\n" + "="*80)
    print(f"🔍 CUSTOM QUERY: {query_text}")
    print("="*80)
    
    # Extract keywords from query
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'for', 'on', 'in', 'to', 'of', 'with'}
    keywords = [w for w in query_text.lower().split() if w not in stop_words and len(w) > 2]
    
    print(f"📝 Keywords extracted: {', '.join(keywords)}\n")
    
    results = search_by_keywords(cursor, keywords=keywords, limit=10)
    
    if results:
        print(f"✅ Found {len(results)} relevant sources:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']}")
            print(f"   📐 {result['dimension']} | {result['category']} | Authority: {result['authority_score']}")
            print(f"   🔗 {result['url']}\n")
    else:
        print("❌ No results found")

def main():
    """Main entry point"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if len(sys.argv) > 1:
            # Custom query mode
            query = ' '.join(sys.argv[1:])
            custom_query(cursor, query)
        else:
            # Demo mode
            run_demo_queries(cursor)
        
        print("\n" + "="*80)
        print("✅ Search demo complete!")
        print("="*80)
        print("\n💡 TIP: Run custom queries with:")
        print("   python3 semantic_search_demo.py \"your query here\"")
        print("\nExamples:")
        print("   python3 semantic_search_demo.py \"FAR subcontracting requirements\"")
        print("   python3 semantic_search_demo.py \"NIST AI risk management\"")
        print("   python3 semantic_search_demo.py \"Azure deployment best practices\"")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
