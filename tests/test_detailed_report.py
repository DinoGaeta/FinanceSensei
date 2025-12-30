import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.agent import AgentEngine

def test_detailed_report():
    print("🤖 Testing Detailed Report Generation...")
    agent = AgentEngine(model_name="gpt-oss:120b-cloud")
    
    prompt = "Research the top 3 crypto trends for 2025 using web search and then save a detailed report named 'crypto_2025.md' with headers, bullet points, and a conclusion."
    
    def log(m): print(f"[AGENT LOG] {m}")
    
    result = agent.run(prompt, on_log=log)
    print(f"\nFinal Result: {result}")
    
    target = os.path.join("reports", "crypto_2025.md")
    if os.path.exists(target):
        print(f"\n✅ SUCCESS: '{target}' created!")
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"Content Length: {len(content)} characters")
            print("--- PREVIEW ---")
            print(content[:500] + "...")
    else:
        print(f"\n❌ FAILURE: '{target}' not found.")

if __name__ == "__main__":
    test_detailed_report()
