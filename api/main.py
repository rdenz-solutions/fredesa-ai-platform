"""
FreDeSa AI Platform - FastAPI Backend
Enterprise-grade API with Azure AD authentication integration
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWKClient
import os

app = FastAPI(
    title="FreDeSa AI Platform API",
    description="Backend API for Federal Proposal Management",
    version="1.0.0"
)

# CORS Configuration - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "http://127.0.0.1:3000",  # Development alternative
        "https://fredesa-ai-platform.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure AD Configuration
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "19815b28-437b-405b-ade0-daea9943eb8b")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "257a158a-c6d6-4595-8dc3-df07e83504ac")
AZURE_AUDIENCE = os.getenv(
    "AZURE_AUDIENCE",
    "api://257a158a-c6d6-4595-8dc3-df07e83504ac",
)
AZURE_ISSUER = f"https://sts.windows.net/{AZURE_TENANT_ID}/"
AZURE_JWKS_URL = (
    f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"
)

security = HTTPBearer()

# Azure AD Token Validation
def get_jwks_client():
    """Get JWKS client for token validation"""
    return PyJWKClient(AZURE_JWKS_URL)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify Azure AD access token and return user claims
    """
    token = credentials.credentials
    
    try:
        # Decode without verification first to see what's in the token
        unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"[token-debug] Token issuer: {unverified.get('iss')}")
        print(f"[token-debug] Token audience: {unverified.get('aud')}")
        print(f"[token-debug] Expected issuer: {AZURE_ISSUER}")
        print(f"[token-debug] Expected audience: {AZURE_AUDIENCE}")
        
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=AZURE_AUDIENCE,
            issuer=AZURE_ISSUER,
            options={"verify_signature": True, "verify_exp": True, "verify_aud": True, "verify_iss": True}
        )
        
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        print("[token-error]", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_role(user_claims: Dict[str, Any]) -> str:
    """
    Extract user role from token claims
    """
    # Check for app roles assigned in Azure AD
    roles = user_claims.get("roles", [])
    
    if "FreDeSa_SuperAdmin" in roles:
        return "FreDeSa_SuperAdmin"
    elif "Customer_User" in roles:
        return "Customer_User"
    else:
        return "Customer_User"  # Default role

# ============================================================================
# PUBLIC ENDPOINTS (No Auth Required)
# ============================================================================

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "service": "FreDeSa AI Platform API",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "authentication": "azure-ad",
        "tenant_id": AZURE_TENANT_ID[:8] + "...",  # Partial for security
    }

# ============================================================================
# AUTHENTICATED ENDPOINTS
# ============================================================================

@app.get("/api/user/profile")
async def get_user_profile(user_claims: Dict = Depends(verify_token)):
    """
    Get current user profile information
    """
    return {
        "user_id": user_claims.get("oid"),
        "email": user_claims.get("preferred_username") or user_claims.get("email"),
        "name": user_claims.get("name"),
        "role": get_user_role(user_claims),
        "tenant_id": user_claims.get("tid"),
    }

@app.get("/api/proposals")
async def list_proposals(user_claims: Dict = Depends(verify_token)):
    """
    List all proposals for the authenticated user
    (Replace with real database queries)
    """
    user_role = get_user_role(user_claims)
    
    # Mock data - replace with database queries
    proposals = [
        {
            "id": "prop-001",
            "title": "Air Force Cyber Defense System",
            "agency": "US Air Force",
            "value": "$2.5M",
            "status": "draft",
            "due_date": "2026-03-15",
            "completion": 35
        },
        {
            "id": "prop-002",
            "title": "Navy AI-Driven Logistics Platform",
            "agency": "US Navy",
            "value": "$5.8M",
            "status": "in_review",
            "due_date": "2026-04-22",
            "completion": 68
        },
        {
            "id": "prop-003",
            "title": "Army Data Analytics Modernization",
            "agency": "US Army",
            "value": "$3.2M",
            "status": "submitted",
            "due_date": "2026-02-10",
            "completion": 100
        }
    ]
    
    return {
        "proposals": proposals,
        "total": len(proposals),
        "user_role": user_role
    }

@app.get("/api/proposals/{proposal_id}")
async def get_proposal(proposal_id: str, user_claims: Dict = Depends(verify_token)):
    """
    Get detailed information about a specific proposal
    """
    # Mock data - replace with database query
    proposal = {
        "id": proposal_id,
        "title": "Air Force Cyber Defense System",
        "agency": "US Air Force",
        "contract_type": "Firm Fixed Price",
        "value": "$2.5M",
        "status": "draft",
        "due_date": "2026-03-15",
        "completion": 35,
        "sections": [
            {"name": "Executive Summary", "status": "complete", "word_count": 850},
            {"name": "Technical Approach", "status": "in_progress", "word_count": 1200},
            {"name": "Management Plan", "status": "not_started", "word_count": 0},
            {"name": "Past Performance", "status": "complete", "word_count": 950},
        ],
        "team": [
            {"name": "John Smith", "role": "Proposal Manager"},
            {"name": "Jane Doe", "role": "Technical Lead"},
        ],
        "created_by": user_claims.get("name"),
        "created_at": "2025-12-20T10:30:00Z"
    }
    
    return proposal

# ============================================================================
# ADMIN-ONLY ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def list_users(user_claims: Dict = Depends(verify_token)):
    """
    Admin-only: List all users in the system
    """
    user_role = get_user_role(user_claims)
    
    if user_role != "FreDeSa_SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Mock data - replace with database query
    users = [
        {
            "id": "user-001",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "role": "FreDeSa_SuperAdmin",
            "status": "active",
            "last_login": "2025-12-31T08:15:00Z"
        },
        {
            "id": "user-002",
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "role": "Customer_User",
            "status": "active",
            "last_login": "2025-12-30T14:22:00Z"
        }
    ]
    
    return {
        "users": users,
        "total": len(users)
    }

@app.get("/api/admin/analytics")
async def get_analytics(user_claims: Dict = Depends(verify_token)):
    """
    Admin-only: Platform analytics and metrics
    """
    user_role = get_user_role(user_claims)
    
    if user_role != "FreDeSa_SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "total_proposals": 47,
        "active_users": 23,
        "proposals_this_month": 8,
        "avg_completion_rate": 72,
        "total_contract_value": "$85.3M",
        "win_rate": 68,
    }

# ============================================================================
# KNOWLEDGE REGISTRY ENDPOINTS
# ============================================================================

@app.get("/api/knowledge/stats")
async def get_knowledge_stats(user_claims: Dict = Depends(verify_token)):
    """
    Get statistics about the knowledge registry
    """
    # Mock data - replace with actual database queries
    return {
        "total_sources": 1043,
        "by_authority": {
            "official_government": 180,  # Authority 90
            "expert_documentation": 592,  # Authority 70
            "community_resources": 271    # Authority 50
        },
        "by_dimension": {
            "theory": 287,
            "practice": 456,
            "history": 189,
            "current": 523,
            "future": 95
        },
        "by_category": {
            "Federal_Contracting": 245,
            "AI_ML": 198,
            "Cybersecurity": 167,
            "Intelligence": 143,
            "Cloud_Infrastructure": 134,
            "Other": 156
        },
        "top_sources": [
            {"name": "Federal Acquisition Regulation (FAR)", "authority": 90, "category": "Federal_Contracting"},
            {"name": "Defense Federal Acquisition Regulation (DFARS)", "authority": 90, "category": "Federal_Contracting"},
            {"name": "NIST AI Framework", "authority": 90, "category": "AI_ML"},
            {"name": "CMMC 2.0 Model", "authority": 90, "category": "Cybersecurity"},
            {"name": "AWS Well-Architected Framework", "authority": 70, "category": "Cloud_Infrastructure"}
        ]
    }

@app.get("/api/knowledge/search")
async def search_knowledge(
    query: str,
    dimension: str = None,
    category: str = None,
    min_authority: int = 70,
    limit: int = 10,
    user_claims: Dict = Depends(verify_token)
):
    """
    Search the knowledge registry
    """
    # Mock data - replace with actual query_knowledge_base call
    mock_sources = [
        {
            "name": "Federal Acquisition Regulation Part 19: Small Business Programs",
            "url": "https://www.acquisition.gov/far/part-19",
            "description": "Comprehensive guidance on small business subcontracting requirements and compliance",
            "dimension": "practice",
            "difficulty": "intermediate",
            "source_type": "government",
            "authority_score": 90,
            "quality_score": 95.0,
            "category": "Federal_Contracting"
        },
        {
            "name": "NIST Cybersecurity Framework 2.0",
            "url": "https://www.nist.gov/cyberframework",
            "description": "Industry standard for managing cybersecurity risks",
            "dimension": "practice",
            "difficulty": "intermediate",
            "source_type": "government",
            "authority_score": 90,
            "quality_score": 94.0,
            "category": "Cybersecurity"
        },
        {
            "name": "DoD Cloud Computing Security Requirements Guide",
            "url": "https://public.cyber.mil/dccs/",
            "description": "Security requirements for cloud service providers working with DoD",
            "dimension": "practice",
            "difficulty": "advanced",
            "source_type": "government",
            "authority_score": 90,
            "quality_score": 92.0,
            "category": "Cloud_Infrastructure"
        }
    ]
    
    return {
        "sources": mock_sources[:limit],
        "query_info": {
            "original_query": query,
            "dimension_filter": dimension,
            "category_filter": category,
            "min_authority": min_authority,
            "results_count": len(mock_sources[:limit])
        },
        "total_count": len(mock_sources)
    }

@app.get("/api/knowledge/categories")
async def get_categories(user_claims: Dict = Depends(verify_token)):
    """
    Get all knowledge categories
    """
    return {
        "categories": [
            {"id": "Federal_Contracting", "name": "Federal Contracting", "count": 245},
            {"id": "AI_ML", "name": "AI & Machine Learning", "count": 198},
            {"id": "Cybersecurity", "name": "Cybersecurity", "count": 167},
            {"id": "Intelligence", "name": "Intelligence Community", "count": 143},
            {"id": "Cloud_Infrastructure", "name": "Cloud Infrastructure", "count": 134},
            {"id": "DevOps", "name": "DevOps & CI/CD", "count": 89},
            {"id": "Data_Science", "name": "Data Science", "count": 67}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
