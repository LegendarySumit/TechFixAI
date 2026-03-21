import json
import sys
import requests

BASE = "http://127.0.0.1:8010"
EMAIL = "rerun_user@example.com"
PASSWORD = "ReRunPass123!"

s = requests.Session()

def post_form(path, data):
    return s.post(BASE + path, data=data, timeout=20, allow_redirects=True)

# Signup (idempotent)
signup_payload = {
    "email": EMAIL,
    "username": "rerunuser",
    "full_name": "Rerun User",
    "password": PASSWORD,
    "confirm_password": PASSWORD,
}
r_signup = post_form("/signup", signup_payload)
print(f"SIGNUP_STATUS={r_signup.status_code}")

# Login
r_login = post_form("/login", {"email": EMAIL, "password": PASSWORD})
print(f"LOGIN_STATUS={r_login.status_code}")

# Verify protected pages (no admin redirect expected)
r_dash = s.get(BASE + "/dashboard", timeout=20, allow_redirects=False)
r_dev = s.get(BASE + "/developers", timeout=20, allow_redirects=False)
print(f"DASHBOARD_STATUS={r_dash.status_code}")
print(f"DEVELOPERS_STATUS={r_dev.status_code}")
print(f"DASHBOARD_LOCATION={r_dash.headers.get('Location','')}")
print(f"DEVELOPERS_LOCATION={r_dev.headers.get('Location','')}")

# Upload tiny wav payload
files = {
    "audio": ("a.wav", b"RIFF$\x00\x00\x00WAVEfmt ", "audio/wav")
}
data = {
    "environment": "production"
}
r_upload = s.post(BASE + "/api/voice/upload", files=files, data=data, timeout=40)
print(f"UPLOAD_STATUS={r_upload.status_code}")
if r_upload.status_code != 200:
    print("UPLOAD_BODY=" + r_upload.text[:500])
    sys.exit(1)

upload_json = r_upload.json()
conversation_id = upload_json.get("conversation_id")
print(f"CONVERSATION_ID={conversation_id}")
if not conversation_id:
    print("NO_CONVERSATION_ID")
    sys.exit(1)

# Poll status
ticket_number = None
for i in range(15):
    r_status = s.get(f"{BASE}/api/voice/status/{conversation_id}", timeout=20)
    if r_status.status_code == 200:
        j = r_status.json()
        ticket_number = j.get("ticket_number")
        if ticket_number:
            break
print(f"TICKET_NUMBER={ticket_number}")
if not ticket_number:
    print("NO_TICKET_NUMBER")
    sys.exit(1)

# Delete as owner
r_delete = s.delete(f"{BASE}/api/tickets/{ticket_number}", timeout=20)
print(f"DELETE_AS_OWNER_STATUS={r_delete.status_code}")
print("DELETE_AS_OWNER_BODY=" + r_delete.text[:300])
