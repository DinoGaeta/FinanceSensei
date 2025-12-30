import ccxt
import yfinance as yf
import pandas as pd
import datetime
import streamlit as st
import requests
from typing import List, Optional, Union, Dict, Any

class DataProvider:
    def __init__(self):
        self.binance = ccxt.binance({'enableRateLimit': True})
        self.mexc = ccxt.mexc({'enableRateLimit': True})
        self.gateio = ccxt.gateio({'enableRateLimit': True})
        self.macro_tickers = {
            "GOLD": "GC=F",
            "S&P500": "^GSPC",
            "DXY": "DX-Y.NYB",
            "NASDAQ": "^IXIC",
            "BTC-USD": "BTC-USD" # Yahoo backup
        }
        self._cached_tickers = []
        self._last_ticker_update = None

    @st.cache_data(ttl=3600, show_spinner=False)
    def get_all_crypto_tickers(_self) -> List[str]:
        """Fetch and cache all available trading pairs from the exchange."""
        try:
            binance_markets = sorted(list(_self.binance.load_markets().keys()))
            mexc_markets = sorted(list(_self.mexc.load_markets().keys()))
            # Combine and unique
            all_markets = sorted(list(set(binance_markets + mexc_markets)))
            return all_markets
        except Exception as e:
            print(f"Error fetching symbols: {e}")
            return ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ICP/USDT", "ATH/USDT"] # Fallback includes ATH

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_crypto_data(_self, symbol: str, timeframe: str = '1d', limit: int = 100) -> pd.DataFrame:
        """Fetch historical data from CCXT (Binance/MEXC). Cached for 5 minutes."""
        # Try Binance first, then MEXC for newer tokens like ATH
        exchanges = [_self.binance, _self.mexc, _self.gateio]
        for ex in exchanges:
            try:
                # Some exchanges might have different names, but we assume standard pair / format
                ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
            except Exception as e:
                continue
        
        print(f"Error: Symbol {symbol} not found on any supported exchanges.")
        return pd.DataFrame()

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_macro_data(_self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical data from YFinance."""
        try:
            # Map common names to yfinance symbols
            yf_ticker = _self.macro_tickers.get(ticker, ticker)
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
            # Convert ticker to YFinance format
            if "/" in ticker:
                # BTC/USDT -> BTC-USD (Yahoo format)
                base = ticker.split("/")[0]
                yf_ticker = f"{base}-USD"
            else:
                yf_ticker = self.macro_tickers.get(ticker, ticker)
            
            t = yf.Ticker(yf_ticker)
            
            # Try different news access methods (YFinance API varies)
            news = []
            try:
                news = t.news if hasattr(t, 'news') and t.news else []
            except:
                pass
            
            # Fallback: try get_news method if available
            if not news:
                try:
                    news = t.get_news() if hasattr(t, 'get_news') else []
                except:
                    pass
            
            return news[:10] if news else []
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []

    def fetch_dex_price(self, pool_address: str) -> Dict[str, Any]:
        """Fetch real-time price from GeckoTerminal for a specific pool on World Chain."""
        url = f"https://api.geckoterminal.com/api/v2/networks/world-chain/pools/{pool_address}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                attr = data.get('data', {}).get('attributes', {})
                return {
                    "price": float(attr.get('base_token_price_usd', 0)),
                    "change_24h": float(attr.get('price_change_percentage', {}).get('h24', 0)),
                    "volume": float(attr.get('volume_usd', {}).get('h24', 0)),
                    "name": attr.get('name', 'Unknown')
                }
            return {"price": 0.0, "change_24h": 0.0, "volume": 0.0, "name": "N/A"}
        except Exception as e:
            print(f"DEX Fetch Error: {e}")
            return {"price": 0.0, "change_24h": 0.0, "volume": 0.0, "name": "Error"}

    def get_world_chain_assets(self):
        """Pre-defined alpha assets for World Chain monitoring."""
        return {
            "WLD_MINER": "0xfacd70fe45bd851dc52da647e6eb7f6ed4724f67",
            "ATHENE": "0x2cad161cf084a8a52cfdd5c0dd0102e49d498c39"
        }

    def get_athene_chain_status(self):
        """Fetch real-time technical status of the Athene Parthenon chain."""
        rpc_url = "https://rpc.parthenon.athenescan.io"
        try:
            payload = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
            resp = requests.post(rpc_url, json=payload, timeout=5)
            if resp.status_code == 200:
                block_hex = resp.json().get('result', "0x0")
                block_num = int(block_hex, 16)
                return {"status": "Online", "block": block_num, "tps_est": "4000 (Peak)"}
            return {"status": "Congested", "block": "N/A", "tps_est": "---"}
        except Exception:
            return {"status": "Offline", "block": "N/A", "tps_est": "---"}
