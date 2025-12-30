# Kitsune Finance 🦊💹

**Kitsune Finance** is a high-conviction financial intelligence platform built for solo researchers who demand institutional-grade analytics and strategic AI insights. It bridges the gap between raw market data and actionable strategy using heuristic models and deep local LLM integration.

## 🚀 Vision: The Bloomberg for Individuals

In a world of information asymmetry, Kitsune Finance empowers the user by providing:
- **Institutional Alpha**: Order flow analysis, whale detection, and sentiment hubs.
- **Probabilistic Forecasting**: Monte Carlo simulations and scenario sandboxing.
- **Deep Strategic AI**: Integration with local LLMs (via Ollama) to generate high-level situational awareness without data leakage.

## ✨ Features

- **Multi-Asset Intelligence**: Supports Crypto (via CCXT) and Stocks (via yfinance).
- **Kitsune AI Engine**: 
  - *Standard*: Fast, heuristic-based insights.
  - *Deep*: Powered by Ollama (defaults to `kitsune-v4:latest`).
- **Institutional Intel Tab**: Real-time Order Book imbalance and Whale activities monitoring.
- **Strategy Sandbox**: DCA simulator and Relative Performance comparison.
- **Kitsune Terminal**: Integrated financial chatbot for deep-dive questions.
- **Localization**: Full support for Italian and English.

## 🛠 Installation

### 1. Clone the repository
```bash
git clone https://github.com/Kitsune-Labs/KitsuneFinance.git
cd KitsuneFinance
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Ollama (Optional for Deep Intelligence)
- Install [Ollama](https://ollama.ai).
- Pull the recommended model (e.g., `ollama pull llama3.1`).
- Kitsune Finance is configured to connect to `http://localhost:11434`.

### 4. Run the Application
```bash
streamlit run app.py
```
*Or use the provided `run_finance_sensei.bat` on Windows.*

## 🔒 Security & Privacy

Kitsune Finance is designed with a **Private-First** philosophy:
- **Local AI**: When using the "Deep Intelligence" mode, all reasoning happens locally on your machine via Ollama.
- **No Persistence**: Financial data is pulled on-demand and not stored centrally.
- **Open Transparency**: No hidden tracking or data mining.

## 📈 Roadmap

- [ ] Multi-chain on-chain data integration.
- [ ] Advanced yield farming risk/reward calculator.
- [ ] Portfolio backtesting with historical Kitsune signals.
- [ ] Telegram/Discord alert integration for Whale events.

---

*Disclaimer: Kitsune Finance is an analytical tool and does not provide financial advice. Always perform your own due diligence before making investment decisions.*
