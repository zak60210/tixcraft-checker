import requests
from flask import Flask
import threading
from bs4 import BeautifulSoup
import time
import datetime
import re

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running."

def run_flask():
    app.run(host='0.0.0.0', port=10000)

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1376952972210208798/q468H-LKCXOyZBrThDN5ZeZyNUwAAl7y9fRzL_EwchS96403JHVS_GEsR5cgVklOe_bP"
TICKET_PAGE_URLS = [
    "https://tixcraft.com/ticket/area/25_lsf/19632",
    "https://tixcraft.com/ticket/area/25_lsf/19788"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send_to_discord_embed(title, description, url):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "embeds": [
            {
                "title": title,
                "description": f"{description}\n🕓 **時間：{now}**",
                "url": url,
                "color": 0x00cc66
            }
        ]
    }
    res = requests.post(DISCORD_WEBHOOK, json=data)
    if res.status_code in [200, 204]:
        print("✅ 通知已送出")
    else:
        print(f"❌ 通知失敗：{res.status_code} | {res.text}")

def check_ticket_page(url):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("li.select_form_b > a[style*='opacity: 1']")
        results = []

        for link in links:
            text = link.get_text(strip=True).replace("\n", " ")
            match = re.search(r"剩餘\s*(\d+)", text)
            if match and int(match.group(1)) > 0:
                results.append(f"🎟️ {text}")

        if results:
            all_text = "\n".join(results)
            send_to_discord_embed("🎉 有票通知", all_text, url)
        else:
            print(f"❌ 無票：{url}")
    except Exception as e:
        print(f"⚠️ 錯誤：{e}")

# 主迴圈
while True:
    for url in TICKET_PAGE_URLS:
        check_ticket_page(url)
        time.sleep(5)
    print("⏱ 等待 60 秒...\n")
    time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    while True:
        # 你的 bot 主程式循環
        for url in TICKET_PAGE_URLS:
            check_ticket_page(url)
        time.sleep(60)
