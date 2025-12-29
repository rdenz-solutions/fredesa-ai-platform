"""
Fix for http_server.py SSE endpoint to implement proper MCP protocol.

The MCP protocol over SSE expects:
1. Client sends POST to /mcp/sse with initialize request
2. Server responds with capabilities and tool list
3. Client can then invoke tools via POST requests

We need to convert from simple ping SSE to actual MCP message handling.
"""

MCP_SSE_HANDLER = '''
@app.post("/mcp/sse")
async def mcp_sse_init(request: Request):
    """Handle MCP protocol initialization over SSE."""
    try:
        body = await request.json()
        method = body.get("method")
        
        if method == "initialize":
            # Return MCP initialization response
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "fredesa-knowledge-registry",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
        
        elif method == "tools/list":
            # Return tool list in MCP format
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "query_knowledge_base",
                            "description": "Search 1,043 authoritative sources with epistemological filtering",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search query"},
                                    "dimension": {"type": "string", "description": "theory/practice/history/current/future"},
                                    "category": {"type": "string", "description": "Knowledge category"},
                                    "min_authority": {"type": "integer", "description": "Minimum authority score (50-90)", "default": 50},
                                    "max_results": {"type": "integer", "description": "Max results (1-15)", "default": 10}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "get_source_details",
                            "description": "Get full metadata for a specific source",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_id": {"type": "string", "description": "UUID of the source"}
                                },
                                "required": ["source_id"]
                            }
                        },
                        {
                            "name": "list_categories",
                            "description": "List all available knowledge categories",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            # Execute tool in MCP format
            tool_name = body.get("params", {}).get("name")
            arguments = body.get("params", {}).get("arguments", {})
            
            if tool_name == "query_knowledge_base":
                result = db.query_knowledge_base(**arguments)
            elif tool_name == "get_source_details":
                result = db.get_source_details(**arguments)
            elif tool_name == "list_categories":
                result = db.list_categories()
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", None),
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }
'''

print("MCP Protocol Fix Ready")
print("Replace the @app.get('/mcp/sse') endpoint in http_server.py with the POST handler above")
