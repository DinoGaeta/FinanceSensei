import requests
import datetime

class ReportGenerator:
    def __init__(self, ai_engine):
        self.ai = ai_engine
        
    def generate_weekly_report(self, assets_data: list, lang: str = "it") -> str:
        """
        Generates a professional financial report based on a list of asset data.
        assets_data: list of dicts reflecting {ticker, price, rsi, volatility, sentiment}
        """
        date_str = datetime.date.today().strftime("%d %B %Y")
        language_ctx = "Italian" if lang == "it" else "English"
        
        # Build the data context for the AI
        data_summary = ""
        for asset in assets_data:
            data_summary += f"- {asset['ticker']}: Price ${asset['price']:,.2f}, RSI {asset['rsi']:.1f}, Vol {asset['vol']:.1%}, Sentiment {asset['sentiment']}\n"
            
        system_prompt = f"""
        System: You are 'FinanceSensei', a top-tier institutional financial strategist.
        Task: Generate a 'Weekly Alpha Recap' report.
        Tone: Deeply professional, objective, and institutional.
        Language: ALWAYS respond in {language_ctx}.
        Structure:
        1. Macro Outlook: A 2-paragraph synthesis of the current market regime.
        2. Top Alpha Signals: Highlight the 2 most interesting assets from the data provided.
        3. Risk Assessment: Briefly mention thematic risks (liquidity, volatility).
        4. Conclusion: A final closing strategic thought.
        """
        
        user_prompt = f"Data Summary for this week ({date_str}):\n{data_summary}\n\nGenerate the complete report in Markdown."
        
        # Reuse SenseiAI's chat or direct ollama call
        # Since ReportGenerator needs a longer synthesis, we use a longer timeout
        try:
            if self.ai.provider == "ollama":
                response = requests.post(self.ai.ollama_url, 
                                         json={"model": self.ai.model, "prompt": f"{system_prompt}\nUser: {user_prompt}", "stream": False},
                                         timeout=30)
                if response.status_code == 200:
                    report_content = response.json().get('response', "Failed to generate report content.")
                else:
                    report_content = "Connection to AI Engine lost during synthesis."
            else:
                report_content = self._heuristic_report(assets_data, lang)
        except Exception as e:
            report_content = f"Error during report generation: {str(e)}"
            
        return f"# FinanceSensei Weekly Alpha Report\n**Date: {date_str}**\n\n---\n\n{report_content}"

    def _heuristic_report(self, assets_data, lang):
        if lang == "it":
            return "Note: L'intelligenza profonda (Ollama) è necessaria per la sintesi dei report settimanali. Ecco un riassunto dei dati:\n" + \
                   "\n".join([f"- {a['ticker']}: RSI {a['rsi']:.1f}" for a in assets_data])
        return "Note: Deep Intelligence (Ollama) is required for strategic report synthesis. Data summary:\n" + \
               "\n".join([f"- {a['ticker']}: RSI {a['rsi']:.1f}" for a in assets_data])
