import os
import re
from datetime import datetime

import requests
from dotenv import load_dotenv

from database import get_connection

import logging

load_dotenv()

# 全球開發者標準官方 IchibaItem 端點
API_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
SEARCH_HITS = 30
REQUEST_TIMEOUT_SECONDS = 20

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


def update_tracked_item_popularity(tracked_item_id, popularity_score):
    """💡 自動回填：將自動算好的熱度與系列名稱更新回 MySQL 專案主表"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 強制將判定出來的系列主題更新進去
            sql = """
                UPDATE tracked_items
                SET popularity_score = %s,
                    updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(sql, (popularity_score, tracked_item_id))
        connection.commit()
    except Exception as e:
        print(f"⚠️ 更新角色中繼資料失敗 (ID: {tracked_item_id}): {e}")
        connection.rollback()
    finally:
        connection.close()


def search_rakuten(keyword, hits=SEARCH_HITS):
    """用關鍵字搜尋日本樂天市場，回傳整理過的商品清單。"""
    if not APPLICATION_ID or not ACCESS_KEY:
        raise ValueError("找不到 RAKUTEN_APPLICATION_ID，請檢查 .env 檔案。")

    params = {
        "applicationId": APPLICATION_ID,
        "accessKey": ACCESS_KEY,
        "keyword": keyword,
        "hits": hits,
        "page": 1,
        "format": "json",
        "formatVersion": 2,
        "sort": "standard"
    }

    headers = {
        "applicationId": APPLICATION_ID,
        "accessKey": ACCESS_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.rakuten.co.jp/",
        "Origin": "https://www.rakuten.co.jp/",
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
        allow_redirects=False,
    )
    
    if response.status_code != 200:
        print(f"\n❌ 樂天伺服器連線失敗，代碼：{response.status_code}")
        print(f"🔍 Rakuten 回應內容：{response.text[:2000]}")
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





def snapshot_exists_today(listing_id):
    """確認此商品今天是否已存過價格快照。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id
                FROM price_snapshots
                WHERE listing_id = %s
                  AND DATE(captured_at) = CURDATE()
                LIMIT 1
            """, (listing_id,))

            return cursor.fetchone() is not None

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
                SELECT %s, %s, %s, NULL, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM price_snapshots
                    WHERE tracked_item_id = %s
                      AND listing_id = %s
                      AND DATE(captured_at) = DATE(%s)
                )
            """
            cursor.execute(
                sql,
                (
                    tracked_item_id,
                    listing_id,
                    item["price_jpy"],
                    item["stock_status"],
                    item["captured_at"],
                    tracked_item_id,
                    listing_id,
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
    """Crawl every active tracked item without one failure stopping the run."""
    try:
        tracked_items = get_active_tracked_items()
    except Exception as error:
        logging.exception("Unable to load active tracked items")
        print(f"Unable to load active tracked items: {error}")
        return

    print(f"Crawling {len(tracked_items)} active tracked item(s).")

    for tracked_item in tracked_items:
        try:
            total_count, raw_items = search_rakuten(
                tracked_item["search_keyword"]
            )
            cleaned_items = clean_items(raw_items)
            popularity_score = calculate_popularity_score(total_count)
            update_tracked_item_popularity(
                tracked_item["id"], popularity_score
            )

            for item in cleaned_items:
                listing_id = upsert_listing(tracked_item["id"], item)
                insert_price_snapshot(tracked_item["id"], listing_id, item)

            print(
                f"Completed tracked item {tracked_item['id']} "
                f"({tracked_item['character_name']}): "
                f"{len(cleaned_items)} listing(s), popularity {popularity_score}."
            )
        except Exception as error:
            logging.exception(
                "Failed to crawl tracked item %s", tracked_item["id"]
            )
            print(
                f"Failed tracked item {tracked_item['id']} "
                f"({tracked_item['character_name']}): {error}"
            )


if __name__ == "__main__":
    main()

