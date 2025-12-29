# Knowledge Gap Manager - Environment-Aware Learning System

## Overview

The Knowledge Gap Manager provides **environment-aware learning** that balances rapid development with production security.

**Key Principle**: Keep autonomous learning in development, notify development team when gaps occur in production.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT ENVIRONMENT                   │
│                                                              │
│  Gap Detected → Auto-Ingest → Update Registry → Test       │
│                                                              │
│  ✅ Single-tenant (safe)                                    │
│  ✅ Controlled by developers                                │
│  ✅ Rapid learning enabled                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   PRODUCTION ENVIRONMENT                     │
│                                                              │
│  Gap Detected → Log + Notify Dev → Human Review → Deploy   │
│                                                              │
│  ✅ Multi-tenant (secure)                                   │
│  ✅ OWASP API5 compliant                                    │
│  ✅ Customer data protected                                 │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
# .env (development)
ENVIRONMENT=development
ENABLE_AUTO_LEARNING=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DEV_KNOWLEDGE_API=http://localhost:8000/api

# .env.production
ENVIRONMENT=production
ENABLE_AUTO_LEARNING=false  # MUST be false in production
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DEV_KNOWLEDGE_API=https://dev.fredesa.com/api
```

### Safety Checks

The system **automatically prevents** production autonomous learning:

```python
# Raises error if misconfigured
if is_production and auto_ingest_enabled:
    raise EnvironmentError("Cannot enable auto-learning in production")
```

## Usage

### Development: Test Gap Detection

```bash
# Test gap detection
python3 scripts/automation/knowledge_gap_manager.py --test-gap "ITAR compliance"

# Output:
# ✅ Gap Detection Result:
# {
#   "gap_detected": true,
#   "action": "ready_for_ingestion",
#   "message": "Gap logged. Run autonomous_learning_agent.py to ingest.",
#   "suggested_keywords": ["ITAR", "compliance"]
# }

# Then run autonomous ingestion
python3 scripts/automation/autonomous_learning_agent.py --topic "ITAR compliance"
```

### Production: View Gap Queue

```bash
# View production gaps waiting for dev review
python3 scripts/automation/knowledge_gap_manager.py --view-queue

# Output:
# 📋 Production Knowledge Gaps (3 total)
#
# 1. ITAR compliance
#    Keywords: ITAR, compliance, export, control
#    Customer: customer-uuid-abc123
#    Time: 2025-12-29T10:30:00Z
#
# 2. CMMC Level 3 requirements
#    Keywords: CMMC, Level, 3, cybersecurity
#    Customer: customer-uuid-def456
#    Time: 2025-12-29T11:15:00Z
```

### Production: Slack Notifications

When a gap is detected in production, dev team receives:

```
🔍 Knowledge Gap Detected in Production

Customer: customer-uuid-abc123
Topic: ITAR compliance
Keywords: ITAR, compliance, export
Query: What are ITAR compliance requirements for software?

Action Required: Review and consider ingesting sources for this topic.
Queue Position: 3
View Queue: `cat logs/production_gaps_queue.jsonl`
```

### Development: Resolve Gaps

After ingesting a source in development:

```bash
# Mark gap as resolved
python3 scripts/automation/knowledge_gap_manager.py --resolve "2025-12-29T10:30:00Z"

# Output:
# ✅ Gap marked as resolved: 2025-12-29T10:30:00Z
```

## Integration with MCP Server

### Production MCP Server

```python
# mcp_servers/knowledge_registry/http_server.py

from scripts.automation.knowledge_gap_manager import KnowledgeGapManager

gap_manager = KnowledgeGapManager()

@app.post("/tools/query_knowledge_base")
async def query_knowledge_base(request: QueryRequest):
    results = db.search(request.query)
    
    # Detect gap if insufficient results
    if len(results) < 2:
        gap_manager.detect_gap(
            topic=request.query,
            keywords=request.query.split(),
            customer_id=request.customer_id,  # From auth token
            query_context=request.query
        )
    
    return {"sources": results}
```

### Development Workflow

```python
# In development, gaps trigger immediate logging
result = gap_manager.detect_gap(
    topic="New AI framework",
    keywords=["new", "ai", "framework"]
)

if result["gap_detected"] and result["action"] == "ready_for_ingestion":
    # Developer can immediately run autonomous ingestion
    # No customer data risk in single-tenant dev environment
    pass
```

## File Outputs

### Development: `logs/knowledge_gaps.jsonl`

```json
{
  "timestamp": "2025-12-29T10:30:00Z",
  "topic": "ITAR compliance",
  "keywords": ["ITAR", "compliance"],
  "matching_sources": [],
  "coverage_sufficient": false,
  "environment": "development"
}
```

### Production: `logs/production_gaps_queue.jsonl`

```json
{
  "timestamp": "2025-12-29T10:30:00Z",
  "topic": "ITAR compliance",
  "keywords": ["ITAR", "compliance"],
  "matching_sources": [],
  "coverage_sufficient": false,
  "environment": "production",
  "customer_id": "019b4ac6-6b06-78d2-95fc-13058e9b5592",
  "query_context": "What are ITAR compliance requirements?"
}
```

### Notifications: `logs/dev_notifications.jsonl`

Backup file-based notifications (always written):

```json
{
  "timestamp": "2025-12-29T10:30:00Z",
  "topic": "ITAR compliance",
  "customer_id": "019b4ac6-6b06-78d2-95fc-13058e9b5592",
  "notification_timestamp": "2025-12-29T10:30:01Z"
}
```

## Security Compliance

### OWASP API Security Top 10

✅ **API1: Broken Object Level Authorization**
- Production gaps logged, not acted upon automatically
- Customer cannot trigger ingestion of sources outside their tier

✅ **API5: Broken Function Level Authorization**
- Ingestion function disabled in production
- Only dev environment has autonomous learning

✅ **API8: Security Misconfiguration**
- Auto-learning explicitly disabled by default in production
- Environment check prevents misconfiguration

### NIST Controls

✅ **AC-3: Access Enforcement**
- Tier-based access maintained (no customer-triggered ingestion)

✅ **AC-4: Information Flow Enforcement**
- Information flow (public web → knowledge base) requires human approval in production

✅ **AU-2: Audit Events**
- All production gaps logged with customer context

✅ **SI-3: Malicious Code Protection**
- No automatic ingestion from untrusted sources in production

### AWS SaaS Lens

✅ **Tenant Isolation**
- Production gaps logged but not ingested (no cross-tenant data leakage)

✅ **Control Plane Security**
- Knowledge ingestion = control plane operation (admin-only in production)

## Development Team Workflow

### Daily Gap Review

```bash
# 1. Check for new production gaps
python3 scripts/automation/knowledge_gap_manager.py --view-queue

# 2. Prioritize gaps by frequency/customer tier
# (Enterprise customers = higher priority)

# 3. Research and ingest in development
cd /path/to/development/environment
python3 scripts/automation/autonomous_learning_agent.py --topic "ITAR"

# 4. Test new sources
python3 scripts/vector/semantic_search.py "ITAR compliance" --top-k 5

# 5. Deploy to production (via normal release)
git add config/sources.yaml ingested/
git commit -m "Add ITAR compliance sources (prod gap #123)"
git push

# 6. Mark gap as resolved
python3 scripts/automation/knowledge_gap_manager.py --resolve "2025-12-29T10:30:00Z"
```

### Weekly Gap Report

```bash
# Generate report for stakeholders
cat logs/production_gaps_queue.jsonl | \
  python3 -c "
import sys, json
from collections import Counter

gaps = [json.loads(line) for line in sys.stdin]
topics = Counter(g['topic'] for g in gaps)

print('📊 Top Knowledge Gaps This Week:')
for topic, count in topics.most_common(10):
    print(f'  {count}x {topic}')
"
```

## Monitoring & Alerts

### Slack Integration

Configure in `.env.production`:

```bash
TEAMS_WEBHOOK_URL=https://YOUR-TENANT.webhook.office.com/webhookb2/YOUR-WEBHOOK-ID
```

Notifications appear in `#knowledge-gaps` channel:

- Real-time gap detection
- Customer context included
- Queue position tracked

### API Integration

Configure dev environment API:

```bash
DEV_KNOWLEDGE_API=https://dev.fredesa.com/api
```

Production posts gaps to dev API:

```http
POST /knowledge-gaps
Content-Type: application/json

{
  "topic": "ITAR compliance",
  "customer_id": "uuid",
  "priority": "high"
}
```

Dev API can:
- Trigger automated ingestion pipeline
- Create Jira tickets
- Update gap dashboard

## Benefits

### Development Benefits

✅ **Rapid Learning**: Gaps auto-ingest immediately
✅ **No Manual Process**: Autonomous agent handles discovery
✅ **Experimentation**: Safe to test with untrusted sources
✅ **Feedback Loop**: Quick iteration on knowledge base

### Production Benefits

✅ **Security-First**: No customer-triggered ingestion
✅ **OWASP Compliant**: Broken authorization prevented
✅ **Tenant Isolation**: No cross-customer data leakage
✅ **Auditability**: All gaps logged with customer context
✅ **Continuous Learning**: Dev team stays informed of real needs

### Customer Benefits

✅ **Improved Coverage**: Real customer needs drive knowledge expansion
✅ **Transparent Process**: "We're reviewing this area" messaging
✅ **No Tier Bypass**: Cannot circumvent access controls
✅ **Quality Assurance**: Human review before production deployment

## Migration Guide

### Update Copilot Instructions

```bash
# .github/copilot-instructions.md

## Knowledge Gap Detection (PRODUCTION-SAFE)

**Development Environment:**
- Auto-ingestion enabled (safe single-tenant)
- Rapid learning for testing and experimentation

**Production Environment:**
- Auto-ingestion DISABLED (OWASP compliance)
- Gaps logged + dev team notified
- Human review required before ingestion

**Usage:**
\`\`\`python
from scripts.automation.knowledge_gap_manager import KnowledgeGapManager

gap_manager = KnowledgeGapManager()  # Auto-detects environment

result = gap_manager.detect_gap(
    topic="New topic",
    keywords=["new", "topic"],
    customer_id="uuid"  # Production only
)
\`\`\`
```

### Update MCP Server

See integration example above in "Integration with MCP Server" section.

---

**Status**: ✅ Production-ready security pattern
**Compliance**: OWASP API5, NIST AC-3, AWS SaaS Lens
**Last Updated**: December 29, 2025
