import os
import time
import threading
from flask import Flask
import requests

app = Flask(__name__)

# Render Environment Variable se Cookie uthayega
COOKIE = os.environ.get("SESSION_COOKIE")

# Asli mobile browser jaisa Header taaki site ko lage real user active hai
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Cookie": COOKIE,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Referer": "https://dash.pingless.org/afk",
    "Connection": "keep-alive"
}

@app.route('/')
def home():
    return "🤖 Pingless AFK Bot is running 24/7!"

def ping_afk():
    if not COOKIE:
        print("❌ Error: SESSION_COOKIE Environment Variable nahi mila!")
        return

    url = "https://dash.pingless.org/afk"
    print("🚀 Advanced AFK Auto-Ping Bot Started!")

    count = 0
    while True:
        try:
            # Page visit ke sath-sath ek session keep-alive request bhejenge
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                count += 1
                print(f"✅ [{count}] Ping successful! Credits update honge.")
            elif response.status_code in [401, 403]:
                print("⚠️ Session Expired! Cookie dobara update karni padegi.")
            else:
                print(f"⚠️ Status Code: {response.status_code}. Retrying...")

        except Exception as e:
            print(f"❌ Connection Error: {e}")

        # Har 30 seconds mein ping karega taaki session active rahe
        time.sleep(30)

# Background thread mein chalu karenge
threading.Thread(target=ping_afk, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
