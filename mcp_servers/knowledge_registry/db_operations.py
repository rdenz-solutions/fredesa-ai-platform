#!/usr/bin/env python3
"""
Database operations for FreDeSa Knowledge Registry
Pure PostgreSQL functions without MCP SDK dependencies
"""

import os
import sys
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class KnowledgeRegistryDB:
    """Database operations for knowledge registry."""
    
    def __init__(self):
        """Initialize database connection parameters."""
        self.db_host = os.getenv("POSTGRES_HOST", "fredesa-db-dev.postgres.database.azure.com")
        self.db_port = os.getenv("POSTGRES_PORT", "5432")
        self.db_name = os.getenv("POSTGRES_DB", "postgres")
        self.db_user = os.getenv("POSTGRES_USER", "fredesaadmin")
        self.db_password = os.getenv("POSTGRES_PASSWORD")
        self.db_sslmode = os.getenv("POSTGRES_SSLMODE", "require")
        
        if not self.db_password:
            # Try Azure Key Vault if available
            try:
                from azure.identity import DefaultAzureCredential
                from azure.keyvault.secrets import SecretClient
                
                vault_name = os.getenv("AZURE_KEY_VAULT_NAME", "fredesa-kv-e997e3")
                vault_url = f"https://{vault_name}.vault.azure.net/"
                credential = DefaultAzureCredential()
                client = SecretClient(vault_url=vault_url, credential=credential)
                self.db_password = client.get_secret("postgres-password").value
            except Exception as e:
                print(f"⚠️  Could not load password from Key Vault: {e}", file=sys.stderr)
    
    def get_connection(self):
        """Get PostgreSQL database connection."""
        return psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            sslmode=self.db_sslmode,
            cursor_factory=RealDictCursor
        )
    
    def query_knowledge_base(
        self,
        query: str,
        dimension: Optional[str] = None,
        category: Optional[str] = None,
        min_authority: int = 50,
        max_results: int = 10
    ) -> Dict:
        """
        Search knowledge base with epistemological filtering.
        
        Args:
            query: Natural language search query
            dimension: Filter by epistemological dimension (theory/practice/history/current/future)
            category: Filter by category name (e.g., "Federal_Contracting", "Cybersecurity")
            min_authority: Minimum authority score (50=community, 70=expert, 90=official)
            max_results: Maximum number of results (hard limit: 15)
        
        Returns:
            Dict with sources, query_info, and summary
        """
        # Security: hard limit on results
        max_results = min(max_results, 15)
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        conn = self.get_connection()
        cur = conn.cursor()
        
        # Build WHERE clauses
        where_clauses = []
        params = []
        
        # Authority filter
        where_clauses.append("s.authority_score >= %s")
        params.append(min_authority)
        
        # Dimension filter
        if dimension:
            valid_dimensions = ['theory', 'practice', 'history', 'current', 'future']
            if dimension.lower() in valid_dimensions:
                where_clauses.append(f"s.epistemological_dimension = %s")
                params.append(dimension.lower())
        
        # Category filter
        if category:
            where_clauses.append("c.name = %s OR c.display_name = %s")
            params.extend([category, category])
        
        # Keyword matching
        if keywords:
            keyword_conditions = []
            for kw in keywords:
                keyword_conditions.append(
                    "(LOWER(s.name) LIKE %s OR LOWER(s.description) LIKE %s OR LOWER(c.name) LIKE %s)"
                )
                params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
            where_clauses.append(f"({' OR '.join(keyword_conditions)})")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query_sql = f"""
            SELECT 
                s.id,
                s.name,
                s.description,
                s.url,
                s.authority_score,
                s.epistemological_dimension,
                s.quality_score,
                c.name as category_name,
                c.display_name as category_display
            FROM sources s
            JOIN categories c ON s.category_id = c.id
            WHERE {where_sql}
            ORDER BY s.authority_score DESC, s.quality_score DESC
            LIMIT %s
        """
        params.append(max_results)
        
        cur.execute(query_sql, params)
        results = cur.fetchall()
        
        # Format response
        sources = []
        for row in results:
            sources.append({
                "id": str(row['id']),
                "name": row['name'],
                "description": row['description'],
                "url": row['url'],
                "authority_score": int(row['authority_score']),
                "epistemological_dimension": row['epistemological_dimension'],
                "quality_score": float(row['quality_score']) if row['quality_score'] else 0.0,
                "category": row['category_display'] or row['category_name']
            })
        
        cur.close()
        conn.close()
        
        # Generate summary
        summary = f"Found {len(sources)} sources"
        if dimension:
            summary += f" in {dimension} dimension"
        if category:
            summary += f" from {category}"
        
        return {
            "sources": sources,
            "query_info": {
                "keywords": keywords,
                "dimension": dimension,
                "category": category,
                "min_authority": min_authority,
                "results_count": len(sources)
            },
            "summary": summary
        }
    
    def get_source_details(self, source_id: str) -> Dict:
        """Get full details for a specific source."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                s.*,
                c.name as category_name,
                c.display_name as category_display
            FROM sources s
            JOIN categories c ON s.category_id = c.id
            WHERE s.id = %s
        """, (source_id,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            return {"error": f"Source {source_id} not found"}
        
        return dict(result)
    
    def list_categories(self) -> List[Dict]:
        """Get list of all available categories with source counts."""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                c.name,
                c.display_name,
                c.description,
                c.total_sources,
                c.theory_sources,
                c.practice_sources,
                c.current_sources
            FROM categories c
            WHERE c.total_sources > 0
            ORDER BY c.total_sources DESC
        """)
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(row) for row in results]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query."""
        import re
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
                      'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'should', 'could', 'may', 'might', 'can', 'what', 'how',
                      'when', 'where', 'who', 'which', 'this', 'that', 'these', 'those'}
        
        # Tokenize
        words = re.findall(r'\b[a-z]{3,}\b', query.lower())
        
        # Filter
        keywords = [w for w in words if w not in stop_words]
        
        return keywords[:5]  # Limit to 5 keywords
