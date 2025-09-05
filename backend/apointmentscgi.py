#!/usr/bin/env python3
import cgi
import cgitb; cgitb.enable()
import json
from datetime import datetime
import requests
from models import session
from appointments import create_appointment

# Enable CORS for API calls (optional, for local testing)
print("Content-Type: application/json\nAccess-Control-Allow-Origin: *\n")

form = cgi.FieldStorage()
data = json.loads(form.getvalue("data", "{}"))  # Expect JSON from fetch API

# Extract data (mimic HTML structure)
name = data.get("name")
phone = data.get("phone")
email = data.get("email", f"{name.replace(' ', '')}@mydesiresalon.com")
special_requests = data.get("specialRequests", "")
contact_method = data.get("contactMethod", "email")
attendant_id = data.get("attendant_id")
service = data.get("service")
date_str = data.get("date")
time_str = data.get("time")

# Validate required fields
if not all([name, phone, attendant_id, service, date_str, time_str]):
    print(json.dumps({"error": "Missing required fields"}))
    session.close()
    exit()

# Combine date and time
try:
    appointment_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%I %p")
except ValueError:
    print(json.dumps({"error": "Invalid date or time format"}))
    session.close()
    exit()

# User creation/login via API
user_data = {"name": name, "email": email, "password": "defaultpassword123"}
signup_response = requests.post("http://localhost:8000/signup", json=user_data)
user_id = None

if signup_response.status_code == 200:
    user_id = signup_response.json().get("user_id")
else:
    login_data = {"identifier": email, "password": "defaultpassword123"}
    login_response = requests.post("http://localhost:8000/login", json=login_data)
    if login_response.status_code == 200:
        user_id = login_response.json().get("user_id")

if not user_id:
    print(json.dumps({"error": "Failed to create or log in user"}))
    session.close()
    exit()

# Create appointment
result = create_appointment(email, attendant_id, service, appointment_time, contact_method)
if isinstance(result, Appointment):
    print(json.dumps({
        "success": True,
        "message": "Appointment booked!",
        "details": {
            "stylist": attendant_id,
            "service": service,
            "date": date_str,
            "time": time_str
        }
    }))
elif isinstance(result, str):
    print(json.dumps({"error": result}))

session.close()