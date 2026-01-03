#!/usr/bin/env python3
"""
Setup FreDeSa Test Environment using Azure REST APIs directly
Uses browser-based authentication to get access token
"""

import requests
import json
import sys
import time
from pathlib import Path

# Configuration
SUBSCRIPTION_ID = "00c89d3e-e58f-456b-bba1-bbf04c3a3b2c"
RESOURCE_GROUP = "fredesa-rg"
LOCATION = "eastus"
POSTGRES_TEST_SERVER = "fredesa-db-test"

def get_access_token():
    """Get Azure access token interactively"""
    print("🔐 Getting Azure access token...")
    print("Please provide your Azure access token:")
    print("\n1. Go to https://portal.azure.com")
    print("2. Open browser Developer Tools (F12)")
    print("3. Go to Console tab")
    print("4. Paste this and press Enter:")
    print("\n   copy(JSON.parse(sessionStorage.getItem('msal.acquireTokenAccountResponse')).accessToken)\n")
    print("5. Paste the copied token below:")
    
    token = input("\nAccess Token: ").strip()
    
    if not token or len(token) < 100:
        print("❌ Invalid token")
        sys.exit(1)
    
    return token

def check_resource_group(token):
    """Check if resource group exists"""
    url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}/resourcegroups/{RESOURCE_GROUP}?api-version=2021-04-01"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Resource group '{RESOURCE_GROUP}' exists")
        print(f"   Location: {data['location']}")
        return True
    elif response.status_code == 404:
        print(f"❌ Resource group '{RESOURCE_GROUP}' not found")
        return False
    else:
        print(f"❌ Error checking resource group: {response.status_code}")
        print(response.text)
        return False

def list_postgres_servers(token):
    """List PostgreSQL servers in resource group"""
    url = f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.DBforPostgreSQL/flexibleServers?api-version=2022-12-01"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        servers = response.json().get('value', [])
        return servers
    else:
        print(f"⚠️  Could not list servers: {response.status_code}")
        return []

def main():
    """Main setup function"""
    
    print("🚀 FreDeSa Test Environment Setup (API Method)")
    print("=" * 60)
    
    # Get access token
    token = get_access_token()
    
    # Check resource group
    print(f"\n📋 Checking resource group '{RESOURCE_GROUP}'...")
    if not check_resource_group(token):
        print("\n💡 Create resource group first in Azure Portal:")
        print(f"   https://portal.azure.com/#create/Microsoft.ResourceGroup")
        sys.exit(1)
    
    # List existing PostgreSQL servers
    print("\n📋 Checking for existing PostgreSQL servers...")
    servers = list_postgres_servers(token)
    
    print(f"\nFound {len(servers)} PostgreSQL server(s):")
    for server in servers:
        print(f"   • {server['name']} - {server['properties'].get('state', 'unknown')}")
        print(f"     FQDN: {server['properties'].get('fullyQualifiedDomainName', 'N/A')}")
    
    # Check if test server exists
    test_server_exists = any(s['name'] == POSTGRES_TEST_SERVER for s in servers)
    
    if test_server_exists:
        print(f"\n✅ Test server '{POSTGRES_TEST_SERVER}' already exists!")
    else:
        print(f"\n⚠️  Test server '{POSTGRES_TEST_SERVER}' does not exist")
        print("\n💡 To create it, go to Azure Portal:")
        print(f"   1. Navigate to: https://portal.azure.com/#create/Microsoft.PostgreSQLServer")
        print(f"   2. Server name: {POSTGRES_TEST_SERVER}")
        print(f"   3. Resource group: {RESOURCE_GROUP}")
        print(f"   4. Location: {LOCATION}")
        print(f"   5. Compute + storage: Burstable, B1ms (1 vCore, 2 GiB RAM)")
        print(f"   6. Click 'Review + create'")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Environment Status")
    print("=" * 60)
    print(f"Subscription: {SUBSCRIPTION_ID}")
    print(f"Resource Group: {RESOURCE_GROUP}")
    print(f"PostgreSQL Servers: {len(servers)}")
    print(f"Test Server Ready: {'✅ Yes' if test_server_exists else '❌ No'}")
    
    if test_server_exists:
        test_server = next(s for s in servers if s['name'] == POSTGRES_TEST_SERVER)
        print(f"\n🎯 Next Steps:")
        print(f"   1. Connect to: {test_server['properties'].get('fullyQualifiedDomainName')}")
        print(f"   2. Configure firewall rules")
        print(f"   3. Deploy MCP test server")
        print(f"   4. Run validation tests")

if __name__ == "__main__":
    main()
