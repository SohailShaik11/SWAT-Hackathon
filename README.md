# CampaignPulse: AI-Powered Pre-Launch Campaign Intelligence

> **Team:** LatentView Analytics — Communications & Devices Entity  
> **Hackathon:** SWAT Hackathon 2026 — AI / AI Agents in Marketing Operations  
> **Clients:** Microsoft, HP

---

## 🎯 Problem Statement

### The Gap in Marketing Operations

Enterprise technology companies like Microsoft and HP run **50–100+ marketing campaigns per quarter**. Every campaign begins with a **campaign brief** — the document that defines what the campaign should achieve, who it targets, and how it will run.

**The problem:** There is no structured quality gate between "brief written" and "money spent."

| Pain Point | Impact |
|---|---|
| **Ambiguous briefs** create 8–15 hours of downstream rework per campaign | A brief says "target enterprise on social" — which platform? What format? What audience parameters? Agencies ask. Meetings happen. Days pass. |
| **Misalignments between brief and assets** go undetected until post-campaign analysis | LinkedIn ad targets junior marketers, but the brief said VP-level. The email says "Learn More," but the brief said "Book a Demo." Nobody catches it until KPIs underperform. |
| **No predictive scoring** exists for campaign readiness | Post-campaign analytics tells you what went wrong. Nothing tells you what *will* go wrong based on the brief's quality — before you commit budget. |

**The cost:** Campaigns with incomplete briefs underperform by **20–35%** against target KPIs. For a $2.4M campaign (like Microsoft Surface's Q3 push), that's $480K–$840K in avoidable waste.

### What Exists Today

```
Brief → [manual handoff, meetings, Slack threads] → Execution → Campaign Runs → MEASUREMENT → Insights
                                                                                    ↑
                                                                        You only learn here
                                                                        (after money is spent)
```

### What's Missing

A **pre-launch intelligence layer** that scores the brief, generates a validated execution plan, and audits all assets for alignment — **before a single dollar is spent**.

---

## 💡 Solution: CampaignPulse

CampaignPulse is an AI-powered system with **three agents** that operate as a pre-launch quality gate:

```
Brief → [SCORE] → [PLAN] → [AUDIT] → ✅ Launch-Ready
         Agent 1    Agent 2   Agent 3
```

### Agent 1: Brief Readiness Scorer

**Input:** Raw campaign brief (text/PDF)  
**Output:** Quantified readiness score (0–100) across 6 dimensions + actionable clarifying questions

| Dimension | What It Checks |
|---|---|
| Audience Precision | Can you build ad targeting from this? Or is it just "enterprise customers"? |
| Channel Specificity | Are channels named with platform + format + ownership? Or just "social"? |
| Message-Product Fit | Does the message connect to a real product feature, or is it generic brand speak? |
| Budget Allocation | Is budget broken down by channel, or just a lump sum (or missing entirely)? |
| Timeline Feasibility | Are there real milestones, or just "launch in Q3"? |
| Measurement Hookability | Can the KPIs actually be tracked with existing tools? |

**Key insight:** The scorer doesn't just flag "budget is missing" — it asks: *"The brief allocates no budget. Should we assume $500K total with 40% to LinkedIn given the enterprise audience, or do you have a different allocation?"*

### Agent 2: Execution Plan Generator

**Input:** Scored brief + campaign manager's answers to gap questions  
**Output:** Structured JSON execution plan with channel specs, weekly timeline, copy guidance, and tracking setup

The plan is operational, not decorative:
- Channel-by-channel spec sheets (audience targeting params, ad format, copy length, CTA)
- Week-by-week milestone calendar with QA windows
- Per-channel copy guidance stubs (headline direction, tone, constraints)
- UTM parameter structure for measurement continuity
- Risk flags for unresolved assumptions

### Agent 3: Pre-Launch Alignment Auditor

**Input:** Brief + Execution Plan + Channel Assets (email copy, LinkedIn ads, landing pages, sales scripts)  
**Output:** Alignment audit report with severity-tagged issues and fix suggestions

Checks 5 dimensions using **both LLM reasoning and embedding-based semantic similarity**:

1. **Audience Alignment** — Is the copy talking to the right people?
2. **Message Consistency** — Has the key message drifted across channels?
3. **CTA Coherence** — Are all CTAs driving to the same objective?
4. **Constraint Compliance** — Does any asset violate brand/legal rules?
5. **Gap Detection** — Are channels in the brief but missing from the plan?

**Key insight:** The auditor distinguishes between **genuine errors** (wrong audience = Critical) and **intentional channel adaptations** (casual tone on LinkedIn = Info). It doesn't false-flag everything — it's smart.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Phase 1  │  │   Phase 2    │  │     Phase 3      │  │
│  │  Score   │  │   Plan Gen   │  │  Alignment Audit │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬─────────┘  │
└───────┼────────────────┼───────────────────┼────────────┘
        │                │                   │
        ▼                ▼                   ▼
┌──────────────────────────────────────────────────────────┐
│                    AGENT LAYER                            │
│                                                          │
│  ┌────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │   Brief    │  │     Plan       │  │  Alignment    │  │
│  │  Scorer    │  │   Generator    │  │   Auditor     │  │
│  └─────┬──────┘  └───────┬────────┘  └──────┬────────┘  │
└────────┼──────────────────┼──────────────────┼───────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────┐
│                   AZURE OPENAI                            │
│                                                          │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │  GPT-5.4 (LLM)      │  │  text-embedding-3-small   │  │
│  │  - JSON Schema mode  │  │  - Semantic similarity    │  │
│  │  - Chain-of-thought  │  │  - Cross-doc comparison   │  │
│  └─────────────────────┘  └───────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit (Python) |
| LLM | Azure OpenAI GPT-5.4 (gpt-5.4-delta deployment) |
| Embeddings | Azure OpenAI text-embedding-3-small |
| Structured Output | JSON Schema mode for consistent, parseable agent responses |
| Human-in-the-Loop | Interactive Q&A in Phase 1 → feeds into Phase 2 |

---

## 📂 Project Structure

```
CampaignPulse/
├── app.py                        # Streamlit UI — 3-phase workflow
├── agents/
│   ├── brief_scorer.py           # Agent 1: scores brief on 6 dimensions
│   ├── plan_generator.py         # Agent 2: generates structured execution plan
│   └── alignment_auditor.py      # Agent 3: semantic audit + embedding similarity
├── utils/
│   ├── llm_client.py             # Azure OpenAI GPT-5.4 client
│   └── embeddings.py             # Embedding-based semantic similarity
├── sample_briefs/
│   ├── msft_surface_pro_q3.txt   # Real-world Microsoft Surface campaign brief
│   └── hp_enterprise_mfp_q3.txt  # Real-world HP Enterprise MFP brief (with gaps)
├── sample_assets/
│   ├── msft_email_draft.txt      # Email with deliberate misalignments
│   ├── msft_linkedin_ad.txt      # LinkedIn ad targeting wrong audience
│   ├── msft_sales_outreach.txt   # Correctly aligned (no false flags)
│   ├── msft_landing_page.txt     # Correctly aligned
│   ├── msft_execution_plan.json  # Plan with missing channels
│   ├── hp_email_draft.txt        # Email violating brand constraints
│   └── hp_linkedin_ad.txt        # Ad targeting wrong segment
├── .env                          # API credentials (gitignored)
├── .gitignore
└── requirements.txt
```

---

## 🚀 How to Run

```bash
# Clone the repository
git clone <repo-url>
cd CampaignPulse

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
AZURE_OPENAI_ENDPOINT=https://lvaiswatopenai2.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_LLM_DEPLOYMENT=gpt-5.4-delta
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small-delta
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Run the app
streamlit run app.py
```

---

## 🎬 Demo Flow (5 minutes)

### Demo 1: Score a Brief (Microsoft Surface — well-written)
1. Select "Microsoft Surface Pro 11 (Q3)" from sidebar
2. Click "Score Brief" → See score: ~82/100 (Launch-Ready)
3. Show dimension breakdown — all green except minor channel gaps

### Demo 2: Score a Brief (HP MFP — has major gaps)
1. Select "HP Enterprise MFP (Q3)" from sidebar
2. Click "Score Brief" → See score: ~38/100 (Not Executable)
3. Show gaps: No budget, vague timeline, generic channels
4. Show clarifying questions: "Budget not specified — what is the total allocation?"

### Demo 3: Generate Execution Plan
1. Answer 2-3 clarifying questions for HP brief
2. Click "Generate Execution Plan"
3. Show structured output: channel specs, timeline, copy guidance
4. Download plan as JSON

### Demo 4: Alignment Audit (the money shot)
1. Load Microsoft Surface brief + sample assets
2. Click "Run Alignment Audit"
3. Show critical issues caught:
   - 🔴 Email references iPad (brief says: "Do not reference Apple by name")
   - 🔴 LinkedIn targets "startups and freelancers" (brief says: IT Directors, VPs)
   - 🔴 Email CTA is "Learn More" (brief says: "Book a Demo")
   - ✅ Sales outreach and landing page pass (no false flags)

---

## 💰 Revenue Model (for LatentView)

| Model | Target Client | Value |
|---|---|---|
| Pre-launch analytics service | Enterprise tech (MSFT, HP) per product line | $25K–50K/quarter |
| Campaign audit per-campaign | Mid-market clients | $2K–5K/campaign |
| Brief scoring API | Embedded in client MarTech stack | $500–1,500/month |
| Managed analytics extension | Existing retainer clients | $120K–300K/year incremental |

---

## 🎯 Why This Wins

| Judging Criteria | Our Edge |
|---|---|
| **Real-world applicability** | Built for actual MSFT Surface and HP Enterprise campaigns with real constraints |
| **Non-obvious approach** | Most teams build brief-to-plan generators. We built a **scoring + audit pipeline** — analytics DNA |
| **Human-in-the-loop** | Campaign manager approves at every stage. AI surfaces options, humans decide |
| **Revenue potential** | Extends existing LatentView analytics services — same clients, earlier in lifecycle |
| **Technical depth** | LLM reasoning + embedding similarity + structured JSON output — not just a wrapper |

---

## 👥 Team

LatentView Analytics — Communications & Devices Entity

---

*"CampaignPulse scores your campaign brief, generates a validated execution plan, and audits every asset for alignment — before you spend a dollar."*
