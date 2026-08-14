# import os
# from datetime import datetime

# import requests
# from dotenv import load_dotenv

# from database import get_connection

# load_dotenv()

# API_URL = (
#     "https://openapi.rakuten.co.jp/"
#     "ichibams/api/IchibaItem/Search/20260701"
# )

# APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")
# ACCESS_KEY = os.getenv("RAKUTEN_ACCESS_KEY")


# EXCLUDE_KEYWORDS = [
#     "セット",
#     "コンプリート",
#     "BOX",
#     "ボックス",
#     "予約",
#     "福袋",
#     "まとめ売り",
# ]





# def search_rakuten(keyword, hits=10):
#     """用關鍵字搜尋日本樂天市場，回傳整理過的商品清單。"""

#     if not APPLICATION_ID or not ACCESS_KEY:
#         raise ValueError("找不到 API 金鑰，請檢查 .env 檔案。")

#     params = {
#         "applicationId": APPLICATION_ID,
#         "accessKey": ACCESS_KEY,
#         "keyword": keyword,
#         "hits": hits,
#         "page": 1,
#         "format": "json",
#         "formatVersion": 2,
#         "sort": "standard",
#         "elements": (
#             "itemName,itemPrice,itemUrl,mediumImageUrls,"
#             "itemCode,shopName,availability"
#         ),
#     }

#     response = requests.get(API_URL, params=params, timeout=20)
#     response.raise_for_status()

#     data = response.json()

#     # print("API 回傳總數：", data.get("count") or data.get("Count"))
#     # print("API 回傳頁數：", data.get("pageCount") or data.get("PageCount"))
#     # print("API 回傳內容：", data)

#     if "error" in data:
#         raise RuntimeError(
#             f"Rakuten API 錯誤：{data['error']} - "
#             f"{data.get('error_description', '')}"
#         )

#     captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     results = []




#     for item in data.get("Items", []):
#         images = item.get("mediumImageUrls", [])

#         if images:
#             first_image = images[0]

#             if isinstance(first_image, dict):
#                 image_url = first_image.get("imageUrl")
#             else:
#                 image_url = first_image
#         else:
#             image_url = None

#         results.append({
#             "title": item.get("itemName"),
#             "price_jpy": item.get("itemPrice"),
#             "product_url": item.get("itemUrl"),
#             "image_url": image_url,
#             "item_code": item.get("itemCode"),
#             "shop_name": item.get("shopName"),
#             "stock_status": item.get("availability"),
#             "captured_at": captured_at,
#         })

#     return results




# def clean_items(items, min_price=500, max_price=30000):
#     """排除套組、預購、缺少資料與明顯異常價格。"""

#     cleaned_items = []

#     for item in items:
#         title = item["title"] or ""
#         price = item["price_jpy"]

#         # 商品名稱或價格缺失，不能分析
#         if not title or price is None:
#             continue

#         # 排除整套、預購、福袋與多件合售
#         if any(word in title for word in EXCLUDE_KEYWORDS):
#             continue

#         # 日圓價格超出範圍時不納入
#         if not min_price <= price <= max_price:
#             continue

#         cleaned_items.append(item)

#     return cleaned_items




# def get_active_tracked_items():
#     """從資料庫取得目前啟用的追蹤角色。"""

#     connection = get_connection()

#     try:
#         with connection.cursor() as cursor:
#             sql = """
#                 SELECT id, anime_title, character_name, search_keyword
#                 FROM tracked_items
#                 WHERE is_active = TRUE
#                 ORDER BY id
#             """
#             cursor.execute(sql)
#             return cursor.fetchall()

#     finally:
#         connection.close()




# def upsert_listing(tracked_item_id, item):
#     """新增商品；若商品網址已存在則更新商品資訊，並回傳 listing_id。"""

#     connection = get_connection()

#     try:
#         with connection.cursor() as cursor:
#             sql = """
#                 INSERT INTO listings (
#                     tracked_item_id,
#                     source,
#                     title,
#                     product_url,
#                     image_url,
#                     last_seen_at,
#                     is_active
#                 )
#                 VALUES (%s, 'Rakuten', %s, %s, %s, NOW(), TRUE)
#                 ON DUPLICATE KEY UPDATE
#                     title = VALUES(title),
#                     image_url = VALUES(image_url),
#                     last_seen_at = NOW(),
#                     is_active = TRUE
#             """

#             cursor.execute(
#                 sql,
#                 (
#                     tracked_item_id,
#                     item["title"],
#                     item["product_url"],
#                     item["image_url"],
#                 ),
#             )

#             # 用網址取得該商品的 id
#             cursor.execute(
#                 "SELECT id FROM listings WHERE product_url = %s",
#                 (item["product_url"],),
#             )

#             listing = cursor.fetchone()
#             connection.commit()

#             return listing["id"]

#     except Exception:
#         connection.rollback()
#         raise

#     finally:
#         connection.close()


# def insert_price_snapshot(tracked_item_id, listing_id, item):
#     """每次爬取都新增一筆價格紀錄。"""

#     connection = get_connection()

#     try:
#         with connection.cursor() as cursor:
#             sql = """
#                 INSERT INTO price_snapshots (
#                     tracked_item_id,
#                     listing_id,
#                     price_jpy,
#                     shipping_jpy,
#                     stock_status,
#                     captured_at
#                 )
#                 VALUES (%s, %s, %s, NULL, %s, %s)
#             """

#             cursor.execute(
#                 sql,
#                 (
#                     tracked_item_id,
#                     listing_id,
#                     item["price_jpy"],
#                     item["stock_status"],
#                     item["captured_at"],
#                 ),
#             )

#         connection.commit()

#     except Exception:
#         connection.rollback()
#         raise

#     finally:
#         connection.close()


# def main():
#     try:
#         tracked_items = get_active_tracked_items()

#         print(f"目前啟用追蹤：{len(tracked_items)} 位角色\n")

#         for tracked_item in tracked_items:
#             print("=" * 70)
#             print(
#                 f"ID：{tracked_item['id']}｜"
#                 f"{tracked_item['anime_title']}｜"
#                 f"{tracked_item['character_name']}"
#             )
#             print(f"關鍵字：{tracked_item['search_keyword']}")

#             raw_items = search_rakuten(tracked_item["search_keyword"])
#             cleaned_items = clean_items(raw_items)

#             print(f"原始資料：{len(raw_items)} 筆")
#             print(f"清洗後資料：{len(cleaned_items)} 筆\n")

#             for number, item in enumerate(cleaned_items, start=1):
#                 print(f"[{number}] {item['title']}")
#                 print(f"價格：¥{item['price_jpy']:,}")
#                 print(f"商店：{item['shop_name']}")
#                 print(f"網址：{item['product_url']}")
#                 print("-" * 50)
#                 listing_id = upsert_listing(tracked_item["id"], item)

#                 insert_price_snapshot(
#                     tracked_item["id"],
#                     listing_id,
#                     item,
#                 )

#                 print(f"已寫入資料庫：listing_id = {listing_id}")

#     except requests.RequestException as error:
#         print(f"樂天 API 請求失敗：{error}")
#     except Exception as error:
#         print(f"程式執行失敗：{error}")


# if __name__ == "__main__":
#     main()






import os
import re
from datetime import datetime

import requests
from dotenv import load_dotenv

from database import get_connection

load_dotenv()

# 全球開發者標準官方 IchibaItem 端點
API_URL = "https://rakuten.co.jp"

APPLICATION_ID = os.getenv("RAKUTEN_APPLICATION_ID")


EXCLUDE_KEYWORDS = [
    "セット",
    "コンプリート",
    "BOX",
    "ボックス",
    "予約",
    "福袋",
    "まとめ売り",
]


def extract_series_name(title, anime_title):
    """從樂天商品名稱中自動擷取一番賞系列主題（穩定版）"""

    if not title:
        return "未分類"

    # 清除常見雜訊
    clean_title = title

    noise_words = [
        "【未開封】", "【中古】", "【新品】",
        "未開封", "中古", "新品",
        "BANDAI SPIRITS", "バンダイ", "日版", "正版"
    ]

    for word in noise_words:
        clean_title = clean_title.replace(word, "")

    clean_title = clean_title.strip()

    # =========================================================
    # 規則 1：擷取「一番くじ 作品名 系列名」
    # 例如：
    # 一番くじ BLEACH Stirring Souls vol.4 C賞
    # → Stirring Souls vol.4
    # =========================================================
    pattern = (
        r'(?:一番くじ|一番クジ)\\s*'
        + re.escape(anime_title)
        + r'\\s+(.+?)(?:\\s+[A-Z]賞|\\s+フィギュア|\\s*$)'
    )

    match = re.search(pattern, clean_title, re.IGNORECASE)

    if match:
        series = match.group(1).strip()

        # 去掉尾端多餘符號
        series = re.sub(r'[】\\]）)]+$', '', series).strip()

        if len(series) >= 3:
            return series

    # =========================================================
    # 規則 2：BLEACH 特例（因為很多商品寫法不一致）
    # =========================================================
    bleach_match = re.search(
        r'BLEACH\\s+(.+?)(?:\\s+[A-Z]賞|\\s+フィギュア|\\s*$)',
        clean_title,
        re.IGNORECASE
    )

    if bleach_match:
        series = bleach_match.group(1).strip()

        if len(series) >= 3:
            return series

    # =========================================================
    # 規則 3：保底
    # =========================================================
    return anime_title



def calculate_popularity_score(total_count):
    """💡 級距換算器：依據樂天市場當前上架的總件數，自動評定 1~5 星的人氣熱度"""
    if total_count >= 2500:
        return 5
    elif total_count >= 800:
        return 4
    elif total_count >= 200:
        return 3
    elif total_count >= 50:
        return 2
    else:
        return 1


def update_tracked_item_meta(tracked_item_id, popularity_score, series_name):
    """💡 自動回填：將自動算好的熱度與系列名稱更新回 MySQL 專案主表"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 強制將判定出來的系列主題更新進去
            sql = """
                UPDATE tracked_items 
                SET popularity_score = %s,
                    series_name = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(sql, (popularity_score, series_name, tracked_item_id))
        connection.commit()
    except Exception as e:
        print(f"⚠️ 更新角色中繼資料失敗 (ID: {tracked_item_id}): {e}")
        connection.rollback()
    finally:
        connection.close()


def search_rakuten(keyword, hits=10):
    """用關鍵字搜尋日本樂天市場，回傳整理過的商品清單。"""
    if not APPLICATION_ID:
        raise ValueError("找不到 RAKUTEN_APPLICATION_ID，請檢查 .env 檔案。")

    params = {
        "applicationId": APPLICATION_ID,
        "keyword": keyword,
        "hits": hits,
        "page": 1,
        "format": "json",
        "sort": "standard"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(API_URL, params=params, headers=headers, timeout=20)
    
    if response.status_code != 200:
        print(f"\n❌ 樂天伺服器連線失敗，代碼：{response.status_code}")
        return 0, []

    try:
        data = response.json()
    except Exception:
        return 0, []

    if "error" in data:
        print(f"⚠️ 樂天 API 傳回內置錯誤訊息: {data.get('error_description', '')}")
        return 0, []

    total_count = data.get("count") or data.get("Count") or 0
    captured_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = []

    # 萬能相容解析：處理官方封裝的 "Item" 雙層外殼
    for item_wrapper in data.get("Items", []):
        if not isinstance(item_wrapper, dict):
            continue
            
        item = item_wrapper.get("Item", item_wrapper) if "Item" in item_wrapper else item_wrapper
        
        # 兼容處理官方多重巢狀圖片格式
        images = item.get("mediumImageUrls", [])
        image_url = None
        if isinstance(images, list) and len(images) > 0:
            first_img = images[0]
            image_url = first_img.get("imageUrl") if isinstance(first_img, dict) else first_img
        elif isinstance(images, dict):
            image_url = images.get("imageUrl")

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

    return total_count, results


def clean_items(items, min_price=500, max_price=30000):
    """排除套組、預購、缺少資料與明顯異常價格。"""
    cleaned_items = []
    for item in items:
        title = item.get("title") or ""
        price = item.get("price_jpy")

        if not title or price is None:
            continue

        if any(word in title for word in EXCLUDE_KEYWORDS):
            continue

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
                    tracked_item_id, source, title, product_url, image_url, last_seen_at, is_active
                )
                VALUES (%s, 'Rakuten', %s, %s, %s, NOW(), TRUE)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title), image_url = VALUES(image_url), last_seen_at = NOW(), is_active = TRUE
            """
            cursor.execute(sql, (tracked_item_id, item["title"], item["product_url"], item["image_url"]))
            cursor.execute("SELECT id FROM listings WHERE product_url = %s", (item["product_url"],))
            listing = cursor.fetchone()
            connection.commit()
            return listing["id"] if listing else None
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def insert_price_snapshot(tracked_item_id, listing_id, item):
    """每次爬取都新增一筆價格紀錄。"""
    if not listing_id:
        return
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO price_snapshots (
                    tracked_item_id, listing_id, price_jpy, shipping_jpy, stock_status, captured_at
                )
                VALUES (%s, %s, %s, NULL, %s, %s)
            """
            cursor.execute(sql, (tracked_item_id, listing_id, item["price_jpy"], item["stock_status"], item["captured_at"]))
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
            print(f"ID：{tracked_item['id']}｜{tracked_item['anime_title']}｜{tracked_item['character_name']}")
            print(f"關鍵字：{tracked_item['search_keyword']}")

            # 1. 呼叫 API 
            total_count, raw_items = search_rakuten(tracked_item["search_keyword"], hits=30)
            cleaned_items = clean_items(raw_items)

            # 🎯 終極修正：使用標準 [0] 取第一筆資料，完美相容無崩潰
            from collections import Counter

            series_counter = Counter()

            for item in cleaned_items:
                series = extract_series_name(item.get("title"), tracked_item["anime_title"])
                if series and series != "未分類":
                    series_counter[series] += 1

            if series_counter:
                detected_series = series_counter.most_common(1)[0][0]
            else:
                detected_series = tracked_item["anime_title"]
            
            # 2. 自動計算 1~5 星熱度分數，並連同系列名更新
            popularity_score = calculate_popularity_score(total_count)
            update_tracked_item_meta(tracked_item["id"], popularity_score, detected_series)

            print(f"原始資料：{len(raw_items)} 筆 (樂天現存總量：{total_count} 件 ➡️ 自動評定熱度：{popularity_score} 星)")
            print(f"🤖 樂天資訊自動判定系列名稱為：【{detected_series}】(已寫入資料庫)")
            print(f"清洗後資料：{len(cleaned_items)} 筆\n")

            for number, item in enumerate(cleaned_items, start=1):
                print(f"[{number}] {item['title'][:35]}...")
                print(f"價格：¥{item['price_jpy']:,} ｜ 商店：{item['shop_name']}")
                print("-" * 50)
                
                listing_id = upsert_listing(tracked_item["id"], item)
                insert_price_snapshot(tracked_item["id"], listing_id, item)

    except Exception as error:
        print(f"程式執行失敗：{error}")


if __name__ == "__main__":
    main()

