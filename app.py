"""Streamlit App for AI for Bharat RAG System"""
import streamlit as st
import os
from pathlib import Path
import time
from rag_engine import RAGEngine
import config

# Page configuration
st.set_page_config(
    page_title="AI for Bharat - RAG System",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern & Attractive Design
st.markdown("""
<style>
    /* Import Premium Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Branding and Header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove top padding/margin */
    .main {
        padding-top: 0 !important;
    }
    
    .block-container {
        padding-top: 0.5rem !important;
    }
    
    /* Main Background - Dark Blue (matching info cards) */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        background-attachment: fixed;
    }
    
    /* Content Container - Glass Morphism Effect */
    .main .block-container {
        padding: 0.5rem 1rem !important;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        max-width: 1900px;
        margin: 0.3rem auto !important;
        max-height: 96vh;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
    }
    
    /* COMPLETELY HIDE SCROLLBAR */
    ::-webkit-scrollbar {
        display: none;
    }
    
    * {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    
    .main .block-container {
        overflow-y: auto;
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    
    .main .block-container::-webkit-scrollbar {
        display: none;
    }
    
    /* Header Styles - Premium */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        color: #ffffff;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
        text-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        text-align: center;
        color: #e2e8f0;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Section Headers - White/Visible */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1e293b !important;
    }
    
    /* Sidebar Styles - Glass Morphism */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 0.8rem !important;
        border-right: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: #e2e8f0 !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 0.95rem !important;
        margin-bottom: 0.3rem !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] hr {
        background: rgba(226, 232, 240, 0.2);
        margin: 0.5rem 0 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.3rem !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e2e8f0 !important;
    }
    
    /* Button Styles - Dark Blue & Orange */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
        letter-spacing: 0.3px;
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        transform: translate(-50%, -50%);
        transition: width 0.5s, height 0.5s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 8px 20px rgba(30, 64, 175, 0.6);
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    }
    
    .stButton>button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    /* Primary Button - Orange */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.5);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        box-shadow: 0 8px 20px rgba(249, 115, 22, 0.7);
        transform: translateY(-2px) scale(1.03);
    }
    
    /* Secondary Button - Dark Blue */
    .stButton>button[kind="secondary"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        box-shadow: 0 8px 20px rgba(30, 58, 138, 0.6);
        transform: translateY(-2px) scale(1.03);
    }
    
    /* Text Input & Text Area - Clean & Readable */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.2rem;
        font-size: 1rem;
        line-height: 1.6;
        transition: all 0.3s ease;
        background: #f8fafc;
        color: #1e293b;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        background: #ffffff;
        outline: none;
    }
    
    .stTextArea>div>div>textarea {
        font-family: 'Poppins', sans-serif;
        resize: vertical;
        overflow-y: hidden !important;
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    
    .stTextArea>div>div>textarea::-webkit-scrollbar {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    /* File Uploader - Dark with Good Contrast */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.9) !important;
        border-radius: 12px;
        padding: 0.6rem;
        border: 2px dashed rgba(249, 115, 22, 0.5) !important;
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
    }
    
    [data-testid="stFileUploader"] label {
        font-size: 0.9rem !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: rgba(51, 65, 85, 0.8) !important;
        border: 2px dashed rgba(249, 115, 22, 0.4) !important;
        border-radius: 10px !important;
    }
    
    [data-testid="stFileUploader"] section > div {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stFileUploader"] small {
        color: #cbd5e1 !important;
    }
    
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #ea580c 0%, #f97316 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Answer Box - Glass Morphism */
    .answer-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.8rem;
        border-radius: 20px;
        border: 2px solid rgba(249, 115, 22, 0.3);
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(249, 115, 22, 0.3);
        animation: slideInUp 0.5s ease-out;
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        position: relative;
        overflow: hidden;
    }
    
    .answer-box h4 {
        color: #ea580c !important;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
        font-weight: 600;
    }
    
    .answer-box p {
        color: #1e293b !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
        font-weight: 400;
    }
    
    /* Source Box - Professional */
    .source-box {
        background: #f8fafc;
        padding: 1.8rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #f97316;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .source-box:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        background: #ffffff;
    }
    
    .source-box b {
        color: #1e293b;
        font-weight: 600;
    }
    
    /* Stats Box - Compact Dark Blue */
    .stats-box {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        color: white;
        padding: 0.4rem 0.6rem;
        border-radius: 12px;
        margin: 0.2rem 0;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .stats-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(30, 64, 175, 0.6);
    }
    
    .stats-box p {
        margin: 0.15rem 0;
        font-size: 0.7rem;
        line-height: 1.3;
        color: white !important;
        font-weight: 500;
    }
    
    .stats-box b {
        color: #ffffff;
        font-weight: 700;
    }
    
    /* Info Panel - Compact Glass Cards */
    .info-card {
        background: rgba(30, 58, 138, 0.7);
        padding: 0.6rem 0.8rem;
        border-radius: 12px;
        margin: 0.3rem 0;
        box-shadow: 0 4px 16px 0 rgba(30, 58, 138, 0.4);
        border: 2px solid rgba(249, 115, 22, 0.3);
        transition: all 0.3s ease;
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
    }
    
    .info-card:hover {
        border-color: rgba(249, 115, 22, 0.6);
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4);
        transform: translateY(-2px);
        background: rgba(30, 58, 138, 0.85);
    }
    
    .info-card h4 {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.4rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .info-card ul, .info-card ol {
        color: #f8fafc !important;
        font-size: 0.8rem !important;
        line-height: 1.5 !important;
        margin: 0 !important;
        padding-left: 1rem !important;
    }
    
    .info-card li {
        margin: 0.2rem 0 !important;
        color: #f8fafc !important;
    }
    
    .info-card div {
        font-size: 0.8rem !important;
        line-height: 1.5 !important;
        color: #f8fafc !important;
    }
    
    .info-card b {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Expander - Professional */
    .streamlit-expanderHeader {
        background: #ffffff;
        border-radius: 10px;
        font-weight: 600;
        padding: 1rem 1.2rem;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        color: #1e293b !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #eff6ff;
        border-color: #3b82f6;
    }
    
    .streamlit-expanderHeader p {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderContent {
        border: 2px solid #e2e8f0;
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 1rem;
        background: #ffffff;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #ea580c 0%, #f97316 100%);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f97316;
    }
    
    /* Divider */
    hr {
        margin: 1rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #f97316, transparent);
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Checkbox & Radio - Compact */
    .stCheckbox, .stRadio {
        padding: 0.2rem;
    }
    
    .stCheckbox label, .stRadio label {
        font-size: 0.8rem !important;
    }
    
    /* Slider - Compact */
    .stSlider {
        padding: 0.3rem 0;
    }
    
    .stSlider label {
        font-size: 0.8rem !important;
    }
    
    /* Caption - Glass Morphism */
    .caption {
        background: rgba(255, 255, 255, 0.2);
        padding: 1rem 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #ffffff;
        border-left: 5px solid #f97316;
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.18);
    }
    
    .caption b {
        color: #ffffff;
        font-weight: 700;
    }
    
    /* Metrics - High Contrast & Readable */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.95) !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetric"] {
        padding: 0.5rem !important;
        background: rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Force ALL Sidebar Text to be Light */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6 {
        color: #ffffff !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Force Info Card Text to be Light */
    .info-card,
    .info-card *,
    .info-card p,
    .info-card li,
    .info-card span,
    .info-card div {
        color: #f8fafc !important;
    }
    
    .info-card h4 {
        color: #ffffff !important;
    }
    
    .info-card b,
    .info-card strong {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize RAG engine
@st.cache_resource
def get_rag_engine():
    engine = RAGEngine()
    # Force reload from disk on startup
    engine.vector_store.load()
    return engine

rag_engine = get_rag_engine()

# Header - Clean
st.markdown('''
<div style="text-align: center; margin-bottom: 1.5rem; margin-top: 1rem;">
    <div class="main-header">RAG using Amazon Bedrock and Knowledge Bases</div>
</div>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📚 Document Management")
    st.markdown("---")
    
    # # File upload with enhanced description
    # st.markdown("""
    # <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
    #     <p style="color: white; font-size: 0.9rem; margin: 0;">
    #         📤 Upload your documents to get started
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'doc', 'txt', 'pptx', 'xlsx', 'csv'],
        accept_multiple_files=True,
        help="Upload PDF, Word, PowerPoint, Excel, or text files",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        if st.button("🚀 Process Documents", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save file temporarily
                file_path = os.path.join(config.UPLOAD_FOLDER, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Ingest document
                result = rag_engine.ingest_document(file_path)
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.info(f"📊 Created {result['chunks_created']} chunks")
                else:
                    st.error(f"❌ {result['message']}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("✨ All documents processed!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
    
    st.markdown("---")
    
    # System stats with enhanced design
    st.markdown("### 📊 System Stats")
    stats = rag_engine.get_stats()
    
    # Create metrics in a nice layout
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("📦 Chunks", stats['total_documents'])
    with col_b:
        st.metric("🎯 Top-K", stats['top_k_rerank'])
    
    st.markdown(f"""
    <div class="stats-box">
        <p><b>🤖 Model:</b> Claude 3.5 Sonnet</p>
        <p><b>🔄 Reranking:</b> Amazon Rerank v1</p>
        <p><b>📏 Chunk Size:</b> {stats['chunk_size']}</p>
        <p><b>🔍 Retrieval:</b> {stats['top_k_retrieval']}</p>
        <p><b>🛡️ Guardrails:</b> {'✅ Enabled' if stats['guardrails_enabled'] else '❌ Disabled'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Settings with better styling
    st.markdown("### ⚙️ Settings")
    
    use_reranking = st.checkbox("Use Reranking", value=True, help="Use Amazon Rerank for better results")
    temperature = st.slider("Temperature", 0.0, 1.0, config.TEMPERATURE, 0.1, help="Higher = more creative")
    
    st.divider()
    
    # Reload button
    if st.button("� Reload Vector Store", type="primary"):
        rag_engine.vector_store.load()
        st.success("✅ Vector store reloaded!")
        st.rerun()
    
    # Clear data
    if st.button("🗑️ Clear All Documents", type="secondary"):
        if st.session_state.get('confirm_clear', False):
            rag_engine.clear_all()
            st.success("✅ All documents cleared!")
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.warning("⚠️ Click again to confirm")
            st.session_state.confirm_clear = True

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%); padding: 1rem 1.5rem; border-radius: 16px; margin-bottom: 0.5rem; box-shadow: 0 8px 24px rgba(30, 64, 175, 0.5); border: 2px solid rgba(255,255,255,0.3); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);">
        <h2 style="color: white; font-weight: 800; margin: 0; font-size: 1.3rem; text-shadow: 0 3px 10px rgba(0,0,0,0.3);">💬 Ask Questions</h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.3rem 0 0 0; font-size: 0.85rem; font-weight: 500;">Get instant answers from your documents</p>
    </div>
    """, unsafe_allow_html=True)
    
    query = st.text_area(
        "Question",
        height=60,
        placeholder="Ask anything about your documents... (Any language: English, Hindi, Tamil, etc.)",
        help="Type your question in any language",
        label_visibility="collapsed"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    
    with col_btn2:
        clear_button = st.button("🔄 Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    # Process query
    if ask_button and query:
        with st.spinner("🤔 Thinking..."):
            start_time = time.time()
            
            # Query RAG system
            result = rag_engine.query(query, use_reranking=use_reranking)
            
            elapsed_time = time.time() - start_time
        
        # Display answer
        st.markdown("""
        <h3 style="color: #1e293b; font-weight: 700; margin-top: 1.5rem;">💡 Answer</h3>
        """, unsafe_allow_html=True)
        
        if result['error']:
            st.error(result['answer'])
        else:
            st.markdown(f"""
            <div class="answer-box">
                <h4 style="color: #667eea; margin-bottom: 1rem;">📝 Response:</h4>
                <p style="font-size: 1.1rem; line-height: 1.8; color: #333;">{result['answer']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="caption">
                ⏱️ <b>Response time:</b> {elapsed_time:.2f}s &nbsp;|&nbsp; 
                📚 <b>Sources used:</b> {result.get('num_sources', 0)} &nbsp;|&nbsp; 
                🤖 <b>Model:</b> {result.get('model', 'Unknown').split('/')[-1]}
            </div>
            """, unsafe_allow_html=True)
        
        # Display sources
        if result['sources']:
            st.markdown("""
            <h3 style="color: #1e293b; font-weight: 700; margin-top: 2rem;">📖 Sources</h3>
            """, unsafe_allow_html=True)
            
            for source in result['sources']:
                with st.expander(f"Source {source['rank']}: {source['filename']} (Chunk {source['chunk_id']})"):
                    st.markdown(f"""
                    <div class="source-box">
                        <b>Text:</b><br>
                        {source['text']}<br><br>
                        <b>Similarity Score:</b> {source['similarity_score']:.4f}<br>
                        <b>Rerank Score:</b> {source.get('rerank_score', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ea580c 0%, #f97316 100%); padding: 1rem 1.5rem; border-radius: 16px; margin-bottom: 0.5rem; box-shadow: 0 8px 24px rgba(249, 115, 22, 0.5); border: 2px solid rgba(255,255,255,0.3); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);">
        <h2 style="color: white; font-weight: 800; margin: 0; font-size: 1.3rem; text-shadow: 0 3px 10px rgba(0,0,0,0.3);">ℹ️ About</h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.3rem 0 0 0; font-size: 0.85rem; font-weight: 500;">Powerful AI features at your fingertips</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>✨ Features</h4>
        <ul>
            <li>🧠 <b>Semantic Chunking</b>: Intelligent text splitting</li>
            <li>🔍 <b>Vector Search</b>: FAISS-powered similarity</li>
            <li>🎯 <b>Reranking</b>: Amazon Rerank precision</li>
            <li>🛡️ <b>Guardrails</b>: Built-in safety</li>
            <li>🌍 <b>Multilingual</b>: 10+ Indian languages</li>
            <li>⚡ <b>Fast</b>: Optimized pipeline</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4 style="color: #1e40af; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 700;">📁 Supported Formats</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; color: #1e293b; font-size: 0.95rem;">
            <div>� TPDF</div>
            <div>📝 Word</div>
            <div>📊 PowerPoint</div>
            <div>📈 Excel</div>
            <div>📋 CSV</div>
            <div>📃 Text</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4 style="color: #1e40af; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 700;">🔄 How It Works</h4>
        <ol style="line-height: 2.2; color: #1e293b; font-size: 0.95rem;">
            <li><b>Upload</b> documents</li>
            <li><b>Process</b> with semantic chunking</li>
            <li><b>Embed</b> using Titan</li>
            <li><b>Store</b> in FAISS vector DB</li>
            <li><b>Query</b> in any language</li>
            <li><b>Retrieve</b> relevant chunks</li>
            <li><b>Rerank</b> for precision</li>
            <li><b>Generate</b> answer with Claude</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4 style="color: #1e40af; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 700;">💡 Quick Tips</h4>
        <ul style="line-height: 2.2; color: #1e293b; font-size: 0.95rem;">
            <li>📤 Upload multiple documents at once</li>
            <li>🌐 Ask questions in any language</li>
            <li>🎯 Use reranking for better accuracy</li>
            <li>🌡️ Adjust temperature for creativity</li>
            <li>📖 Check sources for transparency</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)




