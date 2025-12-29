#!/usr/bin/env python3
"""
FreDeSa Knowledge Registry MCP Server (Airia Gateway Compatible)
=================================================================
Provides AI agents with access to 1,043 authoritative sources via PostgreSQL.

Airia Gateway Deployment:
- Upload this directory to Airia Gateway
- Configure PostgreSQL connection via environment variables
- Register as tool in Airia projects

Tools Provided:
- query_knowledge_base: Search sources by query, dimension, category, authority
- get_source_details: Retrieve full metadata for specific source
- list_categories: Get available knowledge categories
"""

import json
import os
import sys
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# MCP Protocol imports (Airia Gateway provides these)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("⚠️  MCP SDK not available - install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


class KnowledgeRegistryServer:
    """MCP server for FreDeSa Knowledge Registry."""
    
    def __init__(self):
        self.db_host = os.getenv("POSTGRES_HOST", "fredesa-db-dev.postgres.database.azure.com")
        self.db_name = os.getenv("POSTGRES_DB", "postgres")
        self.db_user = os.getenv("POSTGRES_USER", "fredesaadmin")
        self.db_password = os.getenv("POSTGRES_PASSWORD")
        self.db_sslmode = os.getenv("POSTGRES_SSLMODE", "require")
        
        if not self.db_password:
            # Try Azure Key Vault if available
            try:
                from azure.identity import DefaultAzureCredential
                from azure.keyvault.secrets import SecretClient
                
                vault_url = os.getenv("AZURE_KEYVAULT_URL", "https://fredesa-kv-e997e3.vault.azure.net/")
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
        authority_breakdown = {}
        for s in sources:
            auth = s['authority_score']
            authority_breakdown[auth] = authority_breakdown.get(auth, 0) + 1
        
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


# Initialize MCP server
app = Server("fredesa-knowledge-registry")
server = KnowledgeRegistryServer()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="query_knowledge_base",
            description="Search the FreDeSa knowledge base with 1,043 authoritative sources. "
                       "Supports filtering by epistemological dimension (theory/practice/current), "
                       "category (Federal_Contracting, Cybersecurity, etc.), and authority score "
                       "(90=official, 70=expert, 50=community). Returns sources with citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g., 'FAR subcontracting requirements')"
                    },
                    "dimension": {
                        "type": "string",
                        "enum": ["theory", "practice", "history", "current", "future"],
                        "description": "Optional: Filter by epistemological dimension"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional: Filter by category name (use list_categories to see options)"
                    },
                    "min_authority": {
                        "type": "integer",
                        "default": 50,
                        "minimum": 50,
                        "maximum": 90,
                        "description": "Minimum authority score: 50 (community), 70 (expert), 90 (official)"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "maximum": 15,
                        "description": "Maximum number of results to return"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_source_details",
            description="Retrieve full metadata for a specific knowledge source by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "UUID of the source to retrieve"
                    }
                },
                "required": ["source_id"]
            }
        ),
        Tool(
            name="list_categories",
            description="Get list of all available knowledge categories with source counts and "
                       "epistemological dimension breakdowns.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "query_knowledge_base":
            result = server.query_knowledge_base(**arguments)
        elif name == "get_source_details":
            result = server.get_source_details(**arguments)
        elif name == "list_categories":
            result = server.list_categories()
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
