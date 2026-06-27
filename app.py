import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Construction AI Assistant",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Construction AI Assistant")

# ======================================================
# SESSION STATE INIT
# ======================================================
if "question" not in st.session_state:
    st.session_state.question = ""

# ======================================================
# HEALTH CHECK
# ======================================================
try:
    health = requests.get(f"{API_URL}/health", timeout=3).json()
    if health.get("rag_ready"):
        st.success("✅ Knowledge base loaded — ready to answer")
    else:
        st.warning("⚠️ RAG not ready — check API terminal")
except Exception:
    st.error("⚠️ API not running. Start: uvicorn api.main:app --reload")
    st.stop()

st.divider()

tab1, tab2, tab3 = st.tabs([
    "💬 Ask the Assistant",
    "🔍 Knowledge Base",
    "📋 Quick Reference"
])

# ───────────────────────────────────────────────────────
# TAB 1: ASK
# ───────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("Ask Any Construction Question")

        category = st.selectbox(
            "Topic area (for guidance only)",
            [
                "Any / General",
                "Building Codes",
                "Permits & Inspections",
                "Structural & Foundations",
                "Concrete & Materials",
                "Steel Framing",
                "Electrical (NEC)",
                "Plumbing",
                "HVAC & Mechanical",
                "Accessibility (ADA)",
                "Cost Estimation"
            ]
        )

        question = st.text_area(
            "Your question",
            value=st.session_state.question,
            placeholder="What are the fire resistance requirements for a Type VA wood frame apartment building?",
            height=120
        )

        ask_btn = st.button(
            "🔍 Get Answer",
            type="primary",
            use_container_width=True,
            disabled=not question
        )

        # ==================================================
        # EXAMPLES (FIXED KEYS)
        # ==================================================
        st.markdown("**💡 Try these:**")

        examples = [
            "What permits do I need for a residential deck?",
            "What is the minimum concrete strength for a foundation?",
            "How many GFCI outlets are required in a bathroom?",
            "What are the setback requirements for a residential addition?",
            "How do I size HVAC for a 2,000 sq ft house?",
            "What is the cost per square foot for commercial construction?",
            "What are ADA requirements for parking spaces?",
            "What is the minimum slope for drain pipes?",
            "What steel grade is used for structural wide flange beams?",
            "When is a fire sprinkler system required in a restaurant?"
        ]

        for i, ex in enumerate(examples):
            if st.button(
                f"→ {ex}",
                key=f"example_{i}",   # ✅ FIXED UNIQUE KEY
                use_container_width=True
            ):
                st.session_state.question = ex
                question = ex
                ask_btn = True

    with col_b:
        if ask_btn and question:
            with st.spinner("Searching knowledge base..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/query",
                        json={"question": question},
                        timeout=30
                    )
                    result = resp.json()
                except Exception as e:
                    st.error(f"API error: {e}")
                    st.stop()

            st.subheader("Answer")
            st.markdown(result["answer"])

            st.divider()

            if result.get("sources"):
                st.markdown("**📚 Sources Used:**")
                for src in result["sources"]:
                    st.markdown(f"- {src}")

            c1, c2 = st.columns(2)
            c1.metric("Chunks Retrieved", result.get("chunks_used", 0))
            c2.metric("Categories", len(result.get("categories", [])))

        else:
            st.info(
                "Enter a question or click an example to get started.\n\n"
                "The assistant covers IBC building codes, NEC electrical, "
                "UPC plumbing, ADA accessibility, structural engineering, "
                "and construction cost estimation."
            )

# ───────────────────────────────────────────────────────
# TAB 2: KNOWLEDGE BASE
# ───────────────────────────────────────────────────────
with tab2:
    st.subheader("Knowledge Base Contents")

    try:
        kb_info = requests.get(
            f"{API_URL}/knowledge-base",
            timeout=5
        ).json()

        c1, c2, c3 = st.columns(3)
        c1.metric("Documents", kb_info.get("documents", 0))
        c2.metric("Total Chunks", kb_info.get("total_chunks", 0))
        c3.metric("Categories", len(kb_info.get("categories", [])))

        st.divider()

        col_cats, col_titles = st.columns(2)

        with col_cats:
            st.markdown("**Categories:**")
            for cat in sorted(kb_info.get("categories", [])):
                st.markdown(f"- `{cat}`")

        with col_titles:
            st.markdown("**Documents:**")
            for title in kb_info.get("titles", []):
                st.markdown(f"- {title}")

    except Exception as e:
        st.error(f"Could not load KB info: {e}")

    st.divider()
    st.subheader("Search Knowledge Base Directly")

    raw_query = st.text_input(
        "Raw similarity search",
        placeholder="fire resistance rating concrete"
    )

    if raw_query and st.button("Search"):
        try:
            results = requests.get(
                f"{API_URL}/search",
                params={"q": raw_query, "k": 5},
                timeout=10
            ).json()

            for r in results.get("results", []):
                with st.expander(f"📄 {r['title']} [{r['category']}]"):
                    st.text(r["content"])

        except Exception as e:
            st.error(str(e))

# ───────────────────────────────────────────────────────
# TAB 3: QUICK REFERENCE
# ───────────────────────────────────────────────────────
with tab3:
    st.subheader("Construction Quick Reference")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🏛️ IBC Construction Types
        | Type | Description | Max Height |
        |---|---|---|
        | IA | Fire resistive, 3hr | Unlimited |
        | IB | Fire resistive, 2hr | Unlimited |
        | IIA | Non-combustible, 1hr | Varies |
        | IIB | Non-combustible, 0hr | Varies |
        | IIIA | Ordinary, 1hr | 5 stories |
        | VA | Wood frame, 1hr | 3 stories |
        | VB | Wood frame, 0hr | 2 stories |

        ### 🔌 NEC GFCI Requirements
        - Bathrooms
        - Garages
        - Outdoors
        - Crawl spaces
        - Basements
        - Kitchens
        - Pools/spas

        ### 🔩 Concrete Strengths
        - Residential footing: 2,500–3,000 psi
        - Commercial slab: 3,000–4,000 psi
        - Structural column: 4,000–5,000 psi
        - High-rise: 6,000–10,000 psi
        """)

    with col2:
        st.markdown("""
        ### 💰 Cost Estimates (2025 US)
        - Residential: $150–$250/sq ft
        - Custom homes: $350–$500/sq ft
        - Offices: $150–$250/sq ft
        - Warehouses: $50–$120/sq ft
        - Medical: $300–$600/sq ft
        - Restaurants: $350–$600/sq ft

        ### 🏗️ Permits Required
        - New construction
        - Structural changes
        - Electrical work
        - Plumbing changes
        - HVAC replacement
        - Large decks

        ### 🪜 Inspection Steps
        1. Footing
        2. Foundation
        3. Plumbing rough-in
        4. Framing
        5. Electrical rough-in
        6. Insulation
        7. Final inspection
        """)