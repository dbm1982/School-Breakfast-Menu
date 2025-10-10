from datetime import datetime, timedelta
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import uuid

# --- CONFIG ---
SCHOOLS = {
SCHOOLS = {
    "JFK": "https://holbrook.nutrislice.com/menu/jfk/breakfast",
    "HMHS": "https://holbrook.nutrislice.com/menu/hmhs/breakfast"
}
TIMEZONE = "America/New_York"
MEAL_TIME = {"start": "070000", "end": "073000"}

# --- UTILITIES ---
def get_weekdays(year, month):
    date = datetime(year, month, 1)
    weekdays = []
    while date.month == month:
        if date.weekday() < 5:  # Monday–Friday
            weekdays.append(date)
        date += timedelta(days=1)
    return weekdays

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def scrape_menu(driver, url, date_str):
    driver.get(f"{url}?date={date_str}")
    items = driver.find_elements(By.CSS_SELECTOR, ".menu-item-name, .item-name, .food-item")
    return [i.text.strip() for i in items if i.text.strip()]

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
    f.write(f"DTSTAMP:{date.strftime('%Y%m%dT%H%M%SZ')}\n")
    f.write(f"DTSTART;TZID={TIMEZONE}:{start}\n")
    f.write(f"DTEND;TZID={TIMEZONE}:{end}\n")
    f.write(f"SUMMARY:{summary}\n")
    f.write(f"DESCRIPTION:{description}\n")
    f.write("END:VEVENT\n")

# --- MAIN ---
def main():
    eastern = pytz.timezone(TIMEZONE)
    now = datetime.now(eastern)
    dates = get_weekdays(now.year, now.month)

    driver = init_driver()

    with open("menu.ics", "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:menu_scraper\n")
        for date in dates:
            date_str = date.strftime("%Y-%m-%d")
            for school, url in SCHOOLS.items():
                print(f"Scraping {school} for {date_str}")
                items = scrape_menu(driver, url, date_str)
                write_event(f, date, school, items)
        f.write("END:VCALENDAR\n")

    driver.quit()

if __name__ == "__main__":
    main()
