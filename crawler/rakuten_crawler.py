import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = (
    "https://openapi.rakuten.co.jp/"
    "ichibams/api/IchibaItem/Search/20260701"
)

APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
ACCESS_KEY = os.getenv("RAKUTEN_ACCESS_KEY")


def search_rakuten(keyword, hits=10):
    """用關鍵字搜尋日本樂天市場，回傳整理過的商品清單。"""

    if not APPLICATION_ID or not ACCESS_KEY:
        raise ValueError("找不到 API 金鑰，請檢查 .env 檔案。")

    params = {
        "applicationId": APPLICATION_ID,
        "accessKey": ACCESS_KEY,
        "keyword": keyword,
        "hits": hits,
        "page": 1,
        "format": "json",
        "formatVersion": 2,
        "sort": "standard",
        "elements": (
            "itemName,itemPrice,itemUrl,mediumImageUrls,"
            "itemCode,shopName,availability"
        ),
    }

    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    # print("API 回傳總數：", data.get("count") or data.get("Count"))
    # print("API 回傳頁數：", data.get("pageCount") or data.get("PageCount"))
    # print("API 回傳內容：", data)

    if "error" in data:
        raise RuntimeError(
            f"Rakuten API 錯誤：{data['error']} - "
            f"{data.get('error_description', '')}"
        )

    captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = []

    for item in data.get("Items", []):
        images = item.get("mediumImageUrls", [])
        if images:
            first_image = images[0]

            if isinstance(first_image, dict):
                image_url = first_image.get("imageUrl")
            else:
                image_url = first_image
        else:
            image_url = None

        results.append({
            "title": item.get("itemName"),
            "price_jpy": item.get("itemPrice"),
            "product_url": item.get("itemUrl"),
            "image_url": image_url,
            "item_code": item.get("itemCode"),
            "shop_name": item.get("shopName"),
            "stock_status": item.get("availability"),
            "captured_at": captured_at,
        })

    return results


def main():
    keyword = "一番くじ BLEACH 黒崎一護"

    try:
        items = search_rakuten(keyword)

        print(f"關鍵字：{keyword}")
        print(f"找到：{len(items)} 筆\n")

        for number, item in enumerate(items, start=1):
            print(f"[{number}] {item['title']}")
            print(f"價格：¥{item['price_jpy']:,}")
            print(f"商店：{item['shop_name']}")
            print(f"網址：{item['product_url']}")
            print(f"圖片：{item['image_url']}")
            print(f"抓取時間：{item['captured_at']}")
            print("-" * 60)

    except requests.RequestException as error:
        print(f"網路/API 請求失敗：{error}")
    except (ValueError, RuntimeError) as error:
        print(f"程式設定或 API 錯誤：{error}")


if __name__ == "__main__":
    main()