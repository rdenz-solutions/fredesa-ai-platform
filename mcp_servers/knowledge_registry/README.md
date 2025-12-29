# FreDeSa Knowledge Registry MCP Server

## Overview
Provides AI agents with access to 1,043 authoritative sources from the FreDeSa Knowledge Registry via Model Context Protocol (MCP).

## Features
- **1,043 Authoritative Sources**: FAR, DFARS, NIST, DoD standards, AI/LLM frameworks, cybersecurity
- **Epistemological Framework**: Filter by theory/practice/history/current/future dimensions
- **Authority Scoring**: 90 (official), 70 (expert), 50 (community)
- **43 Categories**: Federal contracting, cybersecurity, intelligence, standards, methodologies, and more
- **Semantic Search**: Natural language queries with keyword extraction

## Tools Provided

### 1. query_knowledge_base
Search the knowledge base with advanced filtering.

**Parameters:**
- `query` (required): Natural language search query
- `dimension` (optional): Filter by epistemological dimension (theory/practice/history/current/future)
- `category` (optional): Filter by category name
- `min_authority` (optional): Minimum authority score (50-90), default: 50
- `max_results` (optional): Maximum results (1-15), default: 10

**Example:**
```json
{
  "query": "FAR subcontracting plan requirements",
  "dimension": "practice",
  "min_authority": 90,
  "max_results": 5
}
```

### 2. get_source_details
Retrieve full metadata for a specific source.

**Parameters:**
- `source_id` (required): UUID of the source

### 3. list_categories
Get all available knowledge categories with source counts.

**Returns:** List of categories with epistemological dimension breakdowns.

## Deployment to Airia Gateway

### Prerequisites
1. Airia account with Gateway access
2. Azure PostgreSQL database (fredesa-db-dev) deployed
3. PostgreSQL password stored in secrets

### Steps

1. **Package the MCP server:**
```bash
cd mcp_servers/knowledge_registry
zip -r knowledge-registry-mcp.zip .
```

2. **Upload to Airia Gateway:**
   - Navigate to Airia Gateway dashboard
   - Click "Deploy New MCP Server"
   - Upload `knowledge-registry-mcp.zip`
   - Configure environment variables (auto-loaded from mcp.json)
   - Add secret: `POSTGRES_PASSWORD` = [your password]

3. **Register in Project:**
   - Go to your Airia project settings
   - Navigate to "Tools" section
   - Click "Add MCP Tool"
   - Select "FreDeSa Knowledge Registry"
   - Configure rate limits per tier

4. **Use in Agents:**
   - Add tool to AIOperation steps
   - Agent can now call `query_knowledge_base()` during conversation
   - Results automatically injected into agent context

## Environment Variables

Required in Airia Gateway:
- `POSTGRES_HOST`: fredesa-db-dev.postgres.database.azure.com
- `POSTGRES_DB`: postgres
- `POSTGRES_USER`: fredesaadmin
- `POSTGRES_PASSWORD`: [SECRET - from Azure Key Vault]
- `POSTGRES_SSLMODE`: require
- `AZURE_KEYVAULT_URL`: https://fredesa-kv-e997e3.vault.azure.net/

## Rate Limits

Default limits (configurable per customer tier):
- `query_knowledge_base`: 100 queries/day
- `get_source_details`: 1,000 queries/day
- `list_categories`: 100 queries/day

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_PASSWORD="your-password"

# Run server
python3 server.py
```

## Security Features

✅ **Implemented:**
- SSL-only database connections
- Azure Key Vault credential retrieval
- Hard limit on max_results (15 sources max)
- Read-only database access
- Parameterized SQL queries (SQL injection prevention)

⏳ **Coming Soon:**
- Row-Level Security (RLS) for multi-tenant isolation
- Redis-based rate limiting per API key
- Audit logging to Azure Application Insights
- Content watermarking for ingested documents

## Architecture

```
Airia Agent → Airia Gateway → MCP Server → Azure PostgreSQL
                                    ↓
                            Azure Key Vault (credentials)
```

## Support

For issues or questions:
- Email: support@fredesa.com
- Docs: https://docs.fredesa.com/knowledge-registry
