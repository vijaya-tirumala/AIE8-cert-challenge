"""
Streamlit Frontend for SE RAG Agent
Interactive web interface for the RAG system
"""

import streamlit as st
import requests
import time
import json
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="SolvIQ",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for SolvIQ branding with Tech Blue palette
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
    
    /* SolvIQ Tech Blue Brand Colors */
    :root {
        --primary-color: #0A84FF;  /* Azure Blue */
        --secondary-color: #1C1C1E;  /* Carbon Black */
        --accent-color: #FFD60A;  /* Warm Yellow */
        --success-color: #00B894;  /* Sage Green */
        --warning-color: #FDCB6E;  /* Soft Gold */
        --error-color: #FF6B6B;  /* Soft Red */
        --background-color: #F9FAFB;  /* Light Gray */
        --card-bg: #FFFFFF;  /* White */
        --text-dark: #1C1C1E;  /* Carbon Black */
        --text-light: #F9FAFB;  /* Light Gray */
        --text-muted: #8E8E93;  /* Muted Gray */
    }
    
    /* Main app styling with increased font sizes */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        font-size: 18px; /* Increased by 2 more points */
    }
    
    /* Global font size increases */
    body {
        font-size: 18px !important;
    }
    
    /* Headers */
    h1 { font-size: 2.75rem !important; }
    h2 { font-size: 2.25rem !important; }
    h3 { font-size: 1.75rem !important; }
    h4 { font-size: 1.5rem !important; }
    h5 { font-size: 1.375rem !important; }
    h6 { font-size: 1.25rem !important; }
    
    /* Paragraphs and text */
    p, div, span {
        font-size: 18px !important;
    }
    
    /* Streamlit specific elements */
    .stMarkdown, .stText, .stSelectbox, .stTextInput {
        font-size: 18px !important;
    }
    
    /* Header styling */
    .stApp > header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--dark-bg), var(--card-bg));
    }
    
    /* Custom header with Tech Blue styling */
    .solviq-header {
        background: linear-gradient(135deg, var(--primary-color), #0056CC);
        padding: 1.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(10, 132, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .solviq-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 214, 10, 0.1) 0%, transparent 70%);
        animation: sparkle 4s ease-in-out infinite;
    }
    
    @keyframes sparkle {
        0%, 100% { transform: rotate(0deg) scale(1); opacity: 0.3; }
        50% { transform: rotate(180deg) scale(1.1); opacity: 0.6; }
    }
    
    .solviq-logo-container {
        position: relative;
        z-index: 2;
    }
    
    .solviq-title {
        color: white;
        font-family: 'Poppins', sans-serif;
        font-size: 7.5rem; /* Increased by additional 2.0rem for much bigger logo */
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        letter-spacing: -2px;
        position: relative;
    }
    
    .solviq-title .spark-icon {
        display: inline-block;
        margin-left: 0.5rem;
        animation: pulse 2s ease-in-out infinite;
        filter: drop-shadow(0 0 10px rgba(255, 214, 10, 0.8));
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .solviq-tagline {
        color: rgba(255,255,255,0.95);
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem; /* Increased by 2 more points */
        margin: 1rem 0 0 0;
        font-weight: 400;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 2;
    }
    
    .intelligence-glow {
        background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
        height: 3px;
        width: 60%;
        margin: 1rem auto 0;
        border-radius: 2px;
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { opacity: 0.3; transform: scaleX(0.8); }
        50% { opacity: 1; transform: scaleX(1); }
    }
    
    /* Enhanced card styling with glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(10, 132, 255, 0.2);
        box-shadow: 0 8px 32px rgba(10, 132, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px rgba(10, 132, 255, 0.2);
        border-color: rgba(10, 132, 255, 0.3);
        background: rgba(255, 255, 255, 0.95);
    }
    
    /* Performance dashboard styling */
    .performance-dashboard {
        background: linear-gradient(135deg, rgba(10, 132, 255, 0.05), rgba(255, 214, 10, 0.05));
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(10, 132, 255, 0.1);
    }
    
    /* Loading animation */
    .solviq-loader {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(10, 132, 255, 0.3);
        border-radius: 50%;
        border-top-color: var(--primary-color);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Button styling with Tech Blue */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), #0056CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 18px !important; /* Increased by 2 more points */
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(10, 132, 255, 0.3);
        text-transform: none;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(10, 132, 255, 0.4);
        background: linear-gradient(135deg, #0056CC, var(--primary-color)) !important;
        color: white !important;
    }
    
    /* Ensure button text is visible */
    .stButton > button span {
        color: white !important;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, var(--success-color), #059669);
        border: none;
        border-radius: 10px;
        color: white;
    }
    
    /* Error message styling */
    .stError {
        background: linear-gradient(135deg, var(--error-color), #dc2626);
        border: none;
        border-radius: 10px;
        color: white;
    }
    
    /* Info message styling */
    .stInfo {
        background: linear-gradient(135deg, var(--accent-color), #0891b2);
        border: none;
        border-radius: 10px;
        color: white;
    }
    
    /* Sidebar button styling - reverted to better look */
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), #0056CC);
        color: white;
        border: none;
        border-radius: 8px;
        margin: 0.2rem 0;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 18px !important; /* Increased by 2 more points */
        padding: 0.5rem 1rem;
        box-shadow: 0 2px 8px rgba(10, 132, 255, 0.2);
    }
    
    /* Sample RFP Questions styling with background colors */
    .sample-question-button {
        background: linear-gradient(135deg, rgba(10, 132, 255, 0.1), rgba(255, 214, 10, 0.1)) !important;
        border: 2px solid rgba(10, 132, 255, 0.2) !important;
        color: var(--text-dark) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        text-align: left !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(10, 132, 255, 0.1) !important;
        height: auto !important;
        min-height: 60px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.4 !important;
    }
    
    .sample-question-button:hover {
        background: linear-gradient(135deg, rgba(10, 132, 255, 0.2), rgba(255, 214, 10, 0.2)) !important;
        border-color: rgba(10, 132, 255, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(10, 132, 255, 0.2) !important;
    }
    
    .stSidebar .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(10, 132, 255, 0.3);
        background: linear-gradient(135deg, #0056CC, var(--primary-color));
    }
    
    /* Text area styling - fixed text visibility */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid rgba(10, 132, 255, 0.2);
        background: white !important;
        color: var(--text-dark) !important;
        font-family: 'Inter', sans-serif;
        font-size: 18px; /* Increased by 2 more points */
        padding: 12px;
        box-shadow: 0 2px 8px rgba(10, 132, 255, 0.1);
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.1);
        background: white !important;
        color: var(--text-dark) !important;
    }
    
    /* Ensure placeholder text is visible */
    .stTextArea textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.7;
    }
    
    /* Selectbox styling */
    .stSelectbox select {
        border-radius: 8px;
        border: 2px solid rgba(99, 102, 241, 0.2);
        background: var(--card-bg);
        color: var(--text-light);
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(135deg, var(--card-bg), #334155);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin: 0.5rem 0;
    }
    
    /* Footer styling - clean and minimal */
    .solviq-footer {
        background: rgba(240, 240, 240, 0.8);
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
        margin-top: 8rem;
        border: 1px solid rgba(200, 200, 200, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health() -> bool:
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_agents() -> Dict[str, Any]:
    """Get available agents from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/agents")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def query_rag(question: str, agent_type: str) -> Dict[str, Any]:
    """Query the RAG system"""
    try:
        payload = {
            "question": question,
            "agent_type": agent_type
        }
        response = requests.post(f"{API_BASE_URL}/query", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

# Main UI
def main():
    # SolvIQ Header with new branding
    st.markdown("""
    <div class="solviq-header">
        <div class="solviq-logo-container">
            <h1 class="solviq-title">
                SolvIQ<span class="spark-icon">⚡</span>
            </h1>
            <p class="solviq-tagline">The intelligence layer for every Solution Engineer.</p>
            <div class="intelligence-glow"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Solution Engineer welcome message
    st.info("👋 Welcome, Solution Engineer! SolvIQ is designed to help you create compelling technical proposals, respond to complex RFPs, and deliver enterprise-grade solutions faster than ever.")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configure SolvIQ")
        
        # API Health Check
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Not Connected")
            st.info("Please start the FastAPI backend: `uvicorn app:app --reload --port 8000`")
            return
        
        # Agent Selection
        st.subheader("🤖 Choose Your Agent")
        agents_data = get_agents()
        
        if agents_data and "available_agents" in agents_data:
            agent_options = {agent["type"]: agent["description"] for agent in agents_data["available_agents"]}
            selected_agent = st.selectbox(
                "",
                options=list(agent_options.keys()),
                format_func=lambda x: f"{x.title()} - {agent_options[x]}"
            )
            
            # Display agent features in 2x2 grid
            selected_agent_data = next(agent for agent in agents_data["available_agents"] if agent["type"] == selected_agent)
            if selected_agent_data["features"]:
                # Create 2x2 grid for features
                col1, col2 = st.columns(2)
                features = selected_agent_data["features"]
                
                with col1:
                    if len(features) > 0:
                        st.markdown(f"• {features[0]}")
                    if len(features) > 1:
                        st.markdown(f"• {features[1]}")
                
                with col2:
                    if len(features) > 2:
                        st.markdown(f"• {features[2]}")
                    if len(features) > 3:
                        st.markdown(f"• {features[3]}")
            
            # Display chunk size and overlap information
            if "chunk_size" in selected_agent_data and "chunk_overlap" in selected_agent_data:
                st.markdown(f"**📊 Configuration:** Chunk Size: {selected_agent_data['chunk_size']} Chunk Overlap: {selected_agent_data['chunk_overlap']}")
        
        else:
            selected_agent = st.selectbox(
                "Choose RAG Agent:",
                options=["standard", "advanced", "conservative"],
                index=1
            )
        
        st.divider()
        
        # Features section moved to sidebar
        st.header("⚡ Features")
        
        st.markdown("""
        **⚡ SolvIQ** - Your AI-powered Solution Engineering assistant
        
        **🎯 What SolvIQ Does:**
        - 🔧 **Smart Search**: Finds relevant technical docs and web information instantly
        - 🤖 **AI Responses**: Generates comprehensive RFP answers using GPT-4o-mini
        - 📊 **Quality Metrics**: Measures response accuracy with RAGAS framework
        - 🎯 **Multiple Agents**: Choose from Standard, Advanced, or Conservative approaches
        
        **🚀 Perfect For:**
        - Writing technical proposals and RFP responses
        - Researching compliance and security requirements
        - Creating customer-facing documentation
        - Architecture and deployment planning
        
        **🔧 Powered By:**
        - OpenAI GPT-4o-mini for intelligent responses
        - FAISS vector search for document retrieval
        - Tavily API for real-time web information
        - FastAPI backend with Streamlit interface
        """)
    
    # Sample RFP Questions as horizontal titles - Solution Engineer focused (6 questions in 2 rows)
    st.subheader("💡 Sample Questions")
    sample_questions = [
        "What encryption standards does the platform support for enterprise clients?",
        "What compliance standards (SOC2, ISO27001, GDPR) does the platform meet?",
        "What authentication methods and SSO integrations are supported?",
        "How does the platform scale to handle enterprise-level workloads?",
        "What deployment options are available for on-premise and cloud environments?",
        "How does the platform ensure data privacy and regulatory compliance?"
    ]
    
    # Create horizontal layout for sample questions with full text visible (3 columns, 2 rows)
    cols = st.columns(3)  # 3 columns for 2 rows (6 questions total)
    for i, question in enumerate(sample_questions):
        with cols[i % 3]:  # Distribute across 3 columns
            # Use markdown to apply custom styling to buttons
            st.markdown(f"""
            <style>
            .stButton > button[key="sample_{i}"] {{
                background: linear-gradient(135deg, rgba(10, 132, 255, 0.1), rgba(255, 214, 10, 0.1)) !important;
                border: 2px solid rgba(10, 132, 255, 0.2) !important;
                color: var(--text-dark) !important;
                border-radius: 12px !important;
                padding: 0.75rem 1rem !important;
                margin: 0.25rem 0 !important;
                font-size: 16px !important;
                font-weight: 500 !important;
                text-align: left !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 2px 8px rgba(10, 132, 255, 0.1) !important;
                height: auto !important;
                min-height: 60px !important;
                white-space: normal !important;
                word-wrap: break-word !important;
                line-height: 1.4 !important;
            }}
            .stButton > button[key="sample_{i}"]:hover {{
                background: linear-gradient(135deg, rgba(10, 132, 255, 0.2), rgba(255, 214, 10, 0.2)) !important;
                border-color: rgba(10, 132, 255, 0.4) !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 15px rgba(10, 132, 255, 0.2) !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            
            if st.button(question, key=f"sample_{i}"):
                st.session_state.sample_question = question
    
    st.divider()
    
    # Main Content Area - Full width since Features moved to sidebar
    col1 = st.container()
    
    with col1:
        st.header("🤖 Drop your Q")
        
        # Question input
        question = st.text_area(
            "",
            value=st.session_state.get("sample_question", ""),
            height=120,
            placeholder="e.g., What security measures does the platform implement?\nHow does the system handle high availability?\nWhat are the integration capabilities?\nHow does this solution scale with our enterprise needs?"
        )
        
        # Submit button
        if st.button("✨ Work your magic", type="primary", disabled=not question.strip()):
            if question.strip():
                with st.spinner("🤖 Thinking..."):
                    start_time = time.time()
                    result = query_rag(question, selected_agent)
                    end_time = time.time()
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    # Display results
                    st.success("✅ Answer Generated!")
                    
                    # Answer
                    st.subheader("💬 Answer")
                    st.markdown(result["answer"])
                    
                    # Metrics in main area
                    st.subheader("📊 Response Metrics")
                    
                    col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
                    with col_metrics1:
                        st.metric("Response Time", f"{result['response_time']:.2f}s")
                    with col_metrics2:
                        st.metric("Agent Type", result["agent_type"].title())
                    with col_metrics3:
                        st.metric("Sources Used", len(result["sources"]))
                    with col_metrics4:
                        st.metric("Model", result["model"])
                    
                    # Sources
                    st.subheader("📚 Sources")
                    for i, source in enumerate(result["sources"], 1):
                        st.markdown(f"{i}. `{source.split('/')[-1]}`")
                    
                    # Performance details
                    st.subheader("⚡ Performance Details")
                    api_time = end_time - start_time
                    col_perf1, col_perf2, col_perf3 = st.columns(3)
                    with col_perf1:
                        st.metric("Total Time", f"{api_time:.2f}s")
                    with col_perf2:
                        st.metric("API Time", f"{result['response_time']:.2f}s")
                    with col_perf3:
                        st.metric("Overhead", f"{api_time - result['response_time']:.2f}s")
                    
            else:
                st.warning("Please enter a question.")
    

# Footer
def footer():
    st.markdown("""
    <div class="solviq-footer">
        <p style="color: #333; margin: 0; font-size: 0.7rem; font-family: 'Inter', sans-serif; font-weight: 500;">Built with Streamlit & FastAPI | Powered by OpenAI & RAGAS</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    footer()
