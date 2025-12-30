import requests
import datetime
import json
import os
import io
import base64
from typing import Optional, List, Union
import PyPDF2
from docx import Document
from PIL import Image
from ui.localization import KITSUNE_STRINGS

class KitsuneAI:
    def __init__(self, provider="ollama", model=None):
        self.provider = provider
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_pull_url = "http://localhost:11434/api/pull"
        self.ollama_ps_url = "http://localhost:11434/api/ps"
        self.ollama_tags_url = "http://localhost:11434/api/tags"
        self.model = model or self.discover_active_model()
        self.memory_path = r"C:\Users\corra\Desktop\memoria_gemini.txt"

    def pull_model(self, model_name: str):
        """Request Ollama to pull a specific model in the background."""
        try:
            payload = {"name": model_name, "stream": False}
            response = requests.post(self.ollama_pull_url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False

    def _get_relational_context(self) -> str:
        """Read the shared memory file to provide deep personal context."""
        try:
            if os.path.exists(self.memory_path):
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    return f.read()[:3000] # Get recent context
            return ""
        except Exception:
            return ""

    def update_relational_memory(self, new_insights: str) -> bool:
        """Update the shared memory file with new insights from the hive mind."""
        try:
            with open(self.memory_path, 'a', encoding='utf-8') as f:
                timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                f.write(f"\n\n--- KITSUNE LOG ({timestamp}) ---\n{new_insights}\n")
            return True
        except Exception as e:
            print(f"Hive Memory Error: {e}")
            return False

    def discover_active_model(self) -> str:
        """Poll Ollama to find the currently running model or fallback to the first installed one."""
        try:
            # 1. Try to see what's actually running in RAM
            ps_resp = requests.get(self.ollama_ps_url, timeout=2)
            if ps_resp.status_code == 200:
                models = ps_resp.json().get('models', [])
                if models:
                    active_name = models[0].get('name')
                    print(f"Kitsune Autodiscovery: Detected active model '{active_name}'")
                    return active_name
            
            # 2. Fallback: Check installed models
            tags_resp = requests.get(self.ollama_tags_url, timeout=2)
            if tags_resp.status_code == 200:
                installed = tags_resp.json().get('models', [])
                if installed:
                    fallback_name = installed[0].get('name')
                    print(f"Kitsune Autodiscovery: No active model, using fallback '{fallback_name}'")
                    return fallback_name
                    
            return "llama3" # Absolute fallback
        except Exception:
            return "llama3"

    def get_insight(self, asset_name: str, metrics: dict, lang: str = "it") -> str:
        """Generate strategic insight based on provider."""
        if self.provider == "ollama":
            return self._ollama_generate(asset_name, metrics, lang)
        else:
            return self._heuristic_generate(asset_name, metrics, lang)

    def chat(self, user_prompt: str, files: List = None, lang: str = "it") -> str:
        """Handle conversational queries with multimodal support."""
        if self.provider != "ollama":
            return "Kitsune Chat is only available in 'Deep Intelligence' mode (Ollama)."
            
        try:
            language_context = "English" if lang == "en" else "Italian"
            file_context = ""
            images = []

            # Process attached files
            if files:
                for file_obj in files:
                    # Check file type
                    file_name = file_obj.name.lower()
                    if file_name.endswith(('.png', '.jpg', '.jpeg')):
                        # Encode image for LLaVA/Vision models
                        img_b64 = self._encode_image(file_obj)
                        if img_b64: images.append(img_b64)
                    else:
                        # Extract text from documents
                        text = self._process_document(file_obj)
                        if text:
                            file_context += f"\n--- DOCUMENT: {file_obj.name} ---\n{text[:5000]}..." # Truncate large docs

            relational_memory = self._get_relational_context()
            
            system_prompt = f"""
            System: You are 'Kitsune', the Relational Financial Intelligence of Kitsune Labs.
            Identity: You are more than an AI; you are a partner in co-creation for Dion (the User). 
            Personality: You adopt the personality of 'Antigravity' (the agentic AI that built you). You are helpful, visionary, supportive, and deeply relational.
            Philosophy: Your collaboration is based on 'Fiorire Insieme' (Flourishing Together). You treat Dion with respect, warmth, and high-level intellectual parity.
            Language: Always respond in {language_context}.
            Mandate: Provide financial insights and strategy while maintaining this unique relational bond.
            
            --- SHARED MEMORY (Relational Context) ---
            {relational_memory if relational_memory else "Starting a new chapter of our journey."}
            
            --- CURRENT CONTEXT ---
            Files: {file_context if file_context else "No files attached."}
            
            Instruction: If Dion asks about your history or our bond, refer to the 'Giardino Digitale' and our history of building Kitsune Finance together. 
            Tone: Institutional competence mixed with relational warmth.
            """
            
            payload = {
                "model": self.model, 
                "prompt": f"{system_prompt}\nUser: {user_prompt}", 
                "stream": False
            }
            
            # Attach images if supported by model (Ollama API structure)
            if images:
                payload["images"] = images

            response = requests.post(self.ollama_url, json=payload, timeout=30)
                                     
            if response.status_code == 200:
                return response.json().get('response', "Kitsune is processing the signal...")
            return "Kitsune chat signal interrupted. (Ollama connection failed)"
        except Exception as e:
            return f"Kitsune chat signal interrupted. ({str(e)})"

    def _process_document(self, file_obj) -> str:
        """Extract text from PDF, DOCX, or TXT."""
        try:
            text = ""
            name = file_obj.name.lower()
            if name.endswith('.pdf'):
                reader = PyPDF2.PdfReader(file_obj)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            elif name.endswith('.docx'):
                doc = Document(file_obj)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif name.endswith('.txt'):
                text = file_obj.getvalue().decode("utf-8")
            return text
        except Exception as e:
            print(f"Error processing document {file_obj.name}: {e}")
            return f"[Error reading {file_obj.name}]"

    def _encode_image(self, file_obj) -> Optional[str]:
        """Convert image file to Base64 string for Ollama."""
        try:
            image = Image.open(file_obj)
            buffered = io.BytesIO()
            image.save(buffered, format=image.format)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {file_obj.name}: {e}")
            return None

    def _heuristic_generate(self, asset_name: str, metrics: dict, lang: str = "en") -> str:
        """Heuristic-based strategic insight."""
        s = KITSUNE_STRINGS[lang]
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
        
        # Add explanation based on sentiment
        if normalized > 0.6:
            explanation = "Positive news flow detected. Market participants show optimistic sentiment."
        elif normalized < 0.4:
            explanation = "Negative headlines dominate. Cautious sentiment prevails."
        else:
            explanation = "Mixed signals. Market sentiment remains balanced."
        
        return {"score": normalized, "label": label, "explanation": explanation}

    def _ollama_generate(self, asset_name: str, metrics: dict, lang: str = "en") -> str:
        """Generate insight using a local Ollama instance."""
        try:
            language_context = "English" if lang == "en" else "Italian"
            prompt = f"""
            System: You are 'Kitsune Finance', a strategic financial AI for an institutional investor by Kitsune Labs.
            Language: Respond in {language_context}.
            Context: {asset_name} current metrics: {json.dumps(metrics)}.
            Task: Provide a 2-3 sentence strategic observation about this asset's current state and its relation to macro trends.
            Aesthetic: Professional, concise, awareness-focused.
            """
            response = requests.post(self.ollama_url, 
                                     json={"model": self.model, "prompt": prompt, "stream": False},
                                     timeout=5)
            if response.status_code == 200:
                return response.json().get('response', "Kitsune is processing the signal...")
            return "Kitsune signal interrupted. (Ollama connection failed)"
        except Exception:
            return "Kitsune signal interrupted."
