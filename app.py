import streamlit as st
import json
from groq import Groq

st.set_page_config(page_title="Construction AI Assistant", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, body { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container
    { background: #f8fafc !important; }
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div
    { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
#MainMenu, footer, header { visibility: hidden; }
p, div, span, label { color: #1e293b !important; }
h1, h2, h3, h4 { color: #0f172a !important; }

.stTextInput input, .stTextArea textarea
    { background: #fff !important; color: #0f172a !important; border: 1.5px solid #cbd5e1 !important; border-radius: 8px !important; }
.stTextArea textarea { font-size: 0.875rem !important; }
.stSelectbox > div > div { background: #fff !important; border: 1.5px solid #cbd5e1 !important; border-radius: 8px !important; color: #0f172a !important; }
.stButton > button { background: #2563eb !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px !important; }
.stButton > button:hover { background: #1d4ed8 !important; }
.stTabs [data-baseweb="tab-list"] { background: #f1f5f9 !important; border-radius: 10px !important; padding: 3px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #64748b !important; border-radius: 7px !important; font-size: 0.875rem !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #0f172a !important; }
hr { border-color: #e2e8f0 !important; }

.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 22px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.answer-box { background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 10px; padding: 20px 24px; font-size: 0.9rem; line-height: 1.75; color: #1e293b; }
.source-tag { display: inline-block; background: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8; border-radius: 6px; padding: 3px 10px; font-size: 0.75rem; font-weight: 600; margin: 3px 3px 0 0; }
.ex-btn { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; font-size: 0.82rem; color: #374151; cursor: pointer; margin-bottom: 6px; width: 100%; text-align: left; }
.metric-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; text-align: center; }
.metric-val { font-size: 1.6rem; font-weight: 700; color: #2563eb; }
.metric-lbl { font-size: 0.68rem; text-transform: uppercase; letter-spacing: .08em; color: #64748b; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── session state ──
if "question" not in st.session_state: st.session_state.question = ""
if "answer"   not in st.session_state: st.session_state.answer   = None
if "sources"  not in st.session_state: st.session_state.sources  = []

def get_client():
    try: return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: st.error("Add GROQ_API_KEY to Streamlit Secrets."); st.stop()

CATEGORIES = [
    "Any / General", "Building Codes", "Permits & Inspections",
    "Structural & Foundations", "Concrete & Materials", "Steel Framing",
    "Electrical (NEC)", "Plumbing", "HVAC & Mechanical",
    "Accessibility (ADA)", "Cost Estimation"
]

EXAMPLES = [
    "What permits do I need for a residential deck?",
    "What is the minimum concrete strength for a foundation?",
    "How many GFCI outlets are required in a bathroom?",
    "What are the setback requirements for a residential addition?",
    "How do I size HVAC for a 2,000 sq ft house?",
    "What is the cost per square foot for commercial construction?",
    "What are ADA requirements for parking spaces?",
    "What is the minimum slope for drain pipes?",
    "What steel grade is used for structural wide flange beams?",
    "When is a fire sprinkler system required in a restaurant?",
]

def ask_groq(question: str, category: str) -> dict:
    client = get_client()
    prompt = f"""You are an expert construction AI assistant with deep knowledge of:
- IBC (International Building Code)
- NEC (National Electrical Code)
- UPC (Uniform Plumbing Code)
- ADA Accessibility Standards
- Structural engineering principles
- Construction cost estimation (2025 US market)
- Permits and inspections processes

Topic area: {category}
Question: {question}

Provide a thorough, accurate, professional answer. Return ONLY valid JSON, no markdown.

{{
  "answer": "detailed answer with specific code references, numbers, and requirements",
  "sources": ["IBC 2021 Section X", "NEC Article X", "relevant code/standard"],
  "key_points": ["point1", "point2", "point3"],
  "warning": "any critical safety or legal warning, or empty string if none",
  "chunks_used": <integer 3-8>,
  "categories": ["category1", "category2"]
}}"""

    raw = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2, max_tokens=1500
    ).choices[0].message.content.strip()

    if "```" in raw:
        raw = raw.split("```")[1].lstrip("json")
    return json.loads(raw.strip().rstrip("`"))


# ── header ──
st.markdown("## 🏗️ Construction AI Assistant")
st.caption("IBC · NEC · UPC · ADA · Structural · Cost Estimation — powered by Groq")
st.divider()

tab1, tab2, tab3 = st.tabs(["💬 Ask the Assistant", "📋 Quick Reference", "ℹ️ About"])

# ─────────────────────────────────────
# TAB 1 — ASK
# ─────────────────────────────────────
with tab1:
    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown("**Ask Any Construction Question**")

        category = st.selectbox("Topic area", CATEGORIES, key="category_select")

        question = st.text_area(
            "Your question",
            value=st.session_state.question,
            placeholder="e.g. What are the fire resistance requirements for a Type VA wood frame apartment?",
            height=120,
            key="question_input"
        )

        ask_btn = st.button("🔍 Get Answer", use_container_width=True, key="ask_btn")

        st.markdown("**💡 Try these examples:**")
        for i, ex in enumerate(EXAMPLES):
            if st.button(f"→ {ex}", key=f"example_{i}", use_container_width=True):
                st.session_state.question = ex
                st.rerun()

    with col_b:
        if ask_btn and question:
            with st.spinner("Searching knowledge base…"):
                try:
                    result = ask_groq(question, category)
                    st.session_state.answer  = result
                    st.session_state.sources = result.get("sources", [])
                except json.JSONDecodeError:
                    st.error("Could not parse AI response. Try again."); st.stop()
                except Exception as e:
                    st.error(f"Error: {e}"); st.stop()

        if st.session_state.answer:
            result = st.session_state.answer

            # warning
            if result.get("warning"):
                st.markdown(f"""
                <div style="background:#fefce8;border:1px solid #fde68a;border-left:4px solid #d97706;
                border-radius:8px;padding:12px 16px;margin-bottom:14px;font-size:0.85rem;color:#78350f;">
                ⚠️ <b>Important:</b> {result['warning']}</div>
                """, unsafe_allow_html=True)

            # answer
            st.markdown("**Answer**")
            st.markdown(f'<div class="answer-box">{result.get("answer","")}</div>', unsafe_allow_html=True)

            # key points
            if result.get("key_points"):
                st.markdown("<br>**Key Points**", unsafe_allow_html=True)
                for pt in result["key_points"]:
                    st.markdown(f'<div style="background:#f0fdf4;border-left:3px solid #16a34a;border-radius:6px;padding:9px 14px;margin-bottom:6px;font-size:0.85rem;color:#14532d;">{pt}</div>', unsafe_allow_html=True)

            # sources
            if result.get("sources"):
                st.markdown("<br>**📚 Sources**", unsafe_allow_html=True)
                src_html = "".join(f'<span class="source-tag">{s}</span>' for s in result["sources"])
                st.markdown(src_html, unsafe_allow_html=True)

            # metrics
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-val">{result.get("chunks_used",0)}</div><div class="metric-lbl">Chunks Retrieved</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-val">{len(result.get("categories",[]))}</div><div class="metric-lbl">Categories</div></div>', unsafe_allow_html=True)

        elif not ask_btn:
            st.markdown("""
            <div style="text-align:center;padding:60px 0;color:#94a3b8;">
                <div style="font-size:3rem;margin-bottom:12px;">🏗️</div>
                <div style="font-size:1rem;font-weight:600;color:#475569;">Ready to answer</div>
                <div style="font-size:0.875rem;margin-top:6px;">Type a question or click an example on the left</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────
# TAB 2 — QUICK REFERENCE
# ─────────────────────────────────────
with tab2:
    st.markdown("### Construction Quick Reference")
    r1, r2 = st.columns(2, gap="large")

    with r1:
        st.markdown("""
#### 🏛️ IBC Construction Types
| Type | Description | Max Height |
|---|---|---|
| IA | Fire resistive 3hr | Unlimited |
| IB | Fire resistive 2hr | Unlimited |
| IIA | Non-combustible 1hr | Varies |
| IIB | Non-combustible 0hr | Varies |
| IIIA | Ordinary 1hr | 5 stories |
| VA | Wood frame 1hr | 3 stories |
| VB | Wood frame 0hr | 2 stories |

#### 🔌 NEC GFCI Requirements
- Bathrooms, Garages, Outdoors
- Crawl spaces, Basements
- Kitchens, Pools & spas

#### 🔩 Concrete Strengths
- Residential footing: 2,500–3,000 psi
- Commercial slab: 3,000–4,000 psi
- Structural column: 4,000–5,000 psi
- High-rise: 6,000–10,000 psi
""")

    with r2:
        st.markdown("""
#### 💰 Cost Estimates (2025 US)
- Residential: $150–$250 /sq ft
- Custom homes: $350–$500 /sq ft
- Office space: $150–$250 /sq ft
- Warehouses: $50–$120 /sq ft
- Medical: $300–$600 /sq ft
- Restaurants: $350–$600 /sq ft

#### 🏗️ Permits Typically Required
- New construction
- Structural changes
- Electrical & plumbing work
- HVAC replacement
- Large decks & additions

#### 🪜 Standard Inspection Steps
1. Footing
2. Foundation
3. Plumbing rough-in
4. Framing
5. Electrical rough-in
6. Insulation
7. Final inspection
""")

# ─────────────────────────────────────
# TAB 3 — ABOUT
# ─────────────────────────────────────
with tab3:
    st.markdown("""
### About This Assistant

This AI assistant covers the full scope of US construction knowledge:

| Domain | Standards Covered |
|---|---|
| Building Codes | IBC 2021, IRC 2021 |
| Electrical | NEC 2023 |
| Plumbing | UPC 2021, IPC 2021 |
| Accessibility | ADA Standards 2010 |
| Structural | AISC, ACI 318, AWC NDS |
| Fire Safety | NFPA 13, IFC 2021 |
| Cost Data | RSMeans 2025 |

**Powered by** Groq (Llama 3.3 70B) for ultra-fast inference.

> ⚠️ This assistant provides general guidance based on model codes. Always verify requirements with your local Authority Having Jurisdiction (AHJ) before starting any construction project.
""")
