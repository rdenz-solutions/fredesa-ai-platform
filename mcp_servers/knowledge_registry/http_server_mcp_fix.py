"""
MCP Protocol Implementation for Airia Gateway
Based on MCP Specification 2025-03-26 - Streamable HTTP Transport
"""

# Add this POST endpoint to http_server.py (alongside existing GET)

MCP_POST_HANDLER = '''
@app.post("/mcp/sse")
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP Streamable HTTP endpoint.
    Handles JSON-RPC 2.0 messages: initialize, tools/list, tools/call
    """
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "initialize":
            # Return server capabilities per MCP spec
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "fredesa-knowledge-registry",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            # Return available tools with JSON Schema
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "query_knowledge_base",
                            "description": "Search 1,043 authoritative federal contracting sources with epistemological filtering. Returns sources with authority scores (90=official, 70=expert, 50=community).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query (e.g., 'FAR Part 15', 'DFARS cybersecurity')"
                                    },
                                    "dimension": {
                                        "type": "string",
                                        "enum": ["theory", "practice", "history", "current", "future"],
                                        "description": "Epistemological dimension to filter by"
                                    },
                                    "category": {
                                        "type": "string",
                                        "description": "Knowledge category (e.g., 'Federal_Contracting', 'Cybersecurity')"
                                    },
                                    "min_authority": {
                                        "type": "integer",
                                        "minimum": 50,
                                        "maximum": 90,
                                        "default": 50,
                                        "description": "Minimum authority score (50-90)"
                                    },
                                    "max_results": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 15,
                                        "default": 10,
                                        "description": "Maximum results to return"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "get_source_details",
                            "description": "Get full metadata for a specific knowledge source by UUID.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_id": {
                                        "type": "string",
                                        "description": "UUID of the source"
                                    }
                                },
                                "required": ["source_id"]
                            }
                        },
                        {
                            "name": "list_categories",
                            "description": "List all available knowledge categories with source counts.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            })
        
        elif method == "tools/call":
            # Execute tool and return result
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                if tool_name == "query_knowledge_base":
                    result = db.query_knowledge_base(**arguments)
                elif tool_name == "get_source_details":
                    result = db.get_source_details(**arguments)
                elif tool_name == "list_categories":
                    result = db.list_categories()
                else:
                    return JSONResponse(content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }, status_code=400)
                
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2, default=str)
                            }
                        ]
                    }
                })
                
            except Exception as e:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }, status_code=500)
        
        elif method == "notifications/initialized":
            # Client acknowledgment - return 202 Accepted
            return Response(status_code=202)
        
        else:
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }, status_code=400)
            
    except json.JSONDecodeError:
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }, status_code=400)
    except Exception as e:
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)
'''

print("MCP POST Handler Ready")
print("This implements JSON-RPC 2.0 over HTTP per MCP Specification 2025-03-26")
