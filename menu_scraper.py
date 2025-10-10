from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from ics import Calendar, Event
from datetime import datetime
import time

SCHOOLS = {
    "JFK": "https://holbrook.nutrislice.com/menu/jfk/breakfast/",
    "HMHS": "https://holbrook.nutrislice.com/menu/jrsr-high/breakfast/"
}

def get_menu(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)
    items = driver.find_elements(By.CSS_SELECTOR, ".menu-item-name")
    menu = [item.text for item in items if item.text.strip()]
    driver.quit()
    return menu

def build_calendar(menus):
    c = Calendar()
    e = Event()
    today = datetime.today()
    e.name = "🍽️ Breakfast Menu"
    e.begin = today.replace(hour=6, minute=30).isoformat()
    e.description = "\n".join([f"{school}: {', '.join(items) if items else 'No menu found'}"
                               for school, items in menus.items()])
    c.events.add(e)
    with open("menu.ics", "w") as f:
        f.writelines(c)

if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d")
    menus = {school: get_menu(url + today) for school, url in SCHOOLS.items()}
    build_calendar(menus)
