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
    return "🤖 Webhook AFK Tracker is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ----------------------------------------------------
# 2. CONFIGURATION & ENVIRONMENT VARIABLES
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
# 3. AFK AUTOMATION & STATUS LOOP (Har 10 Seconds Updates)
# ----------------------------------------------------
def status_and_afk_loop():
    if not COOKIE_VALUE:
        msg = "⚠️ Warning: SESSION_COOKIE environment variable missing!"
        print(msg, flush=True)
        send_discord_notification(msg)
        return

    msg = "🚀 Pingless Webhook Status Tracker Started! Bot is monitoring..."
    print(msg, flush=True)
    send_discord_notification(msg)

    count = 0
    while True:
        try:
            # Status update message jo har 10 seconds mein webhook par jayega
            status_msg = f"🔄 **[Status Update]** Bot is active. Total successful pings: `{count}`. Maintaining session..."
            send_discord_notification(status_msg)

            # Session create karke AFK request bhejo
            session = requests.Session()
            cookie_obj = requests.cookies.create_cookie(
                domain='dash.pingless.org',
                name='pingless.sid',
                value=COOKIE_VALUE
            )
            session.cookies.set_cookie(cookie_obj)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
                "Referer": "https://dash.pingless.org/afk"
            }

            response = session.get("https://dash.pingless.org/afk", headers=headers, timeout=15)

            if response.status_code == 200:
                count += 1
                success_msg = f"✅ **[Success]** AFK ping sent successfully! Credits updated. (Count: {count})"
                print(success_msg, flush=True)
                send_discord_notification(success_msg)
            else:
                err_msg = f"❌ **[Error]** Server responded with status code: `{response.status_code}`"
                print(err_msg, flush=True)
                send_discord_notification(err_msg)

        except Exception as e:
            err_msg = f"❌ **[Exception]** Request Error: `{e}`"
            print(err_msg, flush=True)
            send_discord_notification(err_msg)

        # Har 10 seconds mein loop chalega aur update bhejega
        time.sleep(10)

# ----------------------------------------------------
# 4. MAIN EXECUTION START
# ----------------------------------------------------
if __name__ == "__main__":
    # Flask server background thread mein start karna
    threading.Thread(target=run_flask, daemon=True).start()

    # Status & AFK automation background thread mein start karna
    threading.Thread(target=status_and_afk_loop, daemon=True).start()

    # Main thread ko zinda rakhne ke liye loop
    while True:
        time.sleep(1)
