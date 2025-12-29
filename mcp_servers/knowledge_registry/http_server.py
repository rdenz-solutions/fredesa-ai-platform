#!/usr/bin/env python3
"""
HTTP/SSE wrapper for FreDeSa Knowledge Registry MCP Server
Exposes MCP tools via REST API for Airia Gateway integration
"""

import os
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import MCP server logic
from server import KnowledgeRegistryServer

app = FastAPI(
    title="FreDeSa Knowledge Registry MCP Server",
    description="1,043 authoritative sources with epistemological framework",
    version="1.0.0"
)

# CORS for Airia Gateway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Airia Gateway domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize server
server = KnowledgeRegistryServer()

# Request models
class QueryRequest(BaseModel):
    query: str
    dimension: str = None
    category: str = None
    min_authority: int = 50
    max_results: int = 10

class SourceDetailsRequest(BaseModel):
    source_id: str

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        conn = server.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

# MCP tools endpoints
@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "query_knowledge_base",
                "description": "Search 1,043 authoritative sources with epistemological filtering",
                "parameters": {
                    "query": "string (required)",
                    "dimension": "string (optional): theory/practice/history/current/future",
                    "category": "string (optional): Federal_Contracting, Cybersecurity, etc.",
                    "min_authority": "integer (50-90, default: 50)",
                    "max_results": "integer (1-15, default: 10)"
                }
            },
            {
                "name": "get_source_details",
                "description": "Get full metadata for a specific source",
                "parameters": {
                    "source_id": "string (required): UUID of the source"
                }
            },
            {
                "name": "list_categories",
                "description": "List all available knowledge categories",
                "parameters": {}
            }
        ]
    }

@app.post("/tools/query_knowledge_base")
async def query_knowledge_base(request: QueryRequest):
    """Query the knowledge base."""
    try:
        result = server.query_knowledge_base(
            query=request.query,
            dimension=request.dimension,
            category=request.category,
            min_authority=request.min_authority,
            max_results=request.max_results
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/get_source_details")
async def get_source_details(request: SourceDetailsRequest):
    """Get source details."""
    try:
        result = server.get_source_details(request.source_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/list_categories")
async def list_categories():
    """List all categories."""
    try:
        result = server.list_categories()
        return {"categories": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SSE endpoint for MCP protocol
@app.get("/mcp/sse")
async def mcp_sse(authorization: str = Header(None)):
    """Server-Sent Events endpoint for MCP protocol."""
    async def event_generator():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'server': 'fredesa-knowledge-registry'})}\n\n"
        
        # Keep connection alive
        while True:
            import asyncio
            await asyncio.sleep(30)
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Stats endpoint
@app.get("/stats")
async def get_stats():
    """Get knowledge base statistics."""
    try:
        conn = server.get_connection()
        cur = conn.cursor()
        
        # Get total sources
        cur.execute("SELECT COUNT(*) FROM sources")
        total_sources = cur.fetchone()[0]
        
        # Get by authority
        cur.execute("""
            SELECT authority_score, COUNT(*) 
            FROM sources 
            GROUP BY authority_score 
            ORDER BY authority_score DESC
        """)
        authority_breakdown = {row[0]: row[1] for row in cur.fetchall()}
        
        # Get by dimension
        cur.execute("""
            SELECT epistemological_dimension, COUNT(*) 
            FROM sources 
            GROUP BY epistemological_dimension
        """)
        dimension_breakdown = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        return {
            "total_sources": total_sources,
            "authority_breakdown": authority_breakdown,
            "dimension_breakdown": dimension_breakdown,
            "categories": len(server.list_categories())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
