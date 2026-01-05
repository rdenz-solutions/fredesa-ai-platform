# Production Deployment Checklist
**FreDeSa AI Platform - Production Environment**

Last Updated: January 5, 2026  
Environment: `production` (fredesa-db-prod.postgres.database.azure.com)

---

## 🚨 CRITICAL: Production Deployment Requirements

Production deployments require **explicit approval** and must follow this checklist completely. No exceptions.

**Minimum Requirements:**
- ✅ Staging deployment successful for 24+ hours
- ✅ All automated tests passing
- ✅ Security scans clean (no CRITICAL/HIGH findings)
- ✅ Rollback procedure validated
- ✅ On-call engineer assigned and available
- ✅ Customer communication prepared (if user-facing changes)

---

## 📋 Pre-Deployment Checklist (48 Hours Before)

### Code Quality & Testing
- [ ] All CI/CD tests passing (100% pass rate required)
- [ ] Code coverage ≥ 80%
- [ ] Security scans clean (OWASP, Dependabot, CodeQL)
- [ ] Load testing passed (handle expected traffic + 50%)
- [ ] E2E tests passing in staging
- [ ] No known critical/high bugs

### Version Control
- [ ] Code merged to `main` branch
- [ ] Release tag created (semantic versioning: `v1.2.3`)
- [ ] CHANGELOG.md complete with all changes
- [ ] Release notes finalized
- [ ] Migration scripts reviewed and tested

### Staging Validation
- [ ] Staging deployment successful ≥24 hours
- [ ] No errors in Application Insights (staging)
- [ ] Performance metrics acceptable (staging)
- [ ] Stakeholder sign-off received
- [ ] User acceptance testing complete

### Database
- [ ] Database migrations tested in staging
- [ ] Backup strategy verified (automated daily backups)
- [ ] Rollback scripts prepared and tested
- [ ] Data migration plan documented (if applicable)
- [ ] No schema changes affecting existing queries (or coordinated)

### Infrastructure
- [ ] Azure resources provisioned (if new)
- [ ] SSL certificates valid (≥30 days remaining)
- [ ] DNS configured correctly
- [ ] CDN configured (if applicable)
- [ ] WAF rules updated (if needed)

### Security
- [ ] Secrets rotated (if scheduled)
- [ ] Security audit passed
- [ ] Compliance requirements met (SOC 2, GDPR, etc.)
- [ ] Third-party integrations validated
- [ ] Rate limiting configured

### Team Coordination
- [ ] Deployment window scheduled (Friday 5-7 PM ET recommended)
- [ ] All stakeholders notified
- [ ] On-call schedule confirmed (24-hour coverage)
- [ ] Rollback plan communicated
- [ ] Customer support team briefed
- [ ] Monitoring alerts validated

### Communication
- [ ] Customer notification drafted (if user-facing changes)
- [ ] Status page updated (schedule planned maintenance window)
- [ ] Internal announcement prepared
- [ ] Support documentation updated

---

## 🎯 Deployment Window Planning

### Recommended Timing
- **Best:** Friday 5-7 PM ET (off-hours, before weekend monitoring)
- **Avoid:** Monday AM (high traffic), major holidays, during sales campaigns

### Deployment Team Roles
- **Deployment Lead:** Executes deployment, makes go/no-go decisions
- **Database Lead:** Monitors database, handles migrations
- **Frontend Lead:** Monitors web app, handles frontend issues
- **On-Call Engineer:** Available for 24h post-deployment
- **Product Manager:** Stakeholder communication, rollback approval

---

## 🚀 Deployment Process

### Phase 1: Pre-Deployment (30 minutes before)

```bash
# 1. Verify all systems operational
curl https://api.fredesa.com/health
# Expected: {"status": "healthy"}

# 2. Check current production metrics
az monitor metrics list \
  --resource /subscriptions/.../fredesa-api \
  --metric "Requests,Errors,ResponseTime" \
  --interval PT5M

# 3. Create pre-deployment backup
# (Automated Azure Database backups run daily)
# Verify latest backup exists:
az postgres flexible-server backup list \
  --name fredesa-db-prod \
  --resource-group rg-fredesa-prod

# 4. Record current state
CURRENT_BACKEND_REVISION=$(az containerapp revision list \
  --name fredesa-api \
  --resource-group rg-fredesa-prod \
  --query "[?properties.active==\`true\`].name" -o tsv)

CURRENT_FRONTEND_REVISION=$(az containerapp revision list \
  --name fredesa-web \
  --resource-group rg-fredesa-prod \
  --query "[?properties.active==\`true\`].name" -o tsv)

echo "Rollback targets:"
echo "Backend: $CURRENT_BACKEND_REVISION"
echo "Frontend: $CURRENT_FRONTEND_REVISION"
```

### Phase 2: Deployment Execution

**Via GitHub Actions:**

1. Go to: Actions → Deploy to Production
2. Click "Run workflow"
3. Fill in inputs:
   - **Version:** `v1.2.3` (must be a tagged release, NOT "latest")
   - **Reason:** "[Feature/Release name] - Production deployment"
   - **Skip smoke tests:** `false` (only use in emergencies)
4. Click "Run workflow"

**Manual Approval Required:**
- GitHub Environment protection requires manual approval
- Approver reviews checklist and deployment reason
- Click "Approve and deploy" to proceed

**Expected Duration:** 10-15 minutes

### Phase 3: Monitor Deployment (Real-Time)

**Monitor Multiple Channels:**

1. **GitHub Actions Workflow**
   - Watch each step complete
   - Review logs for any warnings

2. **Azure Portal**
   - Container Apps → Watch revision creation
   - Monitor CPU/Memory usage
   - Check for any errors

3. **Application Insights**
   - Watch for error spikes
   - Monitor response times
   - Check dependency failures

4. **Application Endpoints**
   ```bash
   # Backend health (check every 30 seconds)
   watch -n 30 'curl -s https://api.fredesa.com/health | jq'
   
   # Frontend (check loads)
   curl -I https://app.fredesa.com
   ```

### Phase 4: Post-Deployment Validation (15-30 minutes)

#### Automated Validation (CI/CD Runs)
- [x] Health checks passed
- [x] Smoke tests passed
- [x] Blue-green deployment successful
- [x] Previous revision available for rollback

#### Manual Validation Checklist

**1. Backend Validation (5 minutes)**
```bash
# Health endpoint
curl https://api.fredesa.com/health

# API documentation
open https://api.fredesa.com/docs

# Test authentication
curl -X POST https://api.fredesa.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"production-test@fredesa.com","password":"..."}'

# Test critical endpoints (customize for your app)
curl https://api.fredesa.com/api/v1/customers
curl https://api.fredesa.com/api/v1/agents
```

**2. Frontend Validation (5 minutes)**
- [ ] Visit https://app.fredesa.com
- [ ] Login successful
- [ ] Dashboard loads
- [ ] Navigation works
- [ ] Forms submit correctly
- [ ] Data displays from API
- [ ] No console errors (check DevTools)

**3. Database Validation (5 minutes)**
```bash
# Check connection count
az postgres flexible-server show \
  --name fredesa-db-prod \
  --resource-group rg-fredesa-prod

# Verify migrations (check app logs)
az containerapp logs show \
  --name fredesa-api \
  --resource-group rg-fredesa-prod \
  --tail 50 | grep "migration"
```

**4. Integration Validation (10 minutes)**
- [ ] Payment processing (Stripe) - Test transaction
- [ ] Email notifications - Send test email
- [ ] Azure AD authentication - Test SSO login
- [ ] Third-party APIs - Verify connections
- [ ] Webhooks - Trigger test webhook

**5. Performance Validation (5 minutes)**
```bash
# Test response times
for i in {1..10}; do
  curl -w "\nTime: %{time_total}s\n" -o /dev/null -s https://api.fredesa.com/health
done

# Average should be < 200ms
```

---

## 📊 Post-Deployment Monitoring (Critical First Hour)

### Metrics to Watch

**Application Insights:**
```kusto
// Error rate (should be < 0.1%)
requests
| where timestamp > ago(1h)
| summarize 
    Total = count(),
    Errors = countif(success == false),
    ErrorRate = 100.0 * countif(success == false) / count()
| where ErrorRate > 0.1

// Response time (should be < 300ms p95)
requests
| where timestamp > ago(1h)
| summarize p95=percentile(duration, 95), p99=percentile(duration, 99)

// Exceptions
exceptions
| where timestamp > ago(1h)
| summarize count() by type
| order by count_ desc
```

**Azure Monitor:**
- CPU usage < 60%
- Memory usage < 75%
- Active connections < 80% of max
- No container restarts

**Business Metrics:**
- User login success rate ≥ 99%
- API request success rate ≥ 99.9%
- Page load time < 2s
- No customer-reported issues

---

## 🚨 Go/No-Go Decision Points

### Proceed if:
- ✅ All health checks passing
- ✅ Error rate < 0.1%
- ✅ Response times normal (within 10% of pre-deployment)
- ✅ No critical exceptions
- ✅ Business metrics stable

### ROLLBACK if:
- ❌ Error rate > 1%
- ❌ Any critical functionality broken
- ❌ Database corruption detected
- ❌ Security vulnerability exposed
- ❌ Response times degraded > 50%
- ❌ Multiple customer complaints
- ❌ Payment processing failure

---

## 🔄 Rollback Procedure

### Immediate Rollback (< 5 minutes)

**Automated rollback triggers:**
- Health check failures → CI/CD auto-rolls back
- Smoke test failures → CI/CD auto-rolls back

**Manual rollback command:**
```bash
# EXECUTE IMMEDIATELY if critical issue detected

# Get previous revision
ROLLBACK_REVISION=$(az containerapp revision list \
  --name fredesa-api \
  --resource-group rg-fredesa-prod \
  --query "[1].name" -o tsv)

# Activate previous backend revision
az containerapp revision activate \
  --name fredesa-api \
  --resource-group rg-fredesa-prod \
  --revision $ROLLBACK_REVISION

# Activate previous frontend revision
ROLLBACK_REVISION_FE=$(az containerapp revision list \
  --name fredesa-web \
  --resource-group rg-fredesa-prod \
  --query "[1].name" -o tsv)

az containerapp revision activate \
  --name fredesa-web \
  --resource-group rg-fredesa-prod \
  --revision $ROLLBACK_REVISION_FE

# Verify rollback successful
curl https://api.fredesa.com/health
```

### Post-Rollback Actions

1. **Immediate (< 15 minutes):**
   - Notify all stakeholders
   - Update status page
   - Post in #engineering + #customer-success Slack
   - Document rollback reason

2. **Within 1 hour:**
   - Create incident ticket
   - Begin root cause analysis
   - Review logs and metrics
   - Identify what went wrong

3. **Within 24 hours:**
   - Complete incident postmortem
   - Fix identified issues
   - Add regression tests
   - Plan re-deployment

4. **Before retry:**
   - Issue reproduced and fixed in test
   - Additional monitoring added
   - Deployment checklist updated
   - Team retrospective completed

---

## 📢 Communication Plan

### Pre-Deployment Communication

**24 Hours Before:**
```
Subject: Production Deployment Scheduled - [Feature Name]

Team,

We have a production deployment scheduled for:
Date: Friday, [DATE]
Time: 5:00-7:00 PM ET
Version: v1.2.3
Duration: ~15 minutes

Changes:
- [List key features/fixes]

Impact: [None expected / Brief downtime / Feature unavailable]

Rollback plan: Available if needed

Questions? Reply to this email or Slack #engineering.

- Deployment Team
```

**If User-Facing Changes:**
```
Subject: [Product Name] Update - New Features Coming [DATE]

Dear [Customer Name],

We're excited to announce new features coming to [Product Name] on [DATE]:

What's New:
- [Feature 1]: [Benefit]
- [Feature 2]: [Benefit]

When: Friday, [DATE] at 5:00 PM ET
Duration: ~15 minutes
Impact: No disruption expected

We'll send a follow-up once the update is complete.

Questions? Contact support@fredesa.com

Thank you,
The FreDeSa Team
```

### Post-Deployment Communication

**Success:**
```
✅ PRODUCTION DEPLOYMENT SUCCESSFUL

Version: v1.2.3
Deployed: [TIMESTAMP]
Duration: [X] minutes

All systems operational. No issues detected.

Monitor: [Application Insights Link]
```

**Rollback:**
```
⚠️ PRODUCTION DEPLOYMENT ROLLED BACK

Version attempted: v1.2.3
Rollback completed: [TIMESTAMP]
Reason: [Brief description]

Production is stable on previous version.

Incident ticket: [LINK]
Postmortem: TBD

All hands meeting: [TIME]
```

---

## 🎓 Lessons Learned Template

After each production deployment (success or failure), document:

```markdown
# Production Deployment Postmortem - v1.2.3

**Date:** YYYY-MM-DD
**Outcome:** Success / Rollback
**Duration:** X minutes

## What Went Well
- [List successes]

## What Went Wrong
- [List issues]

## Root Cause
- [Detailed analysis]

## Action Items
- [ ] [Item 1] - Owner: @username - Due: DATE
- [ ] [Item 2] - Owner: @username - Due: DATE

## Process Improvements
- Update checklist: [Description]
- Add monitoring: [Description]
- Improve testing: [Description]

## References
- Incident ticket: [LINK]
- Metrics dashboard: [LINK]
- Related commits: [LINKS]
```

---

## ✅ Final Checklist

Before marking deployment complete:

- [ ] All validation checks passed
- [ ] Monitoring active and alerts configured
- [ ] No errors in first hour
- [ ] Performance metrics stable
- [ ] Customer communication sent (if applicable)
- [ ] Team notified of success
- [ ] Documentation updated
- [ ] Deployment log created
- [ ] On-call engineer briefed
- [ ] Status page updated (maintenance complete)

---

## 🔐 Security & Compliance

- [ ] Production secrets rotated regularly (90-day cycle)
- [ ] Audit logs enabled and monitored
- [ ] Compliance attestations current (SOC 2, GDPR, etc.)
- [ ] Security contacts notified of changes
- [ ] Vulnerability scanning post-deployment
- [ ] Access logs reviewed

---

## 📞 Emergency Contacts

**Deployment Lead:** [Name] - [Phone/Slack]  
**Database Lead:** [Name] - [Phone/Slack]  
**On-Call Engineer:** [Name] - [Phone/Slack]  
**CTO/Tech Lead:** [Name] - [Phone/Slack]  
**Customer Success:** [Team Channel]

**Escalation Path:**
1. On-Call Engineer
2. Deployment Lead
3. Tech Lead/CTO

---

**Last Updated:** January 5, 2026  
**Owner:** DevOps Team  
**Review Frequency:** After every production deployment  
**Next Review:** After next deployment

---

**⚠️ REMEMBER:** Production deployments are serious business. When in doubt, rollback and investigate. Better to delay than to break production.
