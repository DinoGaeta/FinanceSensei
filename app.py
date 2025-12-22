import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from engine.data_provider import DataProvider

# Page Configuration
st.set_page_config(
    page_title="FinanceSensei | Strategic Intelligence",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Midnight Professional)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Manrope:wght@300;400;600;800&display=swap');

    :root {
        --bg-deep: #0B0E14;
        --card-bg: #161B22;
        --card-border: #30363D;
        --accent-blue: #58A6FF;
        --accent-green: #7EE787;
        --text-main: #C9D1D9;
        --text-dim: #8B949E;
    }

    /* Base Layout */
    .stApp {
        background-color: var(--bg-deep);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    /* Global Typography */
    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: 1.5px !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
    }

    /* Premium Cards */
    .premium-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    .premium-card:hover {
        border-color: var(--accent-blue);
        transform: translateY(-2px);
    }

    /* Glassmorphism Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(22, 27, 34, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 1px solid var(--card-border);
    }

    /* Scenario Calculator Glass */
    .glass-panel {
        background: rgba(48, 54, 61, 0.3);
        backdrop-filter: blur(12px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
    }

    /* Metrics and Glows */
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
    }
    
    .glow-green { text-shadow: 0 0 10px rgba(126, 231, 135, 0.3); color: var(--accent-green); }
    .glow-blue { text-shadow: 0 0 10px rgba(88, 166, 255, 0.3); color: var(--accent-blue); }

    /* Anti-noise overrides */
    div.stMetric > div { background: transparent !important; }
    div.stButton > button {
        background-color: transparent !important;
        border: 1px solid var(--accent-blue) !important;
        color: var(--accent-blue) !important;
        border-radius: 8px !important;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: rgba(88, 166, 255, 0.1) !important;
    }

    /* Mobile Adaptivity */
    @media (max-width: 768px) {
        .premium-card {
            padding: 1.5rem !important;
            margin-bottom: 1rem !important;
        }
        .metric-value {
            font-size: 1.4rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 5px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding-left: 10px !important;
            padding-right: 10px !important;
            font-size: 0.8rem !important;
        }
        .glass-panel {
            padding: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# App Navigation & Layout
from ui.components import premium_card, sensei_sidebar_header, asset_header, macro_insight_banner, render_mascot
from ui.localization import TRANSLATIONS
from engine.analytics import AnalyticsEngine

# ... (CSS remains same in actual file, but I'll update the main logic)

from engine.sensei import SenseiAI

def main():
    provider = DataProvider()
    analytics = AnalyticsEngine()
    
    # Universal Asset List
    all_tickers = provider.get_all_crypto_tickers()

    # Sidebar - Sensei Intelligence
    with st.sidebar:
        # Language Selector
        lang_display = {"it": "🇮🇹 Italiano", "en": "🇬🇧 English"}
        lang = st.selectbox("Language / Lingua", ["it", "en"], format_func=lambda x: lang_display[x])
        st.session_state['lang'] = lang
        t = TRANSLATIONS[lang]

        # Navigation
        app_mode = st.radio("Navigation", ["Dashboard", "Vision"], index=0, 
                            format_func=lambda x: t["nav_dashboard"] if x == "Dashboard" else t["nav_vision"])
        
        st.divider()

        def render_landing_page(t):
            st.title(f"🦉 {t['vision_title']}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class='premium-card' style='border-left: 5px solid var(--accent-blue);'>
                    <h3>{t['vision_mission']}</h3>
                    <p style='font-size: 1.1rem; line-height: 1.6;'>{t['mission_text']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='premium-card' style='border-left: 5px solid var(--accent-green);'>
                    <h3>{t['market_strategy']}</h3>
                    <p style='font-size: 1.1rem; line-height: 1.6;'>{t['strategy_text']}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class='glass-panel'>
                    <h4>Stack Technology</h4>
                    <ul style='color: var(--text-dim);'>
                        <li>Streamlit Engine</li>
                        <li>Ollama Local LLM</li>
                        <li>CCXT (Crypto)</li>
                        <li>yFinance (TradFi)</li>
                        <li>Plotly Visuals</li>
                    </ul>
                </div>
                <br/>
                <div class='glass-panel'>
                    <h4>Private-First AI</h4>
                    <p style='font-size: 0.9rem; color: var(--text-dim);'>
                        Your data, your strategy. FinanceSensei performs all high-level reasoning locally via Ollama, 
                        ensuring that institutional alpha remains in your hands.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        if app_mode == "Vision":
            render_landing_page(t)
            st.stop()

        # AI Engine Selector
        ai_engine_display = {"heuristic": t["ai_standard"], "ollama": t["ai_deep"]}
        # Default to ollama as requested
        ai_provider = st.selectbox(t["ai_engine"], ["ollama", "heuristic"], format_func=lambda x: ai_engine_display[x])
        
        selected_model = "gpt-oss:120b-cloud"
        if ai_provider == "ollama":
            selected_model = st.text_input(t["ai_model"], value="gpt-oss:120b-cloud")
            
        sensei = SenseiAI(provider=ai_provider, model=selected_model)

        sensei_sidebar_header(lang=lang)
        
        st.subheader(t["discovery_hub"])
        search_ticker = st.selectbox(t["asset_primary"], all_tickers, index=all_tickers.index("BTC/USDT") if "BTC/USDT" in all_tickers else 0)
        compare_ticker = st.selectbox(t["asset_optional"], [""] + all_tickers, index=0)
        
        st.divider()
        st.subheader(t["scenario_params"])
        days_sim = st.slider(t["sim_horizon"], 30, 365, 90)
        simulations = st.number_input(t["path_count"], 10, 1000, 100)
        
        st.divider()
        st.subheader(t["dca_settings"])
        dca_amount = st.number_input(t["dca_amount"], 10, 10000, 100)
        dca_freq = st.selectbox(t["frequency"], [7, 14, 30], format_func=lambda x: t["every_days"].format(x))
        
        if search_ticker:
            st.divider()
            st.subheader(t["strategic_brief"])
            # This will be populated after asset data is fetched in main
            st.session_state['current_insight'] = st.session_state.get('current_insight', t["awaiting_data"])
            st.markdown(f"""
            <div class="glass-panel" style='font-size: 0.85rem; border-left: 3px solid var(--accent-blue);'>
                {st.session_state['current_insight']}
            </div>
            """, unsafe_allow_html=True)

    # Main Dashboard Header
    st.markdown("<h1>FINANCE <span style='color:#58A6FF'>SENSEI</span></h1>", unsafe_allow_html=True)
    # Macro awareness banner
    macro_insight_banner("Global liquidity is stabilizing. Bitcoin correlation with S&P500 remains high (~85%).")

    # Multi-Asset Overview
    st.subheader(t["market_snapshot"])
    cols = st.columns(4)
    market_assets = ["BTC-USD", "S&P500", "GOLD", "DXY"]
    
    for i, asset in enumerate(market_assets):
        price = provider.get_latest_price(asset)
        with cols[i]:
            premium_card(
                title=asset,
                value=f"${price:,.2f}" if price else "N/A",
                subtext="Monitoring Flux" if i % 2 == 0 else "Liquidity High",
                glow_class="glow-blue" if i % 2 == 0 else "glow-green"
            )

    # Search / Detailed Analysis
    if search_ticker:
        data = provider.get_asset_data(search_ticker)
        if not data.empty:
            col = 'close' if 'close' in data.columns else 'Close'
            current_price = data[col].iloc[-1]
            returns = data[col].pct_change().dropna()
            
            asset_header(search_ticker, current_price, returns.iloc[-1]*100)
            
            # Analytics Row
            a1, a2, a3 = st.columns(3)
            ath_stats = analytics.get_ath_stats(data)
            vol = analytics.calculate_volatility(data).iloc[-1]
            sharpe = analytics.calculate_sharpe_ratio(returns)
            
            with a1: premium_card(t["volatility"], f"{vol:.1%}", "Dynamic Risk Profile", "glow-blue")
            with a2: premium_card(t["ath_dist"], f"{ath_stats['distance_pct']:.1f}%", f"ATH: ${ath_stats['ath']:,.2f}", "glow-green")
            with a3: premium_card(t["sharpe"], f"{sharpe:.2f}", "Risk-Adjusted Alpha", "glow-blue")

            # Chart and Correlation Matrix
            st.divider()
            c1, c2 = st.columns([2, 1])
            
            with c1:
                tabs_list = [t["price_action"], t["monte_carlo"], t["scenario_sandbox"], t["inst_intel"], t["chat_tab"]]
                if compare_ticker: tabs_list.append(t["rel_perf"])
                tabs = st.tabs(tabs_list)
                
                with tabs[0]:
                    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                    open=data['open'] if 'open' in data else data['Open'],
                                    high=data['high'] if 'high' in data else data['High'],
                                    low=data['low'] if 'low' in data else data['Low'],
                                    close=data['close'] if 'close' in data else data['Close'])])
                    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                                    xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"), height=450, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
                
                with tabs[1]:
                    mu = returns.mean() * 252
                    sigma = returns.std() * np.sqrt(252)
                    paths = analytics.monte_carlo_simulation(current_price, days_sim, mu, sigma, int(simulations))
                    
                    fig_mc = go.Figure()
                    for i in range(min(int(simulations), 50)):
                        fig_mc.add_trace(go.Scatter(y=paths[i], mode='lines', line=dict(width=0.5, color='rgba(88, 166, 255, 0.15)'), showlegend=False))
                    
                    p95 = np.percentile(paths, 95, axis=0)
                    p05 = np.percentile(paths, 5, axis=0)
                    median_path = np.median(paths, axis=0)
                    
                    fig_mc.add_trace(go.Scatter(y=p95, mode='lines', line=dict(width=0), showlegend=False))
                    fig_mc.add_trace(go.Scatter(y=p05, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(126, 231, 135, 0.05)', showlegend=False))
                    fig_mc.add_trace(go.Scatter(y=median_path, mode='lines', line=dict(width=3, color='#7EE787'), name='Median Projection'))
                    
                    fig_mc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                        xaxis=dict(title="Days Ahead", gridcolor="#21262d"), 
                                        yaxis=dict(title="Price Projection", gridcolor="#21262d"), height=450, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_mc, use_container_width=True)

                with tabs[2]:
                    st.subheader("DCA Accumulation Simulator")
                    dca_stats = analytics.calculate_dca(data, dca_amount, dca_freq)
                    
                    s1, s2, s3 = st.columns(3)
                    with s1: premium_card("Total Invested", f"${dca_stats['total_invested']:,.0f}", "Capital Deployment", "glow-blue")
                    with s2: premium_card("Current Value", f"${dca_stats['current_value']:,.0f}", f"Units: {dca_stats['total_units']:.4f}", "glow-green")
                    with s3: 
                        color = "glow-green" if dca_stats['roi_pct'] >= 0 else "glow-blue"
                        premium_card("ROI", f"{dca_stats['roi_pct']:.1f}%", f"Avg Cost: ${dca_stats['avg_cost']:,.2f}", color)
                    
                    st.markdown("""
                    <div class='glass-panel'>
                        <strong>Note the capital efficiency.</strong> 
                        A disciplined DCA strategy often outperforms raw market timing in volatile regimes.
                    </div>
                    """, unsafe_allow_html=True)

                with tabs[3]:
                    st.subheader(t["inst_alpha_feed"])
                    i1, i2 = st.columns([1, 1])
                    
                    with i1:
                        st.markdown(f"**{t['order_flow']}**")
                        order_book = provider.fetch_order_book(search_ticker)
                        imbalance = analytics.analyze_order_imbalance(order_book)
                        
                        # Visualization of depth
                        bids = pd.DataFrame(order_book.get('bids', []), columns=['price', 'volume'])
                        asks = pd.DataFrame(order_book.get('asks', []), columns=['price', 'volume'])
                        
                        fig_depth = go.Figure()
                        fig_depth.add_trace(go.Bar(x=bids['price'], y=bids['volume'], name='Bids', marker_color='#7EE787'))
                        fig_depth.add_trace(go.Bar(x=asks['price'], y=asks['volume'], name='Asks', marker_color='#FF7B72'))
                        fig_depth.update_layout(template="plotly_dark", height=300, barmode='overlay', 
                                                margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_depth, use_container_width=True)
                        st.caption(f"Bias: {imbalance['bias']} (Ratio: {imbalance['ratio']:.2f})")
                    
                    with i2:
                        st.markdown(f"**{t['whale_monitor']}**")
                        # Use 1h data for crypto to make whale detection more 'real' and granular
                        if "/" in search_ticker:
                            with st.spinner("Analyzing high-frequency volume..."):
                                pulse_data = provider.fetch_crypto_data(search_ticker, timeframe='1h', limit=48)
                        else:
                            pulse_data = data
                            
                        whales = analytics.detect_whale_activity(pulse_data)
                        if not whales.empty:
                            for idx, row in whales.tail(3).iterrows():
                                time_str = idx.strftime('%d/%m %H:%M')
                                st.markdown(f"""
                                <div class='glass-panel' style='padding: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid var(--accent-green);'>
                                    <span style='font-size: 0.8rem; color: #8B949E;'>{time_str}</span><br/>
                                    <strong>{t['whale_detected']}</strong><br/>
                                    <span style='color: var(--accent-green)'>{t['vol_spike']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info(t["no_anomalies"])

                    st.divider()
                    st.markdown(f"**{t['sentiment_pulse']}**")
                    news = provider.fetch_news(search_ticker)
                    sentiment = sensei.analyze_sentiment(news)
                    
                    cols_s = st.columns([1, 2])
                    with cols_s[0]:
                        val = sentiment['score'] * 100
                        color = "#7EE787" if val > 60 else "#FF7B72" if val < 40 else "#58A6FF"
                        st.markdown(f"""
                        <div style='text-align: center; padding: 1rem; border: 2px solid {color}; border-radius: 50%; width: 100px; height: 100px; margin: auto;'>
                            <div style='font-size: 1.5rem; font-weight: 800; margin-top: 15px;'>{val:.0f}</div>
                            <div style='font-size: 0.6rem;'>{sentiment['label']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with cols_s[1]:
                        for item in news[:3]:
                            st.markdown(f"- [{item.get('title')}]({item.get('link')})")

                with tabs[4]:
                    st.subheader(t["chat_tab"])
                    
                    # Initialize chat history
                    if "messages" not in st.session_state:
                        st.session_state.messages = [{"role": "assistant", "content": t["chat_welcome"]}]

                    # Display chat messages
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                    # Chat input
                    if prompt := st.chat_input(t["chat_placeholder"]):
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.markdown(prompt)

                        with st.chat_message("assistant"):
                            with st.spinner("Sensei is thinking..."):
                                response = sensei.chat(prompt, lang=lang)
                                st.markdown(response)
                                st.session_state.messages.append({"role": "assistant", "content": response})

                if compare_ticker and len(tabs) > 5:
                    with tabs[5]:
                        st.subheader(f"Strategy: {search_ticker} / {compare_ticker}")
                        comp_data = provider.get_asset_data(compare_ticker)
                        if not comp_data.empty:
                            c_col = 'close' if 'close' in comp_data.columns else 'Close'
                            # Normalized performance
                            norm_1 = data[col] / data[col].iloc[0]
                            norm_2 = comp_data[c_col] / comp_data[c_col].iloc[0]
                            
                            fig_rel = go.Figure()
                            fig_rel.add_trace(go.Scatter(x=data.index, y=norm_1, name=search_ticker, line=dict(color='#58A6FF')))
                            fig_rel.add_trace(go.Scatter(x=comp_data.index, y=norm_2, name=compare_ticker, line=dict(color='#7EE787')))
                            
                            fig_rel.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                                 yaxis_title="Normalized Return (1.0 Start)", height=450)
                            st.plotly_chart(fig_rel, use_container_width=True)

            with c2:
                st.subheader(t["corr_matrix"])
                # Fetch comparison data for correlation
                with st.spinner("Syncing Alpha..."):
                    macro_dfs = {
                        "S&P500": provider.get_asset_data("S&P500"),
                        "GOLD": provider.get_asset_data("GOLD"),
                        "DXY": provider.get_asset_data("DXY"),
                        "BTC": provider.get_asset_data("BTC-USD")
                    }
                    if compare_ticker:
                        macro_dfs[compare_ticker] = provider.get_asset_data(compare_ticker)
                        
                    corr_df = analytics.calculate_correlations(data, macro_dfs)
                
                if not corr_df.empty:
                    for idx, row in corr_df.iterrows():
                        val = row['Correlation']
                        glow = "glow-green" if val > 0.5 else "glow-blue" if val > 0 else "glow-blue" # simplified
                        st.markdown(f"""
                        <div class="glass-panel" style='margin-bottom: 0.8rem; display: flex; justify-content: space-between;'>
                            <span>{row['Asset']}</span>
                            <span class="{glow}" style='font-weight: 600;'>{val:.2f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Sensei Insight logic
                    strongest = corr_df.iloc[corr_df['Correlation'].abs().idxmax()]
                    rsi = analytics.calculate_rsi(data)
                    
                    insight_metrics = {
                        "volatility": vol,
                        "ath_distance": ath_stats['distance_pct'],
                        "sharpe": sharpe,
                        "rsi": rsi,
                        "top_correlation": strongest.to_dict()
                    }
                    st.session_state['current_insight'] = sensei.get_insight(search_ticker, insight_metrics, lang=lang)
                    st.info(f"Sensei Summary: {st.session_state['current_insight']}")
                else:
                    st.warning("Insufficient data for correlation mapping.")
        else:
            st.error("Asset not found or connection error.")

    # Universal Legal Disclaimer Footer
    st.divider()
    st.markdown(f"""
        <div style='text-align: center; padding: 2rem; color: #8B949E; font-size: 0.75rem; border-top: 1px solid #30363D;'>
            {t['disclaimer']}
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
