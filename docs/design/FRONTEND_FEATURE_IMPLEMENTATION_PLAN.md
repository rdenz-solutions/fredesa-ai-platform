# FreDeSa AI Platform - Frontend Feature Implementation Plan
**16-Week Comprehensive Roadmap**

**Created:** January 5, 2026  
**Status:** Planning - Awaiting Approval  
**Timeline:** 16 weeks (4 months)  
**Owner:** Frontend Team  
**Dependencies:** Backend API development, Database implementation

---

## 📋 **Table of Contents**

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Feature Priority Matrix](#feature-priority-matrix)
4. [16-Week Implementation Plan](#16-week-implementation-plan)
5. [Technical Architecture](#technical-architecture)
6. [Backend API Requirements](#backend-api-requirements)
7. [Success Criteria](#success-criteria)
8. [Critical Blockers](#critical-blockers)
9. [Next Steps](#next-steps)

---

## 🎯 **Executive Summary**

This plan transforms the FreDeSa AI Platform from its current state (basic proposal viewing) into a comprehensive federal contracting AI platform with **17 new major features** across **8 categories**.

### **Current State:**
- ✅ 3 pages: Login, Customer Dashboard, Admin Dashboard
- ✅ 2 roles: `FreDeSa_SuperAdmin`, `Customer_User`
- ✅ Basic proposal viewing only
- ❌ No Knowledge Registry UI
- ❌ No semantic search
- ❌ No agent deployment interface
- ❌ No environment differentiation

### **Target State (Week 16):**
- ✅ 20+ pages across customer and admin portals
- ✅ Full CRUD operations for proposals
- ✅ Knowledge Registry search (1,311 sources)
- ✅ Semantic search with pgvector
- ✅ Agent catalog and deployment
- ✅ Skills marketplace
- ✅ System monitoring dashboards
- ✅ Environment-aware UI (test vs production)

### **Investment:**
- **16 weeks** of frontend development
- **30+ backend API endpoints** required
- **Database layer** must be implemented in parallel
- **~15 new npm packages** to add

---

## 📊 **Current State Analysis**

### **What's Currently Available:**

#### **Roles (2):**
1. **`FreDeSa_SuperAdmin`** - Platform administrators
2. **`Customer_User`** - Federal contracting customers

#### **Pages (3):**

**1. Login Page (`/login`)**
- Azure AD MSAL authentication
- Automatic role-based redirect

**2. Customer Dashboard (`/dashboard`)**
- View proposals (title, agency, value, due date, status)
- Proposal statistics (total, in progress, submitted, avg completion)
- Proposal detail modal (sections, team members)
- Status indicators (draft, in_review, submitted)
- ❌ Cannot create/edit/delete proposals
- ❌ No Knowledge Registry access
- ❌ No AI agent interaction

**3. Admin Dashboard (`/admin`)**
- Platform analytics (proposals, users, contract value, win rate)
- User list (name, email, role, status, last login)
- ❌ Cannot create/edit users
- ❌ No tenant management
- ❌ No system monitoring
- ❌ No Knowledge Registry stats

#### **Backend APIs (6 endpoints):**
- `GET /api/user/profile` - Get current user
- `GET /api/proposals` - List proposals
- `GET /api/proposals/{id}` - Get proposal details
- `GET /api/admin/users` - List all users
- `GET /api/admin/analytics` - Platform analytics
- ❌ No POST/PUT/DELETE for proposals
- ❌ No Knowledge Registry endpoints
- ❌ No semantic search endpoints
- ❌ No agent deployment endpoints

### **What's Missing:**

| Category | Missing Features | Impact |
|----------|------------------|--------|
| **Environment** | Test/prod differentiation, debug tools | High - Safety concern |
| **Knowledge Registry** | Search UI, browsing, source details | Critical - Core value prop |
| **Proposals** | Create, edit, delete, workflows | High - Customer blocker |
| **Admin** | User management, tenant config | High - Operational blocker |
| **AI Features** | Semantic search, agent deployment | Critical - Differentiation |
| **Marketplace** | Skills catalog, purchasing | Medium - Revenue opportunity |
| **Monitoring** | System health, database metrics | Medium - Operational visibility |
| **Settings** | User preferences, API keys | Low - Nice-to-have |

---

## 🎯 **Feature Priority Matrix**

| Priority | Feature | Business Value | Tech Complexity | Weeks | Dependencies |
|----------|---------|----------------|-----------------|-------|--------------|
| **P0** | Environment Detection | High | Low | 1 | None |
| **P0** | Knowledge Registry Search | Very High | Medium | 2-3 | Backend KR APIs |
| **P1** | Proposal CRUD | High | Medium | 2 | Backend Proposal APIs |
| **P1** | Admin User Management | High | Medium | 1 | Backend User APIs |
| **P2** | Semantic Search | Very High | High | 2 | pgvector, Backend APIs |
| **P2** | Agent Deployment | High | High | 2 | Backend Agent APIs |
| **P3** | Skills Marketplace | Medium | Medium | 2 | Backend Skills APIs |
| **P3** | System Dashboards | Medium | Low | 2 | Backend Metrics APIs |
| **P4** | Advanced Analytics | Low | Medium | 2 | Backend Analytics APIs |

---

## 📅 **16-Week Implementation Plan**

---

### **🔥 PHASE 1: Foundation & Safety (Weeks 1-2)**

#### **Week 1: Environment Detection & Branding**
**Goal:** Differentiate test from production visually

**Files to Create:**
```
web/src/
├── utils/
│   └── environment.ts              # Environment detection
├── components/
│   ├── EnvironmentBanner.tsx       # Test/staging banner
│   └── DebugPanel.tsx              # Test-only debug tools
├── config/
│   └── theme.ts                    # Environment-aware colors
└── hooks/
    └── useEnvironment.ts           # Environment context
```

**Features:**
- ✅ Environment banner (amber for test, purple for staging, none for prod)
- ✅ Debug panel (test only) - API status, auth info, performance metrics
- ✅ Environment-aware color scheme (amber vs blue)
- ✅ Different favicons per environment
- ✅ Logging levels based on environment (verbose vs errors only)
- ✅ Session duration differences (8hrs test, 1hr prod)

**Implementation Steps:**
1. Create `environment.ts` with detection logic
2. Build `EnvironmentBanner` component with conditional rendering
3. Implement `DebugPanel` with collapsible sections
4. Update `theme.ts` to use environment-based colors
5. Create environment-specific favicons
6. Update build scripts to inject correct env vars

**Success Criteria:**
- [ ] Test environment shows amber banner + debug panel
- [ ] Production shows no banner, blue colors only
- [ ] Debug panel shows API URL, user info, performance metrics
- [ ] Favicon differs between environments
- [ ] Console logging varies by environment

**Backend Dependencies:** None (frontend only)

---

#### **Week 2: Knowledge Registry Foundation**
**Goal:** Set up infrastructure for KR integration

**Files to Create:**
```
web/src/
├── api/
│   └── knowledge-registry.ts       # KR API client
├── types/
│   └── source.ts                   # Source type definitions
├── hooks/
│   └── useKnowledgeRegistry.ts     # KR data hooks
└── components/
    ├── SourceCard.tsx              # Display source info
    └── TrustScoreBadge.tsx         # Trust score indicator
```

**Features:**
- ✅ TypeScript types for sources (1,311 sources)
- ✅ API client wrapper with error handling
- ✅ React Query hooks for data fetching
- ✅ Reusable source display components
- ✅ Trust score visualization

**Implementation Steps:**
1. Define TypeScript interfaces matching backend schema
2. Create API client with endpoints wrapper
3. Build `useKnowledgeRegistry` hook with React Query
4. Create `SourceCard` component (title, category, trust, description)
5. Build `TrustScoreBadge` with color coding (70-80: yellow, 80-90: green, 90-100: blue)
6. Test data fetching with mock data

**Success Criteria:**
- [ ] Source types match backend schema
- [ ] API client handles errors gracefully
- [ ] React Query caching works correctly
- [ ] SourceCard displays all metadata
- [ ] TrustScoreBadge shows correct colors

**Backend Dependencies:**
- ⚠️ `GET /api/knowledge-registry/sources` - List sources
- ⚠️ `GET /api/knowledge-registry/categories` - List categories
- ⚠️ `GET /api/knowledge-registry/sources/{id}` - Get source details

---

### **🔍 PHASE 2: Knowledge Registry UI (Weeks 3-4)**

#### **Week 3: Knowledge Registry Search Page**
**Goal:** Build comprehensive search interface

**Files to Create:**
```
web/src/
├── pages/
│   └── KnowledgeRegistryPage.tsx       # Main KR page
└── features/knowledge-registry/
    ├── SearchBar.tsx                   # Search component
    ├── FilterPanel.tsx                 # Category/trust filters
    ├── SourceList.tsx                  # Results display
    └── SourceDetailModal.tsx           # Full source view
```

**Features:**
- ✅ Text search across 1,311 sources
- ✅ Filter by category (39 categories)
- ✅ Filter by epistemological type (Declarative, Procedural, Conceptual, Metacognitive, Strategic)
- ✅ Filter by trust score (70-100 range slider)
- ✅ Sort by relevance, date, trust score, alphabetical
- ✅ Pagination (50 results per page)
- ✅ Grid/List view toggle
- ✅ Shareable search URLs (query params)

**Implementation Steps:**
1. Build SearchBar with debouncing (300ms delay)
2. Create FilterPanel sidebar with collapsible sections
3. Implement SourceList with grid/list toggle
4. Build SourceDetailModal with full metadata display
5. Add URL query params for shareable searches
6. Implement pagination controls
7. Add loading skeletons and empty states

**Success Criteria:**
- [ ] Search returns relevant results within 1 second
- [ ] Filters work independently and in combination
- [ ] Pagination handles 1,311 sources correctly
- [ ] URLs are shareable (refresh preserves search)
- [ ] Empty state shows helpful message

**Backend Dependencies:**
- ⚠️ `GET /api/knowledge-registry/search?q=query&category=X&type=Y&min_trust=70&page=1&limit=50`
- ⚠️ `GET /api/knowledge-registry/sources/{source_id}` - Full details

---

#### **Week 4: Knowledge Registry Browse & Stats**
**Goal:** Add browsing and statistics features

**Files to Create:**
```
web/src/features/knowledge-registry/
├── CategoryBrowser.tsx         # Browse by category tree
├── StatsPanel.tsx              # Registry statistics
├── RecentlyAdded.tsx           # New sources widget
├── PopularSources.tsx          # Most accessed sources
└── EpistemologicalChart.tsx    # Distribution chart
```

**Features:**
- ✅ Browse by category tree (39 categories)
- ✅ KR statistics dashboard (1,311 sources, avg trust 91.5)
- ✅ Recently added sources (last 30 days)
- ✅ Most accessed sources (top 10)
- ✅ Epistemological distribution pie chart
- ✅ Category distribution bar chart

**Implementation Steps:**
1. Build category tree with expand/collapse
2. Create stats panel with key metrics
3. Add "Recently Added" feed with timestamps
4. Implement "Popular Sources" ranking
5. Create epistemological distribution chart (Recharts)
6. Add category distribution visualization

**Success Criteria:**
- [ ] Category tree is navigable and intuitive
- [ ] Stats display correctly (1,311 sources, 39 categories)
- [ ] Recently added shows correct timestamps
- [ ] Popular sources reflect actual usage
- [ ] Charts render correctly and are responsive

**Backend Dependencies:**
- ⚠️ `GET /api/knowledge-registry/stats` - Overall statistics
- ⚠️ `GET /api/knowledge-registry/recent?limit=10` - Recent sources
- ⚠️ `GET /api/knowledge-registry/popular?limit=10` - Popular sources

---

### **📝 PHASE 3: Proposal Management (Weeks 5-6)**

#### **Week 5: Create & Edit Proposals**
**Goal:** Enable full proposal lifecycle management

**Files to Create:**
```
web/src/
├── pages/
│   ├── CreateProposalPage.tsx      # New proposal form
│   └── EditProposalPage.tsx        # Edit existing
├── components/
│   └── ProposalForm.tsx            # Reusable form
├── hooks/
│   └── useProposalForm.ts          # Form state
└── utils/
    └── proposalValidation.ts       # Validation logic
```

**Features:**
- ✅ Create new proposal (title, agency, contract type, value, due date)
- ✅ Edit existing proposals
- ✅ Add/remove team members
- ✅ Add/remove/reorder proposal sections
- ✅ Save as draft
- ✅ Submit for review
- ✅ Form validation (required fields, dates, values)
- ✅ Autosave every 30 seconds

**Implementation Steps:**
1. Build multi-step proposal form with React Hook Form
2. Implement validation with Zod schemas
3. Create team member selector (multi-select dropdown)
4. Build section builder with drag-and-drop reordering
5. Wire up to backend API (POST/PUT)
6. Add autosave with debouncing
7. Handle draft vs submitted states
8. Add success/error notifications

**Success Criteria:**
- [ ] Form validates all required fields
- [ ] Autosave works reliably (visible indicator)
- [ ] Team members can be added/removed
- [ ] Sections are reorderable via drag-and-drop
- [ ] Success messages display correctly

**Backend Dependencies:**
- ⚠️ `POST /api/proposals` - Create new proposal
- ⚠️ `PUT /api/proposals/{id}` - Update existing
- ⚠️ `PATCH /api/proposals/{id}/status` - Change status (draft/submitted)

---

#### **Week 6: Proposal Actions & Workflows**
**Goal:** Add proposal lifecycle actions

**Files to Create:**
```
web/src/features/proposals/
├── ProposalActions.tsx         # Action menu
├── DeleteConfirmModal.tsx      # Delete confirmation
├── SubmitModal.tsx             # Submit confirmation
├── ProposalHistory.tsx         # Change history
└── ProposalComments.tsx        # Team comments
```

**Features:**
- ✅ Delete proposals (with confirmation)
- ✅ Duplicate proposals
- ✅ Export to PDF/Word
- ✅ Submit for review workflow
- ✅ View change history (audit trail)
- ✅ Team comments/notes
- ✅ Share proposals with team

**Implementation Steps:**
1. Build action dropdown menu (three-dot icon)
2. Create confirmation modal for delete (shows proposal title)
3. Implement duplicate functionality
4. Add export buttons (PDF/Word generation)
5. Build submission workflow with validation checks
6. Create comment system with timestamps
7. Add activity timeline (who changed what, when)

**Success Criteria:**
- [ ] Confirmation required for destructive actions
- [ ] Duplicate creates exact copy with "(Copy)" suffix
- [ ] Export generates valid PDF/Word files
- [ ] Submit workflow validates completeness
- [ ] Comments display with author and timestamp
- [ ] History shows all changes chronologically

**Backend Dependencies:**
- ⚠️ `DELETE /api/proposals/{id}` - Delete proposal
- ⚠️ `POST /api/proposals/{id}/duplicate` - Duplicate
- ⚠️ `GET /api/proposals/{id}/export?format=pdf` - Export
- ⚠️ `GET /api/proposals/{id}/history` - Change history
- ⚠️ `POST /api/proposals/{id}/comments` - Add comment
- ⚠️ `GET /api/proposals/{id}/comments` - Get comments

---

### **👥 PHASE 4: Admin Enhancements (Weeks 7-8)**

#### **Week 7: User Management**
**Goal:** Full user lifecycle management

**Files to Create:**
```
web/src/
├── pages/admin/
│   └── UsersPage.tsx               # Enhanced user management
└── features/admin/
    ├── CreateUserModal.tsx         # Invite new users
    ├── EditUserModal.tsx           # Edit user details
    ├── UserRoleSelector.tsx        # Role assignment
    └── UserActivityLog.tsx         # User audit trail
```

**Features:**
- ✅ Invite new users (email + role assignment)
- ✅ Edit user details (name, email, role)
- ✅ Deactivate/reactivate users
- ✅ Reset user passwords (send reset email)
- ✅ View user activity logs (logins, actions)
- ✅ Bulk user operations (activate/deactivate multiple)
- ✅ User search and filtering
- ✅ Export user list to CSV

**Implementation Steps:**
1. Build user invitation flow (email input + role dropdown)
2. Create edit modal with form validation
3. Implement role selector with Azure AD roles
4. Add user activity timeline with filters
5. Build bulk operations with checkboxes
6. Add user search (name, email, role)
7. Implement CSV export functionality

**Success Criteria:**
- [ ] Invitation emails sent successfully
- [ ] Role changes sync with Azure AD
- [ ] Activity log shows all user actions
- [ ] Bulk operations work on multiple users
- [ ] Search returns correct results
- [ ] CSV export includes all fields

**Backend Dependencies:**
- ⚠️ `POST /api/admin/users` - Create user (send invite)
- ⚠️ `PUT /api/admin/users/{id}` - Update user
- ⚠️ `DELETE /api/admin/users/{id}` - Deactivate
- ⚠️ `POST /api/admin/users/{id}/reset-password` - Send reset email
- ⚠️ `GET /api/admin/users/{id}/activity` - Activity log
- ⚠️ `POST /api/admin/users/bulk-action` - Bulk operations

---

#### **Week 8: Tenant & Organization Management**
**Goal:** Multi-tenant administration

**Files to Create:**
```
web/src/
├── pages/admin/
│   └── TenantsPage.tsx             # Tenant management
└── features/admin/
    ├── CreateTenantModal.tsx       # New tenant setup
    ├── TenantSettings.tsx          # Tenant config
    └── TenantUsageMetrics.tsx      # Usage tracking
```

**Features:**
- ✅ Create new tenants (organizations)
- ✅ Configure tenant settings (name, logo, domain)
- ✅ View tenant usage metrics (API calls, storage, users)
- ✅ Tenant-level feature flags
- ✅ Billing information display
- ✅ Tenant deactivation/deletion

**Implementation Steps:**
1. Build tenant list view with status indicators
2. Create tenant creation wizard (multi-step)
3. Implement tenant settings panel
4. Add usage metrics dashboard with charts
5. Build feature flag toggles
6. Add billing info display (read-only)
7. Implement tenant search and filtering

**Success Criteria:**
- [ ] New tenants created successfully
- [ ] Settings update correctly
- [ ] Usage metrics accurate and real-time
- [ ] Feature flags toggle instantly
- [ ] Billing info displays correctly
- [ ] Search/filter works across all tenants

**Backend Dependencies:**
- ⚠️ `GET /api/admin/tenants` - List all tenants
- ⚠️ `POST /api/admin/tenants` - Create tenant
- ⚠️ `PUT /api/admin/tenants/{id}` - Update tenant
- ⚠️ `GET /api/admin/tenants/{id}/usage` - Usage metrics
- ⚠️ `PUT /api/admin/tenants/{id}/feature-flags` - Update flags
- ⚠️ `DELETE /api/admin/tenants/{id}` - Deactivate tenant

---

### **🤖 PHASE 5: Semantic Search & AI (Weeks 9-10)**

#### **Week 9: Semantic Search Interface**
**Goal:** pgvector-powered semantic search

**Files to Create:**
```
web/src/
├── pages/
│   └── SemanticSearchPage.tsx          # Semantic search page
└── features/search/
    ├── SemanticSearchBar.tsx           # NLP search input
    ├── SearchResults.tsx               # Ranked results
    ├── SourceHighlighter.tsx           # Highlight passages
    └── RelatedSources.tsx              # Similar sources
```

**Features:**
- ✅ Natural language search ("How do I respond to an RFP?")
- ✅ Semantic similarity scores (0.0-1.0)
- ✅ Highlighted relevant passages in source text
- ✅ Related sources suggestions (top 5 similar)
- ✅ Search history (last 20 searches)
- ✅ Saved searches (bookmarks)
- ✅ Export search results to PDF

**Implementation Steps:**
1. Build semantic search input (supports longer queries)
2. Display results with similarity scores (bars + percentages)
3. Implement passage highlighting (yellow background)
4. Add "Related Sources" sidebar with similarity scores
5. Create search history dropdown
6. Add bookmark/save functionality
7. Implement export to PDF

**Success Criteria:**
- [ ] Semantic search returns results < 2 seconds
- [ ] Similarity scores display correctly (0-100%)
- [ ] Passage highlighting shows most relevant text
- [ ] Related sources are actually similar
- [ ] Search history persists across sessions
- [ ] Bookmarks saved to user profile

**Backend Dependencies:**
- ⚠️ `POST /api/search/semantic` - Semantic search (requires pgvector)
- ⚠️ `GET /api/search/similar/{source_id}?limit=5` - Find similar
- ⚠️ `POST /api/search/history` - Save search to history
- ⚠️ `GET /api/search/history` - Retrieve history
- ⚠️ `POST /api/search/bookmarks` - Save bookmark
- ⚠️ `GET /api/search/bookmarks` - Get bookmarks

---

#### **Week 10: AI Agent Catalog**
**Goal:** Browse and deploy AI agents

**Files to Create:**
```
web/src/
├── pages/
│   ├── AgentCatalogPage.tsx            # Agent marketplace
│   └── MyAgentsPage.tsx                # Deployed agents
└── features/agents/
    ├── AgentCard.tsx                   # Agent display
    ├── AgentDetailModal.tsx            # Full details
    ├── DeployAgentModal.tsx            # Deployment wizard
    └── AgentPerformanceChart.tsx       # Performance metrics
```

**Features:**
- ✅ Browse available agents (Federal Proposal Orchestrator, etc.)
- ✅ Filter by vertical (Federal, Manufacturing, Education, Healthcare, Finance)
- ✅ View agent capabilities, requirements, pricing
- ✅ Deploy agent to customer tenant (wizard)
- ✅ Configure agent settings (API keys, parameters)
- ✅ Monitor agent performance (executions, success rate, avg time)
- ✅ Pause/resume/delete agents

**Implementation Steps:**
1. Build agent catalog grid with filtering
2. Create agent detail modal with specs
3. Implement deployment wizard (3 steps: select, configure, confirm)
4. Add "My Agents" dashboard with status cards
5. Build agent configuration panel
6. Add performance metrics with charts
7. Implement pause/resume/delete actions

**Success Criteria:**
- [ ] Catalog shows all available agents
- [ ] Filters work correctly (vertical, status)
- [ ] Deployment wizard completes successfully
- [ ] Configuration updates save correctly
- [ ] Performance metrics accurate and real-time
- [ ] Pause/resume changes agent status immediately

**Backend Dependencies:**
- ⚠️ `GET /api/agents/catalog` - Available agents
- ⚠️ `POST /api/agents/deploy` - Deploy agent to tenant
- ⚠️ `GET /api/agents/deployed` - Customer's deployed agents
- ⚠️ `PUT /api/agents/{id}/config` - Update configuration
- ⚠️ `GET /api/agents/{id}/performance` - Performance metrics
- ⚠️ `PUT /api/agents/{id}/status` - Pause/resume
- ⚠️ `DELETE /api/agents/{id}` - Remove agent

---

### **💎 PHASE 6: Skills Marketplace (Weeks 11-12)**

#### **Week 11: Skills Catalog**
**Goal:** Browse and purchase skills

**Files to Create:**
```
web/src/
├── pages/
│   ├── SkillsMarketplacePage.tsx       # Skills marketplace
│   └── MySkillsPage.tsx                # Purchased skills
└── features/skills/
    ├── SkillCard.tsx                   # Skill display
    ├── SkillDetailModal.tsx            # Detailed info
    ├── PurchaseModal.tsx               # Purchase flow
    └── SkillUsageChart.tsx             # Usage analytics
```

**Features:**
- ✅ Browse available skills (3 initially: Capture Planning, Technical Writing, Compliance Checking)
- ✅ View skill details (description, pricing, requirements, examples)
- ✅ Purchase skills (payment integration)
- ✅ View purchased skills dashboard
- ✅ Activate/deactivate skills
- ✅ Skill usage analytics (executions, cost)
- ✅ Pricing tiers (per-use, monthly, annual)

**Implementation Steps:**
1. Build skills catalog grid with pricing cards
2. Create skill detail modal with examples
3. Implement purchase flow (payment integration - Stripe)
4. Add "My Skills" dashboard with status
5. Build skill activation/deactivation toggle
6. Add usage tracking with charts
7. Implement pricing tier selection

**Success Criteria:**
- [ ] Catalog displays all available skills
- [ ] Purchase flow completes successfully
- [ ] Payment processing works (test mode)
- [ ] Skills activate/deactivate instantly
- [ ] Usage analytics accurate
- [ ] Pricing tiers clearly displayed

**Backend Dependencies:**
- ⚠️ `GET /api/skills/catalog` - Available skills
- ⚠️ `POST /api/skills/purchase` - Buy skill (payment processing)
- ⚠️ `GET /api/skills/purchased` - Customer's skills
- ⚠️ `PUT /api/skills/{id}/activate` - Enable skill
- ⚠️ `PUT /api/skills/{id}/deactivate` - Disable skill
- ⚠️ `GET /api/skills/{id}/usage` - Usage analytics

---

#### **Week 12: Skills Integration**
**Goal:** Use skills within workflows

**Files to Create:**
```
web/src/features/skills/
├── SkillSelector.tsx           # Select skill in workflow
├── SkillExecutionPanel.tsx     # Run skill
├── SkillResultsViewer.tsx      # View outputs
└── hooks/
    └── useSkillExecution.ts    # Skill execution hook
```

**Features:**
- ✅ Use skills in proposal creation workflow
- ✅ Execute skills on demand (run now button)
- ✅ View skill results (text, files, structured data)
- ✅ Skill execution history (last 50 runs)
- ✅ Export skill outputs (PDF, Word, JSON)
- ✅ Schedule skill execution (future feature)

**Implementation Steps:**
1. Integrate skill selector into proposal form
2. Build skill execution interface with parameters
3. Display skill results with formatting
4. Add execution history table
5. Implement export functionality
6. Add loading states and error handling

**Success Criteria:**
- [ ] Skills selectable in proposal workflow
- [ ] Execution completes successfully
- [ ] Results display correctly (formatted)
- [ ] History shows all past executions
- [ ] Export generates valid files
- [ ] Errors handled gracefully

**Backend Dependencies:**
- ⚠️ `POST /api/skills/{id}/execute` - Run skill with parameters
- ⚠️ `GET /api/skills/{id}/results/{execution_id}` - Get results
- ⚠️ `GET /api/skills/{id}/history` - Execution history
- ⚠️ `GET /api/skills/{id}/export?format=pdf` - Export results

---

### **📊 PHASE 7: System Dashboards (Weeks 13-14)**

#### **Week 13: Database & System Health**
**Goal:** Real-time system monitoring

**Files to Create:**
```
web/src/
├── pages/admin/
│   └── SystemHealthPage.tsx            # System dashboard
└── features/admin/
    ├── DatabaseMetrics.tsx             # DB status
    ├── APIMetrics.tsx                  # API performance
    ├── AzureResourceStatus.tsx         # Azure health
    └── ErrorLogViewer.tsx              # Recent errors
```

**Features:**
- ✅ PostgreSQL connection status (up/down, latency)
- ✅ Database size and growth (GB used, % growth)
- ✅ pgvector index statistics (vectors, dimensions)
- ✅ API response times (avg, p50, p95, p99)
- ✅ Error rate monitoring (errors/hour)
- ✅ Azure resource health (15 resources: App Services, PostgreSQL, Redis, Storage, etc.)
- ✅ Active connections count
- ✅ Query performance (slowest queries)

**Implementation Steps:**
1. Build system health dashboard with status indicators
2. Add database metrics panel with gauges
3. Implement API performance tracking with line charts
4. Display Azure resource status with icons
5. Create error log viewer with filtering
6. Add real-time updates (WebSocket or 30s polling)
7. Implement alerting thresholds (red/yellow/green)

**Success Criteria:**
- [ ] All metrics update in real-time
- [ ] Database status accurate
- [ ] API performance charts render correctly
- [ ] Azure resources show correct status
- [ ] Error logs filterable by severity
- [ ] Alerts trigger on thresholds

**Backend Dependencies:**
- ⚠️ `GET /api/admin/system/health` - Overall health status
- ⚠️ `GET /api/admin/system/database` - DB metrics
- ⚠️ `GET /api/admin/system/api-metrics` - API stats
- ⚠️ `GET /api/admin/system/azure-resources` - Azure health
- ⚠️ `GET /api/admin/system/errors?limit=100` - Recent errors

---

#### **Week 14: Environment Dashboards**
**Goal:** Environment-specific monitoring

**Files to Create:**
```
web/src/
├── pages/admin/
│   └── EnvironmentDashboardPage.tsx    # Env comparison
└── features/admin/
    ├── DeploymentHistory.tsx           # Deploy timeline
    ├── FeatureFlagManager.tsx          # Toggle features
    └── ConfigViewer.tsx                # Environment config
```

**Features:**
- ✅ View all environments (local, test, staging, prod)
- ✅ Deployment history timeline (last 30 days)
- ✅ Feature flag management (toggle on/off)
- ✅ Environment configuration viewer (read-only)
- ✅ Environment comparison (diff view)
- ✅ Rollback triggers (admin only)
- ✅ Environment status (healthy, degraded, down)

**Implementation Steps:**
1. Build environment comparison table
2. Add deployment history timeline with status
3. Implement feature flag toggles with confirmations
4. Create config viewer (JSON formatted)
5. Add environment diff tool
6. Implement rollback trigger (confirmation required)

**Success Criteria:**
- [ ] All environments display correctly
- [ ] Deployment history accurate
- [ ] Feature flags toggle instantly
- [ ] Config viewer shows all settings
- [ ] Diff highlights differences
- [ ] Rollback requires confirmation

**Backend Dependencies:**
- ⚠️ `GET /api/admin/environments` - All environment info
- ⚠️ `GET /api/admin/deployments?limit=30` - Deployment history
- ⚠️ `GET /api/admin/feature-flags` - Current flags
- ⚠️ `PUT /api/admin/feature-flags/{flag}` - Toggle flag
- ⚠️ `GET /api/admin/config/{environment}` - Environment config
- ⚠️ `POST /api/admin/rollback/{deployment_id}` - Trigger rollback

---

### **📈 PHASE 8: Advanced Features (Weeks 15-16)**

#### **Week 15: Advanced Analytics**
**Goal:** Business intelligence dashboards

**Files to Create:**
```
web/src/
├── pages/
│   └── AnalyticsPage.tsx               # Analytics hub
└── features/analytics/
    ├── ContractValueChart.tsx          # Financial charts
    ├── WinRateAnalysis.tsx             # Success metrics
    ├── UserEngagementChart.tsx         # Usage patterns
    └── TrendAnalysis.tsx               # Trends over time
```

**Features:**
- ✅ Contract value trends (monthly, quarterly, yearly)
- ✅ Win rate analysis by agency/contract type
- ✅ User engagement metrics (DAU, MAU, sessions)
- ✅ Proposal completion trends
- ✅ Source usage analytics (most accessed)
- ✅ Custom date ranges
- ✅ Export reports (PDF, Excel)

**Implementation Steps:**
1. Build analytics hub with card grid
2. Create contract value line chart (Recharts)
3. Implement win rate bar chart by agency
4. Add user engagement funnel chart
5. Build trend analysis with predictions
6. Add date range picker
7. Implement report export

**Success Criteria:**
- [ ] All charts render correctly
- [ ] Data accurate for selected date range
- [ ] Export generates valid files
- [ ] Charts responsive on mobile
- [ ] Performance acceptable (< 3s load)

**Backend Dependencies:**
- ⚠️ `GET /api/analytics/contracts?start_date=X&end_date=Y` - Contract data
- ⚠️ `GET /api/analytics/win-rates?group_by=agency` - Win rate stats
- ⚠️ `GET /api/analytics/engagement?period=30d` - User activity
- ⚠️ `GET /api/analytics/trends?metric=proposals` - Trend data

---

#### **Week 16: User Settings & Preferences**
**Goal:** Personalization and configuration

**Files to Create:**
```
web/src/
├── pages/
│   └── SettingsPage.tsx                # User settings
└── features/settings/
    ├── ProfileSettings.tsx             # Profile edit
    ├── NotificationSettings.tsx        # Notification prefs
    ├── APIKeyManager.tsx               # API key management
    └── TeamSettings.tsx                # Team configuration
```

**Features:**
- ✅ Edit user profile (name, email, avatar)
- ✅ Notification preferences (email, in-app, frequency)
- ✅ API key generation and management
- ✅ Team member invitations
- ✅ Theme preferences (light/dark mode)
- ✅ Language settings (English only initially)
- ✅ Two-factor authentication setup

**Implementation Steps:**
1. Build settings page with tabbed navigation
2. Create profile edit form with avatar upload
3. Implement notification preferences checkboxes
4. Build API key manager (generate, revoke, copy)
5. Add team invitation form
6. Implement theme toggle (light/dark)
7. Add 2FA setup wizard (QR code)

**Success Criteria:**
- [ ] Profile updates save correctly
- [ ] Notification preferences work immediately
- [ ] API keys generate and revoke successfully
- [ ] Team invitations sent correctly
- [ ] Theme persists across sessions
- [ ] 2FA setup completes successfully

**Backend Dependencies:**
- ⚠️ `PUT /api/user/profile` - Update profile
- ⚠️ `POST /api/user/avatar` - Upload avatar
- ⚠️ `PUT /api/user/preferences` - Save preferences
- ⚠️ `POST /api/user/api-keys` - Generate API key
- ⚠️ `DELETE /api/user/api-keys/{id}` - Revoke key
- ⚠️ `POST /api/user/2fa/enable` - Enable 2FA
- ⚠️ `POST /api/user/team/invite` - Send invitation

---

## 🏗️ **Technical Architecture**

### **Frontend Stack:**

```json
{
  "framework": "React 19",
  "language": "TypeScript",
  "bundler": "Vite",
  "styling": "TailwindCSS",
  "stateManagement": [
    "React Query (TanStack Query) - Server state",
    "Zustand - Global UI state",
    "React Context - Environment config"
  ],
  "forms": "React Hook Form + Zod validation",
  "charts": "Recharts",
  "icons": "Lucide React",
  "authentication": "Azure AD (MSAL)",
  "testing": [
    "Vitest - Unit tests",
    "React Testing Library - Component tests",
    "Playwright - E2E tests"
  ]
}
```

### **New Dependencies to Add:**

```json
{
  "dependencies": {
    "zustand": "^4.5.0",
    "react-hook-form": "^7.50.0",
    "zod": "^3.22.4",
    "@tanstack/react-table": "^8.11.0",
    "recharts": "^2.10.0",
    "date-fns": "^3.0.0",
    "react-beautiful-dnd": "^13.1.1",
    "react-markdown": "^9.0.0",
    "react-syntax-highlighter": "^15.5.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0",
    "vitest": "^1.0.0",
    "@vitest/ui": "^1.0.0",
    "playwright": "^1.40.0",
    "msw": "^2.0.0"
  }
}
```

### **Project Structure:**

```
web/src/
├── api/                    # API clients
│   ├── client.ts           # Base API client (existing)
│   ├── knowledge-registry.ts
│   ├── proposals.ts
│   ├── agents.ts
│   └── skills.ts
├── components/             # Shared components
│   ├── EnvironmentBanner.tsx
│   ├── DebugPanel.tsx
│   ├── SourceCard.tsx
│   └── ...
├── features/               # Feature modules
│   ├── admin/
│   ├── customer/
│   ├── knowledge-registry/
│   ├── proposals/
│   ├── agents/
│   ├── skills/
│   └── analytics/
├── hooks/                  # Custom hooks
│   ├── useEnvironment.ts
│   ├── useKnowledgeRegistry.ts
│   └── ...
├── pages/                  # Page components
│   ├── LoginPage.tsx
│   ├── KnowledgeRegistryPage.tsx
│   ├── SemanticSearchPage.tsx
│   └── ...
├── types/                  # TypeScript types
│   ├── source.ts
│   ├── proposal.ts
│   ├── agent.ts
│   └── ...
├── utils/                  # Utilities
│   ├── environment.ts
│   ├── validation.ts
│   └── ...
├── config/                 # Configuration
│   └── theme.ts
└── App.tsx
```

---

## 🔌 **Backend API Requirements**

### **Total New Endpoints Needed: 30+**

#### **Knowledge Registry (8 endpoints):**
- `GET /api/knowledge-registry/sources` - List all sources
- `GET /api/knowledge-registry/sources/{id}` - Get source details
- `GET /api/knowledge-registry/categories` - List categories
- `GET /api/knowledge-registry/search?q=query&category=X&type=Y` - Search sources
- `GET /api/knowledge-registry/stats` - Registry statistics
- `GET /api/knowledge-registry/recent?limit=10` - Recently added
- `GET /api/knowledge-registry/popular?limit=10` - Most accessed
- `POST /api/knowledge-registry/access/{id}` - Track access (analytics)

#### **Proposals (10 endpoints):**
- `POST /api/proposals` - Create proposal
- `PUT /api/proposals/{id}` - Update proposal
- `PATCH /api/proposals/{id}/status` - Change status
- `DELETE /api/proposals/{id}` - Delete proposal
- `POST /api/proposals/{id}/duplicate` - Duplicate proposal
- `GET /api/proposals/{id}/export?format=pdf` - Export
- `GET /api/proposals/{id}/history` - Change history
- `POST /api/proposals/{id}/comments` - Add comment
- `GET /api/proposals/{id}/comments` - Get comments
- `POST /api/proposals/{id}/share` - Share with team

#### **Semantic Search (5 endpoints):**
- `POST /api/search/semantic` - Semantic search (pgvector)
- `GET /api/search/similar/{source_id}` - Find similar sources
- `POST /api/search/history` - Save search to history
- `GET /api/search/history` - Retrieve search history
- `POST /api/search/bookmarks` - Save bookmark
- `GET /api/search/bookmarks` - Get bookmarks

#### **Agents (7 endpoints):**
- `GET /api/agents/catalog` - Available agents
- `POST /api/agents/deploy` - Deploy agent
- `GET /api/agents/deployed` - Customer's deployed agents
- `PUT /api/agents/{id}/config` - Update configuration
- `GET /api/agents/{id}/performance` - Performance metrics
- `PUT /api/agents/{id}/status` - Pause/resume
- `DELETE /api/agents/{id}` - Remove agent

#### **Skills (6 endpoints):**
- `GET /api/skills/catalog` - Available skills
- `POST /api/skills/purchase` - Purchase skill
- `GET /api/skills/purchased` - Customer's skills
- `PUT /api/skills/{id}/activate` - Activate skill
- `POST /api/skills/{id}/execute` - Execute skill
- `GET /api/skills/{id}/history` - Execution history

#### **Admin - Users (6 endpoints):**
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Deactivate user
- `POST /api/admin/users/{id}/reset-password` - Reset password
- `GET /api/admin/users/{id}/activity` - Activity log
- `POST /api/admin/users/bulk-action` - Bulk operations

#### **Admin - Tenants (5 endpoints):**
- `GET /api/admin/tenants` - List tenants
- `POST /api/admin/tenants` - Create tenant
- `PUT /api/admin/tenants/{id}` - Update tenant
- `GET /api/admin/tenants/{id}/usage` - Usage metrics
- `DELETE /api/admin/tenants/{id}` - Deactivate tenant

#### **Admin - System (8 endpoints):**
- `GET /api/admin/system/health` - System health
- `GET /api/admin/system/database` - Database metrics
- `GET /api/admin/system/api-metrics` - API performance
- `GET /api/admin/system/azure-resources` - Azure status
- `GET /api/admin/system/errors?limit=100` - Error logs
- `GET /api/admin/environments` - Environment info
- `GET /api/admin/deployments` - Deployment history
- `GET /api/admin/feature-flags` - Feature flags
- `PUT /api/admin/feature-flags/{flag}` - Toggle flag

#### **Analytics (4 endpoints):**
- `GET /api/analytics/contracts` - Contract value data
- `GET /api/analytics/win-rates` - Win rate statistics
- `GET /api/analytics/engagement` - User engagement
- `GET /api/analytics/trends` - Trend analysis

#### **User Settings (5 endpoints):**
- `PUT /api/user/profile` - Update profile
- `POST /api/user/avatar` - Upload avatar
- `PUT /api/user/preferences` - Save preferences
- `POST /api/user/api-keys` - Generate API key
- `DELETE /api/user/api-keys/{id}` - Revoke key
- `POST /api/user/2fa/enable` - Enable 2FA

---

## ✅ **Success Criteria**

### **By End of Week 4:**
- ✅ Environment detection working (test shows amber, prod shows blue)
- ✅ Knowledge Registry searchable (1,311 sources)
- ✅ Users can browse by category
- ✅ Source details display correctly

### **By End of Week 8:**
- ✅ Proposals fully CRUD-capable
- ✅ Admin can manage users (create, edit, deactivate)
- ✅ Tenant management operational
- ✅ All basic workflows functional

### **By End of Week 12:**
- ✅ Semantic search operational (pgvector)
- ✅ Agents deployable from catalog
- ✅ Skills marketplace functional
- ✅ Users can purchase and use skills

### **By End of Week 16:**
- ✅ All system dashboards complete
- ✅ Advanced analytics available
- ✅ User settings and preferences complete
- ✅ Platform feature-complete for MVP

### **Overall Success Metrics:**
| Metric | Target | Measurement |
|--------|--------|-------------|
| **Feature Completeness** | 100% of planned features | Manual checklist |
| **Test Coverage** | >80% | Vitest coverage report |
| **Performance** | <3s page load | Lighthouse score |
| **Accessibility** | WCAG 2.1 AA | axe DevTools |
| **Mobile Responsiveness** | 100% responsive | Manual testing |
| **Bug Rate** | <5 critical bugs | Bug tracking |

---

## 🚨 **Critical Blockers**

### **Backend Must Deliver:**

1. **PostgreSQL Database Layer** (CRITICAL - Week 1)
   - Currently using mock data
   - Must implement database layer with proper schema
   - Required for all data persistence

2. **pgvector Installation** (CRITICAL - Week 7)
   - Required for semantic search
   - Must install and configure pgvector extension
   - Need embedding generation pipeline

3. **API Endpoint Development** (HIGH - Ongoing)
   - 30+ new endpoints required
   - Must be developed in parallel with frontend
   - OpenAPI/Swagger spec recommended

4. **Azure AD Integration** (MEDIUM - Week 1)
   - JWT validation middleware
   - Role-based access control
   - Token refresh logic

5. **Payment Integration** (MEDIUM - Week 11)
   - Stripe or similar payment processor
   - Webhook handling for purchase confirmations
   - Invoice generation

### **DevOps Must Deliver:**

1. **Environment Variables** (HIGH - Week 1)
   - Proper injection in CI/CD pipelines
   - Different values per environment
   - Secret management (Azure Key Vault)

2. **Database Provisioning** (HIGH - Week 1)
   - Automated PostgreSQL setup
   - Migration scripts
   - Backup/restore procedures

3. **Monitoring Setup** (MEDIUM - Week 13)
   - Application Insights integration
   - Custom metrics collection
   - Alert configuration

### **Design Must Deliver:**

1. **UI/UX Design System** (MEDIUM - Week 1)
   - Color palette (already partially defined)
   - Component library guidelines
   - Responsive breakpoints

2. **Logo & Branding Assets** (LOW - Week 1)
   - Environment-specific logos
   - Favicon variations
   - Loading animations

---

## 📋 **Next Steps**

### **Immediate Actions (This Week):**

1. **Review & Approve Plan**
   - Review this document with team
   - Adjust priorities if needed
   - Confirm timeline feasibility

2. **Assign Backend Team**
   - Identify backend developers
   - Assign API endpoint ownership
   - Create backend API spec document

3. **Set Up Project Board**
   - Create GitHub/Jira tickets for each week
   - Assign frontend developers
   - Set up weekly sprint reviews

4. **Database Work Starts**
   - Backend team implements PostgreSQL layer
   - Create migration scripts
   - Set up test database

### **Week 1 Kickoff:**

**Frontend Tasks:**
- [ ] Set up environment detection system
- [ ] Create environment banner component
- [ ] Build debug panel (test only)
- [ ] Update theme configuration
- [ ] Test visual differences across environments

**Backend Tasks:**
- [ ] Implement database layer (PostgreSQL)
- [ ] Create Knowledge Registry API endpoints (8 endpoints)
- [ ] Set up API documentation (Swagger)
- [ ] Configure Azure AD JWT validation

**DevOps Tasks:**
- [ ] Configure environment variables in CI/CD
- [ ] Set up database provisioning automation
- [ ] Configure Application Insights

### **Communication Plan:**

**Daily:**
- Stand-up meetings (15 min)
- Slack updates on progress/blockers

**Weekly:**
- Sprint review (demo completed features)
- Sprint planning (assign next week's tasks)
- Retrospective (improve process)

**Bi-Weekly:**
- Stakeholder demo
- Progress report to leadership

---

## 🎯 **Decision Points**

**You must decide:**

1. **Which priority tier to start with?**
   - Option A: Linear (P0 → P1 → P2 → P3 → P4)
   - Option B: Customer value first (P1 Proposals + P2 AI features)
   - Option C: Foundation first (P0 + Backend APIs, then features)

2. **Backend capacity available?**
   - If YES: Proceed with full plan
   - If NO: Reduce scope or extend timeline

3. **Design system ready?**
   - If YES: Start Week 1 immediately
   - If NO: Allocate 1 week for design system creation

4. **Database status?**
   - If READY: Proceed
   - If NOT READY: Block on database implementation

5. **Budget for external services?**
   - Payment processing (Stripe): ~$0.30 + 2.9% per transaction
   - Email service (SendGrid): ~$15/month
   - Monitoring (Application Insights): Included in Azure credits

---

## 📝 **Document History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-05 | AI Assistant | Initial comprehensive plan created |
| | | | - Current state analysis |
| | | | - 16-week implementation plan |
| | | | - Technical architecture |
| | | | - Backend API requirements |

---

## 📞 **Contact & Approval**

**For Questions:**
- Frontend Lead: [Name]
- Backend Lead: [Name]
- Product Manager: [Name]
- DevOps Lead: [Name]

**Approval Required From:**
- [ ] CTO
- [ ] Product Manager
- [ ] Frontend Team Lead
- [ ] Backend Team Lead
- [ ] UX/UI Designer

**Next Document to Create:**
Once approved, create: `PHASE_1_IMPLEMENTATION_GUIDE.md` with detailed code examples, file structures, and API contracts for Weeks 1-2.

---

**Ready to begin? Toggle to Act mode and let's start building!** 🚀
