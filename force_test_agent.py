from engine.agent import AgentEngine
import os

def force_test():
    print("Testing Agent File Writing...")
    agent = AgentEngine(model_name="gpt-oss:120b-cloud")
    
    prompt = "Create a file named 'sensei_manifesto.txt' with the content: 'Strategic Alpha for everyone. Private and local.'"
    
    # We use a mocked callback to see the output
    def log(m): print(f"[AGENT LOG] {m}")
    
    result = agent.run(prompt, on_log=log)
    print("Test process complete.")
    
    if os.path.exists("sensei_manifesto.txt"):
        print("\nSUCCESS: 'sensei_manifesto.txt' was created!")
        with open("sensei_manifesto.txt", "r") as f:
            print(f"Content: {f.read()}")
    else:
        print("\n❌ FAILURE: File not found. The model might not have used the tool correctly.")

if __name__ == "__main__":
    force_test()
