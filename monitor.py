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
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

def get_notifications():

    r = requests.get(URL, headers=headers)

    if r.status_code != 200:
        raise Exception("Session expired")

    try:
        return r.json()
    except:
        raise Exception("Invalid response")

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


try:
    with open("last.json") as f:
        last = json.load(f)
except:
    last = None

send_telegram("✅ MyGuru monitor started")

while True:

    try:

        current = get_notifications()

        if last:

            diff = compare(last, current)

            if diff:

                send_telegram(
                    "🚨 MyGuru Update\n\n" + "\n".join(diff)
                )

        with open("last.json", "w") as f:
            json.dump(current, f)

        last = current

        print("Checked...")

    except Exception as e:

        send_telegram(f"⚠ MyGuru Error: {e}")

    time.sleep(60)
