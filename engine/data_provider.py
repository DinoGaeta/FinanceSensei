import ccxt
import yfinance as yf
import pandas as pd
import datetime
import streamlit as st
from typing import List, Optional, Union

class DataProvider:
    def __init__(self):
        self.binance = ccxt.binance({
            'enableRateLimit': True,
        })
        self.macro_tickers = {
            "GOLD": "GC=F",
            "S&P500": "^GSPC",
            "DXY": "DX-Y.NYB",
            "NASDAQ": "^IXIC",
            "BTC-USD": "BTC-USD" # Yahoo backup
        }
        self._cached_tickers = []
        self._last_ticker_update = None

    def get_all_crypto_tickers(self) -> List[str]:
        """Fetch and cache all available trading pairs from the exchange."""
        now = datetime.datetime.now()
        if self._cached_tickers and self._last_ticker_update and (now - self._last_ticker_update).seconds < 3600:
            return self._cached_tickers
        
        try:
            markets = self.binance.load_markets()
            self._cached_tickers = sorted(list(markets.keys()))
            self._last_ticker_update = now
            return self._cached_tickers
        except Exception as e:
            print(f"Error fetching symbols: {e}")
            return ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ICP/USDT"] # Fallback

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_crypto_data(_self, symbol: str, timeframe: str = '1d', limit: int = 100) -> pd.DataFrame:
        """Fetch historical data from CCXT (Binance). Cached for 5 minutes."""
        try:
            ohlcv = _self.binance.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching CCXT data for {symbol}: {e}")
            return pd.DataFrame()

    def fetch_macro_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical data from YFinance."""
        try:
            # Map common names to yfinance symbols
            yf_ticker = self.macro_tickers.get(ticker, ticker)
            data = yf.download(yf_ticker, period=period)
            if data.empty:
                return pd.DataFrame()
            return data
        except Exception as e:
            print(f"Error fetching YFinance data for {ticker}: {e}")
            return pd.DataFrame()

    def get_asset_data(self, ticker: str) -> pd.DataFrame:
        """Smart asset selection logic."""
        if "/" in ticker:
            return self.fetch_crypto_data(ticker)
        else:
            return self.fetch_macro_data(ticker)

    def get_latest_price(self, ticker: str) -> Optional[float]:
        """Fetch the most recent price for an asset."""
        df = self.get_asset_data(ticker)
        if not df.empty:
            return float(df['close'].iloc[-1]) if 'close' in df.columns else float(df['Close'].iloc[-1])
        return None

    def fetch_order_book(self, symbol: str, limit: int = 50) -> dict:
        """Fetch the order book for a given symbol."""
        try:
            return self.binance.fetch_order_book(symbol, limit=limit)
        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")
            return {}

    def fetch_news(self, ticker: str) -> List[dict]:
        """Fetch news for a given ticker via Yahoo Finance."""
        try:
            yf_ticker = self.macro_tickers.get(ticker, ticker)
            if "/" in ticker: # Try conversion for crypto
                yf_ticker = ticker.replace("/", "-")
            
            t = yf.Ticker(yf_ticker)
            return t.news[:10]
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []
