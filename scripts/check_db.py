"""確認 MySQL 連線，並顯示各資料表的資料筆數。

用法：
    python -m scripts.check_db
"""

import sys

from database import get_connection

TABLES = ("tracked_items", "listings", "price_snapshots")


def main():
    try:
        connection = get_connection()
    except Exception as error:
        print(f"無法連線到資料庫：{error}")
        print("請檢查 .env 的 DB_HOST、DB_PORT、DB_USER、DB_PASSWORD、DB_NAME。")
        return 1

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS current_database")
            print(f"已連線，目前資料庫：{cursor.fetchone()['current_database']}")

            for table in TABLES:
                cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
                print(f"{table}：{cursor.fetchone()['total']} 筆")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
