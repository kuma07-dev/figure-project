# from flask import Flask, render_template, request
# from database import get_connection
# from collections import defaultdict
# from statistics import median

# app = Flask(__name__)


# @app.route("/")
# def index():
#     connection = get_connection()

#     try:
#         with connection.cursor() as cursor:
#             sql = """
#                 SELECT
#                     t.id AS tracked_item_id,
#                     t.anime_title,
#                     t.character_name,
#                     l.id AS listing_id,
#                     l.title,
#                     l.product_url,
#                     l.image_url,
#                     p.price_jpy,
#                     p.captured_at
#                 FROM tracked_items AS t
#                 JOIN listings AS l
#                     ON l.tracked_item_id = t.id
#                 JOIN (
#                     SELECT
#                         id,
#                         listing_id,
#                         price_jpy,
#                         captured_at,
#                         ROW_NUMBER() OVER (
#                             PARTITION BY listing_id
#                             ORDER BY captured_at DESC, id DESC
#                         ) AS row_num
#                     FROM price_snapshots
#                 ) AS p
#                     ON p.listing_id = l.id
#                    AND p.row_num = 1
#                 WHERE t.is_active = TRUE
#                   AND l.is_active = TRUE
#                 ORDER BY t.anime_title, t.character_name, p.price_jpy ASC;
#             """

#             cursor.execute(sql)
#             items = cursor.fetchall()

#     finally:
#         connection.close()

#     return render_template("index.html", items=items)



# @app.route("/ichigo")
# def ichigo():
#     connection = get_connection()

#     try:
#         with connection.cursor() as cursor:
#             # 取得黑崎一護的角色資料
#             cursor.execute("""
#                 SELECT id, anime_title, character_name
#                 FROM tracked_items
#                 WHERE character_name = %s
#                 LIMIT 1
#             """, ("黑崎一護",))

#             tracked_item = cursor.fetchone()

#             if not tracked_item:
#                 return "找不到黑崎一護資料", 404

#             # 取得黑崎一護所有商品的所有歷史價格
#             cursor.execute("""
#                 SELECT
#                     l.id AS listing_id,
#                     l.title,
#                     l.product_url,
#                     l.image_url,
#                     p.price_jpy,
#                     p.shipping_jpy,
#                     p.captured_at
#                 FROM listings AS l
#                 JOIN price_snapshots AS p
#                     ON p.listing_id = l.id
#                    AND p.tracked_item_id = l.tracked_item_id
#                 WHERE l.tracked_item_id = %s
#                 ORDER BY l.id, p.captured_at DESC
#             """, (tracked_item["id"],))

#             snapshots = cursor.fetchall()

#             daily_prices = defaultdict(list)

#             for snapshot in snapshots:
#                 # datetime 只取日期，例如 2026-08-13
#                 date_key = snapshot["captured_at"].strftime("%Y-%m-%d")
#                 daily_prices[date_key].append(snapshot["price_jpy"])

#             chart_labels = sorted(daily_prices.keys())
#             chart_prices = [
#                 median(daily_prices[date])
#                 for date in chart_labels
#             ]

#     finally:
#         connection.close()

#     return render_template(
#         "ichigo.html",
#         tracked_item=tracked_item,
#         snapshots=snapshots,
#         chart_labels=chart_labels,
#         chart_prices=chart_prices
#     )


# @app.route("/calculator", methods=["GET", "POST"])
# def calculator():
#     result = None

#     if request.method == "POST":
#         price_jpy = float(request.form["price_jpy"])
#         shipping_jpy = float(request.form["shipping_jpy"])
#         exchange_rate = float(request.form["exchange_rate"])
#         proxy_fee_rate = float(request.form["proxy_fee_rate"]) / 100
#         international_shipping_twd = float(
#             request.form["international_shipping_twd"]
#         )
#         platform_fee_rate = float(request.form["platform_fee_rate"]) / 100
#         expected_sale_price_twd = float(
#             request.form["expected_sale_price_twd"]
#         )

#         item_cost_twd = (price_jpy + shipping_jpy) * exchange_rate
#         proxy_fee_twd = item_cost_twd * proxy_fee_rate
#         landed_cost_twd = (
#             item_cost_twd
#             + proxy_fee_twd
#             + international_shipping_twd
#         )
#         platform_fee_twd = expected_sale_price_twd * platform_fee_rate
#         estimated_profit_twd = (
#             expected_sale_price_twd
#             - landed_cost_twd
#             - platform_fee_twd
#         )
#         break_even_price_twd = landed_cost_twd / (1 - platform_fee_rate)

#         if estimated_profit_twd > 0:
#             recommendation = "可觀察"
#         elif estimated_profit_twd == 0:
#             recommendation = "損益兩平"
#         else:
#             recommendation = "不建議"

#         result = {
#             "item_cost_twd": round(item_cost_twd),
#             "proxy_fee_twd": round(proxy_fee_twd),
#             "landed_cost_twd": round(landed_cost_twd),
#             "platform_fee_twd": round(platform_fee_twd),
#             "estimated_profit_twd": round(estimated_profit_twd),
#             "break_even_price_twd": round(break_even_price_twd),
#             "recommendation": recommendation,
#         }

#     return render_template("calculator.html", result=result)




# if __name__ == "__main__":
#     app.run(debug=True)












from flask import Flask, render_template, request
from database import get_connection
from collections import defaultdict
from statistics import median

app = Flask(__name__)


# 1. 首頁：顯示所有追蹤角色的最新商品
@app.route("/")
def index():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    t.id AS tracked_item_id,
                    t.anime_title,
                    t.series_name,
                    t.character_name,
                    l.id AS listing_id,
                    l.title,
                    l.product_url,
                    l.image_url,
                    p.price_jpy,
                    p.captured_at
                FROM tracked_items AS t
                JOIN listings AS l
                    ON l.tracked_item_id = t.id
                JOIN (
                    SELECT
                        id,
                        listing_id,
                        price_jpy,
                        captured_at,
                        ROW_NUMBER() OVER (
                            PARTITION BY listing_id
                            ORDER BY captured_at DESC, id DESC
                        ) AS row_num
                    FROM price_snapshots
                ) AS p
                    ON p.listing_id = l.id
                   AND p.row_num = 1
                WHERE t.is_active = TRUE
                  AND l.is_active = TRUE
                ORDER BY t.anime_title, t.character_name, p.price_jpy ASC;
            """
            cursor.execute(sql)
            items = cursor.fetchall()
    finally:
        connection.close()

    return render_template("index.html", items=items)



# 2. 修改後的分類路由：依作品中文名稱（anime_title）過濾商品
@app.route("/series/<string:series_name>")
def series_filter(series_name):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    t.id AS tracked_item_id,
                    t.anime_title,
                    t.series_name,
                    t.character_name,
                    l.id AS listing_id,
                    l.title,
                    l.product_url,
                    l.image_url,
                    p.price_jpy,
                    p.captured_at
                FROM tracked_items AS t
                JOIN listings AS l
                    ON l.tracked_item_id = t.id
                JOIN (
                    SELECT
                        id,
                        listing_id,
                        price_jpy,
                        captured_at,
                        ROW_NUMBER() OVER (
                            PARTITION BY listing_id
                            ORDER BY captured_at DESC, id DESC
                        ) AS row_num
                    FROM price_snapshots
                ) AS p
                    ON p.listing_id = l.id
                   AND p.row_num = 1
                WHERE t.is_active = TRUE
                  AND l.is_active = TRUE
                  AND t.anime_title = %s  -- 🎯 這裡改成了 anime_title，用中文作品名來找！
                ORDER BY t.character_name, p.price_jpy ASC;
            """
            cursor.execute(sql, (series_name,))
            items = cursor.fetchall()
    finally:
        connection.close()

    return render_template("index.html", items=items)



# 3. 升級後的角色詳情頁：支援所有角色的 ID 查詢，含評分與價格預警數據
@app.route("/character/<int:character_id>")
def character_detail(character_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 依據傳入的 ID 動態取得角色與作品資料（包含所有評分欄位）
            cursor.execute("""
                SELECT id, anime_title, character_name,
                       popularity_score, rarity_score, quality_score, design_score
                FROM tracked_items
                WHERE id = %s
                LIMIT 1
            """, (character_id,))
            tracked_item = cursor.fetchone()

            if not tracked_item:
                return "找不到該角色資料", 404

            # 依據傳入的 ID 動態撈取所有歷史價格明細
            cursor.execute("""
                SELECT
                    l.id AS listing_id,
                    l.title,
                    l.product_url,
                    l.image_url,
                    p.price_jpy,
                    p.shipping_jpy,
                    p.captured_at
                FROM listings AS l
                JOIN price_snapshots AS p
                    ON p.listing_id = l.id
                WHERE l.tracked_item_id = %s
                ORDER BY p.captured_at DESC
            """, (character_id,))
            snapshots = cursor.fetchall()

            # 計算 Chart.js 圖表所需的中位數趨勢數據，以及預警用的總基準線
            daily_prices = defaultdict(list)
            all_prices = []
            
            for snapshot in snapshots:
                if snapshot["captured_at"]:
                    date_key = snapshot["captured_at"].strftime("%Y-%m-%d")
                    daily_prices[date_key].append(snapshot["price_jpy"])
                    all_prices.append(snapshot["price_jpy"])

            chart_labels = sorted(daily_prices.keys())
            chart_prices = [
                median(daily_prices[date])
                for date in chart_labels
            ] if daily_prices else []
            
            # 計算當前所有觀測商品的總中位數，做為前端 HTML 綠/紅燈預警的判定基準
            current_median = median(all_prices) if all_prices else 0

    finally:
        connection.close()

    # 統一渲染至通用詳情網頁模版，並傳入預警所需的變數
    return render_template(
        "character_detail.html",
        tracked_item=tracked_item,
        snapshots=snapshots,
        chart_labels=chart_labels,
        chart_prices=chart_prices,
        current_median=current_median
    )


# 4. 跨境成本試算器（維持原功能）
@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        price_jpy = float(request.form["price_jpy"])
        shipping_jpy = float(request.form["shipping_jpy"])
        exchange_rate = float(request.form["exchange_rate"])
        proxy_fee_rate = float(request.form["proxy_fee_rate"]) / 100
        international_shipping_twd = float(request.form["international_shipping_twd"])
        platform_fee_rate = float(request.form["platform_fee_rate"]) / 100
        expected_sale_price_twd = float(request.form["expected_sale_price_twd"])

        item_cost_twd = (price_jpy + shipping_jpy) * exchange_rate
        proxy_fee_twd = item_cost_twd * proxy_fee_rate
        landed_cost_twd = item_cost_twd + proxy_fee_twd + international_shipping_twd
        platform_fee_twd = expected_sale_price_twd * platform_fee_rate
        estimated_profit_twd = expected_sale_price_twd - landed_cost_twd - platform_fee_twd
        break_even_price_twd = landed_cost_twd / (1 - platform_fee_rate)

        if estimated_profit_twd > 0:
            recommendation = "可觀察"
        elif estimated_profit_twd == 0:
            recommendation = "損益兩平"
        else:
            recommendation = "不建議"

        result = {
            "item_cost_twd": round(item_cost_twd),
            "proxy_fee_twd": round(proxy_fee_twd),
            "landed_cost_twd": round(landed_cost_twd),
            "platform_fee_twd": round(platform_fee_twd),
            "estimated_profit_twd": round(estimated_profit_twd),
            "break_even_price_twd": round(break_even_price_twd),
            "recommendation": recommendation,
        }

    return render_template("calculator.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
