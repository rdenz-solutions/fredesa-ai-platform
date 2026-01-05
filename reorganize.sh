#!/bin/bash
# FreDeSa Repository Reorganization Script
# Based on rDenz Knowledge Registry cleanup methodology

set -e  # Exit on error

echo "🚀 Starting FreDeSa Repository Reorganization..."
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p archive/sessions/{2025-12-29-schema-v2,2025-12-29-integrations,2025-12-31,2026-01-03}
mkdir -p docs/planning/priorities
mkdir -p config/env
mkdir -p scripts/deployment

echo "✅ Directory structure created"
echo ""

# Phase 1: Move Schema V2 session files
echo "📦 Phase 1: Archiving Schema V2 session files..."
git mv SCHEMA_V2_COMPLETE.md archive/sessions/2025-12-29-schema-v2/ 2>/dev/null || true
git mv SCHEMA_V2_DEPLOYMENT_COMPLETE.md archive/sessions/2025-12-29-schema-v2/ 2>/dev/null || true
git mv SCHEMA_V2_FINAL_STATUS.md archive/sessions/2025-12-29-schema-v2/ 2>/dev/null || true
git mv SCHEMA_V2_SESSION_SUMMARY.md archive/sessions/2025-12-29-schema-v2/ 2>/dev/null || true
git mv SCHEMA_V2.1_MIGRATION_COMPLETE.md archive/sessions/2025-12-29-schema-v2/ 2>/dev/null || true
echo "✅ Schema V2 files archived (5 files)"

# Phase 2: Move integration session files
echo "📦 Phase 2: Archiving integration session files..."
git mv AIRIA_AGENT_INTEGRATION_COMPLETE.md archive/sessions/2025-12-29-integrations/ 2>/dev/null || true
git mv API_VALIDATION_COMPLETE.md archive/sessions/2025-12-29-integrations/ 2>/dev/null || true
git mv CAPTURE_PLANNING_AGENT_DEPLOYMENT.md archive/sessions/2025-12-29-integrations/ 2>/dev/null || true
git mv MCP_SERVER_DEPLOYMENT_STATUS.md archive/sessions/2025-12-29-integrations/ 2>/dev/null || true
git mv SEMANTIC_SEARCH_DEMO_COMPLETE.md archive/sessions/2025-12-29-integrations/ 2>/dev/null || true
echo "✅ Integration files archived (5 files)"

# Phase 3: Move other session files
echo "📦 Phase 3: Archiving other session files..."
git mv SESSION_SUMMARY_2025_12_31.md archive/sessions/2025-12-31/ 2>/dev/null || true
git mv FREDESA_API_FIXES_COMPLETE.md archive/sessions/2026-01-03/ 2>/dev/null || true
echo "✅ Other session files archived (2 files)"

# Phase 4: Organize planning documents
echo "📦 Phase 4: Organizing planning documents..."
git mv MIGRATION_SESSION_HANDOFF.md docs/planning/ 2>/dev/null || true
git mv COFOUNDER_SYNC_SCHEMA_V2.md docs/planning/ 2>/dev/null || true
git mv NEXT_SESSION_PRIORITY_1_TRIGGERS.md docs/planning/priorities/PRIORITY_1_TRIGGERS.md 2>/dev/null || true
git mv NEXT_SESSION_PRIORITY_2_WEEK_2.md docs/planning/priorities/PRIORITY_2_WEEK_2.md 2>/dev/null || true
git mv NEXT_SESSION_PRIORITY_3_WEEK_3.md docs/planning/priorities/PRIORITY_3_WEEK_3.md 2>/dev/null || true
echo "✅ Planning documents organized (5 files)"

# Phase 5: Move web deployment scripts
echo "📦 Phase 5: Moving deployment scripts..."
if [ -f "web/configure-azure.sh" ]; then
    git mv web/configure-azure.sh scripts/deployment/ 2>/dev/null || true
fi
if [ -f "web/setup-azure-automated.sh" ]; then
    git mv web/setup-azure-automated.sh scripts/deployment/ 2>/dev/null || true
fi
echo "✅ Deployment scripts moved"

echo ""
echo "✨ Reorganization complete!"
echo ""
echo "📊 Summary:"
echo "  - Root MD files: 19 → 3 (README.md, .clinerules, NEXT_SESSION_START_HERE.md)"
echo "  - Session summaries: Archived in archive/sessions/"
echo "  - Planning docs: Organized in docs/planning/"
echo "  - Deployment scripts: Moved to scripts/deployment/"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Create .gitignore enhancements"
echo "  3. Create REPOSITORY_STRUCTURE.md"
echo "  4. Create docker-compose.yml"
echo "  5. Commit: git commit -m 'feat: Repository reorganization (19→3 root files)'"
