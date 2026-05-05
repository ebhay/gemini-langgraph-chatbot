import requests
import json

BASE_URL = "http://localhost:8000"

def test_signup():
    print("\n=== Testing Signup ===")
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get("access_token")

def test_login():
    print("\n=== Testing Login ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get("access_token")

def test_chat(token):
    print("\n=== Testing Chat ===")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_input": "Hello, my name is John and I am 25 years old",
            "session_id": "default"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_profile(token):
    print("\n=== Testing Get Profile ===")
    response = requests.get(
        f"{BASE_URL}/api/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_hospital_finder(token):
    print("\n=== Testing Hospital Finder ===")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_input": "Find hospitals in Delhi",
            "session_id": "default"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_reminder(token):
    print("\n=== Testing Reminder ===")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_input": "Remind me to drink water",
            "session_id": "default"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_sessions(token):
    print("\n=== Testing Get Sessions ===")
    response = requests.get(
        f"{BASE_URL}/api/sessions",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_notifications(token):
    print("\n=== Testing Get Notifications ===")
    import time
    time.sleep(12)
    response = requests.get(
        f"{BASE_URL}/api/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Starting API Tests...")
    print(f"Base URL: {BASE_URL}")
    
    try:
        token = test_login()
    except:
        token = test_signup()
    
    if token:
        test_chat(token)
        test_profile(token)
        test_hospital_finder(token)
        test_reminder(token)
        test_sessions(token)
        test_notifications(token)
    else:
        print("Failed to get authentication token")
