import streamlit as st
import json
import os
import time
from pathlib import Path
from datetime import datetime

from agents.brief_scorer import score_brief, get_clarifying_questions
from agents.plan_generator import generate_plan
from agents.alignment_auditor import audit_alignment, compute_semantic_scores

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CampaignPulse | AI Pre-Launch Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAMPLE_DIR = Path(__file__).parent / "sample_briefs"
ASSET_DIR = Path(__file__).parent / "sample_assets"

# ---------------------------------------------------------------------------
# Custom CSS — Premium minimal theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    :root {
        --brand-primary: #6366f1;
        --brand-primary-dark: #4f46e5;
        --brand-accent: #06b6d4;
        --brand-success: #10b981;
        --brand-warning: #f59e0b;
        --brand-danger: #ef4444;
        --surface: #ffffff;
        --surface-alt: #f8fafc;
        --text-main: #1e293b;
        --text-muted: #64748b;
        --border: #e2e8f0;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-main);
    }

    /* Compact header strip */
    .header-strip {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-strip h2 {
        font-size: 1.3rem;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .header-strip p {
        color: rgba(255,255,255,0.75);
        font-size: 0.85rem;
        margin: 0.2rem 0 0 0;
    }

    /* Metric cards */
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--brand-primary);
        margin: 0;
    }
    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.2rem;
    }

    /* Score badge */
    .score-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .score-badge.high { background: #ecfdf5; color: #065f46; }
    .score-badge.mid { background: #fffbeb; color: #92400e; }
    .score-badge.low { background: #fef2f2; color: #991b1b; }

    /* Issue card */
    .issue-critical {
        border-left: 4px solid var(--brand-danger);
        background: #fef2f2;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.6rem;
    }
    .issue-warning {
        border-left: 4px solid var(--brand-warning);
        background: #fffbeb;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.6rem;
    }
    .issue-info {
        border-left: 4px solid var(--brand-accent);
        background: #ecfeff;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.6rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
    }

    /* Channel card */
    .channel-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .channel-card h4 {
        color: var(--brand-primary-dark);
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }

    /* Primary button — larger, more prominent */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.7rem 2rem;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(99,102,241,0.4);
    }

    /* Action bar — sticky feel */
    .action-bar {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.75rem 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .action-bar .info {
        font-size: 0.82rem;
        color: var(--text-muted);
    }

    /* Textarea shrink */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1.5px solid var(--border) !important;
        font-size: 0.88rem !important;
        line-height: 1.5 !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--brand-primary) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    }

    /* Hide default streamlit footer */
    footer { visibility: hidden; }
    
    /* Tighter top padding */
    .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar — Professional Navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.6rem; font-weight: 800; color: white; letter-spacing: -0.02em;">
            🎯 CampaignPulse
        </div>
        <div style="font-size: 0.78rem; color: rgba(255,255,255,0.6); margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 0.08em;">
            AI Pre-Launch Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    phase = st.radio(
        "Navigation",
        [
            "1️⃣ Brief Scoring",
            "2️⃣ Plan Generation",
            "3️⃣ Alignment Audit",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("##### 📂 Sample Briefs")
    sample_brief_choice = st.selectbox(
        "Load sample",
        ["— Select —", "Microsoft Surface Pro 11 (Q3)", "HP Enterprise MFP (Q3)", "Azure AI Platform Launch (Q4)"],
        label_visibility="collapsed",
    )

    sample_brief_map = {
        "Microsoft Surface Pro 11 (Q3)": SAMPLE_DIR / "msft_surface_pro_q3.txt",
        "HP Enterprise MFP (Q3)": SAMPLE_DIR / "hp_enterprise_mfp_q3.txt",
        "Azure AI Platform Launch (Q4)": SAMPLE_DIR / "azure_ai_platform_q4.txt",
    }

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.72rem; color: rgba(255,255,255,0.4); text-align: center; padding-top: 1rem;">
        LatentView Analytics<br/>
        Communications & Devices Entity<br/>
        SWAT Hackathon 2026
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper functions (must be defined before usage)
# ---------------------------------------------------------------------------
def _render_issue(issue: dict):
    st.markdown(f"**Dimension:** {issue.get('dimension', 'N/A')}")
    st.markdown(f"**Asset:** {issue.get('asset', 'N/A')}")
    st.markdown(f"**Description:** {issue.get('description', 'N/A')}")

    col1, col2 = st.columns(2)
    with col1:
        st.error(f"**Brief says:** {issue.get('brief_says', 'N/A')}")
    with col2:
        st.warning(f"**Asset says:** {issue.get('asset_says', 'N/A')}")

    st.success(f"**Recommended Fix:** {issue.get('fix_suggestion', 'N/A')}")


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
for key, default in {
    "brief_text": "",
    "score_result": None,
    "plan_result": None,
    "audit_result": None,
    "clarifying_answers": "",
    "active_brief_name": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Load sample brief if selected
if sample_brief_choice != "— Select —":
    path = sample_brief_map.get(sample_brief_choice)
    if path and path.exists():
        st.session_state.brief_text = path.read_text(encoding="utf-8")
        st.session_state.active_brief_name = sample_brief_choice


# =========================================================================
# PHASE 1 — BRIEF READINESS SCORING
# =========================================================================
if phase.startswith("1"):
    # Compact header
    st.markdown("""
    <div class="header-strip">
        <div>
            <h2>Brief Readiness Scoring</h2>
            <p>Score your brief on 6 dimensions. Surface gaps before work begins.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Action bar: Upload + Score button + info — all on one line ---
    col_upload, col_btn, col_info = st.columns([2, 1.5, 2])
    with col_upload:
        uploaded = st.file_uploader("Upload brief", type=["txt", "md"], label_visibility="collapsed", key="brief_upload")
        if uploaded:
            st.session_state.brief_text = uploaded.read().decode("utf-8")
            st.rerun()
    with col_btn:
        score_btn = st.button("🔍  Score Brief", type="primary", use_container_width=True)
    with col_info:
        word_count = len(st.session_state.brief_text.split()) if st.session_state.brief_text else 0
        brief_name = st.session_state.active_brief_name or "No brief loaded"
        st.caption(f"📂 **{brief_name}** · {word_count} words")
        if st.session_state.score_result:
            if st.button("Clear results", use_container_width=False):
                st.session_state.score_result = None
                st.rerun()

    # --- Brief text (collapsible if results exist, visible if no results) ---
    if st.session_state.score_result:
        with st.expander("📄 View / edit brief", expanded=False):
            brief_input = st.text_area(
                "Brief",
                value=st.session_state.brief_text,
                height=200,
                label_visibility="collapsed",
            )
            st.session_state.brief_text = brief_input
    else:
        brief_input = st.text_area(
            "Paste your campaign brief below, or select a sample from the sidebar →",
            value=st.session_state.brief_text,
            height=220,
            placeholder="Paste campaign brief here...\n\nOr select a sample brief from the sidebar to get started instantly.",
        )
        st.session_state.brief_text = brief_input

    if score_btn and st.session_state.brief_text.strip():
        with st.spinner("Analyzing brief across 6 execution-readiness dimensions..."):
            start_t = time.time()
            result = score_brief(st.session_state.brief_text)
            result["_analysis_time"] = round(time.time() - start_t, 1)
            st.session_state.score_result = result
            st.rerun()

    if st.session_state.score_result:
        r = st.session_state.score_result

        # --- Header metrics row ---
        st.markdown("---")
        tier = r.get("readiness_tier", "Unknown")
        tier_class = {
            "Launch-Ready": "launch",
            "Needs Refinement": "refine",
            "Major Gaps": "gaps",
            "Not Executable": "fail",
        }.get(tier, "refine")
        tier_icon = {"Launch-Ready": "🟢", "Needs Refinement": "🟡", "Major Gaps": "🟠", "Not Executable": "🔴"}.get(tier, "⚪")

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value">{r['overall_score']}</div>
                <div class="metric-label">Overall Score</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="font-size: 1.2rem;">{tier_icon} {tier}</div>
                <div class="metric-label">Readiness Tier</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            gaps = sum(1 for d in r["dimensions"].values() if d.get("clarifying_question"))
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value">{gaps}</div>
                <div class="metric-label">Gaps Found</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value">{r.get("estimated_rework_hours", "—")}</div>
                <div class="metric-label">Est. Rework Hrs</div>
            </div>""", unsafe_allow_html=True)
        with m5:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value">{r.get("_analysis_time", "—")}s</div>
                <div class="metric-label">Analysis Time</div>
            </div>""", unsafe_allow_html=True)

        # --- Dimension breakdown ---
        st.markdown("")
        st.markdown("### 📊 Dimension Breakdown")
        dims = r["dimensions"]
        dim_labels = {
            "audience_precision": ("🎯", "Audience Precision", 0.20),
            "channel_specificity": ("📡", "Channel Specificity", 0.15),
            "message_product_fit": ("💬", "Message-Product Fit", 0.15),
            "budget_allocation": ("💰", "Budget Allocation", 0.20),
            "timeline_feasibility": ("📅", "Timeline Feasibility", 0.15),
            "measurement_hookability": ("📏", "Measurement Hookability", 0.15),
        }

        for dim_key, (icon, label, weight) in dim_labels.items():
            dim = dims.get(dim_key, {})
            score = dim.get("score", 0)
            score_class = "high" if score >= 80 else "mid" if score >= 60 else "low"

            with st.container():
                col_icon, col_name, col_bar, col_score, col_weight = st.columns([0.5, 2, 4, 1, 1])
                with col_icon:
                    st.markdown(f"### {icon}")
                with col_name:
                    st.markdown(f"**{label}**")
                with col_bar:
                    st.progress(score / 100)
                with col_score:
                    st.markdown(f'<span class="score-badge {score_class}">{score}/100</span>', unsafe_allow_html=True)
                with col_weight:
                    st.caption(f"wt: {int(weight*100)}%")

                st.caption(f"  {dim.get('justification', '')}")
                if dim.get("clarifying_question"):
                    st.warning(f"❓ {dim['clarifying_question']}")

        # --- Top issues ---
        st.markdown("---")
        col_issues, col_summary = st.columns([1, 1])

        with col_issues:
            st.markdown("### 🚨 Top Issues to Resolve")
            for i, issue in enumerate(r.get("top_issues", []), 1):
                st.markdown(f"""<div class="issue-critical" style="border-left-color: {'#ef4444' if i == 1 else '#f59e0b' if i == 2 else '#06b6d4'};">
                    <strong>{i}.</strong> {issue}
                </div>""", unsafe_allow_html=True)

        with col_summary:
            st.markdown("### 📋 Executive Summary")
            st.info(r.get("executive_summary", ""))

        # --- Clarifying questions collector ---
        questions = get_clarifying_questions(r)
        if questions:
            st.markdown("---")
            st.markdown("### 💬 Resolve Gaps Before Plan Generation")
            st.caption("Answer these questions so Phase 2 can generate a validated execution plan. Unanswered gaps become assumptions.")

            answers_text = ""
            cols_q = st.columns(min(len(questions), 3))
            for idx, q in enumerate(questions):
                with cols_q[idx % len(cols_q)]:
                    answer = st.text_input(
                        f"{q['dimension']}",
                        placeholder=q["question"],
                        key=f"q_{q['dimension']}",
                        help=f"Current score: {q['score']}/100",
                    )
                    if answer:
                        answers_text += f"\n{q['dimension']}: {answer}"

            st.session_state.clarifying_answers = answers_text


# =========================================================================
# PHASE 2 — EXECUTION PLAN GENERATION
# =========================================================================
elif phase.startswith("2"):
    st.markdown("""
    <div class="header-strip">
        <div>
            <h2>Execution Plan Generation</h2>
            <p>Structured channel-level plan with timeline, copy guidance, and tracking.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.brief_text.strip():
        st.warning("⚠️ No brief loaded. Navigate to Phase 1 and paste or upload a brief first.")
        st.stop()

    # Status indicators
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.success("✅ Brief loaded")
    with col_s2:
        if st.session_state.clarifying_answers.strip():
            st.success("✅ Clarifying answers provided")
        else:
            st.info("ℹ️ No gap answers — plan uses assumptions")
    with col_s3:
        if st.session_state.score_result:
            score = st.session_state.score_result.get("overall_score", 0)
            st.metric("Brief Score", f"{score}/100")

    with st.expander("📄 View loaded brief", expanded=False):
        st.text(st.session_state.brief_text[:2000] + ("..." if len(st.session_state.brief_text) > 2000 else ""))

    if st.session_state.clarifying_answers.strip():
        with st.expander("💬 View clarifying answers"):
            st.text(st.session_state.clarifying_answers)

    st.markdown("---")

    extra_context = st.text_area(
        "Additional instructions (optional)",
        height=80,
        placeholder="E.g., 'Focus LinkedIn budget on decision-maker InMail, not broad sponsored content' or 'Partner channel priority: CDW first'",
    )

    combined_answers = st.session_state.clarifying_answers
    if extra_context.strip():
        combined_answers += f"\n\nAdditional instructions: {extra_context}"

    gen_btn = st.button("⚡ Generate Execution Plan", type="primary", use_container_width=False)

    if gen_btn:
        with st.spinner("🤖 Building structured execution plan with channel specs, timeline, and tracking..."):
            start_t = time.time()
            plan = generate_plan(st.session_state.brief_text, combined_answers)
            plan["_generation_time"] = round(time.time() - start_t, 1)
            st.session_state.plan_result = plan

    if st.session_state.plan_result:
        plan = st.session_state.plan_result

        st.markdown("---")
        st.markdown(f"### 📋 {plan.get('campaign_name', 'Execution Plan')}")
        if plan.get("_generation_time"):
            st.caption(f"Generated in {plan['_generation_time']}s")

        # --- Tabs for organized plan viewing ---
        tab_channels, tab_timeline, tab_tracking, tab_risks = st.tabs([
            "📡 Channels", "📅 Timeline", "📏 Tracking", "⚠️ Risks"
        ])

        with tab_channels:
            st.markdown("#### Channel Specifications")
            for ch in plan.get("channel_specs", []):
                st.markdown(f"""<div class="channel-card">
                    <h4>{ch['channel']}</h4>
                </div>""", unsafe_allow_html=True)

                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    st.markdown(f"**Platform:** {ch.get('platform_details', 'N/A')}")
                    st.markdown(f"**Audience:** {ch.get('audience_targeting', 'N/A')}")
                    st.markdown(f"**Format:** {ch.get('ad_format', 'N/A')}")
                with c2:
                    st.markdown(f"**Budget:** {ch.get('budget', 'TBD')}")
                    st.markdown(f"**CTA:** {ch.get('cta', 'N/A')}")
                    st.markdown(f"**Owner:** {ch.get('owner', 'TBD')}")
                    st.markdown(f"**Go-Live:** {ch.get('go_live_date', 'TBD')}")
                with c3:
                    cg = ch.get("copy_guidance", {})
                    st.markdown("**Copy Guidance:**")
                    st.caption(f"Headline: {cg.get('headline_direction', 'N/A')}")
                    st.caption(f"Angle: {cg.get('message_angle', 'N/A')}")
                    st.caption(f"CTA: {cg.get('cta_phrasing', 'N/A')}")
                    st.caption(f"Tone: {cg.get('tone', 'N/A')}")
                st.markdown("---")

        with tab_timeline:
            st.markdown("#### Week-by-Week Timeline")
            for week in plan.get("weekly_timeline", []):
                with st.expander(f"**{week.get('week', '')}** — {week.get('dates', '')}", expanded=False):
                    for m in week.get("milestones", []):
                        st.markdown(f"- ✓ {m}")

        with tab_tracking:
            st.markdown("#### Tracking & Measurement Setup")
            tracking = plan.get("tracking_setup", {})
            st.markdown(f"**UTM Structure:** `{tracking.get('utm_structure', 'N/A')}`")
            st.markdown(f"**Reporting Cadence:** {tracking.get('reporting_cadence', 'N/A')}")
            st.markdown("---")
            st.markdown("**KPIs per Channel:**")
            for kpi_entry in tracking.get("kpis_per_channel", []):
                st.markdown(f"- **{kpi_entry['channel']}:** {', '.join(kpi_entry.get('kpis', []))}")

        with tab_risks:
            risk_flags = plan.get("risk_flags", [])
            assumptions = plan.get("assumptions", [])

            if risk_flags:
                st.markdown("#### ⚠️ Risk Flags")
                for flag in risk_flags:
                    st.markdown(f"""<div class="issue-warning">{flag}</div>""", unsafe_allow_html=True)

            if assumptions:
                st.markdown("#### 📌 Assumptions Made")
                for a in assumptions:
                    st.markdown(f"""<div class="issue-info">{a}</div>""", unsafe_allow_html=True)

        # --- Download ---
        st.markdown("---")
        dl_col1, dl_col2, _ = st.columns([1, 1, 3])
        with dl_col1:
            st.download_button(
                "📥 Download Plan (JSON)",
                data=json.dumps(plan, indent=2),
                file_name=f"{plan.get('campaign_name', 'plan').replace(' ', '_')}_execution_plan.json",
                mime="application/json",
                use_container_width=True,
            )
        with dl_col2:
            st.button("➡️ Proceed to Audit", on_click=lambda: None, use_container_width=True)


# =========================================================================
# PHASE 3 — PRE-LAUNCH ALIGNMENT AUDIT
# =========================================================================
elif phase.startswith("3"):
    st.markdown("""
    <div class="header-strip">
        <div>
            <h2>Pre-Launch Alignment Audit</h2>
            <p>Audit assets against the brief. Catch misalignments before they cost budget.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Input section ---
    col_brief_status, col_plan_status, col_assets_status = st.columns(3)
    with col_brief_status:
        if st.session_state.brief_text.strip():
            st.success("✅ Brief loaded")
        else:
            st.error("❌ No brief loaded")
    with col_plan_status:
        if st.session_state.plan_result:
            st.success("✅ Plan from Phase 2")
        else:
            st.info("ℹ️ No plan — audit uses brief only")
    with col_assets_status:
        st.info("📎 Upload or load sample assets below")

    # Brief
    with st.expander("📄 Campaign Brief", expanded=False):
        brief_for_audit = st.text_area(
            "Brief text",
            value=st.session_state.brief_text,
            height=200,
            key="audit_brief",
            label_visibility="collapsed",
        )

    # Plan
    plan_text_for_audit = ""
    if st.session_state.plan_result:
        plan_text_for_audit = json.dumps(st.session_state.plan_result, indent=2)
    else:
        with st.expander("📋 Upload Execution Plan (optional)"):
            plan_upload = st.file_uploader("Upload plan", type=["json", "txt"], key="plan_upload", label_visibility="collapsed")
            if plan_upload:
                plan_text_for_audit = plan_upload.read().decode("utf-8")

    st.markdown("---")

    # Channel assets
    st.markdown("#### 📎 Channel Assets")

    asset_col1, asset_col2 = st.columns([1, 1])
    assets = {}

    with asset_col1:
        load_samples = st.checkbox("Load sample assets (with deliberate misalignments)", value=False)
        if load_samples:
            sample_type = st.selectbox(
                "Sample set",
                ["Microsoft Surface Pro 11", "HP Enterprise MFP"],
            )
            asset_map = {
                "Microsoft Surface Pro 11": {
                    "Email Draft": ASSET_DIR / "msft_email_draft.txt",
                    "LinkedIn Ad": ASSET_DIR / "msft_linkedin_ad.txt",
                    "Sales Outreach": ASSET_DIR / "msft_sales_outreach.txt",
                    "Landing Page": ASSET_DIR / "msft_landing_page.txt",
                },
                "HP Enterprise MFP": {
                    "Email Draft": ASSET_DIR / "hp_email_draft.txt",
                    "LinkedIn Ad": ASSET_DIR / "hp_linkedin_ad.txt",
                    "Landing Page": ASSET_DIR / "hp_landing_page.txt",
                    "Webinar Invite": ASSET_DIR / "hp_webinar_invite.txt",
                },
            }
            for name, path in asset_map.get(sample_type, {}).items():
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                    assets[name] = content

    with asset_col2:
        uploaded_assets = st.file_uploader(
            "Upload your own assets",
            type=["txt", "md"],
            accept_multiple_files=True,
            key="asset_uploads",
            label_visibility="collapsed",
        )
        for ua in uploaded_assets:
            content = ua.read().decode("utf-8")
            assets[ua.name.replace(".txt", "")] = content

    # Show loaded assets
    if assets:
        st.markdown(f"**{len(assets)} assets loaded:**")
        asset_tabs = st.tabs(list(assets.keys()))
        for tab, (name, content) in zip(asset_tabs, assets.items()):
            with tab:
                st.code(content, language=None)

    st.markdown("---")

    if not brief_for_audit.strip():
        st.warning("Brief is required for audit. Load one in Phase 1 or paste above.")
    elif not assets:
        st.warning("Upload or load at least one channel asset to audit.")
    else:
        audit_btn = st.button("🔎 Run Alignment Audit", type="primary", use_container_width=False)

        if audit_btn:
            with st.spinner("🤖 Running semantic similarity + LLM alignment audit across all assets..."):
                start_t = time.time()
                sim_scores = compute_semantic_scores(brief_for_audit, assets)
                audit = audit_alignment(
                    brief_for_audit,
                    plan_text_for_audit if plan_text_for_audit.strip() else "(No execution plan provided)",
                    assets,
                )
                audit["semantic_similarity_scores"] = sim_scores
                audit["_audit_time"] = round(time.time() - start_t, 1)
                st.session_state.audit_result = audit

        if st.session_state.audit_result:
            a = st.session_state.audit_result

            # --- Header metrics ---
            st.markdown("---")
            verdict = a.get("readiness_verdict", "Unknown")
            verdict_icons = {"Ready for Launch": "🟢", "Fix Required": "🟡", "Major Rework Needed": "🔴"}
            v_icon = verdict_icons.get(verdict, "⚪")

            m1, m2, m3, m4, m5, m6 = st.columns(6)
            with m1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{a.get('overall_alignment_score', 0)}</div>
                    <div class="metric-label">Alignment Score</div>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="font-size: 1rem;">{v_icon} {verdict}</div>
                    <div class="metric-label">Verdict</div>
                </div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color: #ef4444;">{a.get('critical_count', 0)}</div>
                    <div class="metric-label">Critical</div>
                </div>""", unsafe_allow_html=True)
            with m4:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color: #f59e0b;">{a.get('warning_count', 0)}</div>
                    <div class="metric-label">Warnings</div>
                </div>""", unsafe_allow_html=True)
            with m5:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color: #06b6d4;">{a.get('info_count', 0)}</div>
                    <div class="metric-label">Info</div>
                </div>""", unsafe_allow_html=True)
            with m6:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{a.get('_audit_time', '—')}s</div>
                    <div class="metric-label">Audit Time</div>
                </div>""", unsafe_allow_html=True)

            # --- Tabs for audit results ---
            tab_sim, tab_channels, tab_issues, tab_summary = st.tabs([
                "🧠 Semantic Scores", "📊 Channel Scores", "🔍 Issues", "📋 Summary"
            ])

            with tab_sim:
                st.markdown("#### Embedding-Based Semantic Similarity to Brief")
                st.caption("Higher = more semantically aligned with the campaign brief")
                sim_scores = a.get("semantic_similarity_scores", {})
                for asset_name, score in sorted(sim_scores.items(), key=lambda x: x[1], reverse=True):
                    pct = int(score * 100)
                    col_n, col_bar, col_s = st.columns([2, 5, 1])
                    with col_n:
                        st.markdown(f"**{asset_name}**")
                    with col_bar:
                        st.progress(min(score, 1.0))
                    with col_s:
                        badge_class = "high" if pct >= 75 else "mid" if pct >= 50 else "low"
                        st.markdown(f'<span class="score-badge {badge_class}">{pct}%</span>', unsafe_allow_html=True)

            with tab_channels:
                st.markdown("#### Per-Channel Alignment Scores")
                for ch in a.get("channel_scores", []):
                    status = ch.get("status", "")
                    icon = "✅" if status == "Aligned" else "⚠️" if status == "Needs Fixes" else "❌"
                    score_val = ch.get("score", 0)
                    st.markdown(f"- {icon} **{ch['channel']}** — {score_val}/100 — _{status}_")

            with tab_issues:
                st.markdown("#### Issues Found")
                issues = a.get("issues", [])
                if not issues:
                    st.success("No issues found! All assets are aligned.")
                for issue in issues:
                    sev = issue.get("severity", "Info")
                    css_class = "issue-critical" if sev == "Critical" else "issue-warning" if sev == "Warning" else "issue-info"
                    sev_label = f"🔴 CRITICAL" if sev == "Critical" else f"🟡 WARNING" if sev == "Warning" else f"🔵 INFO"

                    st.markdown(f"""<div class="{css_class}">
                        <strong>{sev_label}</strong> — {issue.get('dimension', '')}
                        <br/><strong>Asset:</strong> {issue.get('asset', 'N/A')}
                        <br/>{issue.get('description', '')}
                    </div>""", unsafe_allow_html=True)

                    with st.expander(f"Details: {issue.get('description', '')[:60]}..."):
                        _render_issue(issue)

            with tab_summary:
                st.markdown("#### Executive Summary")
                st.info(a.get("executive_summary", ""))

            # --- Download ---
            st.markdown("---")
            st.download_button(
                "📥 Download Audit Report (JSON)",
                data=json.dumps(a, indent=2),
                file_name="campaign_alignment_audit.json",
                mime="application/json",
            )
