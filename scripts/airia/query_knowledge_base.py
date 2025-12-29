#!/usr/bin/env python3
"""
Knowledge Base Query Function for Airia Agents
Provides authoritative sources from PostgreSQL to AI agents
"""

import sys
import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from typing import List, Dict, Optional
import json

def get_db_connection():
    """Connect to FreDeSa PostgreSQL database"""
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

def query_knowledge_base(
    query: str,
    dimension: Optional[str] = None,
    category: Optional[str] = None,
    min_authority: int = 70,
    limit: int = 5,
    include_content: bool = False
) -> Dict:
    """
    Query knowledge base with natural language and return authoritative sources.
    
    This function is designed to be called by Airia AI agents to retrieve
    relevant, authoritative knowledge sources for their responses.
    
    Args:
        query: Natural language query (e.g., "FAR subcontracting requirements")
        dimension: Optional filter - "theory", "practice", or "current"
        category: Optional category filter (e.g., "Federal_Contracting")
        min_authority: Minimum authority score (50, 70, or 90)
        limit: Maximum number of sources to return (default 5)
        include_content: If True, include full content/word count details
        
    Returns:
        Dict with:
            - sources: List of source dicts with name, url, description, authority
            - query_info: Query metadata (keywords, filters applied)
            - summary: Human-readable summary for agent context
    """
    
    # Extract keywords from query (remove stop words)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'for', 'on', 'in', 'to', 'of',
        'with', 'what', 'how', 'when', 'where', 'why', 'who', 'which', 'is',
        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
        'must', 'can', 'about', 'from', 'by', 'at', 'as', 'into', 'through'
    }
    
    keywords = [
        w for w in query.lower().split() 
        if w not in stop_words and len(w) > 2
    ]
    
    # Build query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    # Keyword search
    if keywords:
        keyword_conditions = []
        for kw in keywords:
            keyword_conditions.append(
                "(LOWER(s.name) LIKE %s OR LOWER(s.description) LIKE %s OR LOWER(s.metadata::text) LIKE %s)"
            )
            search_pattern = f"%{kw}%"
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
    where_clauses.append("s.authority_score >= %s")
    params.append(min_authority)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Execute query
    sql = f"""
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
    cursor.execute(sql, params)
    
    # Format results
    sources = []
    for row in cursor.fetchall():
        source = {
            'name': row[1],
            'url': row[2],
            'description': row[3][:200] + "..." if row[3] and len(row[3]) > 200 else row[3],
            'dimension': row[4],
            'difficulty': row[5],
            'source_type': row[6],
            'authority_score': int(row[7]) if row[7] else 0,  # Convert Decimal to int
            'quality_score': float(row[8]) if row[8] else 0.0,  # Convert Decimal to float
            'category': row[9]
        }
        
        if include_content:
            source['word_count'] = int(row[10]) if row[10] else 0
            source['metadata'] = row[11]
        
        sources.append(source)
    
    cursor.close()
    conn.close()
    
    # Generate summary for agent
    summary = generate_agent_summary(query, sources, dimension, category, min_authority)
    
    return {
        'sources': sources,
        'query_info': {
            'original_query': query,
            'keywords_extracted': keywords,
            'dimension_filter': dimension,
            'category_filter': category,
            'min_authority': min_authority,
            'results_count': len(sources)
        },
        'summary': summary
    }

def generate_agent_summary(
    query: str,
    sources: List[Dict],
    dimension: Optional[str],
    category: Optional[str],
    min_authority: int
) -> str:
    """
    Generate human-readable summary for AI agent to use in its response.
    This provides context about the knowledge sources found.
    """
    
    if not sources:
        return f"No sources found matching '{query}' with authority {min_authority}+."
    
    # Count by authority type
    official_count = sum(1 for s in sources if s['authority_score'] == 90)
    expert_count = sum(1 for s in sources if s['authority_score'] == 70)
    community_count = sum(1 for s in sources if s['authority_score'] == 50)
    
    # Build summary
    parts = [
        f"Found {len(sources)} authoritative sources for '{query}':"
    ]
    
    if official_count > 0:
        parts.append(f"- {official_count} official government sources (Authority 90)")
    if expert_count > 0:
        parts.append(f"- {expert_count} expert documentation sources (Authority 70)")
    if community_count > 0:
        parts.append(f"- {community_count} community resources (Authority 50)")
    
    if dimension:
        parts.append(f"\nFiltered to {dimension} dimension (epistemological focus)")
    
    if category:
        parts.append(f"Category: {category}")
    
    # List top 3 sources
    parts.append("\nTop sources:")
    for i, source in enumerate(sources[:3], 1):
        parts.append(
            f"{i}. {source['name']} (Authority {source['authority_score']}, {source['category']})"
        )
    
    return "\n".join(parts)

def format_for_agent_prompt(result: Dict) -> str:
    """
    Format query results as a string suitable for including in an AI agent's prompt.
    This gives the agent rich context to reference in its response.
    """
    
    sources = result['sources']
    if not sources:
        return "No relevant knowledge sources found in the database."
    
    output = ["📚 KNOWLEDGE BASE SOURCES:\n"]
    
    for i, source in enumerate(sources, 1):
        output.append(f"{i}. **{source['name']}**")
        output.append(f"   - Authority: {source['authority_score']} ({source['source_type'].upper()})")
        output.append(f"   - Category: {source['category']}")
        output.append(f"   - Dimension: {source['dimension'].upper()}")
        output.append(f"   - URL: {source['url']}")
        
        if source.get('description'):
            output.append(f"   - Description: {source['description']}")
        
        output.append("")  # Blank line
    
    output.append("\n💡 USAGE GUIDANCE:")
    output.append("- Official sources (90): Federal regulations, DoD standards - cite directly")
    output.append("- Expert sources (70): Technical documentation - reference as guidance")
    output.append("- Community sources (50): Open-source resources - validate before citing")
    output.append("\nAlways include source citations in your response with [Source: Name] format.")
    
    return "\n".join(output)

def main():
    """
    CLI interface for testing the knowledge query function.
    """
    
    if len(sys.argv) < 2:
        print("Usage: python3 query_knowledge_base.py \"your query\" [--dimension theory|practice|current] [--category CategoryName] [--min-authority 50|70|90]")
        print("\nExamples:")
        print('  python3 query_knowledge_base.py "FAR subcontracting requirements"')
        print('  python3 query_knowledge_base.py "NIST AI governance" --dimension theory')
        print('  python3 query_knowledge_base.py "cybersecurity threats" --category Cybersecurity --min-authority 90')
        sys.exit(1)
    
    # Parse arguments
    query = sys.argv[1]
    dimension = None
    category = None
    min_authority = 70
    
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == '--dimension' and i + 1 < len(sys.argv):
            dimension = sys.argv[i + 1]
        elif sys.argv[i] == '--category' and i + 1 < len(sys.argv):
            category = sys.argv[i + 1]
        elif sys.argv[i] == '--min-authority' and i + 1 < len(sys.argv):
            min_authority = int(sys.argv[i + 1])
    
    # Execute query
    result = query_knowledge_base(
        query=query,
        dimension=dimension,
        category=category,
        min_authority=min_authority,
        limit=5
    )
    
    # Display results
    print("\n" + "="*80)
    print("🔍 KNOWLEDGE BASE QUERY")
    print("="*80)
    print(f"\nQuery: {query}")
    print(f"Keywords: {', '.join(result['query_info']['keywords_extracted'])}")
    
    if dimension:
        print(f"Dimension: {dimension}")
    if category:
        print(f"Category: {category}")
    print(f"Min Authority: {min_authority}")
    
    print("\n" + "-"*80)
    print("📊 SUMMARY FOR AGENT")
    print("-"*80)
    print(result['summary'])
    
    print("\n" + "-"*80)
    print("📋 FORMATTED FOR AGENT PROMPT")
    print("-"*80)
    print(format_for_agent_prompt(result))
    
    print("\n" + "-"*80)
    print("🔧 RAW JSON OUTPUT")
    print("-"*80)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
