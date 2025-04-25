import requests
import sys
import json

def test_ping():
    """Test if the backend server is running by calling the /ping endpoint."""
    try:
        response = requests.get('http://127.0.0.1:5000/ping')
        if response.status_code == 200:
            print("SUCCESS: Backend server is running!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"ERROR: Backend server returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend server at http://127.0.0.1:5000/ping")
        print("Make sure the Flask server is running with 'flask run' in the backend directory")
        return False

def test_login():
    """Test if the backend login endpoint is working."""
    try:
        data = {
            "userId": "00000000-0000-0000-0000-000000000000",
            "businessId": "1c8cde77-0306-42dd-a0b6-c366a07651ad",
            "businessApiKey": "default_api_key"
        }
        
        response = requests.post(
            'http://127.0.0.1:5000/api/save-config',
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"Login Status Code: {response.status_code}")
        
        try:
            print(f"Login Response: {response.json()}")
        except json.JSONDecodeError:
            print(f"Login Response (not JSON): {response.text}")
            
        if response.status_code == 200:
            print("SUCCESS: Login endpoint is working!")
            return True
        else:
            print(f"ERROR: Login endpoint returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend server at http://127.0.0.1:5000/api/save-config")
        return False

if __name__ == "__main__":
    print("Testing backend server connectivity...")
    ping_success = test_ping()
    
    if ping_success:
        print("\nTesting login endpoint...")
        login_success = test_login()
        
        if login_success:
            print("\nAll tests passed! The backend server is running and accessible.")
            sys.exit(0)
        else:
            print("\nLogin test failed. Check the error messages above.")
            sys.exit(1)
    else:
        print("\nPing test failed. Make sure the Flask server is running.")
        sys.exit(1)