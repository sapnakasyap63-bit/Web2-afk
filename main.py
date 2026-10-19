import os
import time
import threading
import requests
from flask import Flask

# ----------------------------------------------------
# 1. FLASK SERVER (For 24/7 Uptime on Render)
# ----------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Pure Requests AFK Tracker is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ----------------------------------------------------
# 2. CONFIGURATION
# ----------------------------------------------------
COOKIE_VALUE = os.environ.get("SESSION_COOKIE")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_notification(message):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"❌ Webhook Error: {e}", flush=True)

# ----------------------------------------------------
# 3. REQUESTS AFK LOOP (Runs continuously)
# ----------------------------------------------------
def requests_afk_loop():
    if not COOKIE_VALUE:
        msg = "⚠️ Warning: SESSION_COOKIE environment variable missing!"
        print(msg, flush=True)
        send_discord_notification(msg)
        return

    msg = "🚀 Pure Requests AFK Worker Started!"
    print(msg, flush=True)
    send_discord_notification(msg)

    count = 0
    while True:
        try:
            count += 1
            session = requests.Session()
            
            # Cookie inject karna
            cookie_obj = requests.cookies.create_cookie(
                domain='dash.pingless.org',
                name='pingless.sid',
                value=COOKIE_VALUE
            )
            session.cookies.set_cookie(cookie_obj)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Referer": "https://dash.pingless.org/afk"
            }

            # AFK page ya endpoint par request bhejna
            response = session.get("https://dash.pingless.org/afk", headers=headers, timeout=15)

            if response.status_code == 200:
                success_msg = f"✅ **[Ping #{count}]** Request sent successfully! Status: `200 OK`"
                print(success_msg, flush=True)
                send_discord_notification(success_msg)
            else:
                err_msg = f"❌ **[Ping #{count}]** Server responded with status code: `{response.status_code}`"
                print(err_msg, flush=True)
                send_discord_notification(err_msg)

        except Exception as e:
            err_msg = f"❌ **[Error]** `{e}`"
            print(err_msg, flush=True)
            send_discord_notification(err_msg)

        # Har 1 minute (60 seconds) mein request bhejega taaki server par load na pade
        time.sleep(60)

# ----------------------------------------------------
# 4. MAIN EXECUTION
# ----------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=requests_afk_loop, daemon=True).start()

    while True:
        time.sleep(1)

