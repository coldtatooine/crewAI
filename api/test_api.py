import requests
import time

def test_api():
    print("Testing API...")
    url = "http://localhost:8000"
    
    # 1. Health check
    try:
        response = requests.get(f"{url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        return

    # 2. Kickoff Crew
    print("\nKickoff Crew...")
    payload = {"topic": "Artificial Intelligence"}
    try:
        response = requests.post(f"{url}/crew/kickoff", json=payload)
        if response.status_code == 200:
            print("✅ Crew kickoff passed")
            print("Response:", response.json())
        else:
            print(f"❌ Crew kickoff failed: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api()
