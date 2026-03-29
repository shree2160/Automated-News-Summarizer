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
    st.session_state.summary_length = "Medium"

# --- CUSTOM CSS (Sleek Dark Mode & Headline Aesthetics) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;700;900&display=swap');

    /* Dark Theme Base */
    .stApp {
        background-color: #000000;
        color: #E2E8F0;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated-section {
        animation: fadeIn 1s ease-out;
    }
    
    /* MASSIVE CENTERED HEADLINE */
    .header-container {
        text-align: center;
        padding: 4rem 1rem;
        background: radial-gradient(circle at center, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
    }
    
    .main-header {
        font-size: 8rem; /* Ultra Massive Scale */
        text-transform: uppercase;
        font-weight: 900;
        background: linear-gradient(90deg, #60A5FA, #A855F7, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.1;
        letter-spacing: 2px; /* Fixed visibility */
        filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.4));
    }
    
    .sub-header {
        font-size: 1.1rem; /* Reduced size */
        color: #94A3B8;
        font-weight: 400;
        max-width: 850px;
        margin: 0 auto;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Custom Bullets */
    .summary-box ul {
        list-style: none;
        padding-left: 0;
    }
    .summary-box li {
        position: relative;
        padding-left: 2.5rem;
        margin-bottom: 20px;
        color: #E2E8F0;
        font-size: 1.15rem;
    }
    .summary-box li::before {
        content: "⬥";
        position: absolute;
        left: 0;
        color: #A855F7;
        font-size: 1.8rem;
        top: -4px;
        text-shadow: 0 0 15px rgba(168, 85, 247, 0.8);
    }
    
    /* Cards & Containers */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-8px);
        border-color: rgba(139, 92, 246, 0.4);
    }

    /* Disable Image Maximize Button in Sidebar */
    [data-testid="stSidebar"] [data-testid="stImage"] button,
    [data-testid="stSidebar"] button[title="View fullscreen"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("Frontend/futuristic_news_ai_sidebar.png", use_container_width=True)
    st.header("⚙️ Settings")
    
    st.write("**Summary Length**")
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
            <div style="background: rgba(45, 55, 72, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.05);">
                <small style="color: #94A3B8;">{item['time']}</small><br>
                <strong style="color: #E2E8F0;">{item['title'][:40]}...</strong>
            </div>
            """, unsafe_allow_html=True)

# --- MAIN APP ---
backend_url = "http://localhost:8000/api/v1/summarize"

st.markdown(f"""
<div class="header-container">
    <p class="main-header">Automated News Summarizer</p>
    <p class="sub-header">DISTILL ANY NEWS SOURCE INTO PURE INTELLIGENCE WITH OUR NEXT-GEN AI ENGINE</p>
</div>
""", unsafe_allow_html=True)

# Input Section
st.write("### 📌 Enter Article Details")
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
        with st.spinner("🔍 ANALYZING RAW DATA STREAM..."):
            try:
                # Prepare request payload
                payload = {
                    "url": url_input,
                    "length": st.session_state.summary_length.lower()
                }
                
                # Call Backend API
                response = requests.post(backend_url, json=payload, timeout=30)
                
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
        st.write(f"### 📄 {display_title}")
        
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
            
        st.write("### 📝 Extracted Summary")
        st.markdown(f'<div class="summary-box" style="background: rgba(15, 23, 42, 0.8); border-left: 6px solid #A855F7; padding: 30px; border-radius: 12px; margin-top: 20px;">{display_summary}</div>', unsafe_allow_html=True)
        
        st.write("")
        st.download_button(
            label="📥 Download Insight Memo",
            data=display_summary.strip(),
            file_name="intelligence_report.txt",
            mime="text/plain"
        )
        st.markdown('</div>', unsafe_allow_html=True)
