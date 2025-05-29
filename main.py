from flask import Flask
import threading
import os
import requests
from bs4 import BeautifulSoup
import time
import datetime
import re

# ============ 配置 ============
DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1376952972210208798/q468H-LKCXOyZBrThDN5ZeZyNUwAAl7y9fRzL_EwchS96403JHVS_GEsR5cgVklOe_bP"
TICKET_PAGE_URLS = [
    "https://tixcraft.com/ticket/area/25_lsf/19632",
    "https://tixcraft.com/ticket/area/25_lsf/19788"
]
headers = {
    "User-Agent": "Mozilla/5.0"
}

# ============ Flask 假網站 (for Render port 綁定) ============
app = Flask(__name__)

@app.route('/')
def home():
    return "TixCraft Ticket Bot is running 🎟️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # for Render
    app.run(host="0.0.0.0", port=port)

# ============ Discord 發送 ============
def send_to_discord_embed(title, description, url):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "embeds": [
            {
                "title": title,
                "description": f"{description}\n🕓 **通知時間：{now}**",
                "url": url,
                "color": 0x00cc66
            }
        ]
    }
    res = requests.post(DISCORD_WEBHOOK, json=data)
    if res.status_code in [200, 204]:
        print("✅ 通知已發送")
    else:
        print(f"❌ 通知失敗：{res.status_code} | {res.text}")

# ============ 票區掃描邏輯 ============
def check_ticket_page(url):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("li font")
        results = []

        if not links:
            print(f"⚠️ 無法找到票區元素 ➜ {url}")
            return

        for font_tag in links:
            text = font_tag.get_text(strip=True)
            if re.search(r"(剩餘|尚有|可售)", text):
                results.append(f"🎟️ {text}")

        if results:
            all_text = "\n".join(results)
            send_to_discord_embed("🎉 有票啦！", all_text, url)
        else:
            print(f"❌ 無票 ➜ {url}")

    except Exception as e:
        print(f"⚠️ 錯誤 ➜ {url}：{e}")


# ============ 主要執行程式 ============
def run_bot():
    while True:
        for url in TICKET_PAGE_URLS:
            check_ticket_page(url)
            time.sleep(5)
        print("⏱ 等待 60 秒...\n")
        time.sleep(60)

# ============ 程式進入點 ============
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
