import os
import time
import threading
from flask import Flask
import requests

app = Flask(__name__)

# Render Environment Variable se Cookie uthayega
COOKIE = os.environ.get("SESSION_COOKIE")

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

def afk_refresher():
    if not COOKIE:
        print("❌ Error: SESSION_COOKIE Environment Variable nahi mila!")
        return

    url = "https://dash.pingless.org/afk"
    print("🚀 AFK 24/7 Page Refresher Started!")

    # Session object use karne se cookies aur connection browser ki tarah persist rehte hain
    session = requests.Session()
    session.headers.update(HEADERS)

    count = 0
    while True:
        try:
            # Page ko visit / refresh karenge
            response = session.get(url, timeout=20)
            
            if response.status_code == 200:
                count += 1
                print(f"✅ [{count}] AFK Page refreshed successfully! Session active.")
            elif response.status_code in [401, 403]:
                print("⚠️ Session Expired! Cookie (SESSION_COOKIE) invalid ho gayi hai, update karni padegi.")
            else:
                print(f"⚠️ Status Code: {response.status_code}. Retrying...")

        except Exception as e:
            print(f"❌ Connection Error: {e}")

        # Har 3 minutes (180 seconds) mein page refresh hoga
        time.sleep(180)

# Background thread mein refresher loop chalu kar diya
threading.Thread(target=afk_refresher, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
