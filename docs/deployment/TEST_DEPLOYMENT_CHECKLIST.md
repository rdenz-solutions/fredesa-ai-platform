# Test Environment Deployment Checklist
**FreDeSa AI Platform - Test Environment**

Last Updated: January 5, 2026  
Environment: `test` (fredesa-db-test.postgres.database.azure.com)

---

## 🎯 Purpose

This checklist ensures consistent, reliable deployments to the test environment. The test environment auto-deploys when code is merged to the `develop` branch.

---

## 📋 Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing locally (`pytest` + `npm test`)
- [ ] Code coverage ≥ 80%
- [ ] No linting errors (`black`, `flake8`, `npm run lint`)
- [ ] Type checking passes (`mypy`, `npm run type-check`)
- [ ] No security vulnerabilities (`bandit`, `npm audit`)

### Database
- [ ] Migrations tested locally
- [ ] No breaking schema changes (or coordinated with team)
- [ ] Seed data script updated (if needed)
- [ ] Database backup strategy confirmed

### Configuration
- [ ] `.env.test` variables up to date
- [ ] No hardcoded secrets in code
- [ ] Feature flags configured appropriately
- [ ] API endpoints correct for test environment

### Documentation
- [ ] CHANGELOG.md updated
- [ ] API documentation regenerated (if endpoints changed)
- [ ] README updated (if setup changed)

---

## 🚀 Deployment Process

### Automatic Deployment (Default)

1. **Merge to develop branch**
   ```bash
   git checkout develop
   git merge feature/your-feature
   git push origin develop
   ```

2. **Monitor GitHub Actions**
   - Go to: https://github.com/rdenz-solutions/fredesa-ai-platform/actions
   - Watch `Deploy to Test Environment` workflow
   - Expected duration: 5-7 minutes

3. **Verify deployment success**
   - GitHub Actions shows green checkmark
   - Slack notification received (if configured)

### Manual Deployment (If Needed)

1. **Trigger manual deployment**
   - Go to: Actions → Deploy to Test Environment
   - Click "Run workflow"
   - Select branch: `develop`
   - Add reason: "Manual deployment - [your reason]"
   - Click "Run workflow"

2. **Monitor progress** (same as automatic)

---

## ✅ Post-Deployment Validation

### Automated Checks (Run by CI/CD)
- [x] Health endpoint responding (`/health`)
- [x] Frontend loads successfully
- [x] Docker containers running
- [x] No deployment errors in logs

### Manual Checks (5 minutes)

1. **API Health**
   ```bash
   curl https://fredesa-api-test.eastus.azurecontainerapps.io/health
   # Expected: {"status": "healthy", "version": "..."}
   ```

2. **API Documentation**
   - Visit: https://fredesa-api-test.eastus.azurecontainerapps.io/docs
   - Verify Swagger UI loads
   - Test 2-3 endpoints manually

3. **Frontend**
   - Visit: https://fredesa-web-test.eastus.azurecontainerapps.io
   - Verify login page loads
   - Test authentication flow (if applicable)

4. **Database Connectivity**
   ```bash
   # From backend logs in Azure Portal
   # Look for: "Database connection successful"
   # No connection errors
   ```

5. **Semantic Search** (if applicable)
   ```bash
   curl -X POST https://fredesa-api-test.eastus.azurecontainerapps.io/api/v1/search \
     -H "Content-Type: application/json" \
     -d '{"query": "test query", "top_k": 5}'
   ```

---

## 🐛 Troubleshooting

### Deployment Fails at Build Stage

**Symptoms:** Docker build fails, GitHub Actions shows red X

**Steps:**
1. Check build logs in GitHub Actions
2. Common issues:
   - Dependency installation failed → Check `requirements.txt` or `package.json`
   - Dockerfile syntax error → Validate Dockerfile locally
   - Build context missing files → Check `.dockerignore`

**Resolution:**
```bash
# Test Docker build locally
cd api
docker build -t fredesa-backend:test .

cd ../web
docker build -t fredesa-frontend:test .
```

### Deployment Succeeds But Health Check Fails

**Symptoms:** Containers running but `/health` returns 500 or times out

**Steps:**
1. Check container logs in Azure Portal
2. Common issues:
   - Database connection failed → Verify `DATABASE_URL` in environment variables
   - Missing environment variable → Check `.env.test` configuration
   - Application startup error → Review Python/Node.js logs

**Resolution:**
```bash
# View container logs
az containerapp logs show \
  --name fredesa-api-test \
  --resource-group rg-fredesa-dev \
  --tail 100
```

### Frontend Loads But API Calls Fail

**Symptoms:** Frontend loads but can't reach backend

**Steps:**
1. Check browser DevTools → Network tab
2. Common issues:
   - CORS error → Verify `CORS_ORIGINS` includes test frontend URL
   - 404 on API calls → Check `VITE_API_URL` in frontend build
   - Authentication error → Verify Azure AD configuration

**Resolution:**
1. Check `web/.env.production` has correct `VITE_API_URL`
2. Verify CORS settings in `api/main.py`
3. Test API directly with `curl` to isolate issue

---

## 🔄 Rollback Procedure

If test deployment has critical issues:

### Option 1: Revert Git Commit
```bash
git log --oneline develop
git revert <commit-hash>
git push origin develop
```

### Option 2: Redeploy Previous Version
- In GitHub Actions → Deploy to Test Environment
- Find previous successful deployment
- Click "Re-run all jobs"

### Option 3: Manual Rollback (Azure)
```bash
az containerapp revision list \
  --name fredesa-api-test \
  --resource-group rg-fredesa-dev

az containerapp revision activate \
  --name fredesa-api-test \
  --resource-group rg-fredesa-dev \
  --revision <previous-revision-name>
```

---

## 📊 Monitoring

### Key Metrics (First 30 Minutes)

1. **Error Rate** - Target: < 1%
2. **Response Time** - Target: < 500ms p95
3. **Resource Usage** - CPU: < 50%, Memory: < 75%
4. **Database Connections** - < 80% of max

---

## 🔐 Security Considerations

- [ ] No production secrets in test environment
- [ ] Test database isolated from production
- [ ] API rate limiting configured
- [ ] HTTPS enforced
- [ ] Authentication required (except `/health`, `/docs`)

---

## 👥 Team Communication

**Before:** Announce in #engineering Slack  
**After:** Post deployment summary  
**If Rollback:** Immediately notify team

---

**Last Updated:** January 5, 2026  
**Owner:** DevOps Team
