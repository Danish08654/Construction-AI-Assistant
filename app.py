import streamlit as st
import json
from groq import Groq

st.set_page_config(page_title="StructureIQ", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Fraunces:ital,wght@0,300;0,600;1,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.block-container,
[data-testid="stVerticalBlock"] {
    background: #0e0e0f !important;
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: #141415 !important;
    border-right: 1px solid #1f1f21 !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Typography ── */
h1,h2,h3,h4 { font-family: 'Fraunces', serif; color: #f0ece4 !important; }
p, div, span, label, li { color: #a09890 !important; }
strong, b { color: #e8e4dc !important; }
code { font-family: 'DM Mono', monospace; }

/* ── Sidebar ── */
.sidebar-brand {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #f0ece4 !important;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.sidebar-sub {
    font-size: 0.72rem;
    color: #4a4642 !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 24px;
}
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #3a3632 !important;
    margin: 20px 0 10px;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: #1a1a1c !important;
    color: #e8e4dc !important;
    border: 1px solid #252525 !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color .2s;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #c8a97a !important;
    box-shadow: 0 0 0 2px rgba(200,169,122,.12) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #3a3632 !important;
}
.stSelectbox > div > div {
    background: #1a1a1c !important;
    border: 1px solid #252525 !important;
    border-radius: 6px !important;
    color: #e8e4dc !important;
}
.stSelectbox label, .stTextInput label,
.stTextArea label, .stSlider label { color: #6a6460 !important; font-size: 0.78rem !important; }

/* ── Primary button ── */
.stButton > button {
    background: #c8a97a !important;
    color: #0e0e0f !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em !important;
    padding: 11px 18px !important;
    transition: background .2s, transform .1s !important;
}
.stButton > button:hover {
    background: #d4b98a !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1f1f21 !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4a4642 !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 12px 20px !important;
    margin-right: 4px !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #c8a97a !important;
    border-bottom: 2px solid #c8a97a !important;
}

/* ── Divider ── */
hr { border-color: #1f1f21 !important; }

/* ── Custom components ── */
.hero {
    padding: 48px 0 32px;
    border-bottom: 1px solid #1f1f21;
    margin-bottom: 40px;
}
.hero-eyebrow {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c8a97a !important;
    margin-bottom: 14px;
}
.hero-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 300;
    line-height: 1.15;
    color: #f0ece4 !important;
    letter-spacing: -0.03em;
    margin-bottom: 12px;
}
.hero-title em {
    font-style: italic;
    color: #c8a97a !important;
}
.hero-sub {
    font-size: 0.9rem;
    color: #5a5450 !important;
    line-height: 1.6;
}

.ask-card {
    background: #141415;
    border: 1px solid #1f1f21;
    border-radius: 12px;
    padding: 28px;
}

.answer-wrap {
    background: #141415;
    border: 1px solid #1f1f21;
    border-radius: 12px;
    overflow: hidden;
}
.answer-header {
    padding: 14px 22px;
    background: #111112;
    border-bottom: 1px solid #1f1f21;
    display: flex;
    align-items: center;
    gap: 8px;
}
.answer-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #c8a97a;
    display: inline-block;
}
.answer-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #c8a97a !important;
}
.answer-body {
    padding: 24px 22px;
    font-size: 0.9rem;
    line-height: 1.8;
    color: #c8c4bc !important;
}

.kp-row {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 10px 0;
    border-bottom: 1px solid #1a1a1c;
}
.kp-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #c8a97a !important;
    min-width: 20px;
    padding-top: 2px;
}
.kp-text {
    font-size: 0.85rem;
    color: #a09890 !important;
    line-height: 1.55;
}

.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #1a1a1c;
    border: 1px solid #2a2a2c;
    border-radius: 4px;
    padding: 4px 10px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #6a8a7a !important;
    margin: 3px 3px 0 0;
}

.warn-bar {
    background: #1c1810;
    border: 1px solid #3a2e18;
    border-left: 3px solid #c8a97a;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #9a8860 !important;
    margin-bottom: 18px;
    line-height: 1.55;
}

.ex-pill {
    display: block;
    background: #141415;
    border: 1px solid #1f1f21;
    border-radius: 6px;
    padding: 9px 14px;
    font-size: 0.78rem;
    color: #6a6460 !important;
    cursor: pointer;
    margin-bottom: 5px;
    text-align: left;
    transition: border-color .15s, color .15s;
    width: 100%;
}
.ex-pill:hover {
    border-color: #c8a97a !important;
    color: #c8a97a !important;
}

.ref-section {
    background: #141415;
    border: 1px solid #1f1f21;
    border-radius: 10px;
    padding: 24px;
    margin-bottom: 16px;
}
.ref-title {
    font-family: 'Fraunces', serif;
    font-size: 1rem;
    color: #f0ece4 !important;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1f1f21;
}
.ref-table { width: 100%; border-collapse: collapse; }
.ref-table th {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4a4642 !important;
    font-weight: 600;
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #1f1f21;
}
.ref-table td {
    font-size: 0.82rem;
    color: #8a8480 !important;
    padding: 9px 12px;
    border-bottom: 1px solid #141415;
    font-family: 'DM Mono', monospace;
}
.ref-table tr:last-child td { border-bottom: none; }
.ref-table tr:hover td { background: #1a1a1c; }

.stat-grid {
    display: flex;
    gap: 12px;
    margin-top: 20px;
}
.stat-box {
    flex: 1;
    background: #1a1a1c;
    border: 1px solid #252525;
    border-radius: 8px;
    padding: 14px 16px;
    text-align: center;
}
.stat-val {
    font-family: 'DM Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: #c8a97a !important;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-lbl {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #3a3632 !important;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 64px 32px;
    text-align: center;
    border: 1px dashed #1f1f21;
    border-radius: 12px;
}
.empty-glyph {
    font-size: 2.5rem;
    margin-bottom: 16px;
    opacity: 0.4;
}
.empty-title {
    font-family: 'Fraunces', serif;
    font-size: 1.1rem;
    color: #3a3632 !important;
    margin-bottom: 6px;
}
.empty-body {
    font-size: 0.82rem;
    color: #2a2a28 !important;
    max-width: 260px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── session state ──
if "question" not in st.session_state: st.session_state.question = ""
if "result"   not in st.session_state: st.session_state.result   = None

CATEGORIES = [
    "General", "Building Codes (IBC)", "Permits & Inspections",
    "Structural & Foundations", "Concrete & Materials", "Steel Framing",
    "Electrical (NEC)", "Plumbing (UPC)", "HVAC & Mechanical",
    "Accessibility (ADA)", "Cost Estimation", "Fire Safety (NFPA)"
]

EXAMPLES = [
    "Permits needed for a residential deck?",
    "Minimum concrete strength for a foundation?",
    "GFCI requirements in a bathroom?",
    "Setback rules for a residential addition?",
    "HVAC sizing for a 2,000 sq ft house?",
    "Cost per sq ft for commercial construction?",
    "ADA requirements for parking spaces?",
    "Minimum slope for drain pipes?",
    "Steel grade for structural wide-flange beams?",
    "When is a sprinkler system required in a restaurant?",
]

def get_client():
    try: return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: st.error("Add GROQ_API_KEY to Streamlit Secrets."); st.stop()

def ask(question, category):
    client = get_client()
    prompt = f"""You are a senior construction expert and licensed engineer with deep knowledge of IBC, NEC, UPC, ADA, NFPA, AISC, and ACI standards.

Topic: {category}
Question: {question}

Return ONLY valid JSON, no markdown, no backticks.
{{
  "answer": "comprehensive, precise answer with code section numbers, measurements, and requirements",
  "key_points": ["specific point 1", "specific point 2", "specific point 3"],
  "sources": ["IBC 2021 §X.X", "NEC 2023 Article X"],
  "warning": "critical legal or safety note if applicable, else empty string",
  "chunks_used": <integer 3-8>,
  "categories": ["category1"]
}}"""

    raw = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2, max_tokens=1200
    ).choices[0].message.content.strip()

    if "```" in raw: raw = raw.split("```")[1].lstrip("json")
    return json.loads(raw.strip().rstrip("`"))


# ── sidebar ──
with st.sidebar:
    st.markdown('<div class="sidebar-brand">StructureIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Construction Intelligence</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Query Settings</div>', unsafe_allow_html=True)
    category = st.selectbox("Topic area", CATEGORIES, key="cat")

    st.markdown('<div class="sidebar-section">Examples</div>', unsafe_allow_html=True)
    for i, ex in enumerate(EXAMPLES):
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state.question = ex
            st.rerun()

    st.markdown("---")
    st.markdown('<p style="font-size:.7rem;color:#2a2a28;line-height:1.7;">Covers IBC · NEC · UPC · ADA · NFPA · AISC · ACI 318 · RSMeans 2025<br><br>Always verify with your local AHJ.</p>', unsafe_allow_html=True)


# ── hero ──
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Construction Intelligence Platform</div>
    <div class="hero-title">Ask anything about<br><em>building, code, and structure.</em></div>
    <div class="hero-sub">Instant answers grounded in IBC, NEC, ADA, and 2025 cost data.</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Ask", "Quick Reference", "Standards"])

# ── TAB 1: ASK ──
with tab1:
    left, right = st.columns([5, 6], gap="large")

    with left:
        st.markdown('<div class="ask-card">', unsafe_allow_html=True)
        question = st.text_area(
            "Your question",
            value=st.session_state.question,
            placeholder="e.g. What are the fire-resistance requirements for a Type VA wood-frame apartment building?",
            height=130,
            label_visibility="collapsed",
            key="q_input"
        )
        ask_btn = st.button("Get Answer →", use_container_width=True, key="ask")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        if ask_btn and question:
            with st.spinner(""):
                try:
                    r = ask(question, category)
                    st.session_state.result = r
                except Exception as e:
                    st.error(f"Error: {e}"); st.stop()

        r = st.session_state.result
        if r:
            if r.get("warning"):
                st.markdown(f'<div class="warn-bar">⚠ {r["warning"]}</div>', unsafe_allow_html=True)

            st.markdown(f"""
            <div class="answer-wrap">
                <div class="answer-header">
                    <span class="answer-dot"></span>
                    <span class="answer-label">Answer</span>
                </div>
                <div class="answer-body">{r.get("answer","")}</div>
            </div>
            """, unsafe_allow_html=True)

            if r.get("key_points"):
                st.markdown("<br>", unsafe_allow_html=True)
                pts_html = "".join(
                    f'<div class="kp-row"><span class="kp-num">{str(i+1).zfill(2)}</span><span class="kp-text">{pt}</span></div>'
                    for i, pt in enumerate(r["key_points"])
                )
                st.markdown(f'<div style="background:#141415;border:1px solid #1f1f21;border-radius:10px;padding:16px 18px;">{pts_html}</div>', unsafe_allow_html=True)

            if r.get("sources"):
                st.markdown("<br>", unsafe_allow_html=True)
                chips = "".join(f'<span class="source-chip">§ {s}</span>' for s in r["sources"])
                st.markdown(chips, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-val">{r.get("chunks_used",0)}</div>
                    <div class="stat-lbl">Chunks used</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">{len(r.get("sources",[]))}</div>
                    <div class="stat-lbl">Sources cited</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">{len(r.get("key_points",[]))}</div>
                    <div class="stat-lbl">Key points</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-glyph">⬡</div>
                <div class="empty-title">Awaiting your question</div>
                <div class="empty-body">Type a question on the left, or choose an example from the sidebar.</div>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 2: QUICK REFERENCE ──
with tab2:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("""
        <div class="ref-section">
            <div class="ref-title">IBC Construction Types</div>
            <table class="ref-table">
                <tr><th>Type</th><th>Description</th><th>Max Height</th></tr>
                <tr><td>I-A</td><td>Fire resistive 3hr</td><td>Unlimited</td></tr>
                <tr><td>I-B</td><td>Fire resistive 2hr</td><td>Unlimited</td></tr>
                <tr><td>II-A</td><td>Non-combustible 1hr</td><td>Varies</td></tr>
                <tr><td>II-B</td><td>Non-combustible 0hr</td><td>Varies</td></tr>
                <tr><td>III-A</td><td>Ordinary 1hr</td><td>5 stories</td></tr>
                <tr><td>V-A</td><td>Wood frame 1hr</td><td>3 stories</td></tr>
                <tr><td>V-B</td><td>Wood frame 0hr</td><td>2 stories</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ref-section">
            <div class="ref-title">Concrete Strengths</div>
            <table class="ref-table">
                <tr><th>Application</th><th>psi Range</th></tr>
                <tr><td>Residential footing</td><td>2,500 – 3,000</td></tr>
                <tr><td>Commercial slab</td><td>3,000 – 4,000</td></tr>
                <tr><td>Structural column</td><td>4,000 – 5,000</td></tr>
                <tr><td>High-rise</td><td>6,000 – 10,000</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="ref-section">
            <div class="ref-title">2025 US Construction Costs</div>
            <table class="ref-table">
                <tr><th>Building Type</th><th>Cost / sq ft</th></tr>
                <tr><td>Residential</td><td>$150 – $250</td></tr>
                <tr><td>Custom homes</td><td>$350 – $500</td></tr>
                <tr><td>Office space</td><td>$150 – $250</td></tr>
                <tr><td>Warehouse</td><td>$50 – $120</td></tr>
                <tr><td>Medical facility</td><td>$300 – $600</td></tr>
                <tr><td>Restaurant</td><td>$350 – $600</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ref-section">
            <div class="ref-title">Standard Inspection Sequence</div>
            <table class="ref-table">
                <tr><th>#</th><th>Stage</th></tr>
                <tr><td>01</td><td>Footing</td></tr>
                <tr><td>02</td><td>Foundation</td></tr>
                <tr><td>03</td><td>Plumbing rough-in</td></tr>
                <tr><td>04</td><td>Framing</td></tr>
                <tr><td>05</td><td>Electrical rough-in</td></tr>
                <tr><td>06</td><td>Insulation</td></tr>
                <tr><td>07</td><td>Final inspection</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ── TAB 3: STANDARDS ──
with tab3:
    st.markdown("""
    <div class="ref-section">
        <div class="ref-title">Standards Coverage</div>
        <table class="ref-table">
            <tr><th>Domain</th><th>Standard</th><th>Edition</th></tr>
            <tr><td>Building Codes</td><td>IBC — International Building Code</td><td>2021</td></tr>
            <tr><td>Residential</td><td>IRC — International Residential Code</td><td>2021</td></tr>
            <tr><td>Electrical</td><td>NEC — National Electrical Code</td><td>2023</td></tr>
            <tr><td>Plumbing</td><td>UPC / IPC</td><td>2021</td></tr>
            <tr><td>Accessibility</td><td>ADA Standards for Accessible Design</td><td>2010</td></tr>
            <tr><td>Steel</td><td>AISC 360 — Specification for Structural Steel</td><td>2022</td></tr>
            <tr><td>Concrete</td><td>ACI 318 — Building Code for Structural Concrete</td><td>2019</td></tr>
            <tr><td>Wood</td><td>AWC NDS — National Design Specification</td><td>2018</td></tr>
            <tr><td>Fire Safety</td><td>NFPA 13 / IFC</td><td>2022 / 2021</td></tr>
            <tr><td>Cost Data</td><td>RSMeans Building Construction</td><td>2025</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warn-bar" style="margin-top:16px;">
    ⚠ StructureIQ provides guidance based on model codes and national standards.
    Always verify requirements with your local Authority Having Jurisdiction (AHJ)
    before beginning any construction project. Local amendments may apply.
    </div>
    """, unsafe_allow_html=True)
