import os
import time
import threading
import requests
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ----------------------------------------------------
# 1. FLASK SERVER (24/7 Uptime)
# ----------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Selenium JS-Cookie AFK Bot is Live!"

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
# 3. SELENIUM FARMER (Using JavaScript Cookie Injection)
# ----------------------------------------------------
def selenium_afk_farmer():
    if not COOKIE_VALUE:
        msg = "⚠️ Warning: SESSION_COOKIE environment variable missing!"
        print(msg, flush=True)
        send_discord_notification(msg)
        return

    msg = "🚀 Selenium JS-Injection AFK Farmer Started!"
    print(msg, flush=True)
    send_discord_notification(msg)

    session_count = 0
    while True:
        driver = None
        try:
            session_count += 1
            status_msg = f"🔄 **[Session {session_count}]** Launching browser & injecting JS cookie..."
            print(status_msg, flush=True)
            send_discord_notification(status_msg)

            # Chrome options for server environment
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Chrome(options=chrome_options)

            # Step 1: Pehle domain par jao taaki browser ka origin set ho jaye
            driver.get("https://dash.pingless.org/")
            time.sleep(3)

            # Step 2: Selenium add_cookie ki jagah JavaScript se direct cookie set karo (Never fails!)
            js_script = f"document.cookie = 'pingless.sid={COOKIE_VALUE}; path=/; domain=dash.pingless.org; secure; samesite=lax';"
            driver.execute_script(js_script)
            
            # Page ko refresh karo taaki cookie apply hokar login session ban jaye
            driver.refresh()
            time.sleep(3)

            # Step 3: Ab AFK page par jao
            driver.get("https://dash.pingless.org/afk")
            
            # Browser ko 2 minutes tak khula chhodenge taaki credits add ho sakein
            time.sleep(120)

            success_msg = f"✅ **[Session {session_count}]** AFK page active via JS-Cookie. Credits updated!"
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

        time.sleep(5)

# ----------------------------------------------------
# 4. MAIN EXECUTION
# ----------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=selenium_afk_farmer, daemon=True).start()

    while True:
        time.sleep(1)
