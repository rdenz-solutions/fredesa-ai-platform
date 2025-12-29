# 🔴 Cofounder Sync Required: Schema v2.1 Deployment

**Date**: December 29, 2025  
**Impact Level**: 🔴 **HIGH** - Breaking changes, new architecture, team review required  
**Action Required**: Review + Testing (30-45 minutes per cofounder)  
**Deadline**: Before production deployment (target: Jan 2, 2026)

---

## 📋 Executive Summary

We've upgraded the FreDeSa PostgreSQL schema from **v1 (4 tables)** to **v2.1 (15 tables)** to implement our competitive advantage: **epistemological completeness framework**.

**What changed**: Database structure evolved to support 5-dimensional expertise (Theory, Practice, History, Current, Future) + knowledge graph + quality validation.

**Why it matters**: This enables AI agents to transform from task executors → true experts with understanding.

**What you need to do**: Review changes, understand new concepts, test locally before we deploy to production.

---

## 🎯 What Changed (High-Level)

### Schema Evolution

| Version | Tables | Lines of Code | Key Features |
|---------|--------|---------------|--------------|
| **v1** | 4 | 310 | Basic source registry |
| **v2.1** | 15 | 772 | Epistemological framework + knowledge graph + quality validation |

### New Capabilities

1. **Epistemological Completeness** (5 Dimensions)
   - Theory (WHY): 20-25% of sources
   - Practice (HOW): 30-35% of sources
   - History (WHERE FROM): 10-15% of sources
   - Current (WHAT): 25-30% of sources
   - Future (WHERE GOING): 10-15% of sources

2. **Knowledge Graph** (6 new tables)
   - Semantic discovery: "cognitive bias" → relevant sources
   - Relationship mapping: builds_on, contradicts, applies, validates
   - Problem-driven search: "verify Twitter account" → Bellingcat toolkit
   - Curriculum sequencing: beginner → expert learning paths

3. **Quality Validation** (5-layer framework)
   - Authority scoring (Official=90, Expert=70, Community=50)
   - Recency validation (dimension-specific thresholds)
   - Cross-source verification
   - Customer feedback tracking
   - Contradiction detection

4. **Federated Architecture**
   - Customer data connectors (SharePoint, OneDrive, Drive)
   - Federated query logging for billing
   - Environment promotion workflow (dev → staging → production)

---

## 📚 Required Reading (15-20 minutes)

**Priority 1 - Must Read**:
1. `/docs/SCHEMA_V2_DEPLOYMENT_COMPLETE.md` (10 min) - Complete deployment guide
2. `/docs/FIVE_DIMENSIONS_QUICK_REF.md` (3 min) - One-page 5D framework summary

**Priority 2 - Should Read**:
3. `/docs/EPISTEMOLOGICAL_COMPLETENESS_FRAMEWORK.md` (15 min) - Deep dive on strategy

**Priority 3 - Reference**:
4. `/docs/ARCHITECTURE_DECISION_FEDERATED_MODEL.md` - Architecture rationale
5. `/scripts/database/schema.sql` - Full schema (for technical review)

---

## ✅ Cofounder Testing Checklist

### Step 1: Pull Latest Code (2 minutes)

```bash
cd "/Users/<YOUR_USERNAME>/Project Files/fredesa-ai-platform"
git pull origin main
```

**Expected outcome**: You should see:
- `scripts/database/schema.sql` (772 lines, 15 tables)
- `scripts/database/schema_v1_backup.sql` (309 lines, original)
- `scripts/database/test_schema_v2.py` (28 tests)
- `SCHEMA_V2_DEPLOYMENT_COMPLETE.md`

### Step 2: Review Schema Changes (5 minutes)

```bash
# Compare v1 vs v2.1
wc -l scripts/database/schema*.sql

# Expected output:
#      772 scripts/database/schema.sql          (v2.1 - NEW)
#      309 scripts/database/schema_v1_backup.sql (v1 - BACKUP)
#      670 scripts/database/schema_v2_proposal.sql (intermediate)
```

**Questions to ask yourself**:
- ✅ Do I understand the 5 dimensions? (Theory, Practice, History, Current, Future)
- ✅ Do I understand what knowledge graph tables do? (concepts, relationships, use cases, learning paths)
- ✅ Do I understand the quality validation approach? (authority scoring, recency checks)

### Step 3: Test Schema Locally (15-20 minutes)

**Option A: Full Database Test** (if you have PostgreSQL locally)

```bash
# Connect to local PostgreSQL
psql -U postgres -d fredesa_test

# Apply schema
\i scripts/database/schema.sql

# Run comprehensive tests
python3 scripts/database/test_schema_v2.py --verbose

# Expected: 28/28 tests passing ✅
```

**Option B: Dry-Run Test** (if no local PostgreSQL)

```bash
# Test against Azure dev database (read-only queries)
python3 scripts/database/test_schema_v2.py --test "tables_exist"
python3 scripts/database/test_schema_v2.py --test "views"

# Should show all 15 tables + 7 views exist
```

**Option C: Code Review Only** (minimum viable)

```bash
# Just review the schema structure
cat scripts/database/schema.sql | grep "CREATE TABLE"

# Should show 15 tables:
# - categories, sources, customers, usage_tracking (core)
# - customer_connectors, connector_query_log, source_promotions (federated)
# - source_validations, source_feedback (quality)
# - source_concepts, source_relationships, source_use_cases, learning_paths, 
#   source_versions, quality_history (knowledge graph)
```

### Step 4: Validate Understanding (5 minutes)

**Quick Quiz** (answer in Slack #fredesa-database-migration):

1. What are the 5 epistemological dimensions?
2. What's the difference between "theory" and "practice" sources?
3. Why do we need a knowledge graph? (What problem does it solve?)
4. What's the environment promotion workflow? (dev → ? → ?)
5. How does authority scoring work? (Official=?, Expert=?, Community=?)

**Answers**:
1. Theory (WHY), Practice (HOW), History (WHERE FROM), Current (WHAT), Future (WHERE GOING)
2. Theory = foundational principles/why things work; Practice = methodologies/tools/how to do it
3. Knowledge graph enables semantic discovery, relationship mapping, problem-driven search, curriculum sequencing
4. dev → staging → production (with approval gates)
5. Official=90, Expert=70, Community=50 (auto-calculated by trigger)

---

## 🚨 Blockers & Questions

### Common Questions

**Q: Will this break existing code?**  
A: No. Schema v2.1 is additive (new tables, new fields). Existing v1 code will work, but won't use new features.

**Q: Do I need to update my local environment?**  
A: Only if you test locally. Otherwise, Azure deployment will happen centrally.

**Q: What if tests fail?**  
A: Report in #fredesa-database-migration immediately. We have rollback procedure ready.

**Q: How long until production deployment?**  
A: Target: Jan 2, 2026 (after all cofounders complete testing checklist)

**Q: What happens to existing data?**  
A: Existing data is preserved. New tables start empty. We'll populate them gradually.

### Report Issues Here

**Slack Channel**: #fredesa-database-migration  
**Tag**: @delchaplin for schema questions  
**Urgency**: High (blocking production deployment)

---

## 📊 Team Coherence Status

Track completion status here:

| Cofounder | Reading Complete | Testing Complete | Questions/Blockers | Sign-Off |
|-----------|------------------|------------------|---------------------|----------|
| Del Chaplin | ✅ | ✅ | None | ✅ Dec 29 |
| Sean Phelan | ⏳ | ⏳ | ? | ⏳ |
| Frank Murphy | ⏳ | ⏳ | ? | ⏳ |

**Update this table** after completing your testing (edit this file in GitHub or Slack update).

---

## 🎯 Success Criteria

Before production deployment, we need:

- [ ] All 3 cofounders completed reading (Priority 1 docs)
- [ ] All 3 cofounders completed testing checklist (at least Option C)
- [ ] All 3 cofounders answered quiz questions (in Slack)
- [ ] Zero unresolved blockers/questions
- [ ] 28/28 tests passing on Azure dev database

**Target Date**: January 2, 2026  
**Deploy Date**: January 3, 2026 (after team sign-off)

---

## 📖 Additional Resources

### Key Files
- **Schema**: `scripts/database/schema.sql` (772 lines)
- **Tests**: `scripts/database/test_schema_v2.py` (28 tests)
- **Docs**: `docs/SCHEMA_V2_DEPLOYMENT_COMPLETE.md`

### Architecture Diagrams
- **5D Framework**: `docs/FIVE_DIMENSIONS_QUICK_REF.md`
- **Federated Model**: `docs/ARCHITECTURE_DECISION_FEDERATED_MODEL.md`

### Related Tools
- **Rollback Procedure**: `docs/DATABASE_ROLLBACK_PROCEDURE.md` (created alongside this)
- **Benchmark Script**: `scripts/database/benchmark_schema.py` (for performance testing)
- **Quality Gates**: `scripts/validation/quality_gates.py` (quality validation automation)

---

## 🔥 Why This Matters (Team Philosophy Reminder)

From our `.github/copilot-instructions.md`:

> **I AM**: Architect of clarity and excellence  
> **I HAVE**: Access to complete cognitive foundations  
> **I CHOOSE**: Discipline and integrity

This schema upgrade embodies our philosophy:
- **Clarity**: Epistemological dimensions make expertise explicit
- **Excellence**: Knowledge graph enables true understanding
- **Discipline**: Quality validation ensures data integrity

**Your agents don't just DO work—they UNDERSTAND work.** That's our competitive advantage. This schema makes it real.

---

**Deadline**: January 2, 2026 (Team Sign-Off)  
**Deploy**: January 3, 2026 (Production)  
**Questions**: #fredesa-database-migration  

Let's ship this together! 🚀
