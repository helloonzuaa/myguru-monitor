import requests
import json
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
COOKIE = os.getenv("COOKIE")

URL = "https://myguru.upsi.edu.my/stats/progress/notification/"

IGNORE_COURSES = [
    "DMG3033",
    "DTK3013",
    "DTS3043",
    "KPF3012",
    "UPU3112"
]

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

    return r.json()


def compare(old, new):

    changes = []

    old = old[0]
    new = new[0]

    for course in new:

        if course in IGNORE_COURSES:
            continue

        if course not in old:
            continue

        for item in new[course]:

            if item == "course":
                continue

            old_val = old[course][item]
            new_val = new[course][item]

            if new_val > old_val:

                diff = new_val - old_val

                if item == "assignment":
                    text = "New Assignment Posted"

                elif item == "forum":
                    text = "New Forum Post"

                elif item == "material":
                    text = "New Learning Material"

                elif item == "announcement":
                    text = "New Announcement"

                elif item == "quiz":
                    text = "New Quiz"

                else:
                    continue

                changes.append(
                    f"📚 {course}\n{text}"
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

                message = "🚨 MyGuru Update\n\n" + "\n\n".join(diff)

                send_telegram(message)

        with open("last.json", "w") as f:
            json.dump(current, f)

        last = current

        print("Checked...")

    except Exception as e:

        send_telegram(f"⚠ MyGuru Error: {e}")

    time.sleep(60)
