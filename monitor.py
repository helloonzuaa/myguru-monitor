import requests
import json
import time

BOT_TOKEN = "8718487929:AAHr1pJSHPCrqBgCHBQg21F-XIUbZWcpKVY"
CHAT_ID = "1607862436"

URL = "https://myguru.upsi.edu.my/stats/progress/notification/"

COOKIE = "ci_session=bb1c091d7ffa3222f9e4e7a3322dc440; attempt=0; myguru_mydigid_upsi=42d1e8da-f6a4-428c-91fd-ca482d776119; G_ENABLED_IDPS=google; _ga_T4L4DFY928=GS2.1.s1773116305$o70$g1$t1773116963$j60$l0$h0; _ga_6QK4HHC8HB=GS2.1.s1766568963$o13$g0$t1766568963$j60$l0$h0; _ga=GA1.1.1194978508.1740795449"

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

try:
    with open("last.json") as f:
        last = json.load(f)
except:
    last = None

send_telegram("✅ MyGuru monitor started")

while True:

    try:
        current = get_notifications()

        if last and current != last:

            msg = "TEST: MyGuru monitor working ✅"

            send_telegram(msg)

        with open("last.json", "w") as f:
            json.dump(current, f)

        last = current

        print("Checked...")

    except Exception as e:
        print("Error:", e)

    time.sleep(30)
