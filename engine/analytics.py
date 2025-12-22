import numpy as np
import pandas as pd
from scipy.stats import norm

class AnalyticsEngine:
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate the Sharpe Ratio for a given series of returns."""
        if returns.empty: return 0.0
        mean_return = returns.mean() * 252 # Annualized
        std_dev = returns.std() * np.sqrt(252)
        if std_dev == 0: return 0.0
        return (mean_return - risk_free_rate) / std_dev

    @staticmethod
    def monte_carlo_simulation(initial_price: float, days: int, mu: float, sigma: float, simulations: int = 100) -> np.ndarray:
        """Run a simple Monte Carlo simulation for price paths."""
        results = np.zeros((simulations, days))
        for i in range(simulations):
            prices = [initial_price]
            for _ in range(1, days):
                # Geometric Brownian Motion
                change = np.random.normal(mu/252, sigma/np.sqrt(252))
                prices.append(prices[-1] * (1 + change))
            results[i, :] = prices
        return results

    @staticmethod
    def calculate_volatility(df: pd.DataFrame, window: int = 21) -> pd.Series:
        """Calculate rolling annualized volatility."""
        col = 'close' if 'close' in df.columns else 'Close'
        returns = df[col].pct_change()
        return returns.rolling(window=window).std() * np.sqrt(252)

    @staticmethod
    def get_ath_stats(df: pd.DataFrame) -> dict:
        """Calculate ATH and distance from ATH."""
        col = 'close' if 'close' in df.columns else 'Close'
        current_price = df[col].iloc[-1]
        ath = df[col].max()
        distance = (current_price - ath) / ath * 100
        return {"ath": ath, "distance_pct": distance}

    @staticmethod
    def calculate_correlations(target_df: pd.DataFrame, comparison_dfs: dict) -> pd.DataFrame:
        """Calculate correlations between target asset and a set of macro assets."""
        target_col = 'close' if 'close' in target_df.columns else 'Close'
        target_returns = target_df[target_col].pct_change().dropna()
        
        correlations = []
        for name, df in comparison_dfs.items():
            if df.empty: continue
            comp_col = 'close' if 'close' in df.columns else 'Close'
            comp_returns = df[comp_col].pct_change().dropna()
            
            # Align dates
            combined = pd.concat([target_returns, comp_returns], axis=1).dropna()
            if not combined.empty:
                corr = combined.corr().iloc[0, 1]
                correlations.append({"Asset": name, "Correlation": corr})
        
        return pd.DataFrame(correlations)

    @staticmethod
    def calculate_dca(df: pd.DataFrame, amount: float, frequency_days: int) -> dict:
        """Simulate a DCA strategy performance."""
        col = 'close' if 'close' in df.columns else 'Close'
        prices = df[col]
        
        # Select prices at the given frequency
        dca_prices = prices.iloc[::frequency_days]
        total_invested = len(dca_prices) * amount
        total_units = (amount / dca_prices).sum()
        current_value = total_units * prices.iloc[-1]
        roi_pct = ((current_value - total_invested) / total_invested) * 100
        
        return {
            "total_invested": total_invested,
            "total_units": total_units,
            "current_value": current_value,
            "roi_pct": roi_pct,
            "avg_cost": total_invested / total_units if total_units > 0 else 0
        }

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, window: int = 14) -> float:
        """Calculate relative strength index (RSI)."""
        col = 'close' if 'close' in df.columns else 'Close'
        delta = df[col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    @staticmethod
    def detect_whale_activity(df: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
        """Detect volume outliers suggestive of 'Whale' activity."""
        vol_col = 'volume' if 'volume' in df.columns else 'Volume'
        if vol_col not in df.columns or df.empty: return pd.DataFrame()
        
        avg_vol = df[vol_col].rolling(window=20).mean()
        std_vol = df[vol_col].rolling(window=20).std()
        
        # Detect volume > Mean + 2*StdDev
        whales = df[df[vol_col] > (avg_vol + threshold * std_vol)]
        return whales

    @staticmethod
    def analyze_order_imbalance(order_book: dict) -> dict:
        """Analyze the ratio of bids to asks."""
        if not order_book or 'bids' not in order_book or 'asks' not in order_book:
            return {"ratio": 1.0, "bias": "Neutral"}
        
        bid_vol = sum(b[1] for b in order_book['bids'][:10])
        ask_vol = sum(a[1] for a in order_book['asks'][:10])
        
        ratio = bid_vol / ask_vol if ask_vol > 0 else 1.0
        bias = "Bullish" if ratio > 1.2 else "Bearish" if ratio < 0.8 else "Neutral"
        
        return {"ratio": ratio, "bias": bias, "bid_vol": bid_vol, "ask_vol": ask_vol}
