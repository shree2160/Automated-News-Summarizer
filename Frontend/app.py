import streamlit as st
import time

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
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=600&auto=format&fit=crop", use_container_width=True)
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
            time.sleep(2.0) 
            
            mock_article_title = "The Quantum Sovereign: How AI-Driven Central Banking is Redefining Global Economies"
            if output_format == "Bullet Points":
                mock_summary = """
                <ul>
                    <li><b>Algorithmic Dominance:</b> Autonomous trading systems now account for 85% of global market volume, leading to unprecedented volatility and rapid correction cycles.</li>
                    <li><b>CBDC Integration:</b> Over 60 central banks are currently testing AI-governed digital currencies to automate fiscal policy and inflation control.</li>
                    <li><b>Predictive Governance:</b> AI models are now beating human economists in projecting quarterly GDP growth by a margin of 15% through data mining.</li>
                    <li><b>Systemic Risk:</b> The reliance on black-box algorithms creates a 'correlation trap', where simultaneous liquidations could trigger a flash crash.</li>
                </ul>
                """
            else:
                 mock_summary = "The Quantum Sovereign represents a new era in central banking, where AI-driven algorithms dictate global economic policy with robotic precision. While these systems offer unparalleled efficiency in inflation control and GDP projection, they introduce systemic risks that human regulators are struggling to understand. The transition to AI-governed digital currencies is already underway in 60 countries, signaling the end of traditional fiscal governance as we know it."
                 
            mock_sentiment = "Neutral"
            mock_confidence = 96.2
            
            st.session_state.history.append({
                "title": mock_article_title,
                "summary": mock_summary,
                "sentiment": mock_sentiment,
                "confidence": mock_confidence,
                "time": time.strftime("%H:%M:%S")
            })
            
        st.success("✅ INTELLIGENCE REPORT READY")
        
        st.markdown('<div class="animated-section">', unsafe_allow_html=True)
        st.markdown("---")
        st.write(f"### 📄 {mock_article_title}")
        
        met1, met2, met3 = st.columns(3)
        with met1:
            emoji = "😊" if mock_sentiment == "Positive" else "😐" if mock_sentiment == "Neutral" else "😟"
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #94A3B8; margin-top: 0; font-size: 0.9rem; letter-spacing: 2px;">SENTIMENT</h4>
                <span style="font-size: 1.8rem; font-weight: 700; color: #A855F7;">{emoji} {mock_sentiment}</span>
            </div>
            """, unsafe_allow_html=True)
        with met2:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #94A3B8; margin-top: 0; font-size: 0.9rem; letter-spacing: 2px;">AI CONFIDENCE</h4>
                <span style="font-size: 1.8rem; color: #60A5FA; font-weight: 700;">{mock_confidence}%</span>
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
        st.markdown(f'<div class="summary-box" style="background: rgba(15, 23, 42, 0.8); border-left: 6px solid #A855F7; padding: 30px; border-radius: 12px; margin-top: 20px;">{mock_summary}</div>', unsafe_allow_html=True)
        
        st.write("")
        st.download_button(
            label="📥 Download Insight Memo",
            data=mock_summary.strip(),
            file_name="intelligence_report.txt",
            mime="text/plain"
        )
        st.markdown('</div>', unsafe_allow_html=True)
