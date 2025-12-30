
from engine.agent import AgentEngine
import os

def test_agent():
    print("🚀 Starting Agent Test...")
    agent = AgentEngine(model_name="gpt-oss:120b-cloud")
    
    # Test 1: Simple reasoning (no tools needed)
    print("\n--- Test 1: Simple Question ---")
    resp1 = agent.run("Who are you?", on_log=print)
    print(f"Final Response: {resp1}")
    
    # Test 2: Web Search Tool
    print("\n--- Test 2: Web Search ---")
    resp2 = agent.run("Search for the current price of Bitcoin and tell me the source.", on_log=print)
    print(f"Final Response: {resp2}")

    # Test 3: File Read Tool
    print("\n--- Test 3: File Read ---")
    # Create a dummy file first
    with open("test_input.txt", "w") as f:
        f.write("The secret code is 12345")
        
    resp3 = agent.run("Read the file 'test_input.txt' and tell me the secret code.", on_log=print)
    print(f"Final Response: {resp3}")
    
    # Cleanup
    if os.path.exists("test_input.txt"):
        os.remove("test_input.txt")

if __name__ == "__main__":
    test_agent()
