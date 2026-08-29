import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"
ts = int(time.time())

# Unique credentials
cust_a_email = f"m2_local_cust_a_{ts}@test.com"
cust_b_email = f"m2_local_cust_b_{ts}@test.com"
agent_email = f"m2_local_agent_{ts}@test.com"
password = "TestPassword123!"

test_cases = []

def log_test_case(name, aspect, status, details, response_code=None, response_body=None):
    test_cases.append({
        "name": name,
        "aspect": aspect,
        "status": status,
        "response_code": response_code,
        "details": details,
        "response_body": response_body
    })
    print(f"[{status}] {name} ({aspect}) - {details}")

def api_call(path, method="GET", data=None, token=None):
    url = BASE_URL + path
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    encoded = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=encoded, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            body = res.read().decode('utf-8')
            return res.status, json.loads(body) if body else {}, None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            parsed = json.loads(body)
        except:
            parsed = {"raw_html_snippet": body[:500]}
        return e.code, parsed, e
    except Exception as e:
        return 0, {"error": str(e)}, e

print("=== STARTING LOCAL M2 FLOW TEST ===")

# Step 1: Sign up accounts
api_call("/api/auth/register/", "POST", {"username": f"local_ca_{ts}", "email": cust_a_email, "password": password, "mobile": "1234567890", "role": "User"})
api_call("/api/auth/register/", "POST", {"username": f"local_cb_{ts}", "email": cust_b_email, "password": password, "mobile": "1234567890", "role": "User"})
api_call("/api/auth/register/", "POST", {"username": f"local_ag_{ts}", "email": agent_email, "password": password, "mobile": "1234567890", "role": "Agent"})

# --- ASPECT 1: LOGIN ---
code, body, _ = api_call("/api/auth/login/", "POST", {"email": cust_a_email, "password": password})
token_a = body.get("access")
if code == 200 and token_a:
    log_test_case("Customer A Login", "Login", "PASS", "Login succeeded.", code, body)
else:
    log_test_case("Customer A Login", "Login", "FAIL", f"Failed to login. Status: {code}", code, body)

code, body, _ = api_call("/api/auth/login/", "POST", {"email": cust_b_email, "password": password})
token_b = body.get("access")

code, body, _ = api_call("/api/auth/login/", "POST", {"email": agent_email, "password": password})
token_agent = body.get("access")
if code == 200 and token_agent:
    log_test_case("Support Agent Login", "Login", "PASS", "Login succeeded.", code, body)
else:
    log_test_case("Support Agent Login", "Login", "FAIL", f"Failed to login. Status: {code}", code, body)

# --- ASPECT 2: ROLE CHECK ---
if token_a:
    code, body, _ = api_call("/api/auth/me/", "GET", token=token_a)
    if code == 200 and body.get("role") == "User":
        log_test_case("Customer Role Check", "Role Check", "PASS", f"Retrieved role: {body.get('role')}", code, body)
    else:
        log_test_case("Customer Role Check", "Role Check", "FAIL", f"Incorrect role. Status: {code}", code, body)

if token_agent:
    code, body, _ = api_call("/api/auth/me/", "GET", token=token_agent)
    if code == 200 and body.get("role") == "Agent":
        log_test_case("Support Agent Role Check", "Role Check", "PASS", f"Retrieved role: {body.get('role')}", code, body)
    else:
        log_test_case("Support Agent Role Check", "Role Check", "FAIL", f"Incorrect role. Status: {code}", code, body)

# --- ASPECT 3: CUSTOMER CREATE TICKET ---
ticket_id = None
if token_a:
    ticket_payload = {
        "subject": "Unable to login to system",
        "description": "Getting error when entering portal.",
        "category": "Account",
        "priority": "High",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO"
    }
    code, body, _ = api_call("/api/tickets/", "POST", data=ticket_payload, token=token_a)
    if code in (200, 201):
        ticket_id = body.get("ticket", {}).get("ticket_id")
        log_test_case("Customer Create Ticket", "Create Ticket", "PASS", f"Ticket created. Ticket ID: {ticket_id}", code, body)
    else:
        log_test_case("Customer Create Ticket", "Create Ticket", "FAIL", f"Ticket creation failed. Status: {code}", code, body)

# --- ASPECT 4: TICKET QUEUE ---
if token_agent:
    code, body, _ = api_call("/api/tickets/queue/", "GET", token=token_agent)
    if code == 200:
        log_test_case("Agent View Ticket Queue", "View Ticket Queue", "PASS", "Agent successfully loaded the ticket queue without serialization error.", code, body)
    else:
        log_test_case("Agent View Ticket Queue", "View Ticket Queue", "FAIL", f"Server returned status {code}", code, body)

# --- ASPECT 5: VIEW TICKET DETAILS (AGENT & OTHER CUSTOMERS) ---
if token_a and ticket_id:
    code, body, _ = api_call(f"/api/tickets/{ticket_id}/", "GET", token=token_a)
    if code == 200:
        log_test_case("Customer View Ticket Details", "View Ticket", "PASS", "Customer successfully fetched their own ticket details.", code, body)
    else:
        log_test_case("Customer View Ticket Details", "View Ticket", "FAIL", f"Failed to retrieve ticket. Status: {code}", code, body)

if token_b and ticket_id:
    code, body, _ = api_call(f"/api/tickets/{ticket_id}/", "GET", token=token_b)
    if code == 403:
        log_test_case("Security Check: Block Customer B", "View Ticket (Authorization)", "PASS", "Customer B blocked with 403 Forbidden.", code, body)
    else:
        log_test_case("Security Check: Block Customer B", "View Ticket (Authorization)", "FAIL", f"Expected 403 Forbidden, got status {code}.", code, body)

if token_agent and ticket_id:
    code, body, _ = api_call(f"/api/tickets/{ticket_id}/", "GET", token=token_agent)
    if code == 200:
        log_test_case("Agent View Ticket Details", "View Ticket", "PASS", "Agent successfully fetched ticket details.", code, body)
    else:
        log_test_case("Agent View Ticket Details", "View Ticket", "FAIL", f"Agent blocked with status {code}", code, body)

# --- ASPECT 6: AGENT ACTIONS (UPDATE STATUS & RESOLVE) ---
if token_agent and ticket_id:
    code, body, _ = api_call(f"/api/tickets/{ticket_id}/status/", "PATCH", {"status": "In Progress"}, token=token_agent)
    if code == 200:
        log_test_case("Agent Update Status", "Update Status", "PASS", f"Status updated to: {body.get('transition', {}).get('to_status')}", code, body)
    else:
        log_test_case("Agent Update Status", "Update Status", "FAIL", f"Failed to update status. Status: {code}", code, body)

    code, body, _ = api_call(f"/api/tickets/{ticket_id}/status/", "PATCH", {"status": "Resolved", "resolution_summary": "Solved login issue"}, token=token_agent)
    if code == 200:
        log_test_case("Agent Resolve Ticket", "Resolve Ticket", "PASS", f"Ticket resolved. Status in body: {body.get('transition', {}).get('to_status')}", code, body)
    else:
        log_test_case("Agent Resolve Ticket", "Resolve Ticket", "FAIL", f"Failed to resolve ticket. Status: {code}", code, body)

with open(r"C:\Users\sahan\Downloads\Support-AI-Ticket-Management-Team\server\local_m2_test_results.json", "w", encoding="utf-8") as f:
    json.dump(test_cases, f, indent=2)

print("=== LOCAL M2 FLOW TEST COMPLETED ===")
