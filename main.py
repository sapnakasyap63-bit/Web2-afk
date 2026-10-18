import os
import time
import threading
from flask import Flask
import requests

app = Flask(__name__)

# Render Environment Variables se uthayega
COOKIE = os.environ.get("SESSION_COOKIE")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Headers taaki site ko lage real mobile browser se request aa rahi hai
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Cookie": COOKIE,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Referer": "https://dash.pingless.org/afk",
    "Connection": "keep-alive"
}

@app.route('/')
def home():
    return "🤖 Pingless AFK 24/7 Refresher Bot is Running!"

def send_discord_notification(message):
    if not WEBHOOK_URL:
        return
    try:
        payload = {"content": message}
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Discord Webhook Error: {e}", flush=True)

def afk_refresher():
    if not COOKIE:
        msg = "❌ Error: SESSION_COOKIE Environment Variable nahi mila!"
        print(msg, flush=True)
        send_discord_notification(msg)
        return

    url = "https://dash.pingless.org/afk"
    start_msg = "🚀 AFK Page Checker & Refresher Started!"
    print(start_msg, flush=True)
    send_discord_notification(start_msg)

    session = requests.Session()
    session.headers.update(HEADERS)

    count = 0
    while True:
        try:
            # allow_redirects=True rakha hai taaki agar login page par feke toh pata chale
            response = session.get(url, timeout=20, allow_redirects=True)
            
            # Check karenge ki kya URL redirect hoke login par gaya ya wahi hai
            if "afk" in response.url:
                if response.status_code == 200:
                    count += 1
                    msg = f"✅ [{count}] Exact AFK page hit successfully! Session active."
                    print(msg, flush=True)
                    send_discord_notification(msg)
                else:
                    msg = f"⚠️ AFK Page Status Code: {response.status_code}"
                    print(msg, flush=True)
                    send_discord_notification(msg)
            else:
                msg = f"❌ Redirected away from AFK page! Current URL: {response.url}. Cookie update karni padegi!"
                print(msg, flush=True)
                send_discord_notification(msg)

        except Exception as e:
            msg = f"❌ Connection Error: {e}"
            print(msg, flush=True)
            send_discord_notification(msg)

        # Har 3 minutes (180 seconds) mein page refresh hoga
        time.sleep(180)

# Background thread mein refresher loop chalu kar diya
threading.Thread(target=afk_refresher, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
