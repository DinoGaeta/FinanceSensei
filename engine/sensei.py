import requests
import json
import os
from typing import Optional, List
from ui.localization import SENSEI_STRINGS

class SenseiAI:
    def __init__(self, provider="heuristic", model="llama3"):
        self.provider = provider
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"

    def get_insight(self, asset_name: str, metrics: dict, lang: str = "it") -> str:
        """Generate strategic insight based on provider."""
        if self.provider == "ollama":
            return self._ollama_generate(asset_name, metrics, lang)
        else:
            return self._heuristic_generate(asset_name, metrics, lang)

    def chat(self, user_prompt: str, lang: str = "it") -> str:
        """Handle conversational queries with a financial bias."""
        if self.provider != "ollama":
            return "Sensei Chat is only available in 'Deep Intelligence' mode (Ollama)."
            
        try:
            language_context = "English" if lang == "en" else "Italian"
            system_prompt = f"""
            System: You are 'FinanceSensei', a specialized financial AI strategist.
            Tone: Professional, institutional, high-conviction, strategic.
            Language: Always respond in {language_context}.
            Mandate: You are here to provide financial insights, market analysis, and strategic observations.
            Filtering: If the user asks a non-financial or non-market related question, politely pivot back to financial strategy. Do not provide definitive investment advice, but rather probabilistic observations.
            """
            
            response = requests.post(self.ollama_url, 
                                     json={"model": self.model, "prompt": f"{system_prompt}\nUser: {user_prompt}", "stream": False},
                                     timeout=15)
                                     
            if response.status_code == 200:
                return response.json().get('response', "Sensei is processing the signal...")
            return "Sensei chat signal interrupted. (Ollama connection failed)"
        except Exception as e:
            return f"Sensei chat signal interrupted. ({str(e)})"

    def _heuristic_generate(self, asset_name: str, metrics: dict, lang: str = "en") -> str:
        """Heuristic-based strategic insight."""
        s = SENSEI_STRINGS[lang]
        vol = metrics.get('volatility', 0)
        ath_dist = metrics.get('ath_distance', 0)
        sharpe = metrics.get('sharpe', 0)
        rsi = metrics.get('rsi', 50)
        corr = metrics.get('top_correlation', {})
        
        insight = s["analyzing"].format(asset_name)
        
        if rsi > 70:
            insight += s["rsi_overbought"]
        elif rsi < 30:
            insight += s["rsi_oversold"]

        if vol > 0.8:
            insight += s["vol_high"]
        elif vol < 0.2:
            insight += s["vol_low"]
            
        if ath_dist > -10:
            insight += s["ath_near"]
        elif ath_dist < -50:
            insight += s["ath_far"]
            
        if corr:
            insight += s["corr_coupling"].format(corr.get('Asset'), corr.get('Asset'), asset_name)
            
        # Advisory Section
        insight += s["strat_prob"]
        if rsi < 35 and vol < 0.3:
            insight += s["prob_accumulation"]
        elif rsi > 75:
            insight += s["prob_profit"]
        elif sharpe > 2.0:
            insight += s["prob_efficiency"]
        else:
            insight += s["prob_neutral"]

        return insight

    def analyze_sentiment(self, news: List[dict]) -> dict:
        """Heuristic sentiment analysis of news headlines."""
        if not news: return {"score": 0.5, "label": "Neutral"}
        
        pos_words = ["bullish", "growth", "surge", "adoption", "partnership", "gain", "breakout", "accumulate"]
        neg_words = ["bearish", "crash", "drop", "regulation", "fud", "scam", "hack", "sell", "dump"]
        
        score = 0
        for item in news:
            headline = item.get('title', "").lower()
            for w in pos_words:
                if w in headline: score += 1
            for w in neg_words:
                if w in headline: score -= 1
        
        # Clamp score between 0 and 1
        total_news = len(news)
        normalized = 0.5 + (score / (total_news * 2)) if total_news > 0 else 0.5
        normalized = max(0, min(1, normalized))
        
        label = "Greed" if normalized > 0.6 else "Fear" if normalized < 0.4 else "Neutral"
        return {"score": normalized, "label": label}

    def _ollama_generate(self, asset_name: str, metrics: dict, lang: str = "en") -> str:
        """Generate insight using a local Ollama instance."""
        try:
            language_context = "English" if lang == "en" else "Italian"
            prompt = f"""
            System: You are 'FinanceSensei', a strategic financial AI for an institutional investor.
            Language: Respond in {language_context}.
            Context: {asset_name} current metrics: {json.dumps(metrics)}.
            Task: Provide a 2-3 sentence strategic observation about this asset's current state and its relation to macro trends.
            Aesthetic: Professional, concise, awareness-focused.
            """
            response = requests.post(self.ollama_url, 
                                     json={"model": self.model, "prompt": prompt, "stream": False},
                                     timeout=5)
            if response.status_code == 200:
                return response.json().get('response', "Sensei is processing the signal...")
            return "Sensei signal interrupted. (Ollama connection failed)"
        except Exception:
            return "Sensei signal interrupted."
