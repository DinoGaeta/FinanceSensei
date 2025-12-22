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

def sensei_sidebar_header(lang: str = "en"):
    """Render the sidebar header with glass effect."""
    text = TRANSLATIONS[lang]["sensei_sidebar_text"]
    st.markdown(f"""
    <div class="glass-panel" style='margin-bottom: 2rem;'>
        <h2 style='font-size: 1.2rem; margin-top: 0;'>Sensei Intelligence</h2>
        <p style='font-size: 0.85rem; color: #8B949E; line-height: 1.4;'>
            {text}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_mascot(image_path: str = None):
    """Render the Sensei mascot with guaranteed visibility using external CDN or emoji."""
    # Soluzione definitiva: usiamo un'immagine da CDN esterno per garantire la visualizzazione
    st.markdown("""
    <div style='text-align: center; margin: 1rem 0;'>
        <div class='sensei-mascot'>
            <img src='https://img.icons8.com/3d-fluency/200/owl.png' 
                 alt='Sensei Owl' 
                 style='width: 120px; 
                        border-radius: 50%; 
                        box-shadow: 0 0 20px rgba(88, 166, 255, 0.5); 
                        border: 2px solid rgba(88, 166, 255, 0.3);'/>
        </div>
    </div>
    <style>
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    .sensei-mascot img {
        animation: float 3s ease-in-out infinite;
        display: block;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

def asset_header(ticker: str, price: float, change: float):
    """Render a header for a specific asset analysis."""
    # Ensure change is a scalar
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

def macro_insight_banner(message: str):
    """Render a top-level awareness banner."""
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, rgba(88,166,255,0.1) 0%, rgba(126,231,135,0.1) 100%); 
                border: 1px solid var(--card-border); border-radius: 8px; padding: 1rem; margin-bottom: 2rem; 
                display: flex; align-items: center; border-left: 4px solid var(--accent-blue);'>
        <span style='margin-right: 1rem; font-size: 1.2rem;'>💡</span>
        <span style='color: var(--text-main); font-size: 0.95rem;'>{message}</span>
    </div>
    """, unsafe_allow_html=True)
