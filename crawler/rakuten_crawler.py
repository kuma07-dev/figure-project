import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from database import get_connection

load_dotenv()

API_URL = (
    "https://openapi.rakuten.co.jp/"
    "ichibams/api/IchibaItem/Search/20260701"
)

APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
ACCESS_KEY = os.getenv("RAKUTEN_ACCESS_KEY")


EXCLUDE_KEYWORDS = [
    "セット",
    "コンプリート",
    "BOX",
    "ボックス",
    "予約",
    "福袋",
    "まとめ売り",
]





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




def clean_items(items, min_price=500, max_price=30000):
    """排除套組、預購、缺少資料與明顯異常價格。"""

    cleaned_items = []

    for item in items:
        title = item["title"] or ""
        price = item["price_jpy"]

        # 商品名稱或價格缺失，不能分析
        if not title or price is None:
            continue

        # 排除整套、預購、福袋與多件合售
        if any(word in title for word in EXCLUDE_KEYWORDS):
            continue

        # 日圓價格超出範圍時不納入
        if not min_price <= price <= max_price:
            continue

        cleaned_items.append(item)

    return cleaned_items




def get_active_tracked_items():
    """從資料庫取得目前啟用的追蹤角色。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT id, anime_title, character_name, search_keyword
                FROM tracked_items
                WHERE is_active = TRUE
                ORDER BY id
            """
            cursor.execute(sql)
            return cursor.fetchall()

    finally:
        connection.close()




def upsert_listing(tracked_item_id, item):
    """新增商品；若商品網址已存在則更新商品資訊，並回傳 listing_id。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO listings (
                    tracked_item_id,
                    source,
                    title,
                    product_url,
                    image_url,
                    last_seen_at,
                    is_active
                )
                VALUES (%s, 'Rakuten', %s, %s, %s, NOW(), TRUE)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    image_url = VALUES(image_url),
                    last_seen_at = NOW(),
                    is_active = TRUE
            """

            cursor.execute(
                sql,
                (
                    tracked_item_id,
                    item["title"],
                    item["product_url"],
                    item["image_url"],
                ),
            )

            # 用網址取得該商品的 id
            cursor.execute(
                "SELECT id FROM listings WHERE product_url = %s",
                (item["product_url"],),
            )

            listing = cursor.fetchone()
            connection.commit()

            return listing["id"]

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def insert_price_snapshot(tracked_item_id, listing_id, item):
    """每次爬取都新增一筆價格紀錄。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO price_snapshots (
                    tracked_item_id,
                    listing_id,
                    price_jpy,
                    shipping_jpy,
                    stock_status,
                    captured_at
                )
                VALUES (%s, %s, %s, NULL, %s, %s)
            """

            cursor.execute(
                sql,
                (
                    tracked_item_id,
                    listing_id,
                    item["price_jpy"],
                    item["stock_status"],
                    item["captured_at"],
                ),
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def main():
    try:
        tracked_items = get_active_tracked_items()

        print(f"目前啟用追蹤：{len(tracked_items)} 位角色\n")

        for tracked_item in tracked_items:
            print("=" * 70)
            print(
                f"ID：{tracked_item['id']}｜"
                f"{tracked_item['anime_title']}｜"
                f"{tracked_item['character_name']}"
            )
            print(f"關鍵字：{tracked_item['search_keyword']}")

            raw_items = search_rakuten(tracked_item["search_keyword"])
            cleaned_items = clean_items(raw_items)

            print(f"原始資料：{len(raw_items)} 筆")
            print(f"清洗後資料：{len(cleaned_items)} 筆\n")

            for number, item in enumerate(cleaned_items, start=1):
                print(f"[{number}] {item['title']}")
                print(f"價格：¥{item['price_jpy']:,}")
                print(f"商店：{item['shop_name']}")
                print(f"網址：{item['product_url']}")
                print("-" * 50)
                listing_id = upsert_listing(tracked_item["id"], item)

                insert_price_snapshot(
                    tracked_item["id"],
                    listing_id,
                    item,
                )

                print(f"已寫入資料庫：listing_id = {listing_id}")

    except requests.RequestException as error:
        print(f"樂天 API 請求失敗：{error}")
    except Exception as error:
        print(f"程式執行失敗：{error}")


if __name__ == "__main__":
    main()