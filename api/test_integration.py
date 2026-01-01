#!/usr/bin/env python3
"""
Quick integration test for FreDeSa API endpoints
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_public_endpoints():
    """Test public endpoints that don't require auth"""
    print("🧪 Testing Public Endpoints...")
    
    # Root endpoint
    resp = requests.get(f"{API_BASE}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "FreDeSa AI Platform API"
    print("  ✅ Root endpoint: PASS")
    
    # Health check
    resp = requests.get(f"{API_BASE}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    print("  ✅ Health endpoint: PASS")

def test_authenticated_endpoints_without_token():
    """Test that authenticated endpoints properly reject requests without tokens"""
    print("\n🔒 Testing Authentication Protection...")
    
    endpoints = [
        "/api/user/profile",
        "/api/proposals",
        "/api/admin/users",
        "/api/admin/analytics"
    ]
    
    for endpoint in endpoints:
        resp = requests.get(f"{API_BASE}{endpoint}")
        assert resp.status_code in [401, 403], f"{endpoint} should reject unauthorized requests"
    
    print("  ✅ All protected endpoints require authentication: PASS")

def test_api_docs():
    """Test OpenAPI documentation is available"""
    print("\n📚 Testing API Documentation...")
    
    resp = requests.get(f"{API_BASE}/docs")
    assert resp.status_code == 200
    print("  ✅ Swagger UI available: PASS")
    
    resp = requests.get(f"{API_BASE}/openapi.json")
    assert resp.status_code == 200
    print("  ✅ OpenAPI spec available: PASS")

if __name__ == "__main__":
    print("=" * 60)
    print("FreDeSa AI Platform - Integration Test Suite")
    print("=" * 60)
    
    try:
        test_public_endpoints()
        test_authenticated_endpoints_without_token()
        test_api_docs()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Backend API is fully operational")
        print("✅ Authentication protection working")
        print("✅ API documentation available")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR: Backend server not running on port 8000")
        print("   Start with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
