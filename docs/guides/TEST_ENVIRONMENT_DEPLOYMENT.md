# Test Environment Deployment Plan
**FreDeSa AI Platform - 3-Tier Architecture Setup**

**Created:** December 29, 2025  
**Status:** Ready for execution  
**Estimated Time:** 2-3 hours  
**Cost:** ~$50-100/month

---

## 🎯 Objectives

1. Create isolated test environment for safe feature validation
2. Enable 3-cofounder collaboration without production risk
3. Test database migrations (26 remaining tables) safely
4. Validate knowledge gap detection before customer exposure

---

## 📊 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  DEVELOPMENT (Local Laptops)                             │
│  • rdenz-knowledge-registry                              │
│  • YAML-based (config/sources.yaml)                      │
│  • ENVIRONMENT=development                               │
│  • ENABLE_AUTO_LEARNING=true                             │
│  • Each cofounder: delchaplin, speh-w2p, fmurphy-fredesa │
└────────────────────┬─────────────────────────────────────┘
                     │ git push to main
                     ↓
┌──────────────────────────────────────────────────────────┐
│  TEST/STAGING (Azure - NEW)                              │
│  • fredesa-db-test (PostgreSQL clone)                    │
│  • fredesa-mcp-server-test (Container App)               │
│  • fredesa-cache-test (Redis - optional)                 │
│  • ENVIRONMENT=test                                      │
│  • ENABLE_AUTO_LEARNING=false                            │
│  • Slack: #dev-alerts (test notifications)               │
│  • URL: fredesa-mcp-test.eastus.azurecontainerapps.io    │
└────────────────────┬─────────────────────────────────────┘
                     │ manual promotion after validation
                     ↓
┌──────────────────────────────────────────────────────────┐
│  PRODUCTION (Azure - Existing)                           │
│  • fredesa-db-dev (PostgreSQL - rename to prod later)    │
│  • fredesa-mcp-server (Container App)                    │
│  • fredesa-cache-dev (Redis)                             │
│  • ENVIRONMENT=production                                │
│  • ENABLE_AUTO_LEARNING=false                            │
│  • Slack: #knowledge-gaps (customer notifications)       │
│  • URL: fredesa-mcp-server.eastus.azurecontainerapps.io  │
└──────────────────────────────────────────────────────────┘
```

---

## 📋 Pre-Deployment Checklist

### Required Tools
- [ ] Azure CLI installed: `az --version`
- [ ] Logged into Azure: `az login`
- [ ] Subscription set: `az account set --subscription "FreDeSa-Subscription"`
- [ ] Git access to both repos (rdenz-KR, fredesa-ai-platform)

### Required Information
- [ ] Production PostgreSQL connection string
- [ ] Microsoft Teams webhook URL for Dev Alerts channel
- [ ] Azure Container Registry credentials
- [ ] GitHub deployment keys (if using)

### Resource Group Check
```bash
az group show --name fredesa-rg
# If doesn't exist, create: az group create --name fredesa-rg --location eastus
```

---

## 🚀 Phase 1: PostgreSQL Test Database (30 min)

### Step 1.1: Create Test Database Server

**Option A: Clone from Production (Recommended)**
```bash
# Clone production database (includes schema v2.1)
az postgres flexible-server replica create \
  --name fredesa-db-test \
  --source-server fredesa-db-dev \
  --resource-group fredesa-rg \
  --location eastus \
  --tier Burstable \
  --sku-name Standard_B1ms \
  --storage-size 32

# Expected output:
# {
#   "id": "/subscriptions/.../fredesa-db-test",
#   "state": "Ready",
#   "fullyQualifiedDomainName": "fredesa-db-test.postgres.database.azure.com"
# }
```

**Option B: Fresh Database (If you want clean slate)**
```bash
az postgres flexible-server create \
  --name fredesa-db-test \
  --resource-group fredesa-rg \
  --location eastus \
  --admin-user fredesaadmin \
  --admin-password "$(az keyvault secret show --vault-name fredesa-kv-e997e3 --name postgres-password --query value -o tsv)" \
  --tier Burstable \
  --sku-name Standard_B1ms \
  --storage-size 32 \
  --version 15 \
  --public-access 0.0.0.0 \
  --high-availability Disabled \
  --backup-retention 7
```

### Step 1.2: Configure Firewall Rules

```bash
# Allow Azure services
az postgres flexible-server firewall-rule create \
  --name fredesa-db-test \
  --resource-group fredesa-rg \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow your IP (for direct testing)
MY_IP=$(curl -s ifconfig.me)
az postgres flexible-server firewall-rule create \
  --name fredesa-db-test \
  --resource-group fredesa-rg \
  --rule-name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

### Step 1.3: Store Test Database Password in Key Vault

```bash
# Use same password as prod for simplicity
az keyvault secret set \
  --vault-name fredesa-kv-e997e3 \
  --name postgres-password-test \
  --value "$(az keyvault secret show --vault-name fredesa-kv-e997e3 --name postgres-password --query value -o tsv)"

# Store Teams webhook for dev alerts
az keyvault secret set \
  --vault-name fredesa-kv-e997e3 \
  --name teams-webhook-dev-alerts \
  --value "https://YOUR-TENANT.webhook.office.com/webhookb2/YOUR-WEBHOOK-URL"
```

### Step 1.4: Verify Database Connection

```bash
export PGPASSWORD=$(az keyvault secret show --vault-name fredesa-kv-e997e3 --name postgres-password-test --query value -o tsv)
psql -h fredesa-db-test.postgres.database.azure.com -p 5432 -U fredesaadmin -d postgres -c "SELECT version();"

# Expected: PostgreSQL 15.15 on x86_64...
```

### Step 1.5: Run Schema Migration (If using Option B)

```bash
cd /Users/delchaplin/Project\ Files/fredesa-ai-platform

# Apply schema v2.1
python3 scripts/database/create_schema_v2.1.py --execute

# Migrate sources from YAML
python3 scripts/database/migrate_v1_to_v2_complete.py --execute

# Deploy triggers
python3 scripts/database/deploy_priority_1_triggers.py --execute

# Verify
psql -h fredesa-db-test.postgres.database.azure.com -p 5432 -U fredesaadmin -d postgres \
  -c "SELECT COUNT(*) FROM sources;" \
  -c "SELECT COUNT(*) FROM categories;"
```

---

## 🐳 Phase 2: MCP Server Test Container (45 min)

### Step 2.1: Create Container App Environment (If Needed)

```bash
# Check if environment exists
az containerapp env list --resource-group fredesa-rg --query "[].name" -o table

# If not exists, create
az containerapp env create \
  --name fredesa-env \
  --resource-group fredesa-rg \
  --location eastus
```

### Step 2.2: Build and Push Test Container Image

```bash
cd /Users/delchaplin/Project\ Files/fredesa-ai-platform/mcp_servers/knowledge_registry

# Build image with test tag
docker build -t fredesaacr.azurecr.io/mcp-server:test .

# Login to ACR
az acr login --name fredesaacr

# Push image
docker push fredesaacr.azurecr.io/mcp-server:test
```

### Step 2.3: Deploy Test MCP Server

```bash
az containerapp create \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --environment fredesa-env \
  --image fredesaacr.azurecr.io/mcp-server:test \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    DATABASE_PASSWORD=secretref:postgres-password-test \
    REDIS_HOST=fredesa-cache-dev.redis.cache.windows.net \
    REDIS_PORT=6380 \
    REDIS_PASSWORD=secretref:redis-password \
    TEAMS_WEBHOOK_URL=secretref:teams-webhook-dev-alerts \
  --secrets \
    postgres-password-test=keyvaultref:https://fredesa-kv-e997e3.vault.azure.net/secrets/postgres-password-test,identityref:/subscriptions/.../fredesaIdentity \
    redis-password=keyvaultref:https://fredesa-kv-e997e3.vault.azure.net/secrets/redis-password,identityref:/subscriptions/.../fredesaIdentity \
    teams-webhook-dev-alerts=keyvaultref:https://fredesa-kv-e997e3.vault.azure.net/secrets/teams-webhook-dev-alerts,identityref:/subscriptions/.../fredesaIdentity
    REDIS_PASSWORD=secretref:redis-password \
    SLACK_WEBHOOK_URL=secretref:slack-webhook-dev-alerts \
  --secrets \
    postgres-password-test=keyvaultref:https://fredesa-kv-e997e3.vault.azure.net/secrets/postgres-password-test,identityref:/subscriptions/.../fredesaIdentity \
    redis-password=keyvaultref:https://fredesa-kv-e997e3.vault.azure.net/secrets/redis-password,identityref:/subscriptions/.../fredesaIdentity \
    slack-webhook-dev-alerts=https://hooks.slack.com/services/YOUR/TEST/WEBHOOK
```

### Step 2.4: Get Test Server URL

```bash
az containerapp show \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --query properties.configuration.ingress.fqdn \
  -o tsv

# Output: fredesa-mcp-server-test.jollycoast-c7c76241.eastus.azurecontainerapps.io
```

### Step 2.5: Test Health Check

```bash
TEST_URL=$(az containerapp show --name fredesa-mcp-server-test --resource-group fredesa-rg --query properties.configuration.ingress.fqdn -o tsv)

curl https://$TEST_URL/health | jq .

# Expected:
# {
#   "status": "healthy",
#   "database": "connected",
#   "environment": "test"
# }
```

---

## 🔧 Phase 3: Code Sync to Test Environment (30 min)

### Step 3.1: Copy Knowledge Gap Manager to fredesa-ai-platform

```bash
cd /Users/delchaplin/Project\ Files

# Create automation directory if doesn't exist
mkdir -p fredesa-ai-platform/scripts/automation

# Copy gap manager
cp rdenz-knowledge-registry/scripts/automation/knowledge_gap_manager.py \
   fredesa-ai-platform/scripts/automation/

# Copy tests
mkdir -p fredesa-ai-platform/tests
cp rdenz-knowledge-registry/tests/test_gap_manager.py \
   fredesa-ai-platform/tests/

# Copy documentation
mkdir -p fredesa-ai-platform/docs/guides
cp rdenz-knowledge-registry/docs/KNOWLEDGE_GAP_MANAGER.md \
   fredesa-ai-platform/docs/guides/
cp rdenz-knowledge-registry/docs/reference/KNOWLEDGE_GAP_QUICKREF.md \
   fredesa-ai-platform/docs/reference/
```

### Step 3.2: Update MCP Server with Gap Detection

```bash
cd fredesa-ai-platform/mcp_servers/knowledge_registry

# Backup current version
cp http_server.py http_server.py.backup

# Copy updated version from rdenz-KR
cp /Users/delchaplin/Project\ Files/rdenz-knowledge-registry/scripts/mcp/knowledge_registry_server.py \
   http_server.py
```

### Step 3.3: Add Environment Configuration Files

```bash
cd fredesa-ai-platform

# Create .env.test (based on .env.production from rdenz-KR)
cat > .env.test << 'EOF'
# Test Environment Configuration
ENVIRONMENT=test
ENABLE_AUTO_LEARNING=false

# Redis (Shared with prod for cost savings)
REDIS_HOST=fredesa-cache-dev.redis.cache.windows.net
REDIS_PORT=6380

# Microsoft Teams (Dev Alerts channel)
TEAMS_WEBHOOK_URL=https://YOUR-TENANT.webhook.office.com/webhookb2/YOUR-WEBHOOK-URL
DEV_KNOWLEDGE_API=https://fredesa-mcp-server-test.eastus.azurecontainerapps.io/knowledge-gaps
REDIS_HOST=fredesa-cache-dev.redis.cache.windows.net
REDIS_PORT=6380

# Slack (Test channel)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/TEST/WEBHOOK
DEV_KNOWLEDGE_API=https://fredesa-mcp-server-test.eastus.azurecontainerapps.io/knowledge-gaps

# Tier Limits (Same as prod)
STARTER_MAX_SOURCES=200
PRO_MAX_SOURCES=500
ENTERPRISE_MAX_SOURCES=2000

# Feature Flags
ENABLE_KNOWLEDGE_GAP_DETECTION=true
ENABLE_AUTO_INGESTION=false
EOF

# .env.production already exists from earlier work
```

### Step 3.4: Rebuild and Redeploy Test Container

```bash
cd fredesa-ai-platform/mcp_servers/knowledge_registry

# Rebuild with gap detection
docker build -t fredesaacr.azurecr.io/mcp-server:test .
docker push fredesaacr.azurecr.io/mcp-server:test

# Update container app
az containerapp update \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --image fredesaacr.azurecr.io/mcp-server:test

# Wait for deployment (30-60 seconds)
az containerapp revision list \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --query "[0].{name:name, active:properties.active, trafficWeight:properties.trafficWeight}" \
  -o table
```

---

## ✅ Phase 4: Validation & Testing (30 min)

### Test 1: Database Connection

```bash
TEST_URL=$(az containerapp show --name fredesa-mcp-server-test --resource-group fredesa-rg --query properties.configuration.ingress.fqdn -o tsv)

curl https://$TEST_URL/health | jq .

# Expected:
# {
#   "status": "healthy",
#   "database": "connected",
#   "total_sources": 1043,
#   "environment": "test"
# }
```

### Test 2: Query Knowledge Base

```bash
curl -X POST https://$TEST_URL/tools/query_knowledge_base \
  -H "Content-Type: application/json" \
  -d '{"query": "FAR subcontracting requirements", "max_results": 3}' | jq .

# Expected: 3 sources returned with authority scores
```

### Test 3: Gap Detection (Development Mode)

```bash
# Test in development mode (should allow auto-ingestion ready)
curl -X POST https://$TEST_URL/tools/detect_knowledge_gap \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CMMC Level 3 compliance",
    "keywords": ["CMMC", "compliance", "cybersecurity"],
    "customer_id": "test-customer-123",
    "context": "Test environment gap detection"
  }' | jq .

# Expected:
# {
#   "status": "success",
#   "gap_detected": false,
#   "sources_found": 6,
#   "action": "none_needed",
#   "environment": "test"
# }
```

### Test 4: Gap Detection (Production Mode Simulation)

```bash
# Test with unknown topic (should trigger gap logging)
curl -X POST https://$TEST_URL/tools/detect_knowledge_gap \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quantum cryptography security",
    "keywords": ["quantum", "post-quantum", "cryptography"],
    "customer_id": "test-customer-456",
    "context": "Production simulation test"
  }' | jq .

# Expected:
# {
#   "status": "success",
#   "gap_detected": true,
#   "action": "logged_for_review",
#   "message": "We've identified this knowledge area...",
#   "notification_sent": true,
#   "environment": "test"
# }

# Verify Teams notification received in Dev Alerts channel
```

### Test 5: Run Automated Test Suite

```bash
cd fredesa-ai-platform

# Run gap manager tests against test environment
ENVIRONMENT=test python3 tests/test_gap_manager.py

# Expected: All 5 tests passing
```

### Test 6: Database Migration Test (Dry Run)

```bash
# Test adding remaining 26 tables (Priority 2 & 3)
cd fredesa-ai-platform/scripts/database

# Dry run first
python3 create_priority_2_tables.py --dry-run

# If looks good, execute
python3 create_priority_2_tables.py --execute

# Verify
psql -h fredesa-db-test.postgres.database.azure.com -p 5432 -U fredesaadmin -d postgres \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
```

---

## 📊 Phase 5: Monitoring Setup (15 min)

### Step 5.1: Application Insights (Optional but Recommended)

```bash
# Create App Insights for test environment
az monitor app-insights component create \
  --app fredesa-mcp-test-insights \
  --location eastus \
  --resource-group fredesa-rg \
  --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app fredesa-mcp-test-insights \
  --resource-group fredesa-rg \
  --query instrumentationKey -o tsv)

# Update container app with App Insights
az containerapp update \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --set-env-vars APPLICATIONINSIGHTS_INSTRUMENTATION_KEY=$INSTRUMENTATION_KEY
```

### Step 5.2: Log Analytics Queries

```bash
# View recent logs
az containerapp logs show \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --follow

# Filter for gap detection
az containerapp logs show \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --tail 100 | grep "gap_detected"
```

### Step 5.3: Set Up Alerts (Optional)

```bash
# Alert on container app errors
az monitor metrics alert create \
  --name "Test MCP Server Errors" \
  --resource-group fredesa-rg \
  --scopes $(az containerapp show --name fredesa-mcp-server-test --resource-group fredesa-rg --query id -o tsv) \
  --condition "count Requests > 10 where ResponseCode >= 500" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email you@company.com
```

---

## 🔄 Phase 6: Git Integration & Cofounder Onboarding (30 min)

### Step 6.1: Commit Changes to fredesa-ai-platform

```bash
cd /Users/delchaplin/Project\ Files/fredesa-ai-platform

git add scripts/automation/knowledge_gap_manager.py
git add tests/test_gap_manager.py
git add mcp_servers/knowledge_registry/http_server.py
git add docs/guides/KNOWLEDGE_GAP_MANAGER.md
git add docs/reference/KNOWLEDGE_GAP_QUICKREF.md
git add .env.test

git commit -m "feat: Add knowledge gap detection and test environment

- Synced knowledge_gap_manager.py from rdenz-KR
- Updated MCP server with detect_knowledge_gap method
- Added test environment configuration (.env.test)
- Deployed fredesa-db-test and fredesa-mcp-server-test
- All 5 test scenarios passing

Test Environment URLs:
- Database: fredesa-db-test.postgres.database.azure.com
- MCP Server: fredesa-mcp-server-test.eastus.azurecontainerapps.io

See docs/guides/TEST_ENVIRONMENT_DEPLOYMENT.md for details"

git push origin main
```

### Step 6.2: Create Cofounder Onboarding Guide

```bash
cd fredesa-ai-platform

cat > docs/guides/COFOUNDER_TEST_ENV_ACCESS.md << 'EOF'
# Cofounder Access: Test Environment

## Quick Start

### 1. Pull Latest Code
```bash
cd /Users/<your-username>/Project\ Files/fredesa-ai-platform
git pull origin main
```

### 2. Access Test Database
```bash
# Get password from Key Vault
export PGPASSWORD=$(az keyvault secret show \
  --vault-name fredesa-kv-e997e3 \
  --name postgres-password-test \
  --query value -o tsv)

# Connect
psql -h fredesa-db-test.postgres.database.azure.com \
  -p 5432 \
  -U fredesaadmin \
  -d postgres
```

### 3. Test MCP Server
```bash
# Health check
curl https://fredesa-mcp-server-test.jollycoast-c7c76241.eastus.azurecontainerapps.io/health | jq .

# Query knowledge base
curl -X POST https://fredesa-mcp-server-test.jollycoast-c7c76241.eastus.azurecontainerapps.io/tools/query_knowledge_base \
  -H "Content-Type: application/json" \
  -d '{"query": "FAR requirements", "max_results": 3}' | jq .
```

### 4. Run Tests
```bash
cd /Users/<your-username>/Project\ Files/fredesa-ai-platform
ENVIRONMENT=test python3 tests/test_gap_manager.py
```

## Environment URLs

| Environment | Database | MCP Server | Purpose |
|-------------|----------|------------|---------|
| Test | fredesa-db-test.postgres.database.azure.com | fredesa-mcp-server-test.eastus.azurecontainerapps.io | Safe feature testing |
| Production | fredesa-db-dev.postgres.database.azure.com | fredesa-mcp-server.eastus.azurecontainerapps.io | Customer-facing |

## Microsoft Teams Notifications

- **Test Environment**: Dev Alerts channel (test notifications)
- **Production**: Knowledge Gaps channel (customer-facing notifications)

## Rules

1. **Always test in Test environment first**
2. **Never run migrations directly on Production**
3. **Test database can be reset anytime** (it's a clone)
4. **Production database changes require team approval**

## Need Help?

- Deployment guide: `docs/guides/TEST_ENVIRONMENT_DEPLOYMENT.md`
- Gap detection docs: `docs/guides/KNOWLEDGE_GAP_MANAGER.md`
- Quick reference: `docs/reference/KNOWLEDGE_GAP_QUICKREF.md`
EOF

git add docs/guides/COFOUNDER_TEST_ENV_ACCESS.md
git commit -m "docs: Add cofounder test environment access guide"
git push origin main
```

### Step 6.3: Notify Cofounders

**Send Teams/Email:**
```
🚀 Test Environment Now Available!

We've set up a dedicated test environment for safe feature development:

**Test Environment:**
• Database: fredesa-db-test (PostgreSQL clone)
• MCP Server: fredesa-mcp-server-test
• Teams notifications: Dev Alerts channel

**What this means:**
✅ Test database migrations without breaking production
✅ Test gap detection safely (notifications go to Dev Alerts channel)
✅ Each cofounder can experiment independently

**To get started:**
1. git pull origin main
2. Read docs/guides/COFOUNDER_TEST_ENV_ACCESS.md
3. Run: ENVIRONMENT=test python3 tests/test_gap_manager.py

**Workflow:**
Dev (laptop) → Test (Azure) → Production (Azure)

See full deployment guide: docs/guides/TEST_ENVIRONMENT_DEPLOYMENT.md
```

---

## 💰 Cost Breakdown

### Monthly Recurring Costs

| Resource | Tier | Cost/Month | Notes |
|----------|------|------------|-------|
| PostgreSQL Test | Standard_B1ms | ~$15 | Burstable, 32GB storage |
| Container App Test | 0.5 vCPU, 1GB RAM | ~$10-20 | Pay per use |
| Redis (Shared) | Basic C0 | $0 | Already paid for prod |
| App Insights | Basic | ~$5 | First 5GB free |
| **Total** | | **~$30-40** | Can pause when not testing |

### Cost Optimization Tips

1. **Stop test resources when not in use:**
   ```bash
   # Stop test database (save ~$15/month)
   az postgres flexible-server stop --name fredesa-db-test --resource-group fredesa-rg
   
   # Restart when needed
   az postgres flexible-server start --name fredesa-db-test --resource-group fredesa-rg
   ```

2. **Share Redis with production** (already doing this)

3. **Use lower tier for container app:**
   ```bash
   # Scale down when not testing
   az containerapp update \
     --name fredesa-mcp-server-test \
     --resource-group fredesa-rg \
     --min-replicas 0 \
     --max-replicas 1
   ```

4. **Delete and recreate test DB as needed:**
   - Fresh clone from prod takes ~10 minutes
   - Only pay when it exists

---

## 🔒 Security Checklist

- [ ] Test database uses same firewall rules as production
- [ ] Teams webhook points to Dev Alerts channel (not customer channel)
- [ ] ENABLE_AUTO_LEARNING=false in test (same as prod)
- [ ] Test environment secrets stored in Key Vault
- [ ] Container app uses managed identity for secrets
- [ ] Network security groups configured (if using VNet)
- [ ] TLS/SSL enabled on all endpoints
- [ ] Test data doesn't contain real customer PII

---

## 📝 Post-Deployment Validation

### Checklist

- [ ] Test database accessible from Azure and local machine
- [ ] MCP server health check returns "healthy"
- [ ] Gap detection works in both development and production modes
- [ ] Teams notifications arrive in Dev Alerts channel
- [ ] All 5 automated tests pass
- [ ] Cofounders can access test environment
- [ ] Documentation committed to fredesa-ai-platform repo
- [ ] Cost monitoring alerts configured

### Smoke Test Commands

```bash
# 1. Database
psql -h fredesa-db-test.postgres.database.azure.com -p 5432 -U fredesaadmin -d postgres -c "SELECT COUNT(*) FROM sources;"

# 2. MCP Server
curl https://fredesa-mcp-server-test.jollycoast-c7c76241.eastus.azurecontainerapps.io/health | jq .status

# 3. Gap Detection
curl -X POST https://fredesa-mcp-server-test.jollycoast-c7c76241.eastus.azurecontainerapps.io/tools/detect_knowledge_gap \
  -H "Content-Type: application/json" \
  -d '{"query": "Test query", "keywords": ["test"]}' | jq .gap_detected

# 4. Automated Tests
cd fredesa-ai-platform && ENVIRONMENT=test python3 tests/test_gap_manager.py

# All should return success
```

---

## 🔄 Ongoing Workflow

### Developer Workflow (Daily)

```bash
# 1. Develop locally (rdenz-knowledge-registry)
cd rdenz-knowledge-registry
# Make changes, test with YAML files
git commit -m "feat: new feature"
git push origin main

# 2. Sync to fredesa-ai-platform
cd fredesa-ai-platform
# Copy changed files (see Phase 3)
git commit -m "feat: sync from rdenz-KR"
git push origin main

# 3. Test in Azure test environment
# MCP server auto-updates from container registry
# Or manually trigger deployment:
az containerapp update --name fredesa-mcp-server-test --resource-group fredesa-rg

# 4. Validate
curl https://fredesa-mcp-server-test.eastus.azurecontainerapps.io/health

# 5. Promote to production (after team approval)
az containerapp update --name fredesa-mcp-server --resource-group fredesa-rg
```

### Database Migration Workflow

```bash
# 1. Test migration on test database
python3 scripts/database/migrate_new_tables.py \
  --host fredesa-db-test.postgres.database.azure.com \
  --execute

# 2. Run tests
python3 scripts/testing/test_schema_v2.1.py

# 3. If tests pass, run on production
python3 scripts/database/migrate_new_tables.py \
  --host fredesa-db-dev.postgres.database.azure.com \
  --execute
```

---

## 🆘 Troubleshooting

### Issue: Test database won't connect

**Check:**
```bash
# 1. Firewall rules
az postgres flexible-server firewall-rule list \
  --name fredesa-db-test \
  --resource-group fredesa-rg

# 2. Server status
az postgres flexible-server show \
  --name fredesa-db-test \
  --resource-group fredesa-rg \
  --query state -o tsv

# 3. Test from Azure Cloud Shell (bypasses local firewall)
az postgres flexible-server connect \
  --name fredesa-db-test \
  --admin-user fredesaadmin
```

### Issue: MCP server returns 500 errors

**Debug:**
```bash
# 1. Check logs
az containerapp logs show \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --tail 50

# 2. Check environment variables
az containerapp show \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --query properties.configuration.secrets

# 3. Restart container
az containerapp revision restart \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --revision $(az containerapp revision list --name fredesa-mcp-server-test --resource-group fredesa-rg --query "[0].name" -o tsv)
```

### Issue: Gap detection not working

**Check:**
```bash
# 1. Verify gap manager is deployed
curl https://fredesa-mcp-server-test.eastus.azurecontainerapps.io/stats | jq .

# 2. Check environment variable
az containerapp show \
  --name fredesa-mcp-server-test \
  --resource-group fredesa-rg \
  --query "properties.configuration.activeRevisionsMode" -o tsv

# 3. Test locally first
cd fredesa-ai-platform
ENVIRONMENT=test python3 -c "from scripts.automation.knowledge_gap_manager import KnowledgeGapManager; mgr = KnowledgeGapManager(); print(mgr.config)"
```

---

## 📚 Related Documentation

- **Main Setup Guide:** This file
- **Gap Detection:** `docs/guides/KNOWLEDGE_GAP_MANAGER.md`
- **Quick Reference:** `docs/reference/KNOWLEDGE_GAP_QUICKREF.md`
- **Cofounder Access:** `docs/guides/COFOUNDER_TEST_ENV_ACCESS.md`
- **Schema Migration:** `docs/database/SCHEMA_V2.1_MIGRATION.md`
- **MCP Server:** `mcp_servers/knowledge_registry/README.md`

---

## ✅ Success Criteria

Test environment is successfully deployed when:

- [ ] All Azure resources created and running
- [ ] Test database has 1,043 sources from migration
- [ ] MCP server health check returns "healthy"
- [ ] Gap detection works (test with unknown topic)
- [ ] Slack notifications arrive in #dev-alerts
- [ ] All 5 automated tests pass
- [ ] Cofounders can access and use test environment
- [ ] Cost monitoring shows ~$30-40/month
- [ ] Documentation complete in fredesa-ai-platform repo

---

**Deployment Time Estimate:** 2-3 hours for first-time setup  
**Monthly Cost:** ~$30-40 (can pause when not testing)  
**Team Impact:** 🟡 MEDIUM (requires cofounder coordination)  
**Production Risk:** 🟢 LOW (isolated test environment)

---

**Ready to execute? Start with Phase 1 and work through sequentially.**
