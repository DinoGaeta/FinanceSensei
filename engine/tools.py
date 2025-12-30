
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from duckduckgo_search import DDGS

# --- Abstract Tool ---
class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description for the LLM prompt"""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> str:
        pass

# --- Tools Implementation ---

class WebSearchTool(Tool):
    @property
    def name(self):
        return "search_web"

    @property
    def description(self):
        return "Search the internet for real-time information. Param: 'query'"

    def execute(self, params: Dict[str, Any]) -> str:
        query = params.get("query")
        if not query: return "[Error] Missing query parameter"
        
        try:
            results = DDGS().text(query, max_results=3)
            # Format results
            output = ""
            for i, r in enumerate(results):
                output += f"{i+1}. {r['title']}: {r['body']}\nSource: {r['href']}\n\n"
            return output if output else "No results found."
        except Exception as e:
            return f"[Error] Search failed: {str(e)}"

class FileWriteTool(Tool):
    @property
    def name(self):
        return "write_file"
    
    @property
    def description(self):
        return "Write content to a file. Params: 'filename', 'content'. Note: Files are automatically saved in the 'reports/' folder."

    def execute(self, params: Dict[str, Any]) -> str:
        filename = params.get("filename")
        content = params.get("content")
        
        if not filename or not content: return "[Error] 'filename' and 'content' required"
        
        # Guardrail: Force storage into 'reports/' directory
        base_dir = "reports"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        # Strip potential path injection
        clean_filename = os.path.basename(filename)
        target_path = os.path.join(base_dir, clean_filename)

        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully saved to {target_path}"
        except Exception as e:
            return f"[Error] Write failed: {str(e)}"

class FileReadTool(Tool):
    @property
    def name(self):
        return "read_file"

    @property
    def description(self):
        return "Read content of a file. Param: 'filename'. Searches in 'reports/' by default."

    def execute(self, params: Dict[str, Any]) -> str:
        filename = params.get("filename")
        if not filename: return "[Error] 'filename' required"

        # Check in 'reports/' first
        target_path = os.path.join("reports", os.path.basename(filename))
        
        if not os.path.exists(target_path):
            # Fallback for full path if it's within project, but safer to stick to reports/
            target_path = filename

        if not os.path.exists(target_path):
            return f"[Error] File {filename} not found in reports archive."
            
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[Error] Read failed: {str(e)}"

class NeuralPredictTool(Tool):
    def __init__(self, analytics):
        self.analytics = analytics

    @property
    def name(self):
        return "predict_price"

    @property
    def description(self):
        return "Use neural machine learning to predict price direction (7D forecast). Param: 'ticker'. Example tickers: BTC/USDT, ATH/USDT."

    def execute(self, params: Dict[str, Any]) -> str:
        ticker = params.get("ticker")
        if not ticker: return "[Error] Ticker required"
        try:
            from .data_provider import DataProvider
            provider = DataProvider()
            data = provider.get_asset_data(ticker)
            if data.empty: return f"[Error] No data found for {ticker}"
            res = self.analytics.neural_core.predict_price_trend(data)
            if res["status"] == "Success":
                return f"Neural Forecast for {ticker}:\n- Target Price (7D): ${res['target_price']:.6f}\n- Predicted Trend: {res['change_pct']:.2f}%\n- ML Confidence: {res['confidence']*100:.1f}%"
            return f"[Error] {res['message']}"
        except Exception as e:
            return f"[Error] Neural prediction failed: {str(e)}"
