# Staging Environment Deployment Checklist
**FreDeSa AI Platform - Staging Environment**

Last Updated: January 5, 2026  
Environment: `staging` (fredesa-db-staging.postgres.database.azure.com)

---

## 🎯 Purpose

Staging is the final validation environment before production. It mirrors production configuration and is used for final testing, stakeholder demos, and pre-release validation.

---

## 📋 Pre-Deployment Checklist

### Prerequisites
- [ ] Test environment deployment successful
- [ ] All CI/CD tests passing
- [ ] Security scans clean (no CRITICAL/HIGH vulnerabilities)
- [ ] Code review approved by 2+ engineers
- [ ] QA testing complete in test environment
- [ ] Stakeholder demo scheduled (if applicable)

### Version Control
- [ ] Code merged to `main` branch
- [ ] Git tag created for release version (e.g., `v1.2.3`)
- [ ] CHANGELOG.md updated with release notes
- [ ] Release notes drafted (for production deployment)

### Database
- [ ] Database migrations validated in test
- [ ] Data migration scripts tested (if applicable)
- [ ] Rollback scripts prepared
- [ ] Staging database backed up

### Configuration
- [ ] `.env.staging` variables verified
- [ ] Feature flags configured for staging
- [ ] Third-party API keys valid (staging credentials)
- [ ] Azure AD staging app registration configured

### Team Coordination
- [ ] Deployment scheduled (avoid business hours if possible)
- [ ] Stakeholders notified of deployment window
- [ ] On-call engineer assigned
- [ ] Rollback plan communicated to team

---

## 🚀 Deployment Process

### 1. Create Release Tag

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Create semantic version tag
git tag -a v1.2.3 -m "Release v1.2.3: [Brief description]"
git push origin v1.2.3
```

### 2. Trigger Deployment

**Via GitHub Actions:**
1. Go to: Actions → Deploy to Staging Environment
2. Click "Run workflow"
3. Fill in inputs:
   - **Version:** `v1.2.3` (the tag you just created)
   - **Reason:** "Staging deployment for [feature/release name]"
4. Click "Run workflow"

### 3. Monitor Deployment

**Expected Duration:** 8-10 minutes

**Monitor:**
- GitHub Actions workflow progress
- Azure Portal → Container Apps (watch revision creation)
- Application Insights (watch for errors)

### 4. Automated Blue-Green Deployment

The workflow automatically:
1. Builds new Docker images
2. Pushes to Azure Container Registry
3. Creates new container app revision
4. Runs health checks
5. Activates new revision if healthy
6. Keeps previous revision for rollback

---

## ✅ Post-Deployment Validation

### Automated Checks (Run by CI/CD)
- [x] Health endpoint responding
- [x] Smoke tests passed
- [x] No deployment errors
- [x] Previous revision available for rollback

### Manual Validation (15 minutes)

#### 1. Backend Validation
```bash
# Health check
curl https://fredesa-api-staging.eastus.azurecontainerapps.io/health

# API docs
open https://fredesa-api-staging.eastus.azurecontainerapps.io/docs

# Test critical endpoints
curl -X POST https://fredesa-api-staging.eastus.azurecontainerapps.io/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

#### 2. Frontend Validation
- Visit: https://fredesa-web-staging.eastus.azurecontainerapps.io
- Test user flows:
  - [ ] Login/authentication
  - [ ] Dashboard loading
  - [ ] Navigation between pages
  - [ ] Form submissions
  - [ ] Data fetching from API

#### 3. Database Validation
```bash
# Check database connectivity
az postgres flexible-server show \
  --name fredesa-db-staging \
  --resource-group rg-fredesa-staging

# Verify migrations ran
# (Check application logs for migration success messages)
```

#### 4. Integration Testing
- [ ] Run Playwright E2E tests against staging
- [ ] Test third-party integrations (Stripe test mode, Azure AD, etc.)
- [ ] Verify email notifications (use test email addresses)
- [ ] Test file uploads/downloads

#### 5. Performance Check
- [ ] API response times < 500ms (p95)
- [ ] Frontend load time < 2s
- [ ] Database query performance acceptable
- [ ] No memory leaks (monitor for 30 minutes)

---

## 🐛 Troubleshooting

### Deployment Failed - Health Checks Failed

**Symptoms:** Workflow fails at "Run health checks" step

**Investigation:**
```bash
# Check container logs
az containerapp logs show \
  --name fredesa-api-staging \
  --resource-group rg-fredesa-staging \
  --tail 200

# Check recent revisions
az containerapp revision list \
  --name fredesa-api-staging \
  --resource-group rg-fredesa-staging
```

**Common Issues:**
1. Database connection failure → Check connection string
2. Missing environment variable → Verify all required vars set
3. Migration failed → Check migration logs, may need manual intervention

**Resolution:** Fix issue and redeploy, or rollback if critical

### Deployment Succeeded But Features Not Working

**Symptoms:** Deployment successful but specific features broken

**Investigation:**
1. Check Application Insights → Failures blade
2. Review browser console for JavaScript errors
3. Check API logs for 500 errors
4. Verify feature flags are correct

**Resolution:**
- If minor issue: Create hotfix, deploy to staging
- If major issue: Rollback and investigate in test environment

### Performance Degradation

**Symptoms:** Staging slower than test environment

**Investigation:**
```bash
# Check resource usage
az monitor metrics list \
  --resource /subscriptions/.../fredesa-api-staging \
  --metric "CpuPercentage,MemoryPercentage" \
  --interval PT1M

# Check database performance
az postgres flexible-server show \
  --name fredesa-db-staging \
  --resource-group rg-fredesa-staging \
  --query "{cpu:cpuPercent,memory:memoryPercent}"
```

**Common Causes:**
1. Database needs indexing → Run `ANALYZE` on tables
2. Missing connection pooling → Verify PgBouncer configured
3. Inefficient queries → Check slow query log

---

## 🔄 Rollback Procedure

### When to Rollback

Rollback immediately if:
- Critical feature broken
- Security vulnerability exposed
- Data corruption detected
- Performance degradation > 50%
- Multiple user-reported issues

### Automated Rollback (Preferred)

The CI/CD workflow automatically rolls back if health checks fail. Manual rollback if needed:

```bash
# List revisions
az containerapp revision list \
  --name fredesa-api-staging \
  --resource-group rg-fredesa-staging \
  --query "[].{Name:name, Active:properties.active, Traffic:properties.trafficWeight}"

# Activate previous revision
PREVIOUS_REVISION=$(az containerapp revision list \
  --name fredesa-api-staging \
  --resource-group rg-fredesa-staging \
  --query "[1].name" -o tsv)

az containerapp revision activate \
  --name fredesa-api-staging \
  --resource-group rg-fredesa-staging \
  --revision $PREVIOUS_REVISION

# Verify rollback
curl https://fredesa-api-staging.eastus.azurecontainerapps.io/health
```

### Post-Rollback Actions

1. **Immediate:**
   - Notify team in #engineering Slack
   - Document rollback reason
   - Create incident postmortem ticket

2. **Within 24 hours:**
   - Root cause analysis
   - Fix identified issues in test environment
   - Plan re-deployment

3. **Before retry:**
   - All tests passing
   - Issue reproduced and fixed
   - Additional test coverage added
   - Team briefed on changes

---

## 📊 Monitoring & Alerts

### Critical Metrics (Monitor for 1 Hour)

1. **Error Rate**
   - Target: < 0.5%
   - Alert threshold: > 1%

2. **Response Time**
   - Target: < 300ms p95
   - Alert threshold: > 500ms p95

3. **Availability**
   - Target: 99.9%
   - Alert threshold: < 99.5%

4. **Database**
   - Connection pool utilization < 70%
   - Query time < 100ms p95

### Application Insights Queries

```kusto
// Error rate (last hour)
requests
| where timestamp > ago(1h)
| summarize 
    Total = count(),
    Errors = countif(success == false),
    ErrorRate = 100.0 * countif(success == false) / count()

// Slowest endpoints
requests
| where timestamp > ago(1h)
| summarize p95=percentile(duration, 95) by name
| order by p95 desc
| take 10
```

---

## 🎭 Stakeholder Demo Preparation

If staging deployment is for stakeholder demo:

### Before Demo (1 day prior)
- [ ] Verify all demo scenarios work end-to-end
- [ ] Prepare demo accounts with sample data
- [ ] Test on demo network/VPN (if applicable)
- [ ] Screenshot happy path for backup slides
- [ ] Prepare rollback plan if demo breaks

### Demo Day
- [ ] Verify staging health 1 hour before demo
- [ ] Have backup environment ready (test or local)
- [ ] Monitor during demo for any issues
- [ ] Document feedback for next iteration

### After Demo
- [ ] Collect stakeholder feedback
- [ ] Create tickets for requested features
- [ ] Update roadmap based on feedback
- [ ] Plan production deployment timeline

---

## 🔐 Security Considerations

- [ ] Staging uses separate Azure AD tenant (or isolated app registration)
- [ ] Staging database isolated from production
- [ ] No production secrets in staging
- [ ] Staging endpoints not publicly advertised
- [ ] Rate limiting enabled
- [ ] HTTPS enforced with valid certificate
- [ ] Authentication required for all endpoints

---

## 📋 Deployment Approval Matrix

| Approval Required | Scenario |
|-------------------|----------|
| 1 Engineer | Bug fixes, minor updates |
| 2 Engineers | Feature releases |
| Product Manager | User-facing changes |
| Security Team | Security-related changes |
| CTO/Tech Lead | Major architectural changes |

---

## 📝 Deployment Record Template

After each deployment, create: `docs/deployment/logs/staging-YYYY-MM-DD.md`

```markdown
# Staging Deployment - YYYY-MM-DD HH:MM

**Version:** v1.2.3
**Deployed by:** @username
**Duration:** X minutes
**Stakeholders:** [List if demo scheduled]

## Changes
- Feature: [Description]
- Bug fix: [Description]
- Infrastructure: [Description]

## Pre-Deployment
- [x] All checks passed
- [x] Team notified
- [x] Rollback plan ready

## Post-Deployment
- [x] Health checks: PASS
- [x] Smoke tests: PASS
- [x] Performance: PASS
- [x] Monitoring: Active

## Issues Encountered
None / [Description + Resolution]

## Stakeholder Feedback
[If demo occurred, summarize feedback]

## Production Readiness
Ready / Not Ready (reason: ...)

## Next Steps
- [ ] Monitor for 24 hours
- [ ] Schedule production deployment
- [ ] Update documentation
```

---

## ✅ Production Readiness Checklist

Before promoting to production, verify:

- [ ] Staging has been stable for 24+ hours
- [ ] No critical bugs reported
- [ ] Performance metrics acceptable
- [ ] Security scan clean
- [ ] Stakeholder approval received (if required)
- [ ] Documentation updated
- [ ] Rollback procedure validated
- [ ] Production deployment scheduled
- [ ] On-call rotation assigned
- [ ] Customer communication prepared (if user-facing changes)

---

**Last Updated:** January 5, 2026  
**Owner:** DevOps Team  
**Review Frequency:** After each deployment
