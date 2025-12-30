
import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Kitsune Finance | Kitsune Labs",
    page_icon="logokitsunelabpng.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import os
import threading
import time
import json
import re
import base64

from engine.data_provider import DataProvider
from ui.components import premium_card, kitsune_sidebar_header, asset_header, macro_insight_banner, render_mascot, render_header, render_agent_message, render_agent_sandbox
from ui.localization import TRANSLATIONS
from engine.analytics import AnalyticsEngine
from engine.kitsune import KitsuneAI
from engine.report_generator import ReportGenerator
from engine.agent import AgentEngine

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
    
    :root {
        --md-background: #0D1117;
        --md-surface: #161B22;
        --md-surface-variant: #21262D;
        --md-primary: #58A6FF;
        --md-success: #7EE787;
        --md-error: #FF7B72;
        --md-text-primary: #C9D1D9;
        --md-text-secondary: #8B949E;
        --md-border: #30363D;
    }

    .stApp {
        background-color: var(--md-background);
        color: var(--md-text-primary);
        font-family: 'Roboto', sans-serif;
    }

    .premium-card {
        background-color: var(--md-surface);
        border: 1px solid var(--md-border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    .glass-panel {
        background: rgba(33, 38, 45, 0.7);
        backdrop-filter: blur(8px);
        border: 1px solid var(--md-border);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--md-primary);
    }

    /* Terminal Chat Styling */
    .chat-container {
        height: 600px;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(13, 17, 23, 0.4);
        border: 1px solid var(--md-border);
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .user-bubble {
        background: rgba(33, 38, 45, 0.8);
        border: 1px solid #30363D;
        padding: 1rem;
        border-radius: 12px 12px 0 12px;
        margin-bottom: 1rem;
        margin-left: 20%;
        color: #C9D1D9;
    }
    
    .kitsune-bubble {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.1), rgba(0, 0, 0, 0));
        border-left: 3px solid var(--md-primary);
        padding: 1rem;
        border-radius: 0 12px 12px 12px;
        margin-bottom: 1rem;
        margin-right: 20%;
        color: #C9D1D9;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }

    .glow-green { color: var(--md-success); }
    .glow-blue { color: var(--md-primary); }
    .glow-red { color: var(--md-error); }
    
    /* Smooth Scroll */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #30363D; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #58A6FF; }

    @keyframes pulse-athene {
        0% { filter: drop-shadow(0 0 2px rgba(88, 166, 255, 0.4)); }
        50% { filter: drop-shadow(0 0 10px rgba(88, 166, 255, 0.8)); }
        100% { filter: drop-shadow(0 0 2px rgba(88, 166, 255, 0.4)); }
    }
    .athene-icon { animation: pulse-athene 2s infinite; }
</style>
""", unsafe_allow_html=True)

def get_engines():
    if 'provider' not in st.session_state:
        st.session_state.provider = DataProvider()
    if 'analytics' not in st.session_state:
        st.session_state.analytics = AnalyticsEngine()
    if 'sensei' not in st.session_state:
        st.session_state.sensei = KitsuneAI()
    return st.session_state.provider, st.session_state.analytics, st.session_state.sensei

def render_report_hub(t, provider, kitsune, analytics, all_tickers):
    st.title(t['report_hub'])
    st.markdown(f"> {t['report_outlook']}")
    
    col_left, col_right = st.columns([1, 2], gap="large")
    selected_basket_data = []
    
    with col_left:
        st.markdown(f"#### {t['active_selection']}")
        assets = st.multiselect("Add Assets to Brief", 
                                all_tickers,
                                default=["BTC/USDT", "ETH/USDT"] if "BTC/USDT" in all_tickers else [])
        st.divider()
        generate_clicked = st.button(t["generate_report"], use_container_width=True, type="primary")
    
    with col_right:
        st.markdown(f"#### {t['basket_intel']}")
        if not assets:
            st.info("Institutional data will appear here once assets are selected.")
        else:
            # We show a limited grid for the report hub preview
            cols_icons = st.columns(3)
            for i, ticker in enumerate(assets):
                data = provider.fetch_crypto_data(ticker, timeframe='1d', limit=2)
                if not data.empty:
                    close_col = 'close' if 'close' in data.columns else 'Close'
                    price = data[close_col].iloc[-1]
                    change = 0.0
                    if len(data) > 1:
                        prev_price = data[close_col].iloc[-2]
                        change = ((price - prev_price) / prev_price) * 100
                    
                    news = provider.fetch_news(ticker)
                    sentiment = sensei.analyze_sentiment(news)
                    metrics = analytics.calculate_metrics(data)
                    neural_info = analytics.neural_core.predict_price_trend(data)
                    
                    selected_basket_data.append({
                        "ticker": ticker,
                        "price": price,
                        "sentiment": sentiment['label'],
                        "rsi": metrics.get('rsi', 50),
                        "vol": metrics.get('volatility', 0),
                        "neural_target": neural_info.get('target_price', 0) if neural_info['status'] == 'Success' else 0,
                        "neural_conf": neural_info.get('confidence', 0) if neural_info['status'] == 'Success' else 0
                    })
                    
                    with cols_icons[i % 3]:
                        color = "var(--md-success)" if change >= 0 else "var(--md-error)"
                        st.markdown(f"""
                        <div class="glass-panel" style='text-align: center; border-top: 2px solid {color};'>
                            <div style='font-size: 0.8rem; color: var(--md-text-secondary);'>{ticker}</div>
                            <div style='font-weight: 700;'>${price:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)

    if generate_clicked and selected_basket_data:
        with st.spinner("Synthesizing institutional data..."):
            generator = ReportGenerator(kitsune)
            report = generator.generate_weekly_report(selected_basket_data, lang=st.session_state.get('lang', 'it'))
            st.markdown("### Strategic Synthesis")
            st.markdown(report)

def render_archive(t):
    st.title(t.get('archive_title', 'Archive'))
    base_dir = "reports"
    if not os.path.exists(base_dir): os.makedirs(base_dir)
    files = [f for f in os.listdir(base_dir) if f.endswith(('.md', '.txt'))]
    if not files:
        st.info("Archive is empty.")
        return
    selected_file = st.selectbox("Select Report", files)
    if selected_file:
        with open(os.path.join(base_dir, selected_file), "r", encoding="utf-8") as f:
            st.markdown(f.read())

def run_background_shadows(model_name, kitsune):
    """Background thread to run competitive analysis without blocking UI."""
    try:
        agent = AgentEngine(model_name=model_name)
        
        # 1. Alpha Hunter Analysis
        alpha_report = agent.run_alpha_benchmark()
        kitsune.update_relational_memory(f"ALPHA HUNTER LOG:\n{alpha_report}")
        
        # 2. UI Architect Analysis
        ui_report = agent.run_ui_benchmark()
        kitsune.update_relational_memory(f"UI ARCHITECT LOG:\n{ui_report}")
        
        # 3. Kitsune Oracle (Deep $ATH Research)
        oracle_report = agent.run_oracle_research()
        kitsune.update_relational_memory(f"KITSUNE ORACLE LOG:\n{oracle_report}")
        
    except Exception as e:
        print(f"Shadow Agent Thread Error: {e}")

def render_kitsune_terminal(t, kitsune, lang):
    # Main Layout Split (Balanced 1:1 for better visibility)
    col_chat, col_sandbox = st.columns([1, 1], gap="medium")
    
    with col_chat:
        # Mode Selector
        mode = st.radio("UI_MODE", [t["chat_mode_standard"], t["chat_mode_agent"]], 
                        horizontal=True, label_visibility="collapsed", key="terminal_mode_toggle")
        is_agent_mode = (mode == t["chat_mode_agent"])
        
        st.markdown("<h4 style='margin:0; color:#58A6FF;'>KITSUNE INTERFACE <span style='font-size:0.6rem; color:#8B949E;'>v5.0 PERSISTENT</span></h4>", unsafe_allow_html=True)
        
        # Chat History Container
        chat_placeholder = st.empty()
        with chat_placeholder.container():
            if "messages" not in st.session_state: st.session_state.messages = []
            for m in st.session_state.messages:
                render_agent_message(m["role"], m["content"], m.get("screenshot"))

        # Multimodal Uploads
        uploaded_files = st.file_uploader(t.get("upload_label", "Upload Docs/Images"), 
                                        accept_multiple_files=True, 
                                        type=['png', 'jpg', 'jpeg', 'pdf', 'docx', 'txt'],
                                        label_visibility="collapsed",
                                        key=f"uploader_{st.session_state.get('app_nav_radio', 'dash')}")
        
        icon = "🤖" if is_agent_mode else "🧠"
        prompt = st.chat_input(f"{icon} {t['chat_placeholder']}", key=f"terminal_input_{st.session_state.get('app_nav_radio', 'dash')}")
        
        # Quick Commands Chips
        qc1, qc2, qc3 = st.columns(3)
        with qc1: 
            if st.button("🔮 Oracle", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "/oracle"})
                st.rerun()
        with qc2:
            if st.button("🦅 Alpha", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "/alpha"})
                st.rerun()
        with qc3:
            if st.button("🎨 UI", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "/ui"})
                st.rerun()

    with col_sandbox:
        # Sandbox Area (Always Present)
        if "sandbox_logs" not in st.session_state: st.session_state.sandbox_logs = []
        if "sandbox_screenshot" not in st.session_state: st.session_state.sandbox_screenshot = None
        
        # Placeholder for real-time updates during the loop
        sandbox_ui = st.empty()
        with sandbox_ui.container():
            render_agent_sandbox(st.session_state.sandbox_logs, st.session_state.sandbox_screenshot, t["sandbox_title"])

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "files": uploaded_files})
        st.rerun()

    # Process latest message if it's from user
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        latest = st.session_state.messages[-1]
        user_msg = latest["content"]
        
        # Sub-Agent Commands Detection
        if "agent_engine" not in st.session_state:
            st.session_state.agent_engine = AgentEngine(model_name=kitsune.model)
        
        agent_instance = st.session_state.agent_engine
        
        # Reset sandbox for new agent tasks
        if is_agent_mode or user_msg.startswith("/"):
            st.session_state.sandbox_logs = []
            st.session_state.sandbox_screenshot = None

        with st.status("Kitsune Intelligence active...", expanded=True) as status:
            def on_agent_log(msg):
                clean_msg = msg.replace("**Model Output**:", "").replace("**Executing Tool**:", "").replace("**Observation**:", "").strip()
                
                if msg.startswith("RETS_IMG:"):
                    path = msg.replace("RETS_IMG:", "")
                    if os.path.exists(path):
                        st.session_state.sandbox_screenshot = path
                        st.session_state.temp_screenshot = path
                else:
                    thoughts = re.findall(r"Thought:\s*(.*?)(?=Action:|Observation:|Final Answer:|$)", clean_msg, re.DOTALL | re.IGNORECASE)
                    actions = re.findall(r"Action:\s*(.*?)(?=Action Input:|Observation:|Final Answer:|$)", clean_msg, re.DOTALL | re.IGNORECASE)
                    observations = re.findall(r"Observation:\s*(.*?)(?=Thought:|Action:|Final Answer:|$)", clean_msg, re.DOTALL | re.IGNORECASE)
                    
                    if thoughts:
                        for t_text in thoughts:
                            if t_text.strip(): st.session_state.sandbox_logs.append({"type": "thought", "content": t_text.strip()})
                    if actions:
                        for a_text in actions:
                            if a_text.strip(): st.session_state.sandbox_logs.append({"type": "action", "content": a_text.strip()})
                    if observations:
                        for o_text in observations:
                            if o_text.strip(): st.session_state.sandbox_logs.append({"type": "observation", "content": o_text.strip()})
                    
                    if not (thoughts or actions or observations) and clean_msg:
                        st.session_state.sandbox_logs.append({"type": "thought", "content": clean_msg})
                
                # Dynamic update of sandbox placeholder during execution
                with sandbox_ui.container():
                    render_agent_sandbox(st.session_state.sandbox_logs, st.session_state.sandbox_screenshot, t["sandbox_title"])

            if user_msg.lower().startswith("/oracle"):
                resp = agent_instance.run_oracle_research(on_log=on_agent_log)
            elif user_msg.lower().startswith("/alpha"):
                resp = agent_instance.run_alpha_benchmark(on_log=on_agent_log)
            elif user_msg.lower().startswith("/ui"):
                resp = agent_instance.run_ui_benchmark(on_log=on_agent_log)
            elif is_agent_mode:
                resp = agent_instance.run(user_msg, on_log=on_agent_log)
            else:
                resp = kitsune.chat(user_msg, files=latest.get("files"), lang=lang)
        
        shot = st.session_state.get('temp_screenshot')
        st.session_state.messages.append({"role": "assistant", "content": resp, "screenshot": shot})
        if 'temp_screenshot' in st.session_state: del st.session_state.temp_screenshot
        st.rerun()

def render_world_chain_hub(t, provider, kitsune, lang):
    st.title("🛡️ " + t.get('nav_athene', 'World Chain Hub'))
    st.markdown(f"> {t.get('ath_migration_title', 'World Chain Ecosystem Alpha')}")
    
    # Tech Diagnostics (RPC)
    chain_info = provider.get_athene_chain_status()
    st.markdown(f"#### ⛓️ World Chain Tech-Bridge")
    t1, t2, t3 = st.columns(3)
    with t1: st.metric("Network Status", chain_info.get('status', 'N/A'), delta=None if chain_info.get('status') == "Online" else -1)
    with t2: st.metric("Current Block", f"#{chain_info.get('block', 'N/A')}")
    with t3: st.metric("Network Capacity", chain_info.get('tps_est', '---'), help="Expected peak TPS on World Chain")

    col_main, col_oracle, col_chat = st.columns([1.2, 0.8, 1], gap="medium")
    
    with col_main:
        # A. WLD Miner Intelligence Panel
        st.markdown(f"#### 💎 {t.get('wld_miner_title', 'WLD Miner Intelligence')}")
        wld_miner_pool = provider.get_world_chain_assets()["WLD_MINER"]
        wld_miner_data = provider.fetch_dex_price(wld_miner_pool)
        
        w1, w2 = st.columns(2)
        with w1:
            st.markdown(f"""
            <div class="glass-panel" style='border-top: 2px solid #7EE787;'>
                <div style='font-size: 0.7rem; color: #8B949E;'>USDC/WLD DEEP LIQUIDITY</div>
                <div style='font-size: 1.2rem; font-weight: 700; color: #7EE787;'>${wld_miner_data['price']:.10f}</div>
                <div style='font-size: 0.6rem; color: #8B949E;'>{wld_miner_data['name']}</div>
            </div>
            """, unsafe_allow_html=True)
        with w2:
            st.metric(t.get('wld_yield_est', 'Yield Est.'), "12.4% APR", f"{wld_miner_data['change_24h']:.2f}% (24h)")

        # B. Athene Network Migration Tracker Card
        st.markdown(f"""
        <div class="glass-panel" style='border-top: 2px solid #58A6FF; margin: 1.5rem 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4 style='margin:0;'>Athene Network Migration Tracker 🌍</h4>
                <span style='background: rgba(88, 166, 255, 0.1); color: #58A6FF; padding: 2px 8px; border-radius: 10px; font-size: 0.6rem;'>LIVE SYNC</span>
            </div>
            <div style='margin-top: 1rem; background: #30363D; height: 10px; border-radius: 5px; overflow: hidden;'>
                <div style='background: linear-gradient(90deg, #58A6FF, #7EE787); width: 68%; height: 100%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Intelligence Upgrade Button
        if st.button("🚀 Upgrade to World-V2 Intelligence", help="Pull the specialized World Chain model to Ollama"):
            with st.status("Requesting Core from Hive Mind...", expanded=True):
                success = kitsune.pull_model("athene-v2")
                if success:
                    st.success("World-V2 Intelligence successfully added.")
                else:
                    st.warning("Download initiated in background.")
        
        # C. Ecosystem Calculator
        st.markdown(f"#### {t.get('ath_swap_calc', 'Ecosystem Calculator')}")
        c1, c2 = st.columns(2)
        with c1:
            base_amt = st.number_input(t.get('ath_gem_balance', 'GEM/WLD Amount'), value=1000)
        with c2:
            st.metric("Est. USDC Value", f"${base_amt * wld_miner_data['price']:,.2f}") 
            
        # D. Market Pulse
        st.divider()
        st.markdown("#### Real-time World Hub Prices (On-Chain)")
        atn_pool = provider.get_world_chain_assets()["ATHENE"]
        atn_data = provider.fetch_dex_price(atn_pool)
        
        p1, p2 = st.columns(2)
        with p1: st.metric("WLD Miner / WETH", f"${wld_miner_data['price']:.10f}", f"{wld_miner_data['change_24h']:.2f}%")
        with p2: 
            st.metric("Athene Network (ATN)", f"${atn_data['price']:.8f}", f"{atn_data['change_24h']:.2f}%")

    with col_oracle:
        st.markdown(f"#### 🔮 {t.get('ath_oracle_intel', 'Oracle World Intel')}")
        oracle_intel = kitsune._get_relational_context()
        if "ORACLE" in oracle_intel.upper() or "WLD" in oracle_intel.upper():
            logs = [line for line in oracle_intel.split('\n') if any(x in line.upper() for x in ['ORACLE', 'ATH', 'WLD', 'MINER'])]
            for log in logs[-8:]:
                st.info(log)
        else:
            st.info("The Oracle is currently monitoring WLD distribution and $ATH liquidity bridging...")

    with col_chat:
        render_kitsune_terminal(t, kitsune, lang)

def main():
    try:
        # Load Engines
        provider, analytics, kitsune = get_engines()
        
        # Trigger Shadow Agents (Background)
        if 'shadow_agents_started' not in st.session_state:
            st.session_state.shadow_agents_started = True
            threading.Thread(target=run_background_shadows, args=(kitsune.model, kitsune), daemon=True).start()
        
        # Navigation & Language Logic (Top-level Header)
        t_en = TRANSLATIONS['en']
        t_it = TRANSLATIONS['it']
        
        # Header Area
        render_header(None)
        h_logo, h_title, h_status, h_lang = st.columns([0.5, 2, 2, 1])
        
        with h_logo: render_mascot(size=40)
        with h_title:
            st.markdown("<h3 style='color:#58A6FF; margin:0;'>KITSUNE FINANCE</h3>", unsafe_allow_html=True)
            app_mode = st.radio("NAV_V2", ["Dashboard", "Reports", "Athene Hub", "Archive"], horizontal=True, label_visibility="collapsed", key="app_nav_radio")
        
        with h_status:
            # High-frequency Autodiscovery (Silent every rerun)
            new_model = kitsune.discover_active_model()
            if new_model != st.session_state.get('discovered_model'):
                st.session_state.discovered_model = new_model
                st.toast(f"Kitsune synced with {new_model}", icon="🦊")
            
            current_model = st.session_state.get('discovered_model', new_model)
            kitsune.model = current_model
            
            st.markdown(f"""
            <div style='padding: 0.3rem 0.8rem; border-radius: 6px; border: 1px solid #30363D; background: #161B22; display: inline-block;'>
                <span style='color:#8B949E; font-size: 0.7rem;'>OLLAMA:</span> 
                <span style='color:#7EE787; font-size: 0.8rem; font-weight: 500;'>{current_model}</span>
                <span style='color:#58A6FF; font-size: 0.6rem; margin-left: 5px; border-left: 1px solid #30363D; padding-left: 5px;'>🕵️ SHADOW MODE ACTIVE</span>
            </div>
            """, unsafe_allow_html=True)
            
        with h_lang:
            c1, c2 = st.columns(2)
            with c1:
                lang_selection = st.selectbox("L", options=["🇮🇹", "🇺🇸"], label_visibility="collapsed", key="lang_v2")
                lang = "it" if lang_selection == "🇮🇹" else "en"
                st.session_state.lang = lang
                t = TRANSLATIONS.get(lang, t_en)
            with c2:
                st.session_state.agent_mode = st.toggle("🤖", value=st.session_state.get('agent_mode', False), key="agent_toggle_v2")

        st.divider()

        # Strategy Configuration (DCA Inputs)
        with st.expander("🛠️ Strategy Config / DCA", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                dca_amount = st.number_input(t.get('dca_amount', 'DCA Amount'), value=100)
            with c2:
                dca_freq_label = st.selectbox(t.get('dca_frequency', 'Frequency'), ['Daily', 'Weekly', 'Monthly'], index=1)
                dca_freq = {'Daily': 1, 'Weekly': 7, 'Monthly': 30}.get(dca_freq_label, 7)

        # Asset Data Cache
        crypto_tickers = provider.get_all_crypto_tickers()
        macro_tickers = list(provider.macro_tickers.keys())
        all_tickers = macro_tickers + crypto_tickers

        if app_mode == "Reports":
            render_report_hub(t, provider, kitsune, analytics, all_tickers)
        elif app_mode == "Athene Hub":
            render_world_chain_hub(t, provider, kitsune, lang)
        elif app_mode == "Archive":
            render_archive(t)
        else:
            # DASHBOARD
            macro_insight_banner("Global markets monitoring active. Kitsune is scanning for liquidity cycles.")
            
            # Asset Selectors
            c1, c2 = st.columns(2)
            with c1:
                primary_default = "BTC/USDT"
                if "ATH/USDT" in all_tickers: primary_default = "ATH/USDT"
                elif "BTC/USDT" in all_tickers: primary_default = "BTC/USDT"
                
                primary = st.selectbox(t["asset_primary"], all_tickers, index=all_tickers.index(primary_default) if primary_default in all_tickers else 0)
            with c2:
                secondary = st.selectbox(t["asset_optional"], [""] + all_tickers)

            st.divider()
            
            # --- TWO COLUMN TERMINAL LAYOUT ---
            col_data, col_chat = st.columns([1.5, 1], gap="medium")
            
            with col_chat:
                render_kitsune_terminal(t, kitsune, lang)

            with col_data:
                # Market Overview
                cols = st.columns(4)
            for i, tick in enumerate(["BTC-USD", "S&P500", "GOLD", "DXY"]):
                p = provider.get_latest_price(tick)
                with cols[i]:
                    premium_card(tick, f"${p:,.2f}" if p else "N/A", "Market Pulse")

            # Detailed Analysis
            if primary:
                data = provider.get_asset_data(primary)
                if not data.empty:
                    col = 'close' if 'close' in data.columns else 'Close'
                    price = float(data[col].iloc[-1])
                    returns = data[col].pct_change().dropna()
                    change = float(returns.iloc[-1] * 100) if not returns.empty else 0.0
                    
                    asset_header(primary, price, change)
                    
                    tabs = st.tabs([t["price_action"], t["monte_carlo"], t["scenario_sandbox"], t["inst_intel"], t["neural_prediction"]])
                    
                    with tabs[0]:
                        fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['open'] if 'open' in data else data['Open'],
                                        high=data['high'] if 'high' in data else data['High'],
                                        low=data['low'] if 'low' in data else data['Low'],
                                        close=data[col])])
                        fig.update_layout(template="plotly_dark", height=400, margin=dict(t=0,b=0,l=0,r=0))
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tabs[1]:
                        # Monte Carlo
                        mu = returns.mean() * 252
                        sigma = returns.std() * np.sqrt(252)
                        paths = analytics.monte_carlo_simulation(price, 90, mu, sigma, 100)
                        
                        fig_mc = go.Figure()
                        for i in range(50):
                            fig_mc.add_trace(go.Scatter(y=paths[i], mode='lines', line=dict(width=0.5, color='rgba(88, 166, 255, 0.1)'), showlegend=False))
                        
                        median_path = np.median(paths, axis=0)
                        fig_mc.add_trace(go.Scatter(y=median_path, mode='lines', line=dict(width=3, color='#7EE787'), name='Median Projection'))
                        fig_mc.update_layout(
                            template="plotly_dark",
                            plot_bgcolor='rgba(0,0,0,1)',
                            paper_bgcolor='rgba(0,0,0,1)',
                            height=400,
                            margin=dict(t=30, b=30, l=30, r=0),
                            xaxis=dict(gridcolor='#161B22'),
                            yaxis=dict(gridcolor='#161B22')
                        )
                        st.plotly_chart(fig_mc, use_container_width=True)

                    with tabs[2]:
                        # DCA Simulator
                        dca_stats = analytics.calculate_dca(data, dca_amount, dca_freq)
                        s1, s2, s3 = st.columns(3)
                        with s1: premium_card("Invested", f"${dca_stats['total_invested']:,.0f}", "Capital")
                        with s2: premium_card("Value", f"${dca_stats['current_value']:,.0f}", f"Units: {dca_stats['total_units']:.2f}")
                        with s3: premium_card("ROI", f"{dca_stats['roi_pct']:.1f}%", f"Avg Cost: ${dca_stats['avg_cost']:,.2f}")

                    with tabs[3]:
                        # Institutional Intel
                        i1, i2 = st.columns(2)
                        with i1:
                            st.markdown(f"**{t['order_flow']}**")
                            ob = provider.fetch_order_book(primary)
                            imb = analytics.analyze_order_imbalance(ob)
                            st.metric("Bias", imb['bias'], f"Ratio: {imb['ratio']:.2f}")
                        with i2:
                            st.markdown(f"**{t['sentiment_pulse']}**")
                            news = provider.fetch_news(primary)
                            sent = kitsune.analyze_sentiment(news)
                            st.metric("Sentiment", sent['label'], f"Score: {sent['score']:.2f}")

                    with tabs[4]:
                        # Neural Hub
                        st.markdown(f"#### 🧠 {t['neural_prediction']} Engine")
                        pred_data = analytics.neural_core.predict_price_trend(data)
                        
                        if pred_data["status"] == "Success":
                            c1, c2, c3 = st.columns(3)
                            with c1: st.metric(t["neural_target"], f"${pred_data['target_price']:.6f}")
                            with c2: st.metric(t["neural_trend"], f"{pred_data['change_pct']:.2f}%", delta=f"{pred_data['change_pct']:.2f}%")
                            with c3: st.metric(t["neural_confidence"], f"{pred_data['confidence']*100:.1f}%")
                            
                            # Gradient Forecast Viz
                            forecast_fig = go.Figure()
                            forecast_fig.add_trace(go.Scatter(y=pred_data['forecast_path'], mode='lines+markers', 
                                                           line=dict(color='#7EE787', width=4), 
                                                           marker=dict(size=8, color='#58A6FF'),
                                                           name='Neural Forecast'))
                            forecast_fig.update_layout(template="plotly_dark", height=300, 
                                                     title="Technical Directional Forecast (7D Cluster)",
                                                     margin=dict(t=30, b=0, l=30, r=0))
                            st.plotly_chart(forecast_fig, use_container_width=True)
                        else:
                            st.warning(pred_data["message"])
                    
                    
            # Correlation Sidebar (Column or extra section)
            st.divider()
            with st.expander(t["corr_matrix"], expanded=True):
                macro_dfs = {
                    "S&P500": provider.get_asset_data("S&P500"),
                    "GOLD": provider.get_asset_data("GOLD"),
                    "DXY": provider.get_asset_data("DXY"),
                    "BTC": provider.get_asset_data("BTC-USD")
                }
                corr_df = analytics.calculate_correlations(data, macro_dfs)
                if not corr_df.empty:
                    for _, row in corr_df.iterrows():
                        st.write(f"**{row['Asset']}**: {row['Correlation']:.2f}")

        # Universal Legal Disclaimer Footer
        st.divider()
        st.markdown(f"""
            <div style='text-align: center; padding: 2rem; color: #8B949E; font-size: 0.75rem; border-top: 1px solid #30363D;'>
                {t['disclaimer']}
                <br/><br/>
                <strong>Kitsune Finance by Kitsune Labs</strong>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Critical Runtime Exception: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()
