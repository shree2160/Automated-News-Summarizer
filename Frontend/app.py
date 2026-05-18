import streamlit as st
import time
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Automated News Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- INITIALIZE SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'summary_length' not in st.session_state:
    st.session_state.summary_length = "Medium"# --- CUSTOM CSS (Sleek Dark Mode & Headline Aesthetics) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Premium Dark Theme Base */
    .stApp {
        background: radial-gradient(circle at top right, #1a0f30 0%, #06060c 60%, #020205 100%);
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Force white text color for all text, paragraphs, labels, and markdowns (except main header) */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp div {
        color: #FFFFFF !important;
    }
    
    /* Exceptions: Keep specific visual colors for key metrics and gradient accents */
    .stApp h1[style*="background: linear-gradient"],
    .stApp h1[style*="background: linear-gradient"] * {
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* Keep metric highlights vibrant colors */
    .metric-card span {
        background: none !important;
        -webkit-text-fill-color: initial !important;
    }
    
    /* History card time badge */
    .history-card small {
        color: #A78BFA !important;
    }
    
    /* Hide Streamlit default decorations */
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    header {
        visibility: hidden !important;
        height: 0 !important;
    }
    footer {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 15px rgba(168, 85, 247, 0.2); }
        50% { box-shadow: 0 0 25px rgba(168, 85, 247, 0.4); }
        100% { box-shadow: 0 0 15px rgba(168, 85, 247, 0.2); }
    }
    @keyframes textGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .animated-section {
        animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* MASSIVE CENTERED HEADLINE */
    .header-container {
        text-align: center;
        padding: 4rem 1rem 2.5rem;
        position: relative;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50px; left: 50%;
        transform: translateX(-50%);
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
        z-index: 0;
        pointer-events: none;
    }
    
    .main-header {
        font-family: 'Outfit', sans-serif;
        font-size: 4.8rem;
        text-transform: uppercase;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #C084FC 30%, #6366F1 70%, #3B82F6 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textGradient 6s ease infinite;
        margin-bottom: 0.75rem;
        line-height: 1.1;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    
    .sub-header {
        font-size: 1.25rem;
        color: #94A3B8;
        font-weight: 400;
        max-width: 650px;
        margin: 0 auto;
        line-height: 1.6;
        letter-spacing: 0.2px;
        position: relative;
        z-index: 1;
    }
    
    /* Cards & Containers - Glassmorphism */
    .metric-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.6);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(168, 85, 247, 0.3);
        background: rgba(20, 24, 48, 0.6);
        box-shadow: 0 20px 40px -15px rgba(139, 92, 246, 0.25);
    }
    
    /* Summary Box */
    .summary-box {
        background: rgba(15, 23, 42, 0.5) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-left: 5px solid #8B5CF6 !important;
        padding: 30px !important;
        border-radius: 18px !important;
        margin-top: 15px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.4);
        font-size: 1.1rem;
        line-height: 1.85;
        color: #F8FAFC;
    }
    
    .summary-box ul {
        list-style: none;
        padding-left: 0;
        margin: 0;
    }
    .summary-box li {
        position: relative;
        padding-left: 2rem;
        margin-bottom: 14px;
    }
    .summary-box li::before {
        content: "✨";
        position: absolute;
        left: 0;
        font-size: 1.15rem;
        top: 2px;
        filter: drop-shadow(0 0 5px rgba(168, 85, 247, 0.5));
    }
    
    /* Streamlit Input Enhancements */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.25) !important;
    }
    div[data-baseweb="input"] input {
        color: white !important;
        font-size: 1.1rem !important;
        padding: 0.9rem !important;
    }
    
    /* Streamlit Button Enhancements */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8B5CF6 0%, #4F46E5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.7rem 1.6rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, #a78bfa 0%, #6366f1 100%) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        padding: 0.7rem 1.6rem !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
        color: white !important;
    }
    
    /* Sidebar Improvements */
    [data-testid="stSidebar"] {
        background-color: rgba(6, 6, 12, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-family: 'Outfit', sans-serif;
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        margin-top: 1rem !important;
    }
    
    /* Disable Image Maximize Button in Sidebar */
    [data-testid="stSidebar"] button[aria-label="Fullscreen"],
    [data-testid="stSidebar"] [data-testid="stImage"] button,
    [data-testid="stSidebar"] button[title="View fullscreen"] {
        display: none !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        margin-bottom: 10px !important;
    }
    
    /* Target the container of stCheckbox */
    div[data-testid="stCheckbox"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stCheckbox"]:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Keep the default layout structure of label */
    div[data-testid="stCheckbox"] label {
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Format the label text and add margin-left to prevent overlap */
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] label span:last-child {
        color: #FFFFFF !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        line-height: 1.2 !important;
        white-space: nowrap !important; /* Prevent text wrapping! */
    }
    
    /* Ensure the wrapper text container has a solid offset and does not overlap */
    div[data-testid="stCheckbox"] label > div:last-child {
        padding: 0 !important;
        margin: 0 !important;
        margin-left: 18px !important; /* Large spacing to separate from switch toggle! */
    }
    
    /* Target the parent span (child 1 of label) and turn it into the sliding track */
    div[data-testid="stCheckbox"] label > span:first-child,
    div[data-testid="stCheckbox"] label > div:first-child {
        width: 36px !important;
        height: 18px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 100px !important;
        position: relative !important;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
        flex-shrink: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
    }
    
    /* Completely hide default checkboxes, checkmark symbols, and nested borders */
    div[data-testid="stCheckbox"] label svg {
        display: none !important;
    }
    div[data-testid="stCheckbox"] label > span:first-child *,
    div[data-testid="stCheckbox"] label > div:first-child * {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Create the sliding toggle knob inside the track */
    div[data-testid="stCheckbox"] label > span:first-child::after,
    div[data-testid="stCheckbox"] label > div:first-child::after {
        content: "" !important;
        position: absolute !important;
        top: 2px !important;
        left: 2px !important;
        width: 12px !important;
        height: 12px !important;
        border-radius: 50% !important;
        background-color: #94A3B8 !important;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Active Switch State - Change track color and apply a premium glow */
    div[data-testid="stCheckbox"] label:has(input:checked) > span:first-child,
    div[data-testid="stCheckbox"] label:has(input:checked) > div:first-child {
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.5) !important;
    }
    
    /* Active Switch Knob State - Slide the knob to the right and make it bright white */
    div[data-testid="stCheckbox"] label:has(input:checked) > span:first-child::after,
    div[data-testid="stCheckbox"] label:has(input:checked) > div:first-child::after {
        transform: translateX(16px) !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Styled recent history cards */
    .history-card {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease !important;
    }
    .history-card:hover {
        background: rgba(139, 92, 246, 0.06) !important;
        border-color: rgba(139, 92, 246, 0.25) !important;
        transform: translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("futuristic_news_ai_sidebar.png", width="stretch")
    st.header("⚙️ Settings")
    
    st.markdown('<p style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem; font-family: \'Plus Jakarta Sans\', sans-serif;">Summary Length</p>', unsafe_allow_html=True)
    def update_length(length):
        st.session_state.summary_length = length

    st.checkbox("Short", value=(st.session_state.summary_length == "Short"), on_change=update_length, args=("Short",))
    st.checkbox("Medium", value=(st.session_state.summary_length == "Medium"), on_change=update_length, args=("Medium",))
    st.checkbox("Long", value=(st.session_state.summary_length == "Long"), on_change=update_length, args=("Long",))
    
    st.markdown("---")
    output_format = st.radio("Output Format", options=["Bullet Points", "Paragraph"], index=0)
    
    st.markdown("---")
    st.header("🕰️ Recent History")
    if not st.session_state.history:
        st.info("No summaries generated yet.")
    else:
        for idx, item in enumerate(reversed(st.session_state.history[-5:])):
            st.markdown(f"""
            <div class="history-card">
                <small style="color: #A78BFA; font-weight: 600; letter-spacing: 0.5px;">{item['time']}</small><br>
                <div style="color: #FFFFFF; font-weight: 600; margin-top: 4px; font-size: 0.9rem; line-height: 1.4;">{item['title'][:40]}...</div>
            </div>
            """, unsafe_allow_html=True)

# --- MAIN APP ---
backend_url = "http://127.0.0.1:8000/api/v1/summarize"

st.markdown(f"""
<div style="text-align: center; padding: 4rem 1rem 2.5rem; position: relative;" class="animated-section">
    <div style="content: ''; position: absolute; top: -50px; left: 50%; transform: translateX(-50%); width: 400px; height: 400px; background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%); z-index: 0; pointer-events: none;"></div>
    <h1 style="font-family: 'Outfit', sans-serif; font-size: 3.8rem; text-transform: uppercase; font-weight: 800; background: linear-gradient(135deg, #FFFFFF 0%, #C084FC 30%, #6366F1 70%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.75rem; line-height: 1.1; letter-spacing: -0.5px; position: relative; z-index: 1; text-align: center;">Automated News Summarizer</h1>
    <p style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.25rem; color: #FFFFFF; font-weight: 400; max-width: 650px; margin: 0 auto; line-height: 1.6; letter-spacing: 0.2px; position: relative; z-index: 1; text-align: center;">Distill any news source into actionable intelligence with our next-generation AI engine</p>
</div>
""", unsafe_allow_html=True)

# Input Section
st.markdown('<h3 style="color: #FFFFFF; font-family: \'Outfit\', sans-serif; font-weight: 600; margin-bottom: 0.8rem; font-size: 1.5rem;">📌 Enter Article Details</h3>', unsafe_allow_html=True)
url_input = st.text_input("News Article URL", placeholder="https://example.com/news-article...", label_visibility="collapsed")

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    generate_btn = st.button("🚀 Generate Summary", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    st.session_state.history = []
    st.rerun()

# Processing Section
if generate_btn:
    if not url_input.strip():
        st.error("⚠️ Please enter a valid URL to summarize.")
    elif not url_input.startswith(("http://", "https://")):
        st.error("⚠️ Invalid URL. Must start with http:// or https://")
    else:
        with st.spinner("🔍 ANALYZING RAW DATA STREAM... (This may take up to 60 seconds for long articles)"):
            try:
                # Prepare request payload
                payload = {
                    "url": url_input,
                    "length": st.session_state.summary_length.lower()
                }
                
                # Call Backend API with extended timeout for CPU processing
                response = requests.post(backend_url, json=payload, timeout=120)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract data from backend response
                    article_title = data["metadata"]["title"]
                    sentiment_label = data["sentiment"]["label"]
                    confidence_score = data["sentiment"]["score"] * 100
                    
                    # Formatting logic for Bullet Points vs Paragraph
                    if output_format == "Bullet Points":
                        bullets_html = "<ul>"
                        for bullet in data["summary_bullets"]:
                            # Basic formatting: first few words bold (if possible)
                            parts = bullet.split(": ", 1)
                            if len(parts) > 1:
                                bullets_html += f"<li><b>{parts[0]}:</b> {parts[1]}</li>"
                            else:
                                bullets_html += f"<li>{bullet}</li>"
                        bullets_html += "</ul>"
                        final_summary = bullets_html
                    else:
                        final_summary = data["summary_paragraph"]
                    
                    # Update Session History
                    st.session_state.history.append({
                        "title": article_title,
                        "summary": final_summary,
                        "sentiment": sentiment_label,
                        "confidence": round(confidence_score, 1),
                        "time": time.strftime("%H:%M:%S")
                    })
                    
                    # Use these values for display below
                    display_title = article_title
                    display_summary = final_summary
                    display_sentiment = sentiment_label
                    display_confidence = round(confidence_score, 1)
                    
                else:
                    st.error(f"❌ Backend Error ({response.status_code}): {response.text}")
                    st.stop()
                    
            except Exception as e:
                st.error(f"🔌 Connection Failed: Could not reach the AI Engine at {backend_url}. Make sure the backend is running.")
                st.stop()
            
        st.success("✅ INTELLIGENCE REPORT READY")
        
        st.markdown('<div class="animated-section">', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f'<h3 style="color: #F8FAFC; font-family: \'Outfit\', sans-serif; margin-bottom: 1.2rem; font-weight: 700; font-size: 1.8rem; line-height: 1.3;">📄 {display_title}</h3>', unsafe_allow_html=True)
        
        met1, met2, met3 = st.columns(3)
        with met1:
            emoji = "😊" if display_sentiment == "POSITIVE" else "😐" if display_sentiment == "NEUTRAL" else "😟"
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #94A3B8; margin-top: 0; font-size: 0.9rem; letter-spacing: 2px;">SENTIMENT</h4>
                <span style="font-size: 1.8rem; font-weight: 700; color: #A855F7;">{emoji} {display_sentiment}</span>
            </div>
            """, unsafe_allow_html=True)
        with met2:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #94A3B8; margin-top: 0; font-size: 0.9rem; letter-spacing: 2px;">AI CONFIDENCE</h4>
                <span style="font-size: 1.8rem; color: #60A5FA; font-weight: 700;">{display_confidence}%</span>
            </div>
            """, unsafe_allow_html=True)
        with met3:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #94A3B8; margin-top: 0; font-size: 0.9rem; letter-spacing: 2px;">ENGINE STATUS</h4>
                <span style="font-size: 1.4rem; color: #EC4899; font-weight: 700;">HYPERCORE v3.0</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<h3 style="color: #F8FAFC; font-family: \'Outfit\', sans-serif; margin-bottom: 1.2rem; margin-top: 2.5rem; font-weight: 700; font-size: 1.8rem;">📝 Extracted Summary</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-box">{display_summary}</div>', unsafe_allow_html=True)
        
        st.write("")
        st.download_button(
            label="📥 Download Insight Memo",
            data=display_summary.strip(),
            file_name="intelligence_report.txt",
            mime="text/plain"
        )
        st.markdown('</div>', unsafe_allow_html=True)
