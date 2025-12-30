
import ccxt
import yfinance as yf
import pandas as pd

def test_token_fetching():
    tokens = ["ATH/USDT", "ATN/USDT"]
    yf_tokens = ["ATH-USD", "ATN-USD"]

    print("--- Testing CCXT (Binance) ---")
    try:
        binance = ccxt.binance()
        markets = binance.load_markets()
        for t in tokens:
            if t in markets:
                print(f"{t} found on Binance! Price: {binance.fetch_ticker(t)['last']}")
            else:
                print(f"{t} NOT found on Binance.")
    except Exception as e: print(f"Binance Error: {e}")

    print("\n--- Testing YFinance ---")
    for t in yf_tokens:
        try:
            data = yf.Ticker(t).history(period="1d")
            if not data.empty:
                print(f"{t} found on Yahoo! Price: {data['Close'].iloc[-1]}")
            else:
                print(f"{t} NOT found on Yahoo.")
        except Exception as e: print(f"Yahoo Error for {t}: {e}")

    print("\n--- Testing CCXT (MEXC) ---")
    try:
        mexc = ccxt.mexc()
        markets = mexc.load_markets()
        for t in tokens:
            if t in markets:
                print(f"{t} found on MEXC! Price: {mexc.fetch_ticker(t)['last']}")
            else:
                print(f"{t} NOT found on MEXC.")
    except Exception as e: print(f"MEXC Error: {e}")

    print("\n--- Testing CCXT (Gate.io) ---")
    try:
        gate = ccxt.gateio()
        markets = gate.load_markets()
        for t in tokens:
            if t in markets:
                print(f"{t} found on Gate.io! Price: {gate.fetch_ticker(t)['last']}")
            else:
                print(f"{t} NOT found on Gate.io.")
    except Exception as e: print(f"Gate.io Error: {e}")

if __name__ == "__main__":
    test_token_fetching()
