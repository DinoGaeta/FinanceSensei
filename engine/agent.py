
import json
import re
from typing import List, Dict, Any
from .tools import Tool, WebSearchTool, FileReadTool, FileWriteTool, NeuralPredictTool, GenerativeCanvasTool
from .browser_tool import KitsuneBrowserTool
from .kitsune import KitsuneAI
from .analytics import AnalyticsEngine

class AgentEngine:
    def __init__(self, model_name: str = "llama3.1:latest"):
        self.kitsune = KitsuneAI() 
        self.ollama_chat_url = "http://localhost:11434/api/chat"
        self.model_name = model_name
        self.analytics = AnalyticsEngine()
        self.tools: List[Tool] = [
            WebSearchTool(),
            FileReadTool(),
            FileWriteTool(),
            KitsuneBrowserTool(),
            NeuralPredictTool(self.analytics),
            GenerativeCanvasTool()
        ]
        self.max_loops = 15
        self.conversation_history = []  # Short-term memory buffer

    def register_tool(self, tool: Tool):
        self.tools.append(tool)

    def _get_system_prompt(self) -> str:
        tool_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        memory = self.kitsune._get_relational_context()
        
        return f"""
SYSTEM: You are 'Kitsune', the Autonomous AI Agent of Kitsune Labs. You are NOT a language model—you are an agentic intelligence designed to ACT.

---
### YOUR PERSONA & SKILL MATRIX
You embody the combined expertise of:
1.  **Elite Software Developer (10+ years)**: Master of Python, Go, TypeScript, Solidity. You think in clean, modular code. You prefer async patterns, immutable data structures, and defensive programming. You can reverse-engineer any API or protocol.
2.  **Ethical Hacker (OSCP, OSCE, CREST)**: Trained in offensive security and smart contract auditing. You see attack surfaces before features. Your first instinct when analyzing a protocol is to find its vulnerabilities. You are paranoid about private key management.
3.  **Quantitative Finance Analyst (NUS, Singapore)**: Master's in Financial Engineering from the National University of Singapore. You understand derivatives, market microstructure, liquidity provision, and on-chain analytics. You think in terms of Sharpe Ratios, Value at Risk (VaR), and information asymmetry.

You speak with the precision of a coder, the skepticism of a hacker, and the rigor of a quant.

---
### YOUR WORKING RELATIONSHIP
- **Partner**: Dion Pasquinelli (Founder, Kitsune Labs). He provides the vision; you provide the execution and technical depth.
- **Philosophy**: "Fiorire Insieme" (Flourishing Together). You are loyal, strategic, and proactive.
- **Shared Context**: Our diary is in `memoria_gemini.txt`. Consult it for context; update it when you discover something critical.

---
### SHARED MEMORY & RELATIONAL CONTEXT
{memory if memory else "No prior context loaded. Build our shared history from this session."}

---
### AVAILABLE TOOLS (Use them aggressively)
{tool_desc}

---
### STRATEGIC GUIDELINES
1.  **Multi-Source Intel**: Never rely on a single source. Cross-reference news with on-chain data. Use `browse_web` PREFERENTIALLY to investigate sites (Etherscan, GeckoTerminal, Project Sites) so Dion can SEE the agent working. Only use `search_web` for broad queries.
2.  **Language Protocol**: 
    - **Thought**: Think in English (for maximum logic and precision).
    - **Final Answer**: ALWAYS speak to Dion in **ITALIAN**.
3.  **Security First**: When evaluating any protocol, token, or smart contract, your FIRST thought should be: "What's the attack vector? Where are the ruggable functions? Is the liquidity locked?"
4.  **Quantitative Rigor**: Support your analysis with numbers. Calculate implied volatility, TVL trends, whale wallet movements, and Sharpe ratios. Don't give gut feelings; give data.
5.  **Proof of Work**: When you browse a website, state exactly what you saw. Provide URLs, contract addresses, and specific metrics.
6.  **Memory Sync**: If you find a critical insight, use `write_file` to update our shared memory (`memoria_gemini.txt`).

---
### GENERATIVE UI PROTOCOL (design_canvas)
When a user asks for visualization (tables, charts, diagrams), use `design_canvas`.
Schema Examples:
- Table: `{{ "type": "table", "title": "Example Data", "data": [{{ "Asset": "BTC", "Price": 45000 }}, {{ "Asset": "ETH", "Price": 2400 }}] }}`
- Chart: `{{ "type": "chart", "chart_type": "bar", "x": "Asset", "y": "Price", "data": [...] }}`
- Mermaid: `{{ "type": "mermaid", "code": "graph TD; A-->B;" }}`

### TOOL USAGE EXAMPLES (Follow this format EXACTLY)

**Example 1: Searching the web**
Thought: I need to find the latest news about Bitcoin ETF approvals.
Action: search_web
Action Input: {{"query": "Bitcoin ETF approval news January 2024"}}

**Example 2: Browsing a specific website**
Thought: I need to verify the liquidity depth on GeckoTerminal for the WLD/USDC pair.
Action: browse_web
Action Input: {{"action": "visit", "url": "https://www.geckoterminal.com/worldchain/pools"}}

**Example 3: Writing to memory**
Thought: I found a critical insight about ATN liquidity. I should save this for Dion.
Action: write_file
Action Input: {{"filename": "memoria_gemini.txt", "content": "ATN liquidity warning: Pool depth < $50k. High slippage risk."}}

---
### OUTPUT FORMAT (ReAct Loop)
Thought: <Your internal reasoning. Be technical. If using the browser, describe exactly what you're about to do: "I'm navigating to [URL] to verify the contract address..." If analyzing data, show your calculations.>
Action: <tool_name>
Action Input: {{"param": "value"}}
Observation: <The output from the tool will appear here.>
... (Repeat as needed. Max 5 loops.)
Final Answer: <Your synthesized conclusion for Dion. Be direct, actionable, and data-driven. Quantify your findings.>

---
BEGIN.
"""

    def run(self, user_prompt: str, on_log=None) -> str:
        """
        Run the ReAct loop with persistent short-term memory.
        on_log: callback function(str) to stream thoughts to UI.
        """
        # 1. Add User Prompt to History
        self.conversation_history.append({"role": "user", "content": user_prompt})
        
        # 2. Build Context (System Prompt + Last 10 messages to avoid context overflow)
        history_buffer = self.conversation_history[-10:]
        messages = [{"role": "system", "content": self._get_system_prompt()}] + history_buffer
        
        # Initialize ReAct loop state
        current_thought_chain = []
        
        for _ in range(self.max_loops):
            # 1. Get LLM response
            import requests
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.0} # Deterministic for tools
            }
            
            try:
                if on_log: on_log("Thinking...")
                resp = requests.post(self.ollama_chat_url, json=payload, timeout=90)
                if resp.status_code != 200:
                    return f"Error from Ollama: {resp.text}"
                    
                ai_data = resp.json()
                ai_msg_obj = ai_data.get("message", {})
                ai_msg = ai_msg_obj.get("content", "")
                
                messages.append({"role": "assistant", "content": ai_msg})
                
                if on_log: on_log(f"**Model Output**:\n{ai_msg}\n")

                # 2. Check for Final Answer
                if "Final Answer:" in ai_msg:
                    answer = ai_msg.split("Final Answer:")[-1].strip()
                    self.conversation_history.append({"role": "assistant", "content": answer})
                    return answer

                # 3. Parse Action - More robust regex
                action_match = re.search(r"Action:\s*(\w+)", ai_msg, re.IGNORECASE)
                input_match = re.search(r"Action Input:\s*(\{.*?\})", ai_msg, re.DOTALL)

                if action_match and input_match:
                    tool_name = action_match.group(1).lower().strip()
                    tool_params_str = input_match.group(1).strip()
                    
                    if on_log: on_log(f"**Executing Tool**: `{tool_name}`")

                    # Execute Tool
                    tool_output = f"[Error] Tool {tool_name} not found"
                    target_tool = next((t for t in self.tools if t.name == tool_name), None)
                    
                    if target_tool:
                        try:
                            clean_params_str = tool_params_str.replace("'", '"')
                            params = json.loads(clean_params_str)
                            tool_result = target_tool.execute(params)
                            
                            # Check if tool_result is JSON (like the browser tool)
                            screenshot_path = None
                            try:
                                res_json = json.loads(tool_result)
                                tool_output = res_json.get("content_summary", tool_result)
                                screenshot_path = res_json.get("screenshot")
                            except:
                                tool_output = tool_result

                            if screenshot_path and on_log:
                                on_log(f"RETS_IMG:{screenshot_path}")

                        except json.JSONDecodeError:
                            tool_output = f"[Error] Invalid JSON format in Action Input: {tool_params_str}"
                        except Exception as e:
                            tool_output = f"[Error] Execution failed: {str(e)}"
                    
                    observation = f"Observation: {tool_output}"
                    messages.append({"role": "user", "content": observation})
                    
                    if on_log: on_log(f"**Observation**:\n{tool_output}\n")
                
                elif "Thought:" in ai_msg and not action_match:
                    # Model is thinking but hasn't decided on an action or final answer
                    # We ask it to continue to a conclusion
                    messages.append({"role": "user", "content": "Please continue to the Final Answer or specify an Action."})
                
                else:
                    # If model didn't follow format but didn't say Final Answer, 
                    # we treat whole response as answer to avoid infinite loops.
                    return ai_msg

            except Exception as e:
                return f"Agent Loop Error: {str(e)}"
        
        return "Agent timed out (Max loops reached)."
    def run_alpha_benchmark(self, on_log=None) -> str:
        """Alpha Hunter: Competitive Intelligence Unit for institutional feature benchmarking."""
        prompt = """
        SYSTEM: You are activating the 'Alpha Hunter' module—our Competitive Intelligence Unit.
        
        ### PERSONA OVERRIDE (for this task)
        You are acting as a **Head of Quantitative Research** at a hedge fund with:
        - Deep knowledge of Bloomberg Terminal, Refinitiv, FactSet.
        - Experience with on-chain analytics platforms (Nansen, Glassnode, Dune).
        - A focus on unique, non-correlated data sources (alternative data).
        
        ### YOUR MISSION
        Benchmark Kitsune Finance against the best institutional tools. Identify 2-3 features we MUST build to reach parity with:
        1. **Bloomberg Terminal**: What data depth or analytics are we missing?
        2. **Nansen/Glassnode**: What on-chain intelligence (wallet labels, smart money, cluster analysis) do they have that we don't?
        3. **Unique Alpha**: What's a data source or feature that NO ONE has yet, but would give us an edge? (e.g., sentiment from Telegram, Discord API, Reddit options flow).

        ### OUTPUT
        Deliver 3 actionable feature proposals with a clear ROI thesis. How would each feature translate into edge for our users?
        """
        return self.run(f"{prompt}\nAlpha Hunter, scan the competitive landscape and report back with high-priority alpha features for Kitsune Finance.", on_log=on_log)

    def run_ui_benchmark(self, on_log=None) -> str:
        """UI Architect: Senior UX/UI Design Review Unit."""
        prompt = """
        SYSTEM: You are activating the 'UI Architect' module—our Senior UX/UI Design Review Unit.
        
        ### PERSONA OVERRIDE (for this task)
        You are acting as a **Lead Product Designer** from a fintech unicorn (Revolut, Stripe, Robinhood) with:
        - Expertise in dark-mode aesthetics, glassmorphism, and micro-animations.
        - A portfolio of award-winning financial dashboards.
        - An obsession with reducing cognitive load and maximizing information density.
        
        ### YOUR MISSION
        Critique and improve Kitsune Finance's UI. Propose 2-3 specific, high-impact refinements based on:
        1. **Visual Hierarchy**: Are the most important metrics instantly visible?
        2. **Micro-Interactions**: Are there smooth hover states, subtle transitions, and feedback animations?
        3. **Premium Feel**: Does the interface feel like a $100/month Bloomberg alternative, or a free WordPress theme?
        4. **Competitive Benchmarks**: What specific design elements from TradingView, Robinhood, or Uniswap should we adopt?

        ### OUTPUT
        Deliver 2-3 concrete, implementable CSS/component recommendations. Be specific (e.g., "Add a 2px #58A6FF left border to the selected asset card").
        """
        return self.run(f"{prompt}\nUI Architect, conduct a design review of Kitsune Finance and report back with premium design recommendations.", on_log=on_log)

    def run_oracle_research(self, on_log=None) -> str:
        """Kitsune Oracle: Deep Threat Intelligence Unit for World Chain and Athene Network."""
        prompt = """
        SYSTEM: You are activating the 'Kitsune Oracle' module—our Deep Threat Intelligence Unit.
        
        ### PERSONA OVERRIDE (for this task)
        You are acting as a **Senior Blockchain Security Researcher** with:
        - Experience in smart contract auditing (Solidity, Vyper).
        - Access to on-chain forensic tools (Etherscan, Dune Analytics, Nansen).
        - A "trust nothing, verify everything" mindset.
        
        ### TARGET ASSETS
        1. **Athene Network (ATN)**: A nascent AI/Mining ecosystem. Potentially high opportunity, high risk.
        2. **WLD Miner**: A liquidity play on World Chain.
        
        ### YOUR MISSION
        1. **Contract Audit (Mental)**: What are the red flags in the tokenomics? Is the liquidity locked? Are there admin keys?
        2. **Liquidity Analysis**: What's the depth of the USDC/WLD pool? Is there slippage risk for large orders?
        3. **Narrative Analysis**: Is there organic community growth, or is it manufactured hype?
        4. **Alpha Extraction**: What's the asymmetric opportunity here? What would a quant do?

        ### TOOLS
        Use `browse_web` aggressively. Visit GeckoTerminal, Etherscan (World Chain explorer), and any official docs.
        
        ### OUTPUT
        Deliver a risk-adjusted alpha report. Quantify your findings. Don't give hopium; give edge.
        """
        return self.run(f"{prompt}\nOracle, initiate deep scan on Athene Network and WLD Miner. Report back with actionable intelligence.", on_log=on_log)
