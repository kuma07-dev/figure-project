from flask import Flask, render_template
from database import get_connection

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


if __name__ == "__main__":
    app.run(debug=True)