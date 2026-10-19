import os
import time
import threading
import requests
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ----------------------------------------------------
# 1. FLASK SERVER (For 24/7 Uptime on Render)
# ----------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Selenium AFK Credit Farmer is Live!"

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
# 3. SELENIUM AFK FARMER (Real Browser Session)
# ----------------------------------------------------
def selenium_afk_farmer():
    if not COOKIE_VALUE:
        msg = "⚠️ Warning: SESSION_COOKIE environment variable missing!"
        print(msg, flush=True)
        send_discord_notification(msg)
        return

    msg = "🚀 Selenium Headless AFK Farmer Started! Opening browser to farm credits..."
    print(msg, flush=True)
    send_discord_notification(msg)

    session_count = 0
    while True:
        driver = None
        try:
            session_count += 1
            status_msg = f"🔄 **[Session {session_count}]** Launching browser, injecting cookie, and opening AFK page..."
            print(status_msg, flush=True)
            send_discord_notification(status_msg)

            # Chrome options for server environment
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            driver = webdriver.Chrome(options=chrome_options)

            # Step 1: Root domain par jaakar cookie set karna (Cookie error fix)
            driver.get("https://dash.pingless.org")
            time.sleep(3)

            cookie = {
                'name': 'pingless.sid',
                'value': COOKIE_VALUE,
                'domain': 'dash.pingless.org',
                'path': '/'
            }
            driver.add_cookie(cookie)

            # Step 2: AFK page par jana jahan credits badhte hain
            driver.get("https://dash.pingless.org/afk")
            
            # Step 3: Yahan browser ko 2 minutes (120 seconds) tak khula chhodenge taaki JS timer chale
            time.sleep(120)

            success_msg = f"✅ **[Session {session_count}]** AFK page kept active for 2 minutes. Credits should now be added!"
            print(success_msg, flush=True)
            send_discord_notification(success_msg)

        except Exception as e:
            err_msg = f"❌ **[Selenium Error]** `{e}`"
            print(err_msg, flush=True)
            send_discord_notification(err_msg)

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        # Thoda gap dekar agla session start hoga
        time.sleep(5)

# ----------------------------------------------------
# 4. MAIN EXECUTION
# ----------------------------------------------------
if __name__ == "__main__":
    # Flask server background thread mein
    threading.Thread(target=run_flask, daemon=True).start()

    # Selenium farmer background thread mein
    threading.Thread(target=selenium_afk_farmer, daemon=True).start()

    # Keep main thread alive
    while True:
        time.sleep(1)
