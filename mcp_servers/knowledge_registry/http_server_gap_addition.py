# Add after line 317 (after @app.get("/tools/list_categories"))

class GapDetectionRequest(BaseModel):
    query: str
    keywords: list = []
    customer_id: str = None
    context: str = None

@app.post("/tools/detect_knowledge_gap")
async def detect_knowledge_gap(request: GapDetectionRequest):
    """
    Detect knowledge gaps and handle according to environment.
    Development: Enable auto-ingestion workflow
    Production: Log gap, notify development team, return safe message
    """
    try:
        # Import gap manager (lazy load to avoid startup dependency)
        import sys
        from pathlib import Path
        
        # Add scripts to path if not already there
        scripts_path = Path(__file__).parent.parent.parent / "scripts" / "automation"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
        
        from knowledge_gap_manager import KnowledgeGapManager
        
        # Initialize gap manager (reads ENVIRONMENT from env vars)
        gap_manager = KnowledgeGapManager()
        
        # Detect gap
        result = gap_manager.detect_gap(
            query=request.query,
            keywords=request.keywords,
            customer_id=request.customer_id,
            context=request.context or f"MCP request from {request.customer_id}"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap detection error: {str(e)}")

