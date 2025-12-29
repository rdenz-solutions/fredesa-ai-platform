# Architecture Decision: Federated + Curated Hybrid Model

**Date**: December 29, 2025  
**Status**: Approved  
**Decision Makers**: Del Chaplin (Founder/CEO)

## Executive Summary

FreDeSa AI Platform will adopt a **hybrid federated + curated knowledge architecture**, inspired by NexusOne Cognitive's "Unified Intelligence Layer" while maintaining our competitive differentiation through **vertical-specific knowledge completeness**.

### The Core Strategy: Complete Cognitive Foundation

**Vision**: For each industry vertical, curate the COMPLETE intellectual substrate that transforms agents from task executors into true experts.

**What We Curate (The Five Dimensions of Expertise)**:

1. **Theory & Foundations** (WHY) - First principles, academic research, conceptual frameworks, mental models
2. **Application & Practice** (HOW) - Methodologies, techniques, tools, step-by-step guides, best practices
3. **Historical Context** (WHERE IT CAME FROM) - Evolution of the discipline, what worked/failed, lessons learned, pattern recognition
4. **Current State** (WHAT WORKS TODAY) - Modern techniques, current best practices, state-of-the-art, industry standards
5. **Future Trends** (WHERE IT'S GOING) - Emerging practices, innovation trajectories, leading indicators, experimental approaches

**The Transformation**:

Agents don't just execute tasks—they understand:
- **WHY** techniques work (theoretical foundation)
- **HOW** to apply them (practical methodology)
- **WHEN** historical patterns repeat (contextual awareness)
- **WHAT** works today (current best practices)
- **WHERE** the field is evolving (future trajectory)

**Example: Intelligence Community OSINT Agent**

When a customer says "I want to build an OSINT analysis agent," FreDeSa provides:

- ✅ **Theory**: Information theory, cognitive biases in analysis, structured analytic techniques (WHY OSINT works)
- ✅ **Foundations**: Sherman Kent intelligence tradecraft, Richards Heuer's psychology of intelligence analysis (PRINCIPLES)
- ✅ **Historical**: OSINT evolution from Cold War to social media era (HOW it evolved)
- ✅ **Methods**: Bellingcat techniques, social media intelligence frameworks, geolocation (HOW to do it)
- ✅ **Verification**: Source credibility assessment, fact-checking methodologies (WHEN to trust)
- ✅ **Application**: Entity resolution, temporal analysis, network mapping (WHAT to do)
- ✅ **Tools**: Platform-specific guides, API documentation, scraping techniques (HOW to execute)
- ✅ **Trends**: AI-assisted OSINT, synthetic media detection, privacy-preserving techniques (WHERE it's going)

**Result**: The agent doesn't just know HOW to collect social media data—it understands WHY verification matters, WHEN techniques work, WHAT historical patterns indicate, and WHERE the field is heading. True expertise, not just task execution.

### Competitive Differentiation

1. **Complete Cognitive Foundation** - Theory + Practice + History + Current + Future (vs NexusOne's 0 sources)
2. **Vertical-Specific Expertise** - 90%+ epistemological completeness per vertical
3. **Federated Customer Data** - Customer proprietary data stays in their tenant (NexusOne model)
4. **AI Agent Orchestration** - Multi-agent workflows that execute tasks, not just search
5. **SMB Economics** - $417-$4,167/month vs $42K/month enterprise pricing
6. **Rapid Deployment** - 24 hours vs 4-6 weeks enterprise implementation

### The Epistemological Advantage

**What Competitors Provide**:
- Search/retrieval over customer data (RAG)
- Query federation across systems
- Task execution without understanding

**What FreDeSa Provides**:
- **Complete intellectual substrate** for each vertical
- Agents that understand WHY, HOW, WHEN, WHAT, WHERE
- True expertise, not just information access

**Example Comparison: Building an OSINT Agent**

| Dimension | Competitor Approach | FreDeSa Approach |
|-----------|---------------------|------------------|
| **Theory** | ❌ Customer must provide | ✅ Sherman Kent, Richards Heuer, structured analysis |
| **Methods** | ❌ Customer must provide | ✅ Bellingcat, OSINT Framework, platform guides |
| **History** | ❌ Not available | ✅ Cold War → social media evolution, lessons learned |
| **Verification** | ❌ Customer must provide | ✅ RAND disinformation research, fact-checking frameworks |
| **Tools** | ❌ Customer must integrate | ✅ API docs, scraping guides, analysis tools |
| **Trends** | ❌ Not available | ✅ AI-assisted OSINT, deepfake detection, privacy tech |
| **Result** | Task executor ("scrape Twitter") | Expert analyst ("verify source credibility using cognitive bias frameworks") |

**Value Proposition**:
> "Your agents don't just DO intelligence work—they UNDERSTAND intelligence work. From foundational theory to cutting-edge trends, we've curated the complete cognitive foundation that turns code into expertise."

## Context

### The Challenge
- **rDenz Knowledge Registry**: 1,102 curated sources, 39 categories, production-ready
- **Customer Data**: Proprietary documents, SharePoint sites, OneDrive folders
- **Question**: Should we ingest customer data or federate it?

### Competitive Analysis: NexusOne Cognitive

**NexusOne Model** ($42K/month enterprise):
- **Federated Architecture**: Customer data stays in original location
- **Unified Intelligence Layer**: Query federation across disparate systems
- **Apache Iceberg**: Metadata catalog for unified governance
- **Security**: SOC2 Type II, data sovereignty compliance
- **Enterprise Validation**: Bank of America, Wells Fargo, Citibank
- **Funding**: $42M from Insight Partners (Jan 2024)

**Industry Trend (2024-2025)**:
- "Connect, don't copy" - Microsoft Copilot, OpenAI, Anthropic Claude all use federated model
- Compliance advantages: CMMC, FedRAMP, IL4/IL5 (data never leaves customer tenant)
- Cost advantages: Zero storage costs for customer data
- Speed advantages: No ETL delays, real-time queries

## Decision: Hybrid Architecture

### 4-Tier Model

#### **Tier 1: rDenz Curated Knowledge** (COMPLETE COGNITIVE FOUNDATION)
- **Location**: FreDeSa Azure tenant (PostgreSQL + Pinecone)
- **Strategy**: Curate the complete epistemological substrate for each vertical
- **Current State**: 1,067 sources across 42 categories
- **Target State**: 1,500+ sources providing 5-dimensional expertise across 8 priority verticals

**The Five Dimensions of Epistemological Completeness**:

For each vertical, we systematically curate sources across all five dimensions:

**1. THEORY & FOUNDATIONS (WHY)**
- First principles and academic research
- Conceptual frameworks and mental models
- Underlying mechanisms and causal relationships
- Foundational texts and seminal works

*Example (Intelligence)*: Information theory, cognitive biases, structured analytic techniques, Sherman Kent tradecraft

**2. APPLICATION & PRACTICE (HOW)**
- Methodologies and techniques
- Tools and frameworks
- Step-by-step guides and playbooks
- Best practices and standard operating procedures

*Example (Intelligence)*: Bellingcat OSINT methods, geolocation techniques, social media intelligence frameworks, API integration guides

**3. HISTORICAL CONTEXT (WHERE IT CAME FROM)**
- Evolution of the discipline
- What worked and failed historically
- Lessons learned and pattern recognition
- Major paradigm shifts and transitions

*Example (Intelligence)*: Cold War OSINT → satellite imagery → internet era → social media → AI-assisted analysis

**4. CURRENT STATE (WHAT WORKS TODAY)**
- Modern techniques and current best practices
- State-of-the-art approaches
- Industry standards and certifications
- Contemporary case studies and applications

*Example (Intelligence)*: Current platform-specific OSINT (Twitter/X, Telegram, TikTok), fact-checking methodologies, entity resolution techniques

**5. FUTURE TRENDS (WHERE IT'S GOING)**
- Emerging practices and experimental approaches
- Innovation trajectories and leading indicators
- Anticipated disruptions and paradigm shifts
- Research frontiers and bleeding-edge techniques

*Example (Intelligence)*: AI-assisted OSINT, synthetic media detection, privacy-preserving analysis, quantum-resistant cryptography impact

**Vertical Completeness Roadmap** (12 months):

| Vertical | Current Sources | 5D Target | Gap (Sources) | Timeline | Epistemological Coverage |
|----------|----------------|-----------|---------------|----------|-------------------------|
| **Cybersecurity** | 53 | 68 sources | 15 sources | Q1 2026 | Theory: 90%, Practice: 85%, History: 70%, Current: 90%, Future: 60% |
| **Federal Contracting** | 75 | 105 sources | 30 sources | Q1 2026 | Theory: 80%, Practice: 95%, History: 85%, Current: 90%, Future: 50% |
| **Intelligence Community** | 66 | 111 sources | 45 sources | Q1 2026 | Theory: 75%, Practice: 70%, History: 80%, Current: 65%, Future: 55% |
| **K-12 Education** | ~40 | 65 sources | 25 sources | Q2 2026 | Theory: 85%, Practice: 80%, History: 75%, Current: 70%, Future: 45% |
| **Financial Services** | ~35 | 85 sources | 50 sources | Q2 2026 | Theory: 60%, Practice: 65%, History: 55%, Current: 60%, Future: 40% |
| **Legal** | ~30 | 70 sources | 40 sources | Q3 2026 | Theory: 70%, Practice: 75%, History: 60%, Current: 65%, Future: 35% |
| **Manufacturing** | ~25 | 85 sources | 60 sources | Q3 2026 | Theory: 55%, Practice: 60%, History: 50%, Current: 55%, Future: 30% |
| **Healthcare** | ~15 | 95 sources | 80 sources | Q4 2026 | Theory: 45%, Practice: 50%, History: 40%, Current: 45%, Future: 25% |

**Intelligence Community Deep-Dive Example**:

*Dimension 1: Theory & Foundations (75% complete)*
- ✅ Sherman Kent: Intelligence analysis principles
- ✅ Richards Heuer: Psychology of Intelligence Analysis
- ✅ Structured Analytic Techniques (Pherson)
- ✅ Information theory fundamentals
- ❌ Missing: Cognitive bias frameworks (8 sources needed)

*Dimension 2: Application & Practice (70% complete)*
- ✅ Bellingcat investigation guides
- ✅ OSINT Framework methodologies
- ❌ Missing: Platform-specific guides (Twitter/X, Telegram, TikTok) - 15 sources
- ❌ Missing: Entity resolution techniques - 12 sources

*Dimension 3: Historical Context (80% complete)*
- ✅ Cold War intelligence methods
- ✅ Evolution of satellite imagery
- ✅ Rise of open-source intelligence
- ❌ Missing: Social media intelligence history - 3 sources

*Dimension 4: Current State (65% complete)*
- ✅ Modern OSINT techniques
- ❌ Missing: Source credibility assessment - 8 sources
- ❌ Missing: Current fact-checking methodologies - 5 sources
- ❌ Missing: Geolocation verification - 4 sources

*Dimension 5: Future Trends (55% complete)*
- ❌ Missing: AI-assisted OSINT - 7 sources
- ❌ Missing: Synthetic media detection - 6 sources
- ❌ Missing: Privacy-preserving analysis - 4 sources

**Purpose**: Agents don't just know HOW to perform tasks—they understand WHY techniques work, WHERE they came from, WHAT works today, and WHERE the field is evolving. This transforms agents from task executors into true experts.

**Control**: FreDeSa manages epistemological completeness roadmap, validates sources across all 5 dimensions, promotes (dev → staging → prod)

**Market Value**: Complete cognitive foundation = premium pricing power. "True expertise substrate" vs "information access platforms".

#### **Tier 2: Customer Federated Data** (NEXUSONE MODEL)
- **Location**: Customer's tenant (SharePoint, OneDrive, Google Drive, Azure Blob)
- **Access**: OAuth 2.0 read-only permissions
- **Query Pattern**: Real-time API calls when agents need content
- **Security**: Data sovereignty maintained, CMMC/FedRAMP compliant
- **Options**: 
  - Microsoft Graph API (SharePoint, OneDrive)
  - Google Drive API
  - Customer Azure Blob Storage
  - Direct file upload (stored in customer's blob, not FreDeSa's)

#### **Tier 3: Unified Catalog** (APACHE ICEBERG)
- **Purpose**: Metadata layer tracking both rDenz + customer sources
- **Technology**: Apache Iceberg lakehouse
- **Capabilities**:
  - Data lineage across tiers
  - Access policy engine
  - Unified search index
  - Usage analytics for billing
- **Location**: FreDeSa Azure tenant (metadata only, not customer content)

#### **Tier 4: AI Agent Orchestration** (COMPETITIVE ADVANTAGE)
- **Platform**: Airia (5 production agents already deployed)
- **Capability**: Multi-agent orchestration querying BOTH tiers
- **Agents**:
  - Federal Proposal Orchestrator (coordinates 4 specialized agents)
  - Capture Planning Agent (federal opportunity assessment)
  - Capture Strategy Agent (win strategy development)
  - M365 Admin Agent (SharePoint/OneDrive management)
  - Proposal Coordinator Agent (proposal writing orchestration)
- **Differentiation**: Competitors offer federation OR agents, we offer BOTH

## Competitive Positioning

### FreDeSa vs NexusOne

| Dimension | NexusOne Cognitive | FreDeSa AI Platform |
|-----------|-------------------|---------------------|
| **Architecture** | Pure federation | Hybrid (curated + federated) |
| **Target Market** | Enterprise (Fortune 500) | SMB/Mid-market (GovCon firms) |
| **Pricing** | $42K/month | $417-$4,167/month |
| **Contract Length** | 3-5 years | Monthly SaaS |
| **Deployment Time** | 4-6 weeks | 24 hours |
| **Knowledge Model** | Customer provides everything | 5-dimensional epistemological completeness |
| **Domain Expertise** | 0 sources (generic platform) | 1,067 sources → 1,500+ (8 verticals) |
| **Theory (WHY)** | ❌ Customer must provide | ✅ First principles, frameworks, foundations |
| **Practice (HOW)** | ❌ Customer must provide | ✅ Methodologies, tools, guides, best practices |
| **History (WHERE FROM)** | ❌ Not available | ✅ Evolution, lessons learned, patterns |
| **Current (WHAT WORKS)** | ❌ Customer must provide | ✅ Modern techniques, standards, case studies |
| **Future (WHERE GOING)** | ❌ Not available | ✅ Trends, innovations, research frontiers |
| **Agent Capability** | Task executor | Expert with understanding |
| **AI Agents** | ❌ Query only | ✅ Multi-agent orchestration |
| **Data Location** | Customer tenant | Hybrid (FreDeSa curated + customer federated) |
| **Compliance** | SOC2 Type II | SOC2 ready (in progress) |
| **Funding** | $42M (Insight Partners) | Bootstrapped (3 cofounders) |

### Differentiation Strategy

**Adopt NexusOne's strengths**:
- ✅ Federated customer data (compliance advantage)
- ✅ Apache Iceberg metadata catalog (unified governance)
- ✅ OAuth read-only access (security best practice)

**Differentiate on**:
- ✅ **Domain Expertise**: 1,102 curated federal contracting, AI, cybersecurity sources
- ✅ **AI Agents**: Multi-agent orchestration (5 production agents vs none)
- ✅ **SMB Pricing**: $417/month vs $42K/month (100x more affordable)
- ✅ **Deployment Velocity**: 24 hours vs 4-6 weeks (170x faster)
- ✅ **Self-Service**: SaaS model vs enterprise sales cycle

## Schema Changes Required

### Existing Tables (No Changes)
- ✅ `categories` - Already supports taxonomy
- ✅ `customers` - Already multi-tenant ready
- ✅ `usage_tracking` - Already tracks consumption

### Updates to `sources` Table

```sql
ALTER TABLE sources ADD COLUMN IF NOT EXISTS environment_flags JSONB DEFAULT '{"dev": true, "staging": false, "production": false}'::jsonb;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS promoted_to_staging_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS promoted_to_production_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS promoted_by VARCHAR(255);
ALTER TABLE sources ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved_for_staging', 'approved_for_production', 'rejected'));
ALTER TABLE sources ADD COLUMN IF NOT EXISTS source_location VARCHAR(100) DEFAULT 'rdenz_managed' CHECK (source_location IN ('rdenz_managed', 'customer_sharepoint', 'customer_onedrive', 'customer_drive', 'customer_blob', 'customer_upload'));

COMMENT ON COLUMN sources.environment_flags IS 'JSONB flags for environment visibility: {dev: bool, staging: bool, production: bool}';
COMMENT ON COLUMN sources.quality_score IS 'Automated quality score (0-100): authority_level + word_count + freshness + validation';
COMMENT ON COLUMN sources.source_location IS 'Data location: rdenz_managed (FreDeSa tenant) or customer_* (federated)';
```

### New Table: `customer_connectors`

```sql
CREATE TABLE IF NOT EXISTS customer_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_type VARCHAR(50) NOT NULL CHECK (connector_type IN ('microsoft_graph', 'google_drive', 'azure_blob', 'direct_upload')),
    connector_name VARCHAR(255) NOT NULL,
    
    -- OAuth 2.0 tokens (encrypted at application layer)
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Connector configuration
    connector_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Example for Microsoft Graph: {"tenant_id": "...", "site_id": "...", "drive_id": "..."}
    -- Example for Google Drive: {"folder_id": "...", "service_account_key": "..."}
    -- Example for Azure Blob: {"storage_account": "...", "container_name": "..."}
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_sync_status VARCHAR(50),
    last_error TEXT,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(customer_id, connector_name)
);

CREATE INDEX idx_customer_connectors_customer ON customer_connectors(customer_id);
CREATE INDEX idx_customer_connectors_type ON customer_connectors(connector_type);
CREATE INDEX idx_customer_connectors_active ON customer_connectors(customer_id, is_active);

COMMENT ON TABLE customer_connectors IS 'OAuth configurations for federated customer data sources';
COMMENT ON COLUMN customer_connectors.access_token_encrypted IS 'Encrypted OAuth access token (AES-256-GCM at app layer)';
COMMENT ON COLUMN customer_connectors.connector_config IS 'Type-specific configuration (tenant IDs, folder IDs, etc)';
```

### New Table: `source_promotions`

```sql
CREATE TABLE IF NOT EXISTS source_promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Promotion details
    from_environment VARCHAR(50) NOT NULL CHECK (from_environment IN ('dev', 'staging', 'production')),
    to_environment VARCHAR(50) NOT NULL CHECK (to_environment IN ('dev', 'staging', 'production')),
    promoted_by VARCHAR(255) NOT NULL,
    promoted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Quality gate results
    quality_checks_passed JSONB,
    -- Example: {"authority_level": "Official", "word_count": 5000, "staging_days": 10, "approvers": ["user1", "user2"]}
    
    -- Approval workflow
    approval_status VARCHAR(50) DEFAULT 'approved' CHECK (approval_status IN ('approved', 'rejected', 'rolled_back')),
    rejection_reason TEXT,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source_promotions_source ON source_promotions(source_id);
CREATE INDEX idx_source_promotions_customer ON source_promotions(customer_id);
CREATE INDEX idx_source_promotions_timeline ON source_promotions(promoted_at DESC);
CREATE INDEX idx_source_promotions_environment ON source_promotions(to_environment, promoted_at DESC);

COMMENT ON TABLE source_promotions IS 'Audit trail for source environment promotions (dev → staging → production)';
COMMENT ON COLUMN source_promotions.quality_checks_passed IS 'JSON record of quality gate validations at promotion time';
```

### New Table: `connector_query_log`

```sql
CREATE TABLE IF NOT EXISTS connector_query_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    connector_id UUID NOT NULL REFERENCES customer_connectors(id) ON DELETE CASCADE,
    
    -- Query details
    query_type VARCHAR(50) NOT NULL CHECK (query_type IN ('list_files', 'get_content', 'search', 'metadata')),
    resource_path TEXT,
    query_params JSONB,
    
    -- Agent context
    agent_id VARCHAR(255),
    agent_execution_id VARCHAR(255),
    
    -- Performance
    query_started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    query_completed_at TIMESTAMP WITH TIME ZONE,
    response_time_ms INTEGER,
    response_size_bytes INTEGER,
    
    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('success', 'error', 'timeout', 'unauthorized')),
    error_message TEXT,
    
    -- Billing
    billable_units DECIMAL(10,2),
    -- Example: API calls, data transfer GB, compute minutes
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_connector_query_log_customer ON connector_query_log(customer_id, created_at DESC);
CREATE INDEX idx_connector_query_log_connector ON connector_query_log(connector_id, created_at DESC);
CREATE INDEX idx_connector_query_log_agent ON connector_query_log(agent_execution_id);
CREATE INDEX idx_connector_query_log_billing ON connector_query_log(customer_id, created_at DESC, billable_units);

COMMENT ON TABLE connector_query_log IS 'Log of federated queries for analytics, debugging, and billing';
COMMENT ON COLUMN connector_query_log.billable_units IS 'Usage metrics for billing (API calls, data transfer, compute)';
```

## Approval Workflow

### Quality Gates

**Staging Promotion (dev → staging)**:
- ✅ Authority level: "Official" or "Expert" (not "Community")
- ✅ Minimum word count: 1,000 words
- ✅ Minimum time in dev: 7 days (ensures stability testing)
- ✅ Approver count: 1 approver required
- ✅ Quality score: ≥ 70/100

**Production Promotion (staging → production)**:
- ✅ Authority level: "Official" or "Expert"
- ✅ Minimum word count: 1,000 words
- ✅ Minimum time in staging: 14 days
- ✅ Approver count: 2 approvers required (dual authorization)
- ✅ Quality score: ≥ 85/100
- ✅ Zero critical validation errors

### Approval Commands

```bash
# List pending sources for approval
python3 scripts/provisioning/list_pending_sources.py --environment staging

# Approve source for staging
python3 scripts/provisioning/approve_source.py \
  --source-id 019c1234-5678-90ab-cdef-1234567890ab \
  --environment staging \
  --approver "del.chaplin@fredesa.com"

# Approve source for production (requires 2 approvers)
python3 scripts/provisioning/approve_source.py \
  --source-id 019c1234-5678-90ab-cdef-1234567890ab \
  --environment production \
  --approver "frank.murphy@fredesa.com"
```

## Implementation Roadmap

### Week 1 (Dec 29 - Jan 4) - Foundation ✅
- ✅ Day 1: PostgreSQL schema (COMPLETE)
- ✅ Day 1: Architecture decision (THIS DOCUMENT)
- 🔄 Day 1: Update schema with federated fields + vertical completeness tracking
- Day 2: Repository adapter (CRUD operations)
- Day 3-5: API endpoints

### Week 2 (Jan 5-11) - Approval Workflow + Vertical Planning
- Approval CLI tools (`approve_source.py`, `list_pending_sources.py`)
- Quality gate validation
- Multi-approver logic
- Audit trail logging
- **NEW**: Create vertical completeness framework
  - Define 8 priority verticals
  - Map orchestration patterns per vertical
  - Identify knowledge gaps (sources needed)
  - Build 90-day ingestion roadmap

### Week 3-4 (Jan 12-25) - Vertical Gap-Filling: Cybersecurity
- **Target**: 15 sources → 95% completeness
- Advanced threat intelligence sources
- Zero-trust architecture guides
- CMMC 2.0 supplemental materials
- Security automation frameworks
- Incident response playbooks

### Week 5-6 (Jan 26 - Feb 8) - Vertical Gap-Filling: Federal Contracting
- **Target**: 30 sources → 95% completeness
- GovWin competitive intelligence integration
- Agency-specific evaluation criteria (scraped)
- Historical pricing data (FPDS integration)
- Teaming agreement templates
- Subcontracting plan guides

### Week 7-10 (Feb 9 - Mar 8) - Vertical Gap-Filling: Intelligence Community
- **Target**: 45 sources → 90% completeness
- Social media OSINT (15 sources: Bellingcat, platform guides)
- Source credibility assessment (8 sources: RAND, fact-checking)
- Entity resolution (12 sources: NLP, graph databases)
- Satellite imagery analysis (10 sources: NGA, change detection)

### Week 11-16 - Federated Architecture Implementation
- Microsoft 365 Connector (OAuth, SharePoint, OneDrive)
- Google Workspace Connector (OAuth, Drive)
- Apache Iceberg metadata catalog
- Unified catalog tracking rDenz + customer sources

### Week 17-20 (Q2 2026) - Vertical Gap-Filling: Education + Finance
- K-12 Education: 25 sources → 90%
- Financial Services: 50 sources → 85%

### Week 21+ (Q3-Q4 2026) - Remaining Verticals + Advanced Features
- Legal, Manufacturing, Healthcare: 180 sources total
- Custom agent builder (no-code)
- Knowledge gap analyzer (upsell engine)
- Compliance dashboards (CMMC, FedRAMP, HIPAA)

### End State (December 2026)
- **1,500+ total sources** (1,067 current + 433 new)
- **8 verticals at 90%+ completeness**
- **Federated architecture deployed**
- **Market positioning**: "Complete knowledge substrate for [your vertical]"

## Product Features Enabled

### 1. Customer Ingestion Portal (HIGHEST VALUE)
**Problem**: Customers have proprietary data that rDenz doesn't cover  
**Solution**: Let customers upload/link their own documents  
**Implementation**: 
- Option A: Direct file upload → stored in customer's Azure Blob (NOT FreDeSa's)
- Option B: Link SharePoint/OneDrive → OAuth read-only access
- Option C: Link Google Drive → OAuth read-only access
**Pricing Tier**: Professional ($833/mo) and Enterprise ($4,167/mo)

### 2. Custom Agent Builder (NO-CODE)
**Problem**: Every customer needs slightly different agent workflows  
**Solution**: Drag-and-drop agent builder using rDenz knowledge + customer's proprietary data  
**Implementation**: Airia platform UI + rDenz + customer federated sources  
**Pricing Tier**: Enterprise ($4,167/mo)

### 3. Semantic Search API (PROGRAMMATIC ACCESS)
**Problem**: Customers want to integrate FreDeSa into their own applications  
**Solution**: REST API for semantic search across rDenz + customer knowledge  
**Implementation**: FastAPI endpoint + Pinecone + federated query layer  
**Pricing Tier**: Professional ($833/mo) - API calls metered separately

### 4. Knowledge Gap Analyzer (UPSELL ENGINE)
**Problem**: Customers don't know what knowledge they're missing  
**Solution**: AI analyzes customer's questions, identifies gaps, recommends tier upgrades  
**Implementation**: Track agent queries → identify missing sources → recommend ingestion  
**Pricing Tier**: Built into all tiers, drives upsell

### 5. Compliance Dashboards (CMMC/FEDRAMP)
**Problem**: GovCon firms need to prove CMMC/FedRAMP readiness  
**Solution**: Real-time compliance dashboards showing coverage gaps  
**Implementation**: Map customer's knowledge to CMMC/FedRAMP controls → visualize gaps  
**Pricing Tier**: Enterprise ($4,167/mo)

## Security & Compliance

### Data Sovereignty
- ✅ **Customer Data**: Never leaves customer's tenant
- ✅ **rDenz Data**: Stored in FreDeSa Azure tenant (US East)
- ✅ **Metadata**: Apache Iceberg catalog tracks lineage, not content

### Access Control
- ✅ **OAuth 2.0**: Read-only permissions
- ✅ **Row-Level Security**: PostgreSQL RLS policies for tenant isolation
- ✅ **Token Encryption**: AES-256-GCM for stored OAuth tokens
- ✅ **Audit Logging**: All federated queries logged in `connector_query_log`

### Compliance Certifications (In Progress)
- 🔄 SOC2 Type II (target: Q2 2026)
- 🔄 CMMC Level 2 (target: Q3 2026)
- 🔄 FedRAMP Moderate (target: Q4 2026)
- 🔄 IL4/IL5 (target: 2027)

## Success Metrics

### Technical Metrics
- **Query Latency**: <500ms for federated queries (p95)
- **Availability**: 99.9% uptime (8.76 hours downtime/year)
- **Data Loss**: Zero customer data loss (federated model = customer controls)
- **Token Security**: Zero OAuth token breaches

### Business Metrics
- **Customer Adoption**: 80% of Professional/Enterprise customers enable connectors
- **Cost Savings**: $0 storage costs for customer data (vs $X/TB for ingestion)
- **Compliance Wins**: 50% of GovCon customers cite data sovereignty as key decision factor
- **Upsell Rate**: 30% of Starter ($417/mo) customers upgrade to Professional ($833/mo) after 90 days

## Risks & Mitigations

### Risk 1: OAuth Token Management Complexity
**Impact**: High - Security breach if tokens leaked  
**Likelihood**: Medium  
**Mitigation**: 
- AES-256-GCM encryption for stored tokens
- Azure Key Vault for encryption keys
- Token rotation every 90 days
- Audit logging for all token access

### Risk 2: Federated Query Performance
**Impact**: Medium - Slow queries = poor UX  
**Likelihood**: Medium  
**Mitigation**: 
- Cache embeddings in customer's Pinecone namespace (optional)
- Parallel query execution across sources
- Pre-fetch common documents (with customer consent)
- CDN for static content

### Risk 3: Customer Connector Setup Friction
**Impact**: High - Complex setup = low adoption  
**Likelihood**: High  
**Mitigation**: 
- One-click OAuth flows (Microsoft/Google)
- Pre-built connector templates
- Video tutorials and documentation
- White-glove onboarding for Enterprise customers

### Risk 4: Apache Iceberg Operational Overhead
**Impact**: Medium - Complex to maintain  
**Likelihood**: Low (we have expertise)  
**Mitigation**: 
- Managed Iceberg service (Azure Data Lake)
- Automated backups and monitoring
- SRE playbooks for common issues

## Conclusion

**Decision**: Adopt hybrid federated + curated architecture with **vertical knowledge completeness** strategy

**Rationale**:
1. **Vertical Completeness**: Systematic curation of 90%+ sources per vertical = competitive moat
2. **Customer Enablement**: Customers build THEIR agents with OUR complete knowledge substrate
3. **Compliance**: Federated customer data (NexusOne model) required for CMMC/FedRAMP/HIPAA
4. **Market Differentiation**: "Complete knowledge for [vertical]" vs generic platforms
5. **Scalable Growth**: Proven model (NexusOne $42M) + vertical-specific expertise (unique)

**The Winning Formula**:
```
FreDeSa = NexusOne's Federated Architecture
        + Vertical Knowledge Completeness (90%+ sources per vertical)
        + AI Agent Orchestration (multi-agent workflows)
        + SMB Economics ($417/mo vs $42K/mo)
```

**Strategic Priorities (2026)**:

**Q1**: Fill critical gaps in 3 anchor verticals
- Cybersecurity: +15 sources → 95% complete
- Federal Contracting: +30 sources → 95% complete  
- Intelligence Community: +45 sources → 90% complete

**Q2**: Implement federated architecture + expand to 2 more verticals
- Microsoft 365 + Google Drive connectors
- K-12 Education: +25 sources → 90% complete
- Financial Services: +50 sources → 85% complete

**Q3-Q4**: Complete remaining 3 verticals + advanced features
- Legal, Manufacturing, Healthcare: +180 sources
- Custom agent builder (no-code)
- Compliance dashboards

**End State (Dec 2026)**:
- **1,500+ sources** across 8 verticals at 90%+ completeness
- **Market positioning**: "The complete knowledge substrate for [your vertical]"
- **Customer value**: "We have 90% of what you need. Build your agents in hours, not months."

**Approval**: ✅ Del Chaplin (Founder/CEO) - December 29, 2025

---

*This strategy transforms FreDeSa from a generic platform to the **definitive knowledge substrate** for each industry vertical we serve. Vertical completeness = competitive moat = premium pricing power.*
