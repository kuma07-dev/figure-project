from collections import defaultdict
from statistics import median

from flask import Flask, render_template, request

from database import get_connection
from services.cost import CostInputError, calculate_landed_cost, parse_cost_form


app = Flask(__name__)


def get_latest_items(anime_title=None):
    """取得每個商品的最新快照；可依作品名稱篩選。"""
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
            """
            if anime_title is not None:
                sql += " AND t.anime_title = %s"
                params = (anime_title,)
                sql += " ORDER BY t.character_name, p.price_jpy ASC;"
            else:
                params = ()
                sql += " ORDER BY t.anime_title, t.character_name, p.price_jpy ASC;"

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()


@app.route("/")
def index():
    return render_template("index.html", items=get_latest_items())


@app.route("/series/<string:anime_title>")
def series_filter(anime_title):
    return render_template("index.html", items=get_latest_items(anime_title))


@app.route("/character/<int:character_id>")
def character_detail(character_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, anime_title, character_name,
                       popularity_score, rarity_score, quality_score, design_score
                FROM tracked_items
                WHERE id = %s
                LIMIT 1
            """, (character_id,))
            tracked_item = cursor.fetchone()

            if not tracked_item:
                return "找不到黑崎一護資料", 404

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

            # 依資料日分組，供趨勢圖與商品價格狀態共用。
            daily_prices = defaultdict(list)
            for snapshot in snapshots:
                if snapshot["captured_at"]:
                    date_key = snapshot["captured_at"].strftime("%Y-%m-%d")
                    daily_prices[date_key].append(snapshot["price_jpy"])

            chart_labels = sorted(daily_prices.keys())
            daily_medians = {
                date: median(prices)
                for date, prices in daily_prices.items()
            }
            chart_prices = [daily_medians[date] for date in chart_labels]

            # 商品價格狀態：每筆商品與「同一資料日」的中位數比較。
            for snapshot in snapshots:
                date_key = snapshot["captured_at"].strftime("%Y-%m-%d")
                daily_median = daily_medians[date_key]
                difference_percent = (
                    (snapshot["price_jpy"] - daily_median) / daily_median
                ) * 100

                snapshot["daily_median"] = daily_median
                snapshot["price_difference_percent"] = round(difference_percent, 1)

                if difference_percent <= -15:
                    snapshot["price_status"] = "低估特價"
                elif difference_percent >= 15:
                    snapshot["price_status"] = "溢價偏高"
                else:
                    snapshot["price_status"] = "價格平穩"

            alert = {
                "status": "資料不足",
                "change_percent": None,
                "previous_median": None,
                "latest_median": None,
            }
            if len(chart_prices) >= 2 and chart_prices[-2] > 0:
                previous_price = chart_prices[-2]
                latest_price = chart_prices[-1]
                change_percent = (
                    (latest_price - previous_price) / previous_price
                ) * 100

                alert["change_percent"] = round(change_percent, 1)
                alert["previous_median"] = previous_price
                alert["latest_median"] = latest_price
                alert["status"] = (
                    "潛在漲幅預警" if change_percent >= 15 else "正常觀察"
                )
    finally:
        connection.close()

    return render_template(
        "character_detail.html",
        tracked_item=tracked_item,
        snapshots=snapshots,
        chart_labels=chart_labels,
        chart_prices=chart_prices,
        alert=alert,
    )


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None
    error = None
    if request.method == "POST":
        try:
            values = parse_cost_form(request.form)
        except CostInputError as input_error:
            error = str(input_error)
        else:
            result = calculate_landed_cost(**values)

    return render_template("calculator.html", result=result, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
