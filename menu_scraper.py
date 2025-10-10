import requests
from datetime import date, timedelta, datetime
import uuid

# --- CONFIG ---
SCHOOLS = {
    "JFK": "jfk",
    "HMHS": "hmhs"
}
DISTRICT = "holbrook"
BASE_URL = "https://holbrook.nutrislice.com/menu/api/weeks/school"
TIMEZONE = "America/New_York"
MEAL = "breakfast"
MEAL_TIME = {"start": "070000", "end": "073000"}

# --- FETCHER ---
def fetch_menu(school, date_str):
    url = f"{BASE_URL}/{school}/{MEAL}?date={date_str}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for day in data.get("days", []):
            if day.get("date") == date_str:
                return [item["name"] for item in day.get("menu_items", []) if item.get("name")]
        return []
    except Exception as e:
        print(f"⚠️ Failed to fetch {school} menu for {date_str}:", e)
        return []

# --- WRITER ---
def write_event(f, date_obj, school, items):
    if not items:
        return
    start = date_obj.strftime(f"%Y%m%dT{MEAL_TIME['start']}")
    end = date_obj.strftime(f"%Y%m%dT{MEAL_TIME['end']}")
    uid = f"{school.lower()}-{date_obj.strftime('%Y%m%d')}-{uuid.uuid4()}"
    summary = f"{school} Breakfast"
    description = "\\n".join(items)

    f.write("BEGIN:VEVENT\n")
    f.write(f"UID:{uid}\n")
    f.write(f"DTSTAMP:{date_obj.strftime('%Y%m%dT060000Z')}\n")
    f.write(f"DTSTART;TZID={TIMEZONE}:{start}\n")
    f.write(f"DTEND;TZID={TIMEZONE}:{end}\n")
    f.write(f"SUMMARY:{summary}\n")
    f.write(f"DESCRIPTION:{description}\n")
    f.write("END:VEVENT\n")

# --- DATE RANGE ---
def get_date_range():
    today = date.today()
    first_this_month = today.replace(day=1)
    first_next_month = (first_this_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_next_month = (first_next_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    return first_this_month, last_next_month

# --- MAIN ---
def main():
    start_date, end_date = get_date_range()
    current = start_date

    with open("menu.ics", "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:menu_scraper\n")
        while current <= end_date:
            if current.weekday() < 5:  # Monday–Friday
                date_str = current.strftime("%Y-%m-%d")
                for school in SCHOOLS.values():
                    items = fetch_menu(school, date_str)
                    write_event(f, current, school.upper(), items)
            current += timedelta(days=1)
        f.write("END:VCALENDAR\n")

    print("✅ Finished. Check menu.ics")

if __name__ == "__main__":
    main()
