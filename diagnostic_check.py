
try:
    print("Step 1: Importing streamlit...")
    import streamlit as st
    print("Step 2: Importing pandas/numpy...")
    import pandas as pd
    import numpy as np
    print("Step 3: Importing engine components...")
    from engine.data_provider import DataProvider
    from engine.analytics import AnalyticsEngine
    from engine.kitsune import KitsuneAI
    from engine.report_generator import ReportGenerator
    from engine.agent import AgentEngine
    print("Step 4: Importing UI components...")
    from ui.components import premium_card, kitsune_sidebar_header, asset_header, macro_insight_banner, render_mascot
    from ui.localization import TRANSLATIONS
    print("Step 5: Testing DataProvider initialization...")
    p = DataProvider()
    print("Step 6: Testing KitsuneAI initialization...")
    s = KitsuneAI()
    print("Step 7: Testing AnalyticsEngine initialization...")
    a = AnalyticsEngine()
    print("All imports and initializations successful.")
except Exception as e:
    print(f"\nCRITICAL ERROR FOUND: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
