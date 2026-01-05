# Rollback Procedures
**FreDeSa AI Platform - All Environments**

Last Updated: January 5, 2026

---

## 🎯 Purpose

This document provides step-by-step rollback procedures for all environments. Rollbacks restore the system to a previous working state when deployments fail or critical issues are discovered.

**Key Principle:** When in doubt, rollback. It's better to be cautious than to leave production broken.

---

## 🚨 When to Rollback

### Immediate Rollback Required

Execute rollback **immediately** if any of these occur:

**Critical Issues:**
- ❌ Complete service outage (site down, API unresponsive)
- ❌ Data corruption or data loss detected
- ❌ Security vulnerability exposed
- ❌ Payment processing failures
- ❌ Authentication system broken (users can't login)

**High Severity:**
- ❌ Error rate > 5% sustained for 5+ minutes
- ❌ Response time degradation > 100% (2x slower)
- ❌ Database connection failures
- ❌ Critical feature completely broken
- ❌ Multiple customer escalations

**Business Impact:**
- ❌ Revenue-generating features broken
- ❌ SLA violations occurring
- ❌ Compliance violations detected
- ❌ Negative PR/social media attention

### Consider Rollback

Evaluate rollback if:

- ⚠️ Error rate 1-5%
- ⚠️ Performance degradation 50-100%
- ⚠️ Non-critical features broken
- ⚠️ Isolated customer reports
- ⚠️ Monitoring alerts firing

**Decision Criteria:**
- Can issue be fixed forward quickly (< 30 min)?
- Is workaround available for users?
- What's the blast radius (how many users affected)?

### Monitor and Proceed

Continue monitoring if:

- ✅ Error rate < 1%
- ✅ Performance within normal range
- ✅ All critical features working
- ✅ No customer complaints
- ✅ Metrics stable

---

## 🔄 Rollback Methods

### Method 1: Automated Rollback (CI/CD)

**When:** CI/CD health checks fail during deployment

**How:** Automatic - no action needed

**Details:**
- GitHub Actions workflow automatically detects failures
- Activates previous container app revision
- Restores both backend and frontend
- Sends notification to team

**Verify:**
```bash
# Check rollback completed
az containerapp revision list \
  --name fredesa-api \
  --resource-group rg-fredesa-[env] \
  --query "[?properties.active==\`true\`].{Name:name,Created:properties.createdTime}"
```

### Method 2: Manual Rollback (Azure CLI)

**When:** Issues discovered after deployment completes

**How:** Execute commands below

**Time:** < 5 minutes

#### Test Environment

```bash
# Backend rollback
az containerapp revision activate \
  --name fredesa-api-test \
  --resource-group rg-fredesa-dev \
  --revision $(az containerapp revision list \
    --name fredesa-api-test \
    --resource-group rg-fredesa-dev \
    --query "[1].name" -o tsv)

# Frontend rollback
az containerapp revision activate \
  --name fredesa-web-test \
  --resource-group rg-fredesa-dev \
  --revision $(az containerapp revision list \
    --name fredesa-web-test \
    --resource-group rg-fredesa-dev \
    --query "[1].name" -o tsv)

# Verify
curl https://fredesa-api-test.eastus.azurecontainerapps.io/health
```

#### Staging Environment

```bash
# Backend rollback
az containerapp revision activate \
  --name fredesa-api-staging \
  --resource-group rg-fredesa-staging \
  --revision $(az containerapp revision list \
    --name fredesa-api-staging \
    --resource-group rg-fredesa-staging \
    --query "[1].name" -o tsv)

# Frontend rollback
az containerapp revision activate \
  --name fredesa-web-staging \
  --resource-group rg-fredesa-staging \
  --revision $(az containerapp revision list \
    --name fredesa-web-staging \
    --resource-group rg-fredesa-staging \
    --query "[1].name" -o tsv)

# Verify
curl https://fredesa-api-staging.eastus.azurecontainerapps.io/health
```

#### Production Environment

```bash
# ⚠️ PRODUCTION ROLLBACK - REQUIRES APPROVAL

# 1. Get rollback target
echo "Previous revisions:"
az containerapp revision list \
  --name fredesa-api \
  --resource-group rg-fredesa-prod \
  --query "[0:3].{Name:name,Created:properties.createdTime,Traffic:properties.trafficWeight}"

# 2. Confirm with team lead before proceeding
read -p "Approved by [NAME]? (yes/no): " approval
if [ "$approval" != "yes" ]; then
  echo "Rollback cancelled"
  exit 1
fi

# 3. Execute backend rollback
az containerapp revision activate \
  --name fredesa-api \
  --resource-group rg-fredesa-prod \
  --revision $(az containerapp revision list \
    --name fredesa-api \
    --resource-group rg-fredesa-prod \
    --query "[1].name" -o tsv)

# 4. Execute frontend rollback
az containerapp revision activate \
  --name fredesa-web \
  --resource-group rg-fredesa-prod \
  --revision $(az containerapp revision list \
    --name fredesa-web \
    --resource-group rg-fredesa-prod \
    --query "[1].name" -o tsv)

# 5. Verify immediately
curl https://api.fredesa.com/health
curl -I https://app.fredesa.com

# 6. Monitor for 5 minutes
watch -n 10 'curl -s https://api.fredesa.com/health | jq'
```

### Method 3: Git Revert and Redeploy

**When:** Rollback via Azure fails or multiple revisions need to be skipped

**How:** Revert git commits and trigger new deployment

**Time:** 10-15 minutes

```bash
# 1. Identify problem commit
git log --oneline -10

# 2. Revert commit (creates new commit)
git revert <commit-hash>

# 3. Push to trigger redeployment
git push origin main  # (or develop for test)

# 4. Monitor GitHub Actions
# Go to: https://github.com/rdenz-solutions/fredesa-ai-platform/actions

# 5. Verify after deployment
curl https://api.fredesa.com/health
```

### Method 4: Database Rollback

**When:** Database migration causes issues

**How:** Restore from backup or run down migration

**⚠️ CRITICAL:** Only use for test/staging unless absolute emergency

#### Option A: Rollback Migration (Preferred)

```bash
# If your migrations support down migrations
az containerapp exec \
  --name fredesa-api-[env] \
  --resource-group rg-fredesa-[env] \
  --command "python scripts/database/rollback_migration.py --steps 1"
```

#### Option B: Restore from Backup (Production Only)

```bash
# List available backups
az postgres flexible-server backup list \
  --name fredesa-db-prod \
  --resource-group rg-fredesa-prod

# Restore from backup (CREATES NEW SERVER)
az postgres flexible-server restore \
  --name fredesa-db-prod-restored \
  --resource-group rg-fredesa-prod \
  --source-server fredesa-db-prod \
  --restore-time "2026-01-05T12:00:00Z"

# Update connection strings to point to restored database
# This requires application redeployment
```

---

## 📋 Rollback Checklist

### Pre-Rollback

- [ ] Confirm rollback is necessary (severity assessment)
- [ ] Notify team in #engineering Slack
- [ ] Get approval if production (from tech lead/CTO)
- [ ] Document reason for rollback
- [ ] Take snapshot of current state (logs, metrics)

### During Rollback

- [ ] Execute rollback commands
- [ ] Verify health endpoints
- [ ] Check error rates
- [ ] Test critical functionality
- [ ] Monitor for 5-10 minutes

### Post-Rollback

- [ ] Update status page
- [ ] Notify stakeholders
- [ ] Notify customers (if production and user-facing)
- [ ] Create incident ticket
- [ ] Document what happened
- [ ] Schedule postmortem

---

## 🔍 Verification Steps

After any rollback, verify these:

### 1. Health Checks
```bash
# All environments should return {"status": "healthy"}
curl https://fredesa-api-test.eastus.azurecontainerapps.io/health
curl https://fredesa-api-staging.eastus.azurecontainerapps.io/health
curl https://api.fredesa.com/health
```

### 2. Critical Endpoints
```bash
# Test authentication
curl -X POST https://api.fredesa.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test data retrieval
curl https://api.fredesa.com/api/v1/customers
```

### 3. Frontend Loading
- Visit application URL
- Verify login page loads
- Test user login
- Check dashboard displays

### 4. Database Connectivity
```bash
# Check active connections
az postgres flexible-server show \
  --name fredesa-db-[env] \
  --resource-group rg-fredesa-[env]
```

### 5. Error Rates
```kusto
// Application Insights query
requests
| where timestamp > ago(10m)
| summarize 
    Total = count(),
    Errors = countif(success == false),
    ErrorRate = 100.0 * countif(success == false) / count()
```

---

## 📊 Post-Rollback Monitoring

### First 30 Minutes

Monitor these metrics closely:

**Success Criteria:**
- Error rate < 1%
- Response time back to baseline
- No new exceptions
- Customer complaints stop
- All critical features working

**If Issues Persist:**
- May need to rollback further (multiple versions)
- Database may need attention
- Cache may need clearing
- DNS propagation may be needed

### Monitoring Commands

```bash
# Watch health endpoint
watch -n 30 'curl -s https://api.fredesa.com/health | jq'

# Monitor error rate
az monitor metrics list \
  --resource /subscriptions/.../fredesa-api \
  --metric "Requests" \
  --interval PT1M \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## 🚨 Escalation Path

If rollback doesn't resolve the issue:

**Level 1:** On-Call Engineer (15 minutes)
- Attempt rollback
- Verify and monitor
- Document issue

**Level 2:** Tech Lead (if issues persist after 30 min)
- Review logs and metrics
- Make architectural decisions
- Approve emergency fixes

**Level 3:** CTO (if major outage > 1 hour)
- Customer communication
- Business continuity decisions
- External escalation if needed

**External:** Cloud Provider Support (Azure)
- If infrastructure issues suspected
- If rollback capabilities not working
- If regional outage

---

## 📝 Rollback Documentation Template

After every rollback, create: `docs/deployment/logs/rollback-YYYY-MM-DD.md`

```markdown
# Rollback - YYYY-MM-DD HH:MM

**Environment:** Test / Staging / Production
**Version Rolled Back:** v1.2.3
**Rolled Back To:** v1.2.2
**Duration:** X minutes
**Executed By:** @username
**Approved By:** @username (if production)

## Reason for Rollback
[Detailed description of issue]

## Severity Assessment
- Impact: Critical / High / Medium / Low
- Users Affected: X% / X users
- Features Broken: [List]
- Duration Before Rollback: X minutes

## Rollback Method Used
- [ ] Automated (CI/CD)
- [ ] Manual (Azure CLI)
- [ ] Git Revert + Redeploy
- [ ] Database Restore

## Verification Results
- [ ] Health checks: PASS
- [ ] Critical endpoints: PASS
- [ ] Frontend: PASS
- [ ] Error rate: < 1%
- [ ] Performance: Normal

## Post-Rollback Status
- System Stable: Yes / No
- Issues Resolved: Yes / Partially / No
- Additional Actions Needed: [List]

## Root Cause (Preliminary)
[What went wrong]

## Lessons Learned
- What should we have caught? [Description]
- Process improvements: [List]
- Monitoring gaps: [List]

## Action Items
- [ ] Fix underlying issue - @owner - Due: DATE
- [ ] Add regression test - @owner - Due: DATE
- [ ] Update deployment checklist - @owner - Due: DATE
- [ ] Schedule postmortem - @owner - Due: DATE

## References
- Incident ticket: [LINK]
- Metrics: [LINK]
- Logs: [LINK]
```

---

## 🎓 Common Scenarios

### Scenario 1: API Returns 500 Errors

**Symptoms:** High error rate, 500 responses

**Likely Cause:**
- Code bug
- Database connection issue
- Missing environment variable

**Rollback Decision:** YES - Execute immediately

**Steps:**
1. Rollback application (Method 2)
2. Verify error rate drops
3. Investigate logs
4. Fix and redeploy

### Scenario 2: Slow Performance

**Symptoms:** Response times 2-3x normal

**Likely Cause:**
- Inefficient query
- Memory leak
- Resource exhaustion

**Rollback Decision:** EVALUATE - Check severity

**Steps:**
1. Check if worsening (rollback if yes)
2. Check resource usage
3. If stable but slow, may fix forward
4. If degrading, rollback

### Scenario 3: Frontend Won't Load

**Symptoms:** Blank page, JavaScript errors

**Likely Cause:**
- Build error
- API URL misconfigured
- CORS issue

**Rollback Decision:** YES - User-facing outage

**Steps:**
1. Rollback frontend only (Method 2)
2. Verify page loads
3. Check browser console
4. Fix and redeploy

### Scenario 4: Database Migration Failed

**Symptoms:** App starts but queries fail

**Likely Cause:**
- Migration syntax error
- Schema conflict
- Missing constraint

**Rollback Decision:** YES - Data layer broken

**Steps:**
1. Rollback application
2. Run down migration (Method 4)
3. Verify database state
4. Fix migration script
5. Test in test environment
6. Redeploy

---

## 🔐 Security Considerations

**Production Rollback Access:**
- Restricted to senior engineers only
- Requires two-person approval for production
- All rollbacks logged and audited
- Azure RBAC enforced

**Audit Trail:**
- All rollback commands logged
- GitHub Actions logs preserved
- Azure activity logs retained
- Postmortem documents required

---

## ✅ Prevention is Better Than Rollback

**To minimize rollbacks:**

1. **Test Thoroughly**
   - 100% passing tests required
   - Staging validation for 24+ hours
   - Load testing before production

2. **Deploy Gradually**
   - Test → Staging → Production
   - Blue-green deployments
   - Feature flags for risky changes

3. **Monitor Proactively**
   - Real-time alerting
   - Automated health checks
   - Application Insights dashboards

4. **Learn from Failures**
   - Postmortems after every rollback
   - Update checklists
   - Add regression tests

---

**Last Updated:** January 5, 2026  
**Owner:** DevOps Team  
**Emergency Contact:** @on-call-engineer

---

**Remember:** A fast rollback is better than a slow fix. When in doubt, roll it back.
