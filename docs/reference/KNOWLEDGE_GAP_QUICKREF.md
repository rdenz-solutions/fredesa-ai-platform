# Knowledge Gap Management - Quick Reference

**Status**: ✅ Production-Ready (Dec 29, 2025)

## 🎯 What It Does

Environment-aware knowledge gap detection for multi-tenant SaaS:
- **Development**: Gaps enable auto-ingestion workflow
- **Production**: Gaps logged, dev team notified, customers get safe message

## 🔒 Security Compliance

- ✅ **OWASP API5** - Prevents broken function level authorization
- ✅ **NIST AC-3** - Enforces access control boundaries
- ✅ **AWS SaaS Lens** - Tenant isolation maintained
- ✅ **Defense-in-depth** - Multiple security layers

## 📁 Files

| File | Purpose | Lines |
|------|---------|-------|
| `scripts/automation/knowledge_gap_manager.py` | Core gap detection logic | 377 |
| `docs/KNOWLEDGE_GAP_MANAGER.md` | Full documentation | 500+ |
| `.env.development` | Dev environment config | - |
| `.env.production` | Prod environment config (auto-learning OFF) | - |
| `tests/test_gap_manager.py` | Test suite (5 scenarios) | 175 |
| `scripts/mcp/knowledge_registry_server.py` | MCP integration | +93 |

## ⚡ Quick Start

### Test Gap Detection

```bash
# Run test suite (all 5 scenarios)
python3 tests/test_gap_manager.py

# Test via MCP server (development)
echo '{"jsonrpc": "2.0", "id": 1, "method": "detect_knowledge_gap", "params": {"query": "CMMC Level 3", "keywords": ["CMMC", "compliance"]}}' | \
  ENVIRONMENT=development python3 scripts/mcp/knowledge_registry_server.py 2>/dev/null | jq .

# Test via MCP server (production)
echo '{"jsonrpc": "2.0", "id": 1, "method": "detect_knowledge_gap", "params": {"query": "Quantum security", "customer_id": "cust-123"}}' | \
  ENVIRONMENT=production ENABLE_AUTO_LEARNING=false python3 scripts/mcp/knowledge_registry_server.py 2>/dev/null | jq .
```

### View Production Gaps Queue

```bash
# View all gaps
python3 scripts/automation/knowledge_gap_manager.py --view-queue

# View recent gaps
tail -20 logs/production_gaps_queue.jsonl | jq .
```

### Resolve a Gap

```bash
# Mark gap as resolved
python3 scripts/automation/knowledge_gap_manager.py --resolve "gap-id-here" --notes "Ingested CMMC sources"
```

## 🔄 Workflows

### Development Flow

```
Gap Detected → Logged to logs/knowledge_gaps.jsonl 
            → Developer runs autonomous_learning_agent.py
            → Sources ingested → Gap resolved
```

### Production Flow

```
Gap Detected → Logged to logs/production_gaps_queue.jsonl
            → Slack notification sent
            → Dev API notified (if configured)
            → Customer gets: "We've identified this knowledge area..."
            → Dev team reviews queue
            → Ingest in dev environment
            → Test → Deploy via normal release
```

## 🎛️ Configuration

### Environment Variables

```bash
# Required
ENVIRONMENT=development|production

# Security (CRITICAL in production)
ENABLE_AUTO_LEARNING=true|false  # MUST be false in production

# Notifications (optional but recommended)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DEV_KNOWLEDGE_API=https://dev-api.fredesa.com/knowledge-gaps

# Tier Limits (production)
STARTER_MAX_SOURCES=200
PRO_MAX_SOURCES=500
ENTERPRISE_MAX_SOURCES=2000
```

### Security Check

```bash
# This will CRASH (intentional security feature)
ENVIRONMENT=production ENABLE_AUTO_LEARNING=true python3 scripts/automation/knowledge_gap_manager.py --config

# Expected error:
# ⚠️ SECURITY VIOLATION: Autonomous learning cannot be enabled in production.
```

## 🧪 Test Results

All 5 tests passing ✅:

1. ✅ Development mode - Auto-ingestion available
2. ✅ Production mode - Logged + notified
3. ✅ Security violation - Hard block works
4. ✅ Queue management - Multiple gaps tracked
5. ✅ Existing coverage - No false positives

## 📊 MCP Server Integration

**New method**: `detect_knowledge_gap`

**Parameters**:
- `query` (required): Topic query string
- `keywords` (optional): List of keywords to search
- `customer_id` (optional): Customer identifier (for tracking)
- `context` (optional): Additional context

**Response** (development):
```json
{
  "status": "success",
  "gap_detected": true,
  "action": "ready_for_ingestion",
  "message": "Gap logged. Run autonomous_learning_agent.py to ingest.",
  "environment": "development"
}
```

**Response** (production):
```json
{
  "status": "success",
  "gap_detected": true,
  "action": "logged_for_review",
  "message": "We've identified this knowledge area for enhancement...",
  "environment": "production",
  "notification_sent": true,
  "queue_position": 4
}
```

## 🎯 Use Cases

### GitHub Copilot (via MCP)

```
User: "What are CMMC Level 3 requirements?"
Copilot: [searches knowledge base]
         [detects gap if < 2 sources]
         [calls detect_knowledge_gap via MCP]
         [returns environment-appropriate response]
```

### Airia Agents

```python
# In agent step
response = requests.post(
    f"{MCP_SERVER_URL}/detect_knowledge_gap",
    json={
        "query": user_query,
        "customer_id": customer.id,
        "context": f"Agent: {agent_name}"
    }
)
```

### API Endpoints

```python
# In FastAPI route
from scripts.automation.knowledge_gap_manager import KnowledgeGapManager

gap_manager = KnowledgeGapManager()
result = gap_manager.detect_gap(
    topic=query,
    keywords=extracted_keywords,
    customer_id=request.customer_id,
    query_context=request.endpoint
)
```

## 📈 Monitoring

### Weekly Metrics

```bash
# Generate weekly report
python3 scripts/automation/knowledge_gap_manager.py --weekly-report

# Output includes:
# - Total gaps detected
# - Top 5 missing topics
# - Customer tier distribution
# - Average response time
```

### Slack Notifications

Configure webhook in `.env.production`:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Notification format:
```
🔍 Knowledge Gap Detected (Production)

Topic: Quantum Cryptography Security
Customer: cust-prod-789
Keywords: quantum, cryptography, post-quantum
Context: Production customer query

Queue Position: #4
Review: https://fredesa.com/admin/gaps
```

## 🚀 Deployment

### Azure Container Apps

```bash
# Set environment variables
az containerapp update \
  --name fredesa-mcp-server \
  --set-env-vars \
    ENVIRONMENT=production \
    ENABLE_AUTO_LEARNING=false \
    SLACK_WEBHOOK_URL=secretref:slack-webhook

# Verify
az containerapp show --name fredesa-mcp-server --query "properties.configuration.secrets"
```

### Local Development

```bash
# Use .env.development
cp .env.development .env
source .env

# Or inline
ENVIRONMENT=development ENABLE_AUTO_LEARNING=true python3 your_script.py
```

## 🔮 Future Phases

### Phase 2: Tier-Based Control (Q2 2026)

- Database-driven feature flags
- Per-customer auto-learning permissions
- Usage tracking and quotas
- Admin UI for gap review

### Phase 3: Feature Flags (Q3 2026)

- LaunchDarkly integration
- A/B testing for ingestion triggers
- Gradual rollout by customer tier
- Real-time feature toggles

## 📚 Related Documentation

- **Full Guide**: `docs/KNOWLEDGE_GAP_MANAGER.md`
- **Architecture**: `docs/KNOWLEDGE_GAP_MANAGER.md` (Architecture Diagram section)
- **Security**: `docs/SECURITY.md`
- **Input Validation**: `docs/INPUT_VALIDATION_SECURITY.md`
- **MCP Integration**: `docs/guides/GITHUB_COPILOT_KNOWLEDGE_INJECTOR.md`

## 🤝 Team Context

**Decision Date**: December 29, 2025
**Pattern**: Salesforce/Zendesk early-stage approach
**Rationale**: Start simple (env flags), add complexity as scale demands
**Compliance**: OWASP + NIST validated
**Status**: Production-ready, tested, documented

---

**Next Steps**:
1. ✅ Test suite passing
2. ✅ Retrospection logged
3. ✅ Git committed (2 commits)
4. ✅ MCP integration complete
5. ⏭️ Deploy to Azure with production env vars
6. ⏭️ Monitor production gaps queue
7. ⏭️ Weekly team gap review process
