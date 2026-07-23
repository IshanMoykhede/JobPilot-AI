import sys
import requests

def test():
    try:
        # Login
        login_data = {
            "email": "email@example.com",
            "password": "password123"
        }
        res_login = requests.post("http://localhost:8000/auth/login", json=login_data)
        if res_login.status_code != 200:
            print("Login failed:", res_login.status_code, res_login.text)
            return
            
        token = res_login.json().get("access_token")
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        res = requests.get("http://localhost:8000/api/resume/a762af22-9e79-431b-9043-2f124e9b058b", headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
