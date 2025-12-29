# MCP Server Deployment Status
**Updated:** December 29, 2025

## 🎯 Mission
Deploy FreDeSa Knowledge Registry MCP server to Azure Container Apps for Airia Gateway integration.

## ✅ Completed

### 1. Test Agent Deployment
- **Agent ID:** 8800c4f0-1cdd-4ba2-aa05-8df35d986d72
- **Project:** Intel MCP Demo (019b61fe-3fba-716f-b0aa-8bdff5004898)
- **Model:** GPT-4o mini (cost-optimized)
- **Status:** Deployed successfully, but only uses LLM training data (no real KR access)

### 2. MCP Server Development
- **File:** `mcp_servers/knowledge_registry/server.py` (390 lines)
- **Tools Provided:**
  1. `query_knowledge_base` - Search 1,043 sources with filters
  2. `get_source_details` - Individual source metadata lookup
  3. `list_categories` - Category enumeration with stats
- **Database:** Azure PostgreSQL (fredesa-db-dev.postgres.database.azure.com)
- **Security:** Azure Key Vault for credentials
- **Test Results:** ✅ Local test successful (5 FAR sources returned)

### 3. HTTP/SSE Wrapper
- **File:** `mcp_servers/knowledge_registry/http_server.py` (180 lines)
- **Framework:** FastAPI with Uvicorn
- **Endpoints:**
  - `/health` - Database connection check ✅ TESTED
  - `/tools` - List available tools ✅ TESTED
  - `/tools/query_knowledge_base` - Search endpoint ✅ TESTED
  - `/tools/get_source_details` - Details endpoint
  - `/tools/list_categories` - Categories endpoint
  - `/mcp/sse` - Server-Sent Events for Airia
  - `/stats` - Knowledge base statistics (minor bug)

### 4. Containerization
- **File:** `mcp_servers/knowledge_registry/Dockerfile`
- **Base Image:** python:3.11-slim
- **Dependencies:** PostgreSQL client, FastAPI, Azure SDKs
- **Port:** 8000 (8001 for local testing)
- **Status:** ✅ Complete

### 5. Azure Deployment Script
- **File:** `mcp_servers/knowledge_registry/deploy_azure.sh`
- **Features:**
  - Automated ACR build and push
  - Container Apps deployment with auto-scaling (1-3 replicas)
  - Environment variables for PostgreSQL
  - Key Vault secret injection
  - Public URL output
- **Status:** ✅ Script ready

## 🔄 In Progress

### Azure Provider Registration
**Status:** Registering (2-3 minutes)
- ⏳ Microsoft.ContainerRegistry
- ⏳ Microsoft.App
- ⏳ Microsoft.OperationalInsights

**Once complete, run:**
```bash
cd mcp_servers/knowledge_registry
./deploy_azure.sh
```

## 📋 Next Steps

### 1. Complete Azure Deployment (15 minutes)
- Wait for provider registration
- Run `./deploy_azure.sh`
- Verify health endpoint
- Test query endpoint
- Get public URL: `https://fredesa-mcp-server.*.azurecontainerapps.io`

### 2. Register in Airia Gateway (5 minutes)
- Navigate to Custom MCP Server dialog (user has open)
- Paste URL: `https://fredesa-mcp-server.*.azurecontainerapps.io/mcp/sse`
- Configure authentication (if needed)
- Verify 3 tools appear in project

### 3. Attach to Test Agent (5 minutes)
- Open agent 8800c4f0-1cdd-4ba2-aa05-8df35d986d72
- Add MCP tool to AIOperation step
- Select `query_knowledge_base` tool
- Save configuration

### 4. Test Knowledge Queries (10 minutes)
**Test queries:**
- "What are FAR Part 15 requirements for contracting by negotiation?"
- "Explain DFARS cybersecurity compliance requirements"
- "List all sources about small business subcontracting programs"

**Expected behavior:**
- Agent calls MCP server via Airia Gateway
- PostgreSQL query executes with epistemological filtering
- Authoritative sources returned (Authority 90+)
- Agent synthesizes response using real knowledge

### 5. Security Implementation (Deferred - 2-3 hours)
- Rate limiting (Redis, 100 queries/day)
- Audit logging (Application Insights)
- Row-Level Security (RLS) for multi-tenancy
- Content watermarking
- Access token authentication

## 🧪 Test Results

### Local HTTP Server Tests
```bash
# Health check
curl http://localhost:8001/health
{"status": "healthy", "database": "connected"}

# Query test
curl -X POST http://localhost:8001/tools/query_knowledge_base \
  -H "Content-Type: application/json" \
  -d '{"query": "FAR subcontracting", "min_authority": 90, "max_results": 3}'

# Results: 3 sources returned
- DFARS (Authority 90, theory, quality 98.6)
- FAR Subpart 31.2 (Authority 90, practice, quality 98.6)
- FAR Part 15 (Authority 90, theory, quality 98.6)
```

## 🏗️ Architecture

```
[Airia Agent] 
    ↓ HTTP/SSE
[Airia Gateway]
    ↓ HTTPS
[Azure Container Apps - MCP Server]
    ↓ Port 8000
[FastAPI (http_server.py)]
    ↓ Python
[MCP Server (server.py)]
    ↓ PostgreSQL SSL
[Azure PostgreSQL]
    ↓ Key Vault
[Azure Key Vault - Secrets]
```

## 📊 Knowledge Base Stats
- **Total Sources:** 1,043
- **Categories:** 37
- **Authority Breakdown:**
  - Official (90): Government docs, regulations
  - Expert (70): Expert guides, best practices
  - Community (50): Open source, community docs
- **Epistemological Dimensions:**
  - Theory (foundational knowledge)
  - Practice (applied knowledge)
  - History (past context)
  - Current (present state)
  - Future (emerging trends)

## 🔗 Resources
- **GitHub Commit:** 79fe9fa (HTTP server + deployment)
- **Previous Commit:** 715b62f (MCP server core)
- **Resource Group:** rg-fredesa-dev
- **Region:** East US
- **Project:** https://airia.ai/019b61fe-3fba-716f-b0aa-8bdff5004898

## 🚨 Known Issues
1. `/stats` endpoint has minor bug (count logic) - non-blocking
2. Azure provider registration required before first deployment
3. Port 8000 in use locally (using 8001 for testing)

## 💡 Key Learnings
1. Test agent only uses LLM training data without database connection
2. Airia Gateway requires HTTP/SSE, not stdio protocol
3. MCP tools must be registered and attached to agents
4. Epistemological filtering provides valuable context dimension
5. Authority scores (90/70/50) enable quality filtering
6. FastAPI provides clean REST API for MCP tools
7. Azure Container Apps ideal for auto-scaling MCP servers
