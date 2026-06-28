import requests
from datetime import datetime, timedelta
import json

# Define exactly how we want the names to appear on your website
RINKS_MAPPING = {
    "raleigh": "Polar Ice Raleigh",
    "cary": "Polar Ice Cary",
    "wake forest": "Polar Ice Wake Forest",
    "invisalign": "Invisalign Arena"
}

# Calculate 2-week date range
start_date = datetime.now().strftime("%Y-%m-%d")
end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

# This updated URL requests the calendar data across all company locations at once
url = f"https://apps.daysmartrecreation.com/dash/x/api/online/v1/calendar?start={start_date}&end={end_date}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    # DaySmart sometimes nests the events under 'data' or 'events'
    response_data = response.json()
    all_events = response_data.get('data', []) if isinstance(response_data.get('data'), list) else response_data.get('events', [])
    
    # If the response is a dictionary of days, flatten it into a single list
    if isinstance(all_events, dict):
        flattened = []
        for day, events in all_events.items():
            if isinstance(events, list):
                flattened.extend(events)
        all_events = flattened
except Exception:
    all_events = []

filtered_events = []

for event in all_events:
    # Convert the entire single event to text to search it thoroughly
    event_text = json.dumps(event).lower()
    
    title = event.get('title', 'Public Admission Session')
    
    # Check for the words "Public Admission" anywhere in the event title or description
    if "public admission" in title.lower() or "public admission" in event_text:
        
        # Figure out which of our 4 specific rinks this event belongs to
        matched_location_name = None
        for keyword, full_name in RINKS_MAPPING.items():
            if keyword in event_text:
                matched_location_name = full_name
                break
        
        # If it matches one of our 4 preferred rinks, extract the details
        if matched_location_name:
            # Try to grab clean times, or default to whatever text is there
            start_time = event.get('start_time') or event.get('start', 'See Site')
            end_time = event.get('end_time') or event.get('end', 'See Site')
            event_date = event.get('start_date') or event.get('date') or start_date
            
            filtered_events.append({
                "location": matched_location_name,
                "title": title,
                "date": event_date,
                "start_time": start_time,
                "end_time": end_time
            })

# Save the finalized, clean list for your webpage
with open('schedule.json', 'w') as f:
    json.dump({
        "refreshed_at": datetime.now().strftime("%Y-%m-%d %I:%M %p"), 
        "events": filtered_events
    }, f, indent=2)
