
print("Step 1: Importing core libs...")
import os
import sys
import json
import datetime
print("Step 2: Importing pandas/numpy...")
import pandas as pd
import numpy as np
print("Step 3: Importing duckduckgo_search...")
from duckduckgo_search import DDGS
print("Imported DDGS successfully.")

print("Step 4: Importing engine components...")
print("  - DataProvider")
from engine.data_provider import DataProvider
print("  - AnalyticsEngine")
from engine.analytics import AnalyticsEngine
print("  - SenseiAI")
from engine.sensei import SenseiAI
print("  - ReportGenerator")
from engine.report_generator import ReportGenerator
print("  - AgentEngine")
from engine.agent import AgentEngine

print("Step 5: Testing initializations...")
p = DataProvider()
print("DataProvider OK.")
s = SenseiAI()
print("SenseiAI OK.")
a = AnalyticsEngine()
print("AnalyticsEngine OK.")

print("Step 6: Testing data fetch (mock)...")
# Try a quick market check without CCXT if possible, or just a trivial CCXT call
try:
    print("Testing CCXT connection (timeout 2s)...")
    import ccxt
    ex = ccxt.binance({'timeout': 2000})
    # DON'T load markets here, just check instantiation
    print("CCXT instantiation OK.")
except Exception as e:
    print(f"CCXT Issue: {e}")

print("\n--- ALL CORE SYSTEMS READY ---")
