# Database Rollback Procedure - Schema v2.1

**Document Version**: 1.0  
**Last Updated**: December 29, 2025  
**Owner**: Del Chaplin (Database Administrator)  
**Status**: READY FOR USE

---

## 🚨 When to Use This Procedure

**Trigger rollback if**:
- Schema deployment fails (PostgreSQL errors during `apply_schema.py`)
- Tests fail after deployment (< 25/28 tests passing)
- Data corruption detected (source counts don't match, integrity violations)
- Performance degradation (queries >5x slower than v1)
- Application errors (APIs failing due to schema changes)

**Do NOT rollback for**:
- Minor test failures (1-2 tests) that don't affect core functionality
- Expected data migration delays (populating knowledge graph takes time)
- Temporary network issues (Azure PostgreSQL connectivity)

---

## 📋 Pre-Rollback Checklist

Before executing rollback, verify:

1. ✅ **Identify failure point**: What specifically broke?
   - Schema creation error? (SQL syntax, constraint violation)
   - Test failure? (Which tests? Are they critical?)
   - Application error? (API endpoints, data access)
   - Performance issue? (Slow queries, timeouts)

2. ✅ **Assess impact**: Who's affected?
   - Development only? (Safe to rollback)
   - Staging environment? (Notify team)
   - Production environment? (CRITICAL - page on-call)

3. ✅ **Document failure**:
   ```bash
   # Capture error logs
   pg_dump fredesa-db-dev > /tmp/failed_deployment_$(date +%Y%m%d_%H%M%S).sql
   
   # Capture test results
   python3 scripts/database/test_schema_v2.py --verbose > /tmp/test_results.txt 2>&1
   ```

4. ✅ **Notify team**:
   - Post in #fredesa-database-migration: "🚨 Schema v2.1 deployment failed. Initiating rollback."
   - Include: failure point, impact assessment, ETA for resolution

---

## 🔧 Rollback Procedure

### Option A: Automated Rollback (Recommended)

**Use case**: Standard deployment failure, schema is the problem

```bash
#!/bin/bash
# File: scripts/database/rollback_to_v1.sh

set -e  # Exit on error

echo "🚨 ROLLBACK: Schema v2.1 → v1"
echo "=========================================="

# Step 1: Backup current state (even if broken)
echo "📦 Step 1: Backing up failed v2.1 deployment..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -h fredesa-db-dev.postgres.database.azure.com \
        -U fredesaadmin \
        -d postgres \
        -f "/tmp/failed_v2_deployment_${TIMESTAMP}.sql"

echo "✅ Failed deployment backed up to /tmp/failed_v2_deployment_${TIMESTAMP}.sql"

# Step 2: Drop all v2.1 tables/views/triggers
echo "🗑️  Step 2: Dropping v2.1 schema objects..."
psql -h fredesa-db-dev.postgres.database.azure.com \
     -U fredesaadmin \
     -d postgres \
     -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "✅ v2.1 schema dropped"

# Step 3: Restore v1 schema
echo "📥 Step 3: Restoring v1 schema..."
psql -h fredesa-db-dev.postgres.database.azure.com \
     -U fredesaadmin \
     -d postgres \
     -f scripts/database/schema_v1_backup.sql

echo "✅ v1 schema restored"

# Step 4: Restore v1 data (if backup exists)
if [ -f "/tmp/v1_data_backup_${TIMESTAMP}.sql" ]; then
    echo "📥 Step 4: Restoring v1 data..."
    psql -h fredesa-db-dev.postgres.database.azure.com \
         -U fredesaadmin \
         -d postgres \
         -f "/tmp/v1_data_backup_${TIMESTAMP}.sql"
    echo "✅ v1 data restored"
else
    echo "⚠️  No v1 data backup found. Schema restored, but data empty."
fi

# Step 5: Validate rollback
echo "🧪 Step 5: Validating rollback..."
python3 scripts/database/test_schema.py  # v1 test suite (10 tests)

echo ""
echo "=========================================="
echo "✅ ROLLBACK COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review failure logs: /tmp/failed_v2_deployment_${TIMESTAMP}.sql"
echo "2. Investigate root cause of deployment failure"
echo "3. Fix schema issues in development"
echo "4. Re-test deployment before retrying production"
echo "5. Update COFOUNDER_SYNC_SCHEMA_V2.md with lessons learned"
```

**Execute rollback**:
```bash
chmod +x scripts/database/rollback_to_v1.sh
./scripts/database/rollback_to_v1.sh
```

### Option B: Manual Rollback (If Script Fails)

**Step 1: Connect to PostgreSQL**
```bash
export PGPASSWORD=$(az keyvault secret show \
  --vault-name fredesa-kv-e997e3 \
  --name postgres-password \
  --query value -o tsv)

psql -h fredesa-db-dev.postgres.database.azure.com \
     -U fredesaadmin \
     -d postgres
```

**Step 2: Drop v2.1 objects**
```sql
-- Drop all views first (to avoid dependency errors)
DROP VIEW IF EXISTS active_sources CASCADE;
DROP VIEW IF EXISTS production_sources CASCADE;
DROP VIEW IF EXISTS vertical_completeness CASCADE;
DROP VIEW IF EXISTS knowledge_graph_summary CASCADE;
DROP VIEW IF EXISTS curriculum_ready_sources CASCADE;
DROP VIEW IF EXISTS customer_stats CASCADE;
DROP VIEW IF EXISTS pending_approvals CASCADE;

-- Drop all triggers
DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;
DROP TRIGGER IF EXISTS update_sources_updated_at ON sources;
DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
DROP TRIGGER IF EXISTS update_connectors_updated_at ON customer_connectors;
DROP TRIGGER IF EXISTS update_learning_paths_updated_at ON learning_paths;
DROP TRIGGER IF EXISTS maintain_category_stats ON sources;
DROP TRIGGER IF EXISTS calculate_authority_score ON sources;
DROP TRIGGER IF EXISTS maintain_citation_counts_trigger ON source_relationships;

-- Drop all tables (reverse dependency order)
DROP TABLE IF EXISTS quality_history CASCADE;
DROP TABLE IF EXISTS source_versions CASCADE;
DROP TABLE IF EXISTS learning_paths CASCADE;
DROP TABLE IF EXISTS source_use_cases CASCADE;
DROP TABLE IF EXISTS source_relationships CASCADE;
DROP TABLE IF EXISTS source_concepts CASCADE;
DROP TABLE IF EXISTS source_feedback CASCADE;
DROP TABLE IF EXISTS source_validations CASCADE;
DROP TABLE IF EXISTS source_promotions CASCADE;
DROP TABLE IF EXISTS connector_query_log CASCADE;
DROP TABLE IF EXISTS customer_connectors CASCADE;
DROP TABLE IF EXISTS usage_tracking CASCADE;
DROP TABLE IF EXISTS sources CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
```

**Step 3: Restore v1 schema**
```sql
\i scripts/database/schema_v1_backup.sql
```

**Step 4: Verify rollback**
```sql
-- Should show 4 tables only
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Expected: categories, customers, sources, usage_tracking
```

**Step 5: Exit and test**
```bash
\q
python3 scripts/database/test_schema.py  # v1 tests (10 tests)
```

---

## 🧪 Post-Rollback Validation

After rollback, verify system health:

### 1. Database Health Check
```bash
# Run v1 test suite
python3 scripts/database/test_schema.py

# Expected: 10/10 tests passing ✅
```

### 2. Application Health Check
```bash
# Test API endpoints
curl https://fredesa-api-dev.azurewebsites.net/health
curl https://fredesa-api-dev.azurewebsites.net/api/sources?limit=10

# Expected: 200 OK responses
```

### 3. Data Integrity Check
```sql
-- Connect to database
psql -h fredesa-db-dev.postgres.database.azure.com -U fredesaadmin -d postgres

-- Verify source counts
SELECT category_id, COUNT(*) FROM sources GROUP BY category_id;

-- Verify no orphaned data
SELECT COUNT(*) FROM sources WHERE category_id NOT IN (SELECT id FROM categories);
-- Expected: 0
```

### 4. Performance Check
```bash
# Run benchmark against v1
python3 scripts/database/benchmark_schema.py

# Compare with v1 baseline (should be ~same performance)
```

---

## 📊 Rollback Success Criteria

Rollback is successful when:

- ✅ **All 4 v1 tables exist**: categories, sources, customers, usage_tracking
- ✅ **10/10 v1 tests passing**
- ✅ **API endpoints responding** (200 OK)
- ✅ **No orphaned data** (all foreign keys valid)
- ✅ **Performance matches v1 baseline** (queries <50ms)

---

## 📝 Post-Rollback Actions

### Immediate (Within 1 hour)

1. **Document root cause**:
   ```markdown
   # File: logs/deployment_failure_YYYYMMDD.md
   
   ## Deployment Failure Report
   
   **Date**: YYYY-MM-DD HH:MM
   **Environment**: dev/staging/production
   **Failure Point**: [Schema creation / Test failure / Application error]
   **Root Cause**: [SQL syntax error / Constraint violation / Performance issue]
   **Impact**: [Who was affected / How long]
   **Rollback Success**: [Yes/No + validation results]
   ```

2. **Update team**:
   - Post in #fredesa-database-migration: "✅ Rollback complete. v1 restored and validated."
   - Share failure report link
   - Schedule post-mortem (within 24 hours)

3. **Preserve evidence**:
   ```bash
   # Move failure logs to permanent storage
   mkdir -p logs/failed_deployments/$(date +%Y%m%d)
   mv /tmp/failed_v2_deployment_*.sql logs/failed_deployments/$(date +%Y%m%d)/
   mv /tmp/test_results.txt logs/failed_deployments/$(date +%Y%m%d)/
   ```

### Short-term (Within 24 hours)

4. **Root cause analysis**:
   - Review SQL errors
   - Analyze test failures
   - Check Azure PostgreSQL logs
   - Identify schema bugs

5. **Fix and re-test**:
   - Fix schema issues in `schema.sql`
   - Test locally FIRST (don't deploy to Azure yet)
   - Run all 28 tests locally
   - Get cofounder code review

6. **Update documentation**:
   - Add lessons learned to `SCHEMA_V2_DEPLOYMENT_COMPLETE.md`
   - Update `COFOUNDER_SYNC_SCHEMA_V2.md` with new warnings
   - Revise deployment procedure if needed

### Long-term (Before retry)

7. **Improve deployment process**:
   - Add more pre-deployment validation
   - Create staging environment test
   - Automate rollback trigger detection
   - Add monitoring/alerting for schema health

8. **Team sign-off**:
   - All cofounders review failure report
   - All cofounders approve retry plan
   - Schedule deployment window (off-hours)

---

## 🔐 Emergency Contacts

**Database Issues**:
- **Primary**: Del Chaplin (@delchaplin) - Slack/Mobile
- **Backup**: Sean Phelan (@speh-w2p) - Slack

**Infrastructure Issues**:
- **Azure Support**: Open ticket via Azure Portal
- **Microsoft for Startups**: Email support@startups.microsoft.com

**Escalation Path**:
1. Try automated rollback (5-10 minutes)
2. Try manual rollback (10-15 minutes)
3. Contact Del Chaplin (immediate)
4. Contact Azure Support (if infrastructure issue)
5. Restore from daily backup (last resort)

---

## 📦 Backup Strategy

**Automated Backups** (Azure PostgreSQL):
- **Frequency**: Daily at 2 AM UTC
- **Retention**: 7 days
- **Location**: Azure Backup vault (geo-redundant)

**Manual Backups** (Before deployment):
```bash
# Create pre-deployment backup
pg_dump -h fredesa-db-dev.postgres.database.azure.com \
        -U fredesaadmin \
        -d postgres \
        -f "backups/pre_v2_deployment_$(date +%Y%m%d).sql"

# Verify backup
ls -lh backups/pre_v2_deployment_*.sql
```

**Restore from Azure Backup** (if needed):
```bash
# List available backups
az postgres flexible-server backup list \
  --resource-group rg-fredesa-dev \
  --server-name fredesa-db-dev

# Restore to new server
az postgres flexible-server restore \
  --resource-group rg-fredesa-dev \
  --name fredesa-db-dev-restored \
  --source-server fredesa-db-dev \
  --restore-time "2025-12-28T02:00:00Z"
```

---

## 🎯 Prevention (Avoiding Future Rollbacks)

**Pre-Deployment Checklist**:
- [ ] All tests passing locally (28/28)
- [ ] Schema validated in development PostgreSQL
- [ ] Performance benchmarks acceptable (<5% overhead)
- [ ] All cofounders completed testing checklist
- [ ] Rollback procedure tested (dry-run)
- [ ] Backup created and verified
- [ ] Deployment window scheduled (low-traffic time)
- [ ] On-call engineer available (1 hour post-deployment)

**Deployment Best Practices**:
1. Deploy to dev environment first
2. Run full test suite
3. Monitor for 24 hours
4. Deploy to staging
5. Run full test suite again
6. Monitor for 48 hours
7. Deploy to production (only if staging stable)

---

## 📚 Related Documentation

- **Deployment Guide**: `SCHEMA_V2_DEPLOYMENT_COMPLETE.md`
- **Testing Guide**: `scripts/database/test_schema_v2.py`
- **Cofounder Sync**: `COFOUNDER_SYNC_SCHEMA_V2.md`
- **Architecture Decision**: `docs/ARCHITECTURE_DECISION_FEDERATED_MODEL.md`

---

**Last Tested**: Not yet (ready for use)  
**Next Review**: After first deployment (success or failure)  
**Version**: 1.0 (Initial rollback procedure)
