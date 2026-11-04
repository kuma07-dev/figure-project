"""確認樂天 API 金鑰與連線是否正常。只查詢，不寫入資料庫。

用法：
    python -m scripts.check_rakuten_api
    python -m scripts.check_rakuten_api "一番くじ ワンピース ルフィ"
"""

import sys

from crawler.rakuten_crawler import ACCESS_KEY, APPLICATION_ID, search_rakuten

DEFAULT_KEYWORD = "一番くじ 呪術廻戦 五条悟"


def main():
    missing = [
        name
        for name, value in (
            ("RAKUTEN_APPLICATION_ID", APPLICATION_ID),
            ("RAKUTEN_ACCESS_KEY", ACCESS_KEY),
        )
        if not value
    ]
    if missing:
        print(f"找不到 {', '.join(missing)}，請檢查 .env 檔案。")
        return 1

    keyword = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KEYWORD
    print(f"查詢關鍵字：{keyword}")

    total_count, items = search_rakuten(keyword, hits=5)
    if not items:
        print("沒有取得任何商品，請檢查金鑰是否正確，或換一個關鍵字再試。")
        return 1

    print(f"連線成功：樂天市場共有 {total_count} 件商品，以下為前 {len(items)} 筆")
    for number, item in enumerate(items, start=1):
        print(f"[{number}] ¥{item['price_jpy']:,}｜{item['title'][:40]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
