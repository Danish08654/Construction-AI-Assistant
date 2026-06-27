import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict, List
import time

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title=" Construction AI Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS STYLING
# ============================================================
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --success-color: #2ecc71;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
        --dark-bg: #0f1419;
        --light-text: #ecf0f1;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 1px solid #667eea30;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Answer section */
    .answer-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .answer-box h3 {
        color: #333;
        margin-top: 0;
    }
    
    /* Source list styling */
    .source-item {
        background: #e8f4f8;
        padding: 0.75rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        border-left: 3px solid #3498db;
    }
    
    /* Button styling */
    .button-group {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    /* Example button */
    .example-btn {
        background: #f0f2f6;
        border: 1px solid #ddd;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .example-btn:hover {
        background: #e0e2e6;
        transform: translateY(-2px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    /* Spinner animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading {
        animation: spin 1s linear infinite;
    }
    
    /* Success/Error messages */
    .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .error-msg {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Knowledge base grid */
    .kb-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
    }
    
    /* Conversation history */
    .chat-item {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        border-left: 3px solid #667eea;
    }
    
    .chat-item.user {
        background: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .chat-item.assistant {
        background: #f5f5f5;
        border-left-color: #4caf50;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .kb-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CONFIGURATION & CONSTANTS
# ============================================================


MOCK_ANSWER = {
    "answer": """### Foundation Requirements

For a residential foundation, you typically need:

1. **Depth**: Minimum 3-4 feet below grade (below frost line)
2. **Concrete Strength**: 2,500-3,000 psi for residential footings
3. **Slope**: Ground should slope away at least 5-10% for drainage
4. **Backfill**: Compacted fill material (6" lifts maximum)

**Frost Line Considerations:**
- Northern climates: 4-6 feet
- Southern climates: 0-2 feet
- Check local building codes for your area

**Inspection Points:**
- Footing depth inspection
- Concrete strength test (air pressure test)
- Compaction of backfill
- Drainage verification""",
    "sources": [
        "IBC 2021 - Chapter 3: Fire and Life Safety",
        "Residential Code for One- and Two-Family Dwellings (IRC)",
        "Building Foundation Design Handbook"
    ],
    "chunks_used": 5,
    "categories": ["Structural & Foundations", "Building Codes"]
}

MOCK_KB_INFO = {
    "documents": 12,
    "total_chunks": 847,
    "categories": [
        "Building Codes", "Permits & Inspections", "Structural & Foundations",
        "Concrete & Materials", "Steel Framing", "Electrical (NEC)",
        "Plumbing", "HVAC & Mechanical", "Accessibility (ADA)", "Cost Estimation"
    ],
    "titles": [
        "IBC 2021 Building Code Summary",
        "NEC Electrical Standards",
        "IRC Residential Code",
        "Concrete Design Fundamentals",
        "Structural Steel Design Guide",
        "ADA Accessibility Guidelines",
        "Construction Cost Estimation",
        "Plumbing System Design",
        "HVAC System Sizing",
        "Foundation Design Handbook",
        "Building Permit Checklist",
        "Inspection Procedures Manual"
    ]
}

EXAMPLE_QUESTIONS = [
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

CATEGORIES = [
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

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "api_status" not in st.session_state:
    st.session_state.api_status = None

if "question" not in st.session_state:
    st.session_state.question = ""

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

def search_knowledge_base(query: str, k: int = 5) -> Dict:
    """Search the knowledge base directly."""
    try:
        response = requests.get(
            f"{API_URL}/search",
            params={"q": query, "k": k},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"results": []}

def get_knowledge_base_info() -> Dict:
    """Get information about the knowledge base."""
    try:
        response = requests.get(f"{API_URL}/knowledge-base", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return MOCK_KB_INFO

def add_to_conversation_history(question: str, answer: str):
    """Add Q&A pair to conversation history."""
    st.session_state.conversation_history.append({
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer
    })

def download_conversation_history():
    """Generate downloadable conversation history."""
    if not st.session_state.conversation_history:
        return None
    
    content = "# Construction AI Assistant - Conversation History\n\n"
    content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for i, item in enumerate(st.session_state.conversation_history, 1):
        content += f"## Q{i}. {item['question']}\n\n"
        content += f"{item['answer']}\n\n"
        content += f"*Time: {item['timestamp']}*\n\n"
        content += "---\n\n"
    
    return content

def format_answer(result: Dict):
    """Format API response for display."""
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("✅ Answer")
        st.markdown(result.get("answer", "No answer generated."))
    
    with col_b:
        st.subheader("📊 Stats")
        c1, c2 = st.columns(2)
        c1.metric("Chunks", result.get("chunks_used", 0))
        c2.metric("Categories", len(result.get("categories", [])))
    
    st.divider()
    
    # Sources
    if result.get("sources"):
        st.subheader("📚 Sources Used")
        cols = st.columns(min(2, len(result["sources"])))
        for idx, src in enumerate(result["sources"]):
            with cols[idx % len(cols)]:
                st.markdown(f"📄 {src}")

# ============================================================
# HEADER
# ============================================================

st.markdown("""
    <div class="main-header">
        <h1>🏗️ Construction AI Assistant</h1>
        <p>Powered by RAG • Building Codes • Cost Estimation • Regulations</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# HEALTH CHECK & STATUS
# ============================================================

health = check_api_health()
st.session_state.api_status = health

if health["status"] == "online" and health["rag_ready"]:
    st.success(health["message"])
elif health["status"] == "offline":
    st.warning(health["message"])
    st.session_state.demo_mode = True
else:
    st.error(health["message"])
    st.session_state.demo_mode = True

st.divider()

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Ask the Assistant",
    "🔍 Knowledge Base",
    "📋 Quick Reference",
    "📝 History",
    "⚙️ Settings"
])

# ═══════════════════════════════════════════════════════════
# TAB 1: ASK ASSISTANT
# ═══════════════════════════════════════════════════════════

with tab1:
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.subheader("Ask Any Construction Question")
        
        category = st.selectbox(
            "Select topic area (optional)",
            CATEGORIES,
            key="category_select"
        )
        
        question = st.text_area(
            "Your question",
            value=st.session_state.question,
            placeholder="e.g., What are the fire resistance requirements for a Type VA wood frame apartment building?",
            height=120,
            key="main_question"
        )
        
        col_btn_1, col_btn_2 = st.columns(2)
        with col_btn_1:
            ask_btn = st.button(
                "🔍 Get Answer",
                type="primary",
                use_container_width=True,
                disabled=not question,
                key="ask_button"
            )
        
        with col_btn_2:
            clear_btn = st.button(
                "🗑️ Clear",
                use_container_width=True,
                key="clear_button"
            )
        
        if clear_btn:
            st.session_state.question = ""
            st.rerun()
        
        st.markdown("---")
        st.markdown("**💡 Example Questions:**")
        
        for i, example in enumerate(EXAMPLE_QUESTIONS):
            if st.button(
                f"→ {example}",
                key=f"example_{i}",
                use_container_width=True,
                help="Click to use this example"
            ):
                st.session_state.question = example
                st.rerun()
    
    with col_right:
        if ask_btn and question:
            with st.spinner("🔄 Searching knowledge base..."):
                time.sleep(0.5)  # UX feedback
                
                if st.session_state.demo_mode:
                    # Use mock data
                    result = MOCK_ANSWER
                else:
                    # Query real API
                    result = query_api(question, category)
                    if result is None:
                        st.session_state.demo_mode = True
                        result = MOCK_ANSWER
            
            if result:
                format_answer(result)
                add_to_conversation_history(question, result.get("answer", ""))
                
                # Feedback section
                st.divider()
                st.subheader("👍 Was this helpful?")
                col_feedback_1, col_feedback_2 = st.columns(2)
                with col_feedback_1:
                    if st.button("👍 Yes", use_container_width=True, key="feedback_yes"):
                        st.success("Thanks for the feedback!")
                with col_feedback_2:
                    if st.button("👎 No", use_container_width=True, key="feedback_no"):
                        st.info("We'll improve! Consider asking with different wording.")
        
        else:
            st.info(
                "📌 **Get Started:**\n\n"
                "1. Enter a construction question\n"
                "2. Or click an example question\n"
                "3. Optionally select a topic area\n\n"
                "The assistant covers IBC building codes, NEC electrical standards, "
                "UPC plumbing, ADA accessibility, structural engineering, and "
                "construction cost estimation."
            )

# ═══════════════════════════════════════════════════════════
# TAB 2: KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════

with tab2:
    st.subheader("📚 Knowledge Base Contents")
    
    kb_info = get_knowledge_base_info()
    
    # Stats cards
    col_k1, col_k2, col_k3 = st.columns(3)
    col_k1.metric("📄 Documents", kb_info.get("documents", 0))
    col_k2.metric("📦 Total Chunks", kb_info.get("total_chunks", 0))
    col_k3.metric("🏷️ Categories", len(kb_info.get("categories", [])))
    
    st.divider()
    
    col_cats, col_titles = st.columns(2)
    
    with col_cats:
        st.markdown("**📂 Categories:**")
        for cat in sorted(kb_info.get("categories", [])):
            st.markdown(f"- `{cat}`")
    
    with col_titles:
        st.markdown("**📋 Documents:**")
        for title in kb_info.get("titles", []):
            st.markdown(f"- {title}")
    
    st.divider()
    
    # Direct search
    st.subheader("🔎 Direct Knowledge Base Search")
    
    col_search_1, col_search_2 = st.columns([4, 1])
    with col_search_1:
        search_query = st.text_input(
            "Enter search terms",
            placeholder="e.g., fire resistance rating concrete",
            key="search_input"
        )
    with col_search_2:
        search_btn = st.button("Search", use_container_width=True, key="search_button")
    
    if search_btn and search_query:
        with st.spinner("🔄 Searching..."):
            results = search_knowledge_base(search_query, k=5)
        
        if results.get("results"):
            for r in results["results"]:
                with st.expander(f"📄 {r.get('title', 'Unknown')} [{r.get('category', 'N/A')}]"):
                    st.text_area(
                        "Content",
                        value=r.get("content", ""),
                        height=150,
                        disabled=True,
                        key=f"result_{r.get('title', 'unknown')}"
                    )
        else:
            st.info("No results found. Try different search terms.")

# ═══════════════════════════════════════════════════════════
# TAB 3: QUICK REFERENCE
# ═══════════════════════════════════════════════════════════

with tab3:
    st.subheader("📚 Construction Quick Reference Guide")
    
    col_qr_1, col_qr_2 = st.columns(2)
    
    with col_qr_1:
        st.markdown("""
        ### 🏛️ IBC Construction Types
        
        | Type | Fire Rating | Max Height |
        |------|-------------|-----------|
        | IA | 3 hours | Unlimited |
        | IB | 2 hours | Unlimited |
        | IIA | 1 hour | Unlimited |
        | IIB | 0 hours | Unlimited |
        | IIIA | 1 hour | 5 stories |
        | IIIB | 0 hours | 3 stories |
        | VA | 1 hour | 3 stories |
        | VB | 0 hours | 2 stories |
        
        ### 🔌 NEC GFCI Requirements
        
        GFCI protection required for:
        - ✓ Bathrooms
        - ✓ Garages
        - ✓ Outdoor receptacles
        - ✓ Crawl spaces
        - ✓ Basements
        - ✓ Kitchen countertops
        - ✓ Pools and spas
        - ✓ Hot tubs
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ### 🔩 Concrete Strengths
        
        | Application | PSI Range |
        |-------------|-----------|
        | Residential footing | 2,500–3,000 |
        | Commercial slab | 3,000–4,000 |
        | Structural column | 4,000–5,000 |
        | High-rise | 6,000–10,000 |
        | Parking structure | 4,500–5,500 |
        """)
    
    with col_qr_2:
        st.markdown("""
        ### 💰 2025 Construction Cost Estimates
        
        | Type | Cost/sq ft |
        |------|-----------|
        | Residential | $150–$250 |
        | Custom homes | $350–$500 |
        | Office | $150–$250 |
        | Warehouse | $50–$120 |
        | Medical | $300–$600 |
        | Restaurant | $350–$600 |
        | Retail | $100–$300 |
        
        ### 🏗️ Common Permits Required
        
        - ✓ New construction
        - ✓ Structural changes
        - ✓ Electrical work >$750
        - ✓ Plumbing changes
        - ✓ HVAC replacement
        - ✓ Roofing
        - ✓ Large decks
        - ✓ Additions
        
        ### 🪜 Inspection Checklist
        
        1. **Footing** - Before foundation pour
        2. **Foundation** - After concrete cures
        3. **Framing** - Before drywall
        4. **Plumbing rough-in** - Before walls
        5. **Electrical rough-in** - Before walls
        6. **Insulation** - Before drywall
        7. **Drywall** - Before finishing
        8. **Final inspection** - Before occupancy
        """)

# ═══════════════════════════════════════════════════════════
# TAB 4: CONVERSATION HISTORY
# ═══════════════════════════════════════════════════════════

with tab4:
    st.subheader("📝 Conversation History")
    
    if st.session_state.conversation_history:
        col_hist_1, col_hist_2, col_hist_3 = st.columns([1, 1, 1])
        
        with col_hist_1:
            st.metric("Total Questions", len(st.session_state.conversation_history))
        
        with col_hist_2:
            if st.button("🗑️ Clear History", use_container_width=True, key="clear_history"):
                st.session_state.conversation_history = []
                st.success("History cleared!")
                st.rerun()
        
        with col_hist_3:
            history_text = download_conversation_history()
            if history_text:
                st.download_button(
                    label="💾 Download as Text",
                    data=history_text,
                    file_name=f"construction_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_history_txt"
                )
        
        st.divider()
        
        for idx, item in enumerate(st.session_state.conversation_history):
            with st.expander(f"**Q{idx + 1}:** {item['question'][:60]}...", expanded=False):
                st.markdown(f"**Time:** {item['timestamp']}")
                st.markdown("---")
                st.markdown(f"**Question:**\n{item['question']}")
                st.markdown("---")
                st.markdown(f"**Answer:**\n{item['answer']}")
                
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    if st.button("📋 Copy Question", key=f"copy_q_{idx}"):
                        st.session_state.question = item['question']
                        st.success("Question copied to input!")
                with col_h2:
                    if st.button("📥 Copy to Text", key=f"copy_a_{idx}"):
                        st.info("Copy from the answer section above")
    
    else:
        st.info("📌 No conversation history yet. Ask a question to get started!")

# ═══════════════════════════════════════════════════════════
# TAB 5: SETTINGS
# ═══════════════════════════════════════════════════════════

with tab5:
    st.subheader("⚙️ Settings & Information")
    
    col_set_1, col_set_2 = st.columns(2)
    
    with col_set_1:
        st.markdown("### 🔧 System Status")
        
        status_info = {
            "API Status": "🟢 Online" if health["status"] == "online" else "🔴 Offline",
            "RAG Ready": "✅ Yes" if health["rag_ready"] else "❌ No",
            "Mode": "📡 Live" if not st.session_state.demo_mode else "📊 Demo",
            "API URL": API_URL,
        }
        
        for key, value in status_info.items():
            st.write(f"**{key}:** {value}")
    
    with col_set_2:
        st.markdown("### 📊 Statistics")
        
        stats = {
            "Questions Asked": len(st.session_state.conversation_history),
            "Session Duration": "Active",
            "Knowledge Base": f"{MOCK_KB_INFO['documents']} documents",
            "Total Chunks": f"{MOCK_KB_INFO['total_chunks']} indexed",
        }
        
        for key, value in stats.items():
            st.write(f"**{key}:** {value}")
    
    st.divider()
