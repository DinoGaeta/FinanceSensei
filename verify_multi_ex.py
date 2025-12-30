
from engine.data_provider import DataProvider
import pandas as pd

def verify_provider():
    provider = DataProvider()
    print("--- Fetching All Tickers ---")
    tickers = provider.get_all_crypto_tickers()
    print(f"Total tickers found: {len(tickers)}")
    
    ath_present = "ATH/USDT" in tickers
    print(f"ATH/USDT in tickers: {ath_present}")
    
    print("\n--- Fetching ATH/USDT Data ---")
    df = provider.fetch_crypto_data("ATH/USDT")
    if not df.empty:
        print(f"Success! Latest Price: {df['close'].iloc[-1]}")
        print(f"Data Head:\n{df.head()}")
    else:
        print("Failed to fetch ATH/USDT data.")

if __name__ == "__main__":
    verify_provider()
