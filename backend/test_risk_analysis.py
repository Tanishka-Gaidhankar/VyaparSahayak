"""
Quick test to verify the Risk Analysis endpoint with Cohere integration
"""
import requests
import json

# Test the risk analysis endpoint
url = "http://localhost:8000/risk-analysis"

# Use profile_id 1 (assuming it exists from previous setup)
payload = {
    "startup_profile_id": 1
}

print("Testing Risk Analysis endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n[SUCCESS] Risk Analysis completed!")
        print(f"Risk Level: {data.get('risk_level')}")
        print(f"AI Model Used: {data.get('ai_model')}")
        print(f"\nAI Action Plan Preview:")
        print(data.get('ai_action_plan', '')[:300] + "...")
    else:
        print(f"\n[ERROR] Request failed")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n[ERROR] Could not connect to backend server.")
    print("Make sure the backend is running on http://localhost:8000")
except Exception as e:
    print(f"\n[ERROR] {e}")
