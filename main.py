import os
import time
import threading
from flask import Flask
import requests

app = Flask(__name__)

# Render Environment Variable se Cookie uthayega
COOKIE = os.environ.get("SESSION_COOKIE")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Cookie": COOKIE,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://dash.pingless.org/afk"
}

@app.route('/')
def home():
    return "🤖 Pingless AFK Bot is running 24/7!"

def ping_afk():
    if not COOKIE:
        print("❌ Error: SESSION_COOKIE Environment Variable nahi mila!")
        return

    url = "https://dash.pingless.org/afk"
    print("🚀 AFK Auto-Ping Bot Started on Render Web Service!")

    count = 0
    while True:
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                count += 1
                print(f"✅ [{count}] Ping successful! Page refreshed. AFK session active.")
            elif response.status_code in [401, 403]:
                print("⚠️ Session Expired or Disconnected! Cookie check karo.")
            else:
                print(f"⚠️ Status Code: {response.status_code}. Retrying...")

        except Exception as e:
            print(f"❌ Connection Error: {e}")

        # Har 1 minute (60 seconds) me automatic ping karega
        time.sleep(60)

# AFK loop ko background thread me chalayenge
threading.Thread(target=ping_afk, daemon=True).start()

if __name__ == "__main__":
    # Render automatic PORT variable deta hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
