import os
import time
import threading
import requests
import discord
from discord.ext import commands
from flask import Flask

# ----------------------------------------------------
# 1. FLASK SERVER (For 24/7 Uptime)
# ----------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Discord Bot + AFK Automation is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ----------------------------------------------------
# 2. CONFIGURATION & CONFIG CHECK
# ----------------------------------------------------
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
COOKIE_VALUE = os.environ.get("SESSION_COOKIE")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

# Helper function to send webhook alerts
def send_discord_notification(message):
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"❌ Webhook Error: {e}", flush=True)

# ----------------------------------------------------
# 3. BACKGROUND AFK AUTOMATION LOOP
# ----------------------------------------------------
def afk_automation_loop():
    if not COOKIE_VALUE:
        msg = "⚠️ Warning: SESSION_COOKIE environment variable missing! AFK loop stopped."
        print(msg, flush=True)
        send_discord_notification(msg)
        return

    msg = "🚀 Pingless AFK Background Loop Active!"
    print(msg, flush=True)
    send_discord_notification(msg)

    count = 0
    while True:
        try:
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
                status_msg = f"✅ [{count}] AFK ping successful! Credits updated."
                print(status_msg, flush=True)
                send_discord_notification(status_msg)
            else:
                err_msg = f"❌ Server responded with status code: {response.status_code}"
                print(err_msg, flush=True)
                send_discord_notification(err_msg)

        except Exception as e:
            err_msg = f"❌ AFK Request Error: {e}"
            print(err_msg, flush=True)
            send_discord_notification(err_msg)

        # Har 3 minutes (180 seconds) mein repeat hoga
        time.sleep(180)

# ----------------------------------------------------
# 4. DISCORD BOT EVENTS & COMMANDS
# ----------------------------------------------------
@bot.event
async def on_ready():
    print(f"✅ Discord Bot Logged in as: {bot.user.name}", flush=True)
    # Bot status set karna
    activity = discord.Activity(type=discord.ActivityType.watching, name="AFK Credits | Prefix: $")
    await bot.change_presence(activity=activity)

@bot.command(name="ping")
async def ping(ctx):
    """Bot latency check karne ke liye command ($ping)"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: **{latency}ms**")

@bot.command(name="status")
async def status(ctx):
    """Bot ka current status check karne ke liye ($status)"""
    embed = discord.Embed(
        title="🤖 Bot Status",
        description="Bot dynamic mode par successfully chal raha hai!",
        color=discord.Color.green()
    )
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="AFK Loop", value="🟢 Active", inline=True)
    await ctx.send(embed=embed)

# ----------------------------------------------------
# 5. MAIN EXECUTION START
# ----------------------------------------------------
if __name__ == "__main__":
    # Flask app background thread mein chalu karna
    threading.Thread(target=run_flask, daemon=True).start()

    # AFK automation background thread mein chalu karna
    threading.Thread(target=afk_automation_loop, daemon=True).start()

    # Discord Bot run karna
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("❌ Error: DISCORD_TOKEN Environment Variable nahi mila!", flush=True)
