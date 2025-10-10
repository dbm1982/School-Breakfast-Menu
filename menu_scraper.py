import requests
from datetime import date, timedelta
import uuid

# --- CONFIG ---
DISTRICT = "holbrook"
SCHOOLS = {
    "jfk": "JFK Elementary",
    "jrsr-high": "Holbrook Middle High School"
}
MEAL_TYPE = "breakfast"
TIMEZONE = "America/New_York"
MEAL_TIME = {"start": "070000", "end": "073000"}
KEYWORDS = ["pancake", "waffles", "cinnis", "Strawberry Cream Cheese Stuffed Bagel","french toast"]

# --- DATE RANGE ---
def get_weekdays(start_date, end_date):
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            yield current
        current += timedelta(days=1)

# --- FETCH MENU ---
def fetch_menu(school_key, d):
    y, m, d_str = d.strftime("%Y"), d.strftime("%m"), d.strftime("%d")
    url = f"https://{DISTRICT}.api.nutrislice.com/menu/api/weeks/school/{school_key}/menu-type/{MEAL_TYPE}/{y}/{m}/{d_str}?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for day in data.get("days", []):
            if day.get("date") == f"{y}-{m}-{d_str}":
                return [
                    item["food"]["name"].strip()
                    for item in day.get("menu_items", [])
                    if item.get("food") and any(k in item["food"]["name"].lower() for k in KEYWORDS)
                ]
    except Exception as e:
        print(f"⚠️ Failed to fetch {school_key} menu for {d.strftime('%Y-%m-%d')}: {e}")
    return []

# --- WRITE EVENT ---
def write_event(f, d, school_key, school_name, items):
    if not items:
        return
    start = d.strftime(f"%Y%m%dT{MEAL_TIME['start']}")
    end = d.strftime(f"%Y%m%dT{MEAL_TIME['end']}")
    uid = f"{school_key}-{d.strftime('%Y%m%d')}-{uuid.uuid4()}"
    summary = f"{school_name} Breakfast"
    description = "\\n".join(items)

    f.write("BEGIN:VEVENT\n")
    f.write(f"UID:{uid}\n")
    f.write(f"DTSTAMP:{d.strftime('%Y%m%dT060000Z')}\n")
    f.write(f"DTSTART;TZID={TIMEZONE}:{start}\n")
    f.write(f"DTEND;TZID={TIMEZONE}:{end}\n")
    f.write(f"SUMMARY:{summary}\n")
    f.write(f"DESCRIPTION:{description}\n")
    f.write("END:VEVENT\n")

# --- MAIN ---
if __name__ == "__main__":
    today = date.today()
    start = date(today.year, today.month, 1)
    next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    end = (next_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    with open("menu.ics", "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:menu_scraper\n")
        for d in get_weekdays(start, end):
            combined_items = []
            for school_key, school_name in SCHOOLS.items():
                items = fetch_menu(school_key, d)
                if items:
                    combined_items.append(f"{school_name}:\n" + "\n".join(items))
            if combined_items:
                write_event(f, d, "combined", "School Breakfast", combined_items)

    
        f.write("END:VCALENDAR\n")

    print("✅ Finished. Check menu.ics")
