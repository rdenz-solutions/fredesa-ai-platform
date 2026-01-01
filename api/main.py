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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
