import requests
from datetime import datetime
import uuid

# --- CONFIG ---
SCHOOLS = {
    "JFK": "jfk",
    "HMHS": "hmhs"
}
DISTRICT = "holbrook"
BASE_URL = "https://api.nutrislice.com/menu/api/weeks/school"
DATE_STR = "2025-10-14"
TIMEZONE = "America/New_York"
MEAL = "breakfast"
MEAL_TIME = {"start": "070000", "end": "073000"}

# --- FETCHER ---
def fetch_menu(school, date_str):
    url = f"{BASE_URL}/{DISTRICT}/{school}/{MEAL}?date={date_str}"
    print(f"Fetching: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for day in data.get("days", []):
            if day.get("date") == date_str:
                items = [item["name"] for item in day.get("menu_items", []) if item.get("name")]
                print(f"{school} items:", items)
                return items
        print(f"No menu found for {school} on {date_str}")
        return []
    except Exception as e:
        print(f"⚠️ Failed to fetch {school} menu:", e)
        return []

# --- WRITER ---
def write_event(f, date, school, items):
    if not items:
        return
    start = date.strftime(f"%Y%m%dT{MEAL_TIME['start']}")
    end = date.strftime(f"%Y%m%dT{MEAL_TIME['end']}")
    uid = f"{school.lower()}-{date.strftime('%Y%m%d')}-{uuid.uuid4()}"
    summary = f"{school} Breakfast"
    description = "\\n".join(items)

    f.write("BEGIN:VEVENT\n")
    f.write(f"UID:{uid}\n")
    f.write(f"DTSTAMP:{date.strftime('%Y%m%dT060000Z')}\n")
    f.write(f"DTSTART;TZID={TIMEZONE}:{start}\n")
    f.write(f"DTEND;TZID={TIMEZONE}:{end}\n")
    f.write(f"SUMMARY:{summary}\n")
    f.write(f"DESCRIPTION:{description}\n")
    f.write("END:VEVENT\n")

# --- MAIN ---
def main():
    date = datetime.strptime(DATE_STR, "%Y-%m-%d")
    with open("menu.ics", "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:menu_scraper\n")
        for school in SCHOOLS.values():
            items = fetch_menu(school, DATE_STR)
            write_event(f, date, school.upper(), items)
        f.write("END:VCALENDAR\n")
    print("✅ Finished. Check menu.ics")

if __name__ == "__main__":
    main()
