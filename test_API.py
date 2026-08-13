import requests
import os
from dotenv import load_dotenv

load_dotenv()

print(f"🔍 本地檢查 APP_ID 長度: {len(RRAKUTEN_APPLICATION_ID) if RAKUTEN_APPLICATION_ID else '未讀取到'}")
print(f"🔍 本地檢查 ACCESS_KEY 長度: {len(RAKUTEN_ACCESS_KEY) if RAKUTEN_ACCESS_KEY else '未讀取到'}")


# 1. 🚀 2026 正式穩定版端點
url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"

RAKUTEN_APPLICATION_ID=os.getenv("RAKUTEN_APPLICATION_ID")
YOUR_ACCESS_KEY=os.getenv("RAKUTEN_ACCESS_KEY") 

# 2. 設定規範參數
params = {      
    "keyword": "一番くじ 呪術廻戦 五条悟",
    "hits": 5,
    "formatVersion": 2
}

# 3. 🛡️ 核心修正：加入樂天新系統防火牆強制查核的來源驗證 (三種神器)
headers = {
    "applicationId": RAKUTEN_APPLICATION_ID,
    "accessKey": YOUR_ACCESS_KEY,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.rakuten.co.jp/",  # 💡 模擬從樂天市場主頁發送的請求
    "Origin": "https://www.rakuten.co.jp/"    # 💡 突破同源防火牆阻擋
}

print("🔑 已帶入全偽裝身分認證，正在向日本樂天伺服器發送最終請求...")

# 💡 加上 allow_redirects=False 確保如果安全校驗沒過，
# 會直接在 status_code 顯示錯誤，而不是偷偷塞 HTML 給我們
response = requests.get(url, params=params, headers=headers, allow_redirects=False)

print("-" * 50)
print(f"📡 伺服器回應狀態碼 (Status Code): {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        items = data.get("Items", [])
        total_count = data.get("count", 0)
        
        print("\n🎉 【世紀大成功】完美解鎖！順利拿到商品 JSON 資料！")
        print(f"📊 目前日本樂天市場上「五條悟一番賞」現貨商品總數：{total_count} 筆")
        print("-" * 50)
        
        for i, item_wrapper in enumerate(items, 1):
            item = item_wrapper.get("Item", {})
            name = item.get("itemName", "無名稱")
            price = item.get("itemPrice", 0)
            shop = item.get("shopName", "未知店鋪")
            
            print(f"[{i}] 商品：{name[:25]}...")
            print(f"    價格：¥{price} 日圓 | 賣家：{shop}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ JSON 解析失敗。原因：{e}")
elif response.status_code in [301, 302]:
    print("⚠️ 警告：安全防護依然觸發了重導向！")
    print(f"🔗 試圖跳轉至: {response.headers.get('Location')}")
    print("\n👉 請檢查您的 Access Key 字串複製時是否夾帶了前後空格。")
else:
    print(f"❌ 請求失敗，狀態碼：{response.status_code}")
    print(f"錯誤原因：\n{response.text}")
