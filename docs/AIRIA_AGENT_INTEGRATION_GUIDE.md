# Airia Agent Integration Guide - Knowledge Base Query

**Purpose:** Connect existing Airia agents to FreDeSa PostgreSQL knowledge base (1,043 sources)

---

## 🎯 Quick Start (15 minutes)

### 1. Copy Function to Airia Environment

The core function is `query_knowledge_base()` in:
```
scripts/airia/query_knowledge_base.py
```

**Key function signature:**
```python
def query_knowledge_base(
    query: str,
    dimension: Optional[str] = None,  # "theory", "practice", or "current"
    category: Optional[str] = None,   # "Federal_Contracting", "Intelligence", etc.
    min_authority: int = 70,          # 50, 70, or 90
    limit: int = 5,                   # Max results
    include_content: bool = False     # Include word counts
) -> Dict
```

### 2. Test Query Function

```bash
# Test capture planning query
python3 scripts/airia/query_knowledge_base.py "capture planning strategies"

# Test with filters
python3 scripts/airia/query_knowledge_base.py "proposal writing" --dimension practice --min-authority 90

# Test intelligence query
python3 scripts/airia/query_knowledge_base.py "OSINT collection methods" --category Intelligence
```

---

## 🤖 Agent Integration Patterns

### Pattern 1: Pre-Prompt Knowledge Injection

**Use Case:** Agent gets relevant sources BEFORE generating response

**Implementation:**
1. User query arrives at agent
2. Extract keywords from user query
3. Call `query_knowledge_base(query)`
4. Get `format_for_agent_prompt(result)` output
5. Prepend to agent's system prompt
6. Agent generates response with authoritative citations

**Example:**
```python
# User asks: "How do I create a subcontracting plan?"

# 1. Query knowledge base
kb_result = query_knowledge_base(
    query="subcontracting plan requirements",
    dimension="practice",
    min_authority=70,
    limit=5
)

# 2. Format for agent
knowledge_context = format_for_agent_prompt(kb_result)

# 3. Inject into prompt
agent_prompt = f"""
{knowledge_context}

USER QUESTION: {user_query}

Using the knowledge sources above, provide a detailed answer with citations.
Format citations as [Source: Name].
"""

# 4. Agent processes with context
agent_response = airia_agent.process(agent_prompt)
```

### Pattern 2: Post-Response Citation Addition

**Use Case:** Agent generates response, then adds authoritative citations

**Implementation:**
1. Agent generates initial response
2. Extract key topics from response
3. Query knowledge base for each topic
4. Append "References" section with sources
5. Return enhanced response

**Example:**
```python
# Agent response about FAR compliance
agent_response = "To comply with FAR regulations..."

# Extract topics
topics = extract_topics(agent_response)  # ["FAR", "compliance", "cost accounting"]

# Get citations for each
citations = []
for topic in topics:
    kb_result = query_knowledge_base(topic, min_authority=90, limit=2)
    citations.extend(kb_result['sources'])

# Append references
enhanced_response = f"""
{agent_response}

---
**REFERENCES:**
{format_citations(citations)}
"""
```

### Pattern 3: Knowledge-Augmented Validation

**Use Case:** Verify agent response against authoritative sources

**Implementation:**
1. Agent generates response
2. Query knowledge base with response keywords
3. Compare agent claims vs. source content
4. Flag any conflicts or add warnings
5. Return validated response

---

## 📋 Agent-Specific Integration

### Capture Planning Agent
**Agent ID:** `58044acf-9b68-4137-bfe2-7aa3dcb085d1` (Dev) / `210b5785-15fa-4051-a4f6-c15686a91efb` (Customer)

**Query Strategy:**
- **Dimension:** `practice` (focus on how-to guidance)
- **Categories:** `Federal_Contracting`, `Intelligence`, `Methodologies`
- **Min Authority:** `70` (mix of official + expert sources)

**Sample Queries:**
```python
# Opportunity analysis
query_knowledge_base("competitive analysis federal contracts", dimension="practice")

# Capture strategy
query_knowledge_base("win themes proposal strategy", dimension="practice", min_authority=70)

# Customer intelligence
query_knowledge_base("customer engagement strategies government", category="Intelligence")
```

**Integration Point:** Add to Capture Planning Agent's system prompt:
```
Before answering, search the knowledge base using query_knowledge_base().
Cite authoritative sources (Authority 70+) using [Source: Name] format.
Prefer official DoD/federal sources (Authority 90) for compliance questions.
```

### Capture Strategy Agent
**Agent ID:** `bed0ff99-2689-4fdb-b2d0-06b9ab62eb04` (Dev) / `5b1541d1-d973-47e2-bdc6-7bb0a4808344` (Customer)

**Query Strategy:**
- **Dimension:** Mix of `theory` (frameworks) + `practice` (implementation)
- **Categories:** `Methodologies`, `Federal_Contracting`, `Proposal Development`
- **Min Authority:** `70`

**Sample Queries:**
```python
# Win strategy development
query_knowledge_base("Shipley win strategy", category="Methodologies", min_authority=70)

# Discriminators
query_knowledge_base("competitive discriminators proposal", dimension="practice")

# Pricing strategy
query_knowledge_base("FAR cost proposal pricing", dimension="practice", min_authority=90)
```

### Proposal Coordinator Agent
**Agent ID:** `d3715faf-bdb1-4f7b-9c87-3b36c8e41c23` (Dev) / `2114192d-0846-494e-b0f4-631b96e73811` (Customer)

**Query Strategy:**
- **Dimension:** `practice` (proposal execution guidance)
- **Categories:** `Proposal Development`, `Federal_Contracting`, `Methodologies`
- **Min Authority:** `90` (official guidance only for compliance)

**Sample Queries:**
```python
# Compliance matrix
query_knowledge_base("FAR compliance requirements", min_authority=90)

# Volume structure
query_knowledge_base("proposal volume organization", dimension="practice")

# Review gates
query_knowledge_base("proposal review process Shipley", category="Methodologies")
```

### M365 Admin Agent
**Agent ID:** `b848d458-be12-4a22-b527-2b991bc22cca` (Dev)

**Query Strategy:**
- **Dimension:** `practice` (technical how-to)
- **Categories:** `Cloud Platforms`, `AI/LLM Platforms`, `LLM Frameworks`
- **Min Authority:** `70` (mix of official + expert technical docs)

**Sample Queries:**
```python
# SharePoint automation
query_knowledge_base("SharePoint document automation", category="Cloud Platforms")

# Azure integration
query_knowledge_base("Azure OpenAI deployment government cloud", min_authority=90)

# Microsoft Graph API
query_knowledge_base("Microsoft Graph API authentication", dimension="practice")
```

### Orchestrator Agent (v3)
**Agent ID:** `cf6e3fb4-085c-456f-b4e2-4b69c65e484b` (Dev)

**Query Strategy:**
- **Dimension:** All dimensions (orchestrator needs comprehensive knowledge)
- **Categories:** All relevant to user query
- **Min Authority:** `70` (balanced approach)

**Sample Queries:**
```python
# Route to correct agent based on knowledge availability
topics = query_knowledge_base(user_query, limit=10)

if any(s['category'] == 'Federal_Contracting' for s in topics['sources']):
    route_to = "Capture Planning Agent"
elif any(s['category'] == 'Intelligence' for s in topics['sources']):
    route_to = "Capture Strategy Agent"
# ... routing logic
```

---

## 🔧 Implementation Steps

### Step 1: Add to Agent System Prompt (5 min)

Edit each agent in Airia UI:

**Before:**
```
You are a federal capture planning expert.
```

**After:**
```
You are a federal capture planning expert with access to 1,043 authoritative knowledge sources.

KNOWLEDGE BASE ACCESS:
- 180 official government sources (FAR, DFARS, NIST)
- 592 expert technical documentation sources
- 271 community resources
- Epistemological dimensions: theory, practice, current

CITATION REQUIREMENT:
Always cite sources using [Source: Name] format.
Prefer official sources (Authority 90) for compliance/regulatory questions.
Use expert sources (Authority 70) for technical guidance.
```

### Step 2: Create Knowledge Query Step (10 min)

Add AIOperation step to each agent:

1. **Input:** User query
2. **Process:** Call `query_knowledge_base()` function
3. **Output:** Formatted knowledge context
4. **Pass to:** Main agent operation

**Airia Step Configuration:**
```json
{
  "stepType": "AIOperation",
  "stepTitle": "Query Knowledge Base",
  "modelId": "gpt-4o-mini",
  "temperature": 0.3,
  "maxTokens": 2048,
  "inputTemplate": "Extract 3-5 key topics from this query: {{userInput}}",
  "tools": ["python-code-execution"],
  "systemPrompt": "Extract key topics and return Python code: query_knowledge_base(topics, dimension='practice', min_authority=70)"
}
```

### Step 3: Test Each Agent (30 min)

**Test Script:**
```bash
# Capture Planning Agent test
curl -X POST https://api.airia.ai/v1/PipelineExecution/58044acf-9b68-4137-bfe2-7aa3dcb085d1 \
  -H "X-API-Key: $AIRIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "userInput": "How do I analyze a federal opportunity for capture planning?",
    "debug": true
  }'

# Verify knowledge sources appear in response
```

Run test for each agent:
- ✅ Capture Planning Agent
- ✅ Capture Strategy Agent
- ✅ Proposal Coordinator Agent
- ✅ M365 Admin Agent
- ✅ Orchestrator Agent

### Step 4: Create Demo Video (30 min)

**Demo Script:**
1. Show knowledge base stats (1,043 sources, 43 categories)
2. Test query function in terminal
3. Show agent WITHOUT knowledge integration (generic response)
4. Show agent WITH knowledge integration (cited, authoritative response)
5. Highlight authority scores and epistemological dimensions

**Recording:** Loom/QuickTime, 5-minute video

---

## 📊 Expected Results

### Before Integration
```
User: "How do I create a subcontracting plan?"
Agent: "A subcontracting plan typically includes goals for small business participation..."
```
*Generic, no citations, no authority*

### After Integration
```
User: "How do I create a subcontracting plan?"
Agent: "According to FAR Part 19 [Source: FAR Part 19: Small Business Subcontracting Programs],
a subcontracting plan must include:

1. Separate goals for small business, SDVOSB, HUBZone, WOSB, and 8(a) participation
2. Description of principal types of supplies/services to be subcontracted
3. Methods used to develop subcontracting goals [Source: FAR Subpart 31.2]
4. Planned procedures to maximize subcontracting opportunities

The plan must comply with FAR 19.704 requirements and be reviewed by the contracting officer
prior to contract award [Source: DFARS PGI 215.3 Source Selection Procedures].

AUTHORITATIVE SOURCES:
• FAR Part 19 (Authority: 90, Official, 45,638 words)
• FAR Subpart 31.2 (Authority: 90, Official, 32,486 words)
• DFARS PGI 215.3 (Authority: 90, Official)"
```
*Specific, cited, authoritative, actionable*

---

## 🎬 Demo Talking Points

### 30-Second Pitch
"Our agents now have access to 1,043 authoritative knowledge sources - 180 official government sources like FAR and DFARS, plus 592 expert technical docs. Every response includes citations with authority scores. Watch..."

### 2-Minute Demo
1. "Here's a capture planning question: 'How do I analyze an opportunity?'"
2. "Agent queries our knowledge base in real-time"
3. "Returns 5 authoritative sources - all official DoD/federal guidance"
4. "Agent response includes specific FAR citations with authority scores"
5. "This is the difference between generic AI and authoritative AI"

### Key Differentiators
- ✅ **Authority Scoring:** Not all sources are equal (90 official > 70 expert > 50 community)
- ✅ **Epistemological Dimensions:** Theory (frameworks) vs. Practice (how-to) vs. Current (state-of-art)
- ✅ **Multi-Tenant:** Each customer gets their own knowledge base + shared federal sources
- ✅ **Compliance-Ready:** Direct FAR/DFARS citations for audit trails
- ✅ **Always Current:** Knowledge base updates don't require agent retraining

---

## 🚀 Next Steps After Integration

### Option 1: Customer-Specific Knowledge
**Time:** 1 hour per customer  
Add customer's internal sources:
- Company procedures
- Past proposals (sanitized)
- Win themes from successful captures
- Lessons learned documents

### Option 2: Knowledge Graph Enhancement
**Time:** 2 hours  
Map relationships:
- "FAR Part 15 implements the theory from FAR Part 1"
- "Shipley methodology applies to federal contracting"
- "NIST AI RMF guides Azure OpenAI deployment"

### Option 3: Semantic Search Upgrade
**Time:** 3 hours  
Add vector embeddings:
- pgvector extension in PostgreSQL
- Semantic similarity (not just keywords)
- "Find sources similar to this one"

### Option 4: Real-Time Updates
**Time:** 2 hours  
Automated source ingestion:
- Monitor FAR/DFARS updates
- Ingest new regulations automatically
- Alert agents to regulatory changes

---

## 📝 Success Metrics

Track these after integration:

1. **Citation Rate:** % of agent responses with knowledge base citations
   - Target: >80%

2. **Authority Score:** Average authority of cited sources
   - Target: >75 (mix of official + expert)

3. **User Satisfaction:** "Was this response helpful?"
   - Target: >90% for cited responses vs. <70% for uncited

4. **Response Quality:** Specificity, actionability, compliance
   - Measure: Review team rating 1-5 scale
   - Target: Average 4.5+ for knowledge-augmented responses

5. **Time to Value:** Days until first customer demo
   - Target: TODAY (within 2 hours of integration completion)

---

## 🔒 Security & Compliance

### Data Protection
- ✅ All connections use SSL (Azure PostgreSQL)
- ✅ Credentials via Azure Key Vault (no hardcoded secrets)
- ✅ Row-Level Security (RLS) for multi-tenant isolation
- ✅ Audit logging (all queries tracked)

### Compliance Readiness
- ✅ FedRAMP-ready infrastructure (Azure Government Cloud)
- ✅ NIST 800-53 controls implemented
- ✅ Audit trail for all knowledge access
- ✅ Source authority tracking (official/expert/community)

### Access Control
- ✅ Airia agents use service principal authentication
- ✅ Customer-scoped queries (RLS enforcement)
- ✅ Read-only access to knowledge base
- ✅ No PII/CUI in source content (validated during ingestion)

---

**Time to Complete:** 1-2 hours  
**Immediate Value:** Demo-ready knowledge-augmented agents TODAY  
**Customer Impact:** Authoritative, cited responses vs. generic AI responses

**Ready to integrate? Let's start with Capture Planning Agent!**
