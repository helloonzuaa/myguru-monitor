import requests
import json
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
COOKIE = os.getenv("COOKIE")

URL = "https://myguru.upsi.edu.my/stats/progress/notification/"

headers = {
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0"
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def get_notifications():
    r = requests.get(URL, headers=headers)
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

            old_val = old[course][item]
            new_val = new[course][item]

            if old_val != new_val:

                changes.append(
                    f"{course} {item}: {old_val} → {new_val}"
                )

    return changes

try:
    with open("last.json") as f:
        last = json.load(f)
except:
    last = None

send_telegram("✅ MyGuru monitor started (cloud)")

while True:

    try:

        current = get_notifications()

        if last:

            diff = compare(last, current)

            if diff:

                message = "🚨 MyGuru Update\n\n" + "\n".join(diff)

                send_telegram(message)

        with open("last.json", "w") as f:
            json.dump(current, f)

        last = current

        print("Checked...")

    except Exception as e:

        send_telegram(f"MyGuru monitor error: {e}")

    time.sleep(60)
