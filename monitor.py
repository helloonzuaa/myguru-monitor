import requests
import json
import time
import os
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("MYGURU_USER")
PASSWORD = os.getenv("MYGURU_PASS")

URL = "https://myguru.upsi.edu.my/stats/progress/notification/"

cookies = None

def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message}
    )

def login():

    global cookies

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://myguru.upsi.edu.my")

        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)

        page.click('button[type="submit"]')

        page.wait_for_timeout(5000)

        cookies = page.context.cookies()

        browser.close()

def get_notifications():

    global cookies

    jar = {c['name']: c['value'] for c in cookies}

    r = requests.get(URL, cookies=jar)

    return r.json()

def compare(old, new):

    changes = []

    old = old[0]
    new = new[0]

    for course in new:

        if course not in old:
            continue

        for item in new[course]:

            if item == "course":
                continue

            if new[course][item] != old[course][item]:

                changes.append(
                    f"{course} {item}: {old[course][item]} → {new[course][item]}"
                )

    return changes

login()

send_telegram("✅ MyGuru monitor started (auto login)")

try:
    with open("last.json") as f:
        last = json.load(f)
except:
    last = None

while True:

    try:

        current = get_notifications()

        if last:

            diff = compare(last, current)

            if diff:

                send_telegram(
                    "🚨 MyGuru Update\n\n" + "\n".join(diff)
                )

        with open("last.json","w") as f:
            json.dump(current,f)

        last = current

        print("Checked...")

    except Exception as e:

        send_telegram("⚠ Relogin...")

        login()

    time.sleep(60)
