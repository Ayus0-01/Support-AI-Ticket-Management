import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"
ts = int(time.time())

cust_a_email = f"c_a_{ts}@test.com"
cust_b_email = f"c_b_{ts}@test.com"
agent_email = f"agent_{ts}@test.com"
password = "TestPassword123!"

def test_step(name, path, method, data):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    encoded = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"[{name}] SUCCESS - Status: {res.status}")
            body = res.read().decode('utf-8')
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"[{name}] FAILED - Status: {e.code}")
        print("  Response:", body)
        return {}
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
        return {}

# 1. Register Customer A
test_step("Register Customer A", "/api/auth/register/", "POST", {
    "username": f"ca_{ts}", "email": cust_a_email, "password": password, "mobile": "1234567890", "role": "User"
})

# 2. Register Customer B
test_step("Register Customer B", "/api/auth/register/", "POST", {
    "username": f"cb_{ts}", "email": cust_b_email, "password": password, "mobile": "1234567890", "role": "User"
})

# 3. Register Agent
test_step("Register Agent", "/api/auth/register/", "POST", {
    "username": f"ag_{ts}", "email": agent_email, "password": password, "mobile": "1234567890", "role": "Agent"
})

# 4. Login Customer A
test_step("Login Customer A", "/api/auth/login/", "POST", {
    "email": cust_a_email, "password": password
})

# 5. Login Customer B
test_step("Login Customer B", "/api/auth/login/", "POST", {
    "email": cust_b_email, "password": password
})

# 6. Login Agent
test_step("Login Agent", "/api/auth/login/", "POST", {
    "email": agent_email, "password": password
})
