import requests
from datetime import datetime, timedelta
import json

# The 4 locations we want to keep
ALLOWED_RINKS = ["raleigh", "cary", "wake forest", "invisalign"]

# Calculate 2-week date range
start_date = datetime.now().strftime("%Y-%m-%d")
end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

# Fetch from DaySmart API
url = f"https://apps.daysmartrecreation.com/dash/x/api/online/v1/calendar?event_types=16&start={start_date}&end={end_date}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    all_events = response.json().get('data', [])
except Exception:
    all_events = []

filtered_events = []

for event in all_events:
    # Convert the entire event data into one giant string of text so we can scan it easily
    event_text = json.dumps(event).lower()
    
    title = event.get('title', 'Public Admission')
    
    # Check if this event is Public Admission and belongs to our allowed rinks
    if "public admission" in event_text:
        # Determine which rink it belongs to by scanning the text
        matched_rink = None
        for rink in ALLOWED_RINKS:
            if rink in event_text:
                matched_rink = rink.title() if rink != "invisalign" else "Invisalign Arena"
                break
        
        # If it matches one of our rinks, save it!
        if matched_rink:
            filtered_events.append({
                "location": matched_rink,
                "title": title,
                "date": event.get('start_date') or start_date,
                "start_time": event.get('start_time') or "See Site",
                "end_time": event.get('end_time') or "See Site"
            })

# Save to the file your webpage reads
with open('schedule.json', 'w') as f:
    json.dump({
        "refreshed_at": datetime.now().strftime("%Y-%m-%d %I:%M %p"), 
        "events": filtered_events
    }, f, indent=2)
