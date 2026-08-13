from flask import Flask, render_template, request
from database import get_connection
from collections import defaultdict
from statistics import median

app = Flask(__name__)


@app.route("/")
def index():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    t.id AS tracked_item_id,
                    t.anime_title,
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



@app.route("/ichigo")
def ichigo():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # 取得黑崎一護的角色資料
            cursor.execute("""
                SELECT id, anime_title, character_name
                FROM tracked_items
                WHERE character_name = %s
                LIMIT 1
            """, ("黑崎一護",))

            tracked_item = cursor.fetchone()

            if not tracked_item:
                return "找不到黑崎一護資料", 404

            # 取得黑崎一護所有商品的所有歷史價格
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
                   AND p.tracked_item_id = l.tracked_item_id
                WHERE l.tracked_item_id = %s
                ORDER BY l.id, p.captured_at DESC
            """, (tracked_item["id"],))

            snapshots = cursor.fetchall()

            daily_prices = defaultdict(list)

            for snapshot in snapshots:
                # datetime 只取日期，例如 2026-08-13
                date_key = snapshot["captured_at"].strftime("%Y-%m-%d")
                daily_prices[date_key].append(snapshot["price_jpy"])

            chart_labels = sorted(daily_prices.keys())
            chart_prices = [
                median(daily_prices[date])
                for date in chart_labels
            ]

    finally:
        connection.close()

    return render_template(
        "ichigo.html",
        tracked_item=tracked_item,
        snapshots=snapshots,
        chart_labels=chart_labels,
        chart_prices=chart_prices
    )


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None

    if request.method == "POST":
        price_jpy = float(request.form["price_jpy"])
        shipping_jpy = float(request.form["shipping_jpy"])
        exchange_rate = float(request.form["exchange_rate"])
        proxy_fee_rate = float(request.form["proxy_fee_rate"]) / 100
        international_shipping_twd = float(
            request.form["international_shipping_twd"]
        )
        platform_fee_rate = float(request.form["platform_fee_rate"]) / 100
        expected_sale_price_twd = float(
            request.form["expected_sale_price_twd"]
        )

        item_cost_twd = (price_jpy + shipping_jpy) * exchange_rate
        proxy_fee_twd = item_cost_twd * proxy_fee_rate
        landed_cost_twd = (
            item_cost_twd
            + proxy_fee_twd
            + international_shipping_twd
        )
        platform_fee_twd = expected_sale_price_twd * platform_fee_rate
        estimated_profit_twd = (
            expected_sale_price_twd
            - landed_cost_twd
            - platform_fee_twd
        )
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