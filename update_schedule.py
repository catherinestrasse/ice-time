import requests
from datetime import datetime, timedelta
import json

# The 4 locations we want to keep
ALLOWED_RINKS = ["Raleigh", "Cary", "Wake Forest", "Invisalign Arena"]

# Calculate 2-week date range
start_date = datetime.now().strftime("%Y-%m-%d")
end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

# Fetch from DaySmart API
url = f"https://apps.daysmartrecreation.com/dash/x/api/online/v1/calendar?event_types=16&start={start_date}&end={end_date}"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers)
    all_events = response.json().get('data', [])
except Exception:
    all_events = []

filtered_events = []

for event in all_events:
    title = event.get('title', '')
    # Check location data
    location = ""
    if event.get('site'):
        location = event.get('site', {}).get('name', '')
    elif event.get('facility_name'):
        location = event.get('facility_name', '')

    # Filter conditions: Must be Public Admission, and NOT Garner
    if "Public Admission" in title and any(rink.lower() in location.lower() for rink in ALLOWED_RINKS):
        filtered_events.append({
            "location": location,
            "title": title,
            "date": event.get('start_date'),
            "start_time": event.get('start_time'),
            "end_time": event.get('end_time')
        })

# Save to a file your web page can read
with open('schedule.json', 'w') as f:
    json.dump({"refreshed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "events": filtered_events}, f, indent=2)
