import os
import time
import threading
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

app = Flask(__name__)

COOKIE_VALUE = os.environ.get("SESSION_COOKIE")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

@app.route('/')
def home():
    return "🤖 Pingless Selenium AFK Bot is Running!"

def send_discord_notification(message):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"❌ Discord Error: {e}", flush=True)

def selenium_afk_bot():
    if not COOKIE_VALUE:
        msg = "❌ Error: SESSION_COOKIE Environment Variable nahi mila!"
        print(msg, flush=True)
        send_discord_notification(msg)
        return

    msg = "🚀 Selenium Headless Browser AFK Bot Started!"
    print(msg, flush=True)
    send_discord_notification(msg)

    count = 0
    while True:
        driver = None
        try:
            # Chrome options for headless server environment
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Start Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
            
            # 1. Pehle domain ke root URL par jao (Domain matching ke liye zaroori hai)
            driver.get("https://dash.pingless.org")
            time.sleep(3)
            
            # 2. Ab yahan cookie inject karo domain ke sath
            cookie = {
                'name': 'pingless.sid',
                'value': COOKIE_VALUE,
                'domain': 'dash.pingless.org',
                'path': '/'
            }
            driver.add_cookie(cookie)
            
            # 3. Ab target AFK page par jao jahan credits badhte hain
            driver.get("https://dash.pingless.org/afk")
            time.sleep(15)
            
            if "afk" in driver.current_url:
                count += 1
                msg = f"✅ [{count}] Selenium successfully loaded AFK page & updated credits!"
                print(msg, flush=True)
                send_discord_notification(msg)
            else:
                msg = f"❌ Redirected away! Current URL: {driver.current_url}"
                print(msg, flush=True)
                send_discord_notification(msg)

        except Exception as e:
            msg = f"❌ Selenium Error: {e}"
            print(msg, flush=True)
            send_discord_notification(msg)
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        # Har 3 minutes (180 seconds) baad dobara refresh hoga
        time.sleep(180)

# Background thread mein bot chalu kar diya
threading.Thread(target=selenium_afk_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
