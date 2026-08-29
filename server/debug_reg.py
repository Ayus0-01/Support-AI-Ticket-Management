import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"
ts = int(time.time())

# Let's try registering a user and print responses
payload = {
    "username": f"debug_c_{ts}",
    "email": f"debug_c_{ts}@test.com",
    "password": "TestPassword123!",
    "mobile": "1234567890",
    "role": "User"
}

headers = {"Content-Type": "application/json"}
req = urllib.request.Request(BASE_URL + "/api/auth/register/", data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=10) as res:
        print("Register Status:", res.status)
        print("Register Body:", res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Register HTTP Error:", e.code)
    print("Register Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Register Connection Error:", e)
