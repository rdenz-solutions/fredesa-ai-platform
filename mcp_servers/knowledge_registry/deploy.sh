#!/bin/bash
# Deploy FreDeSa Knowledge Registry MCP Server to Airia Gateway

echo "🚀 FreDeSa Knowledge Registry MCP Server Deployment"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

# Check if required files exist
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found"
    exit 1
fi

if [ ! -f "mcp.json" ]; then
    echo "❌ Error: mcp.json not found"
    exit 1
fi

echo "✅ All required files present"
echo ""

# Test local dependencies
echo "📦 Checking dependencies..."
python3 -c "import psycopg2; import mcp; print('✅ Dependencies OK')" 2>/dev/null || {
    echo "⚠️  Dependencies missing - installing..."
    pip3 install -r requirements.txt
}

echo ""
echo "🧪 Testing database connection..."
python3 << 'PYTHON'
import os
import sys

# Load password from environment or Key Vault
password = os.getenv("POSTGRES_PASSWORD")
if not password:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        
        credential = DefaultAzureCredential()
        vault_url = "https://fredesa-kv-e997e3.vault.azure.net/"
        client = SecretClient(vault_url=vault_url, credential=credential)
        password = client.get_secret("postgres-password").value
        print("✅ Retrieved password from Azure Key Vault")
    except Exception as e:
        print(f"❌ Could not get password: {e}")
        sys.exit(1)

# Test connection
try:
    import psycopg2
    conn = psycopg2.connect(
        host="fredesa-db-dev.postgres.database.azure.com",
        database="postgres",
        user="fredesaadmin",
        password=password,
        sslmode="require"
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sources")
    count = cur.fetchone()[0]
    print(f"✅ Database connection successful - {count} sources available")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
PYTHON

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Pre-deployment checks failed"
    exit 1
fi

echo ""
echo "📦 Creating deployment package..."
zip -r knowledge-registry-mcp.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc" -x "deploy.sh" -x "test_local.py"

if [ $? -eq 0 ]; then
    echo "✅ Package created: knowledge-registry-mcp.zip"
else
    echo "❌ Package creation failed"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ READY FOR AIRIA GATEWAY DEPLOYMENT"
echo "=================================================="
echo ""
echo "Next Steps:"
echo "1. Go to Airia Gateway dashboard"
echo "2. Click 'Deploy New MCP Server'"
echo "3. Upload: knowledge-registry-mcp.zip"
echo "4. Configure secrets:"
echo "   - POSTGRES_PASSWORD = [from Azure Key Vault]"
echo "5. Deploy and register in your project"
echo ""
echo "Package: $(pwd)/knowledge-registry-mcp.zip"
echo "Size: $(du -h knowledge-registry-mcp.zip | cut -f1)"
echo ""
