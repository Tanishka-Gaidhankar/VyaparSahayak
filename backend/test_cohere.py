import os
import json
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def test_cohere_connection():
    cohere_key = os.getenv("COHERE_API_KEY")
    print(f"Checking COHERE_API_KEY: {cohere_key[:10]}..." if cohere_key else "COHERE_API_KEY NOT SET")
    
    if not cohere_key or "your_cohere_api_key_here" in cohere_key:
        print("[ERROR] Valid COHERE_API_KEY not found in .env")
        return

    try:
        import cohere
        client = cohere.ClientV2(api_key=cohere_key)
        
        print("Testing Cohere chat completion...")
        response = client.chat(
            model="command-r-plus-08-2024",
            messages=[{"role": "user", "content": "Hello, this is a test from VyaaparSahayak. Just say 'Success!'"}]
        )
        
        content = response.message.content[0].text
        print(f"Response: {content}")
        
        if "Success" in content:
            print("[SUCCESS] Cohere Integration Verified!")
        else:
            print("[WARNING] Response received but didn't contain expected text.")
            
    except Exception as e:
        print(f"[ERROR] Connection Failed: {e}")

if __name__ == "__main__":
    test_cohere_connection()
