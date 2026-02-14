import streamlit as st
import os
import base64
from PIL import Image
from ui.localization import TRANSLATIONS

def premium_card(title: str, value: str, subtext: str, glow_class: str = "glow-blue"):
    """Render a premium styled card."""
    st.markdown(f"""
    <div class="premium-card">
        <h3 style='font-size: 0.8rem; color: #8B949E; margin-bottom: 0.5rem;'>{title}</h3>
        <div class="metric-value">{value}</div>
        <div class="{glow_class}" style='font-size: 0.9rem; margin-top: 0.5rem;'>{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

def kitsune_sidebar_header(lang: str = "en"):
    """Render the sidebar header with glass effect."""
    text = TRANSLATIONS[lang]["kitsune_sidebar_text"]
    st.markdown(f"""
    <div class="glass-panel" style='margin-bottom: 2rem;'>
        <h2 style='font-size: 1.2rem; margin-top: 0;'>Kitsune Intelligence</h2>
        <p style='font-size: 0.85rem; color: #8B949E; line-height: 1.4;'>
            {text}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_mascot(size: int = 150):
    """Render the Kitsune mascot as an image with glow."""
    logo_path = "logokitsunelabpng.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        st.markdown(f"""
        <div class="kitsune-mascot" style='text-align: center;'>
            <img src='data:image/png;base64,{encoded}' 
                 alt='Kitsune Logo' 
                 style='width: {size}px; border-radius: 12px; box-shadow: 0 0 20px rgba(88, 166, 255, 0.3);'/>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; font-size:2rem;'>🦊</div>", unsafe_allow_html=True)

def render_header(t):
    """Render a premium horizontal navigation header."""
    logo_path = "logokitsunelabpng.png"
    encoded = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; 
                padding: 1rem 2rem; background: rgba(22, 27, 34, 0.8); 
                backdrop-filter: blur(10px); border-bottom: 1px solid #30363D; 
                position: sticky; top: 0; z-index: 1000; margin-bottom: 2rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <img src='data:image/png;base64,{encoded}' style='width: 40px; border-radius: 4px;'/>
            <h2 style='margin: 0; font-size: 1.2rem; font-family: "Inter", sans-serif; color: #58A6FF;'>KITSUNE FINANCE</h2>
        </div>
        <div id="nav-container" style='display: flex; gap: 2rem;'>
            <!-- Navigation will be handled by Streamlit tabs or buttons below -->
        </div>
    </div>
    """, unsafe_allow_html=True)

def asset_header(ticker: str, price: float, change: float):
    """Render a header for a specific asset analysis."""
    try:
        val = float(change)
    except:
        val = 0.0
    color = "#7EE787" if val >= 0 else "#FF7B72"
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 2rem;'>
        <h1 style='margin:0;'>{ticker}</h1>
        <div style='text-align: right;'>
            <div style='font-size: 2rem; font-weight: 800;'>${float(price):,.2f}</div>
            <div style='color: {color}; font-weight: 600;'>{"+" if val >= 0 else ""}{val:.2f}% (24h)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_agent_message(role: str, content: str, screenshot: str = None):
    """Render a specialized message bubble for either user or agent."""
    if role == "user":
        st.markdown(f"""
        <div class="user-bubble">
            <div style='font-size: 0.7rem; color: #8B949E; margin-bottom: 0.4rem; font-weight: 500;'>👤 YOU</div>
            <div style='line-height: 1.5;'>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Agent / Kitsune bubble
        mascot_path = "ui/assets/mascot.png"
        encoded_mascot = ""
        if os.path.exists(mascot_path):
            with open(mascot_path, "rb") as f:
                encoded_mascot = base64.b64encode(f.read()).decode()
        
        avatar_html = f"<img src='data:image/png;base64,{encoded_mascot}' style='width: 22px; height: 22px; border-radius: 50%; border: 1px solid #30363D;'/>" if encoded_mascot else "🦊"
        
        st.markdown(f"""
        <div class="kitsune-bubble">
            <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 0.6rem;'>
                {avatar_html}
                <span style='font-size: 0.7rem; color: #58A6FF; font-weight: 600; letter-spacing: 0.5px;'>KITSUNE</span>
            </div>
            <div style='line-height: 1.6; font-size: 0.95rem;'>{content}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if screenshot and os.path.exists(screenshot):
            with open(screenshot, "rb") as f:
                encoded_shot = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style='margin-top: 0.8rem; border-radius: 10px; overflow: hidden; border: 1px solid #30363D; box-shadow: 0 4px 12px rgba(0,0,0,0.4);'>
                <img src='data:image/png;base64,{encoded_shot}' style='width: 100%; display: block;'/>
                <div style='font-size: 0.65rem; color: #8B949E; padding: 0.5rem 0.8rem; background: #161B22; border-top: 1px solid #30363D;'>🔍 Live Crawler View: {os.path.basename(screenshot)}</div>
            </div>
            """, unsafe_allow_html=True)

def render_agent_sandbox(logs: list, current_screenshot: str = None, title: str = "Agent Sandbox"):
    """Render a dedicated sandbox area that looks like a real browser interface."""
    # Extract current URL from logs if possible
    current_url = "https://www.google.com"
    for log in reversed(logs):
        if "action" in log.get("type", "").lower() and "visit" in log.get("content", "").lower():
            import re
            url_match = re.search(r"url':\s*'([^']+)'", log.get("content", ""))
            if url_match:
                current_url = url_match.group(1)
                break

    # Build screenshot HTML
    screenshot_html = ""
    if current_screenshot and os.path.exists(current_screenshot):
        with open(current_screenshot, "rb") as f:
            encoded_shot = base64.b64encode(f.read()).decode()
        screenshot_html = f"""
        <div class="screenshot-wrapper">
            <img src='data:image/png;base64,{encoded_shot}'/>
        </div>
        """

    # Build logs HTML
    logs_html = ""
    if logs:
        logs_html = "<div class='trace-header'>Intelligence Trace</div>"
        for log in logs:
            ltype = log.get("type", "thought").upper()
            color = "#58A6FF" if ltype == "THOUGHT" else "#7EE787" if ltype == "ACTION" else "#8B949E"
            bg = "rgba(88, 166, 255, 0.03)" if ltype == "THOUGHT" else "rgba(126, 231, 135, 0.03)" if ltype == "ACTION" else "rgba(48, 54, 61, 0.05)"
            content = log.get('content', '').replace('<', '&lt;').replace('>', '&gt;')
            logs_html += f"""
            <div class="log-entry" style="background: {bg}; border-left: 2px solid {color};">
                <div class="log-type" style="color: {color};">{ltype}</div>
                <div class="log-content">{content}</div>
            </div>
            """
    
    # Idle state content
    idle_html = ""
    if not logs and not current_screenshot:
        idle_html = "<div class='idle-message'>Initializing Kitsune Browser Environment...</div>"

    # Build the complete sandbox HTML (self-contained)
    sandbox_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: transparent; }}
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
        100% {{ opacity: 1; }}
    }}
    .sandbox-container {{
        border: 1px solid #30363D;
        border-radius: 12px;
        background: #0D1117;
        display: flex;
        flex-direction: column;
        height: 600px;
        overflow: hidden;
    }}
    .browser-header {{
        background: #161B22;
        padding: 10px;
        border-bottom: 1px solid #30363D;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .traffic-lights {{ display: flex; gap: 6px; }}
    .traffic-light {{ width: 10px; height: 10px; border-radius: 50%; }}
    .nav-buttons {{ display: flex; gap: 10px; color: #8B949E; font-size: 0.8rem; }}
    .address-bar {{
        flex-grow: 1;
        background: #0D1117;
        border: 1px solid #30363D;
        border-radius: 6px;
        padding: 4px 12px;
        color: #C9D1D9;
        font-size: 0.75rem;
        font-family: monospace;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }}
    .live-indicator {{ display: flex; align-items: center; gap: 6px; }}
    .live-dot {{ width: 6px; height: 6px; border-radius: 50%; background: #F85149; animation: pulse 1.5s infinite; }}
    
    .viewport {{
        background: #010409;
        flex-grow: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        min-height: 0;
    }}
    
    .screenshot-wrapper {{
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .screenshot-wrapper img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        display: block;
    }}
    
    .console-panel {{
        height: 200px;
        background: #0D1117;
        border-top: 1px solid #30363D;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
    }}

    .placeholder {{
        color: #30363D;
        font-size: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }}
    .idle-message {{ color: #8B949E; font-style: italic; text-align: center; margin-top: 4rem; }}
    .trace-header {{ margin-bottom: 0.8rem; font-size: 0.7rem; color: #8B949E; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
    .log-entry {{ padding: 0.6rem 0.8rem; margin-bottom: 0.6rem; border-radius: 0 4px 4px 0; }}
    .log-type {{ font-size: 0.55rem; font-weight: 800; margin-bottom: 0.2rem; }}
    .log-content {{ font-size: 0.8rem; color: #C9D1D9; line-height: 1.4; }}
    </style>
    </head>
    <body>
    <div class="sandbox-container">
        <div class="browser-header">
            <div class="traffic-lights">
                <div class="traffic-light" style="background: #FF5F56;"></div>
                <div class="traffic-light" style="background: #FFBD2E;"></div>
                <div class="traffic-light" style="background: #27C93F;"></div>
            </div>
            <div class="nav-buttons"><span>◀</span> <span>▶</span> <span>↻</span></div>
            <div class="address-bar">
                <span style="color: #7EE787;">https://</span>{current_url.replace("https://", "").replace("http://", "")}
            </div>
            <div class="live-indicator">
                <div class="live-dot"></div>
                <span style="font-size: 0.6rem; color: #F85149; font-weight: 800; letter-spacing: 1px;">LIVE</span>
            </div>
        </div>
        <div class="content-area">
            <div class="viewport">
                {screenshot_html if screenshot_html else '<div class="placeholder"><span>🕸️</span><span style="font-size:0.8rem;">Ready to Browse</span></div>'}
            </div>
            
            <div class="console-panel">
                <div class="logs-scroll">
                    {logs_html if logs else '<div class="trace-header">Waiting for Signal...</div>'}
                </div>
            </div>
        </div>
    </div>
    <script>
        // Auto scroll logs
        const el = document.querySelector('.logs-scroll');
        if(el) el.scrollTop = el.scrollHeight;
    </script>
    </body>
    </html>
    """
    
    import streamlit.components.v1 as components
    components.html(sandbox_html, height=600, scrolling=False)

def macro_insight_banner(message: str):
    """Render a top-level awareness banner."""
    st.markdown(f"""
    <div style='background: rgba(26, 115, 232, 0.05); 
                border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 1rem; margin-bottom: 2rem; 
                display: flex; align-items: center; border-left: 4px solid #58A6FF;'>
        <span style='color: #E8EAED; font-size: 0.95rem;'>{message}</span>
    </div>
    """, unsafe_allow_html=True)
