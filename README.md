# 台日一番賞價格監測與跨境成本試算系統

[![CI](https://github.com/kuma07-dev/figure-project/actions/workflows/ci.yml/badge.svg)](https://github.com/kuma07-dev/figure-project/actions/workflows/ci.yml)

以日本樂天市場為資料來源，追蹤指定一番賞角色的刊登價格，保存每日價格快照，並在網站上呈現價格走勢、價格預警與跨境購入的成本試算。

> 本專案為資展國際 Python AI 應用工程師就業養成班（AIPE04）的個人期中專題（2026/08）。
> 價格資料為樂天市場的**刊登價**，不是實際成交價；本系統用於價格觀察與成本試算，不保證套利獲利。

## 功能

- **價格蒐集**：串接樂天市場商品搜尋 API，依追蹤清單（3 部作品、9 個角色）搜尋商品，每個角色每次取 30 筆
- **資料清洗**：排除套組、預購、福袋、合售等商品，並只保留 ¥500 – ¥30,000 的價格
- **歷史價格**：以商品網址去重，同一商品同一天只記一筆快照，累積成時間序列
- **價格走勢**：依日期計算每日中位數，以 Chart.js 折線圖呈現
- **價格狀態**：單筆價格比當日中位數低 15% 以上標示「低估特價」，高 15% 以上標示「溢價偏高」
- **漲幅預警**：最近兩個資料日的中位數上漲 15% 以上時，顯示「潛在漲幅預警」
- **跨境成本試算**：輸入商品價格、日本運費、匯率、代購費率、國際運費、平台手續費率與預估售價，計算落地成本、損益兩平售價與預估淨利，並檢查不合理的輸入

## 技術

| 類別 | 使用 |
| --- | --- |
| 語言 | Python |
| 資料蒐集 | Requests、樂天市場 Ichiba Item Search API |
| 資料庫 | MySQL、PyMySQL |
| 網站 | Flask、Jinja2、Chart.js |
| 設定 | python-dotenv |
| 容器 | Docker、Docker Compose、Gunicorn |
| 測試與 CI | pytest、ruff、GitHub Actions |

## 系統流程

```text
tracked_items（追蹤清單）
  → 樂天市場商品搜尋 API
  → 清洗（排除關鍵字、價格範圍）
  → listings（商品，網址唯一） + price_snapshots（價格快照，每日去重）
  → Flask 網站：首頁、作品篩選、角色詳情與走勢圖、成本試算器
```

## 資料表

| 資料表 | 內容 |
| --- | --- |
| `tracked_items` | 追蹤的作品、角色、搜尋關鍵字與評分欄位 |
| `listings` | 樂天市場商品（名稱、網址、圖片），網址唯一 |
| `price_snapshots` | 每次抓取的日圓價格、庫存狀態與時間 |

建表語法在 `database/schema.sql`，初始追蹤清單在 `database/seed_data.sql`。

## 網站頁面

| 路徑 | 內容 |
| --- | --- |
| `/` | 所有追蹤商品的最新價格 |
| `/series/<作品名稱>` | 依作品篩選 |
| `/character/<id>` | 角色詳情：價格走勢圖、預警、各筆價格狀態 |
| `/calculator` | 跨境成本試算器 |

## 執行方式

### 方法一：Docker（推薦）

需要 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

1. 建立 `.env`，填入樂天 API 金鑰（不要提交到 Git）

   ```bash
   cp .env.example .env
   ```

2. 啟動 MySQL 與網站。第一次啟動時會自動建立資料表與追蹤清單

   ```bash
   docker compose up --build
   ```

3. 執行爬蟲抓取價格（另開一個終端機）

   ```bash
   docker compose run --rm web python -m crawler.rakuten_crawler
   ```

4. 開啟 http://localhost:5000

停止：`docker compose down`。加上 `-v` 會一併刪除資料庫資料。

### 方法二：本機直接執行

1. 安裝套件

   ```bash
   pip install -r requirements.txt
   ```

2. 複製 `.env.example` 為 `.env`，填入樂天 API 金鑰與本機 MySQL 帳密

3. 建立資料表與追蹤清單

   ```bash
   mysql -u <帳號> -p < database/schema.sql
   mysql -u <帳號> -p < database/seed_data.sql
   ```

4. 執行爬蟲，再啟動網站（http://localhost:5000）

   ```bash
   python -m crawler.rakuten_crawler
   python app.py
   ```

## 測試

```bash
pip install pytest ruff
ruff check .
pytest
```

測試涵蓋成本試算公式、輸入檢查、資料清洗規則與試算頁面，不需要資料庫或 API 金鑰。每次 push 到 GitHub 時，GitHub Actions 會自動執行程式碼檢查、測試與 Docker 映像檔建置。

## 檢查工具

```bash
python -m scripts.check_rakuten_api   # 確認樂天 API 金鑰與連線（只查詢 5 筆，不寫入資料庫）
python -m scripts.check_db            # 確認資料庫連線與各資料表筆數
```

使用 Docker 時，在指令前加上 `docker compose run --rm web`。

## 限制

- 只有樂天市場一個資料來源，價格為刊登價而非成交價
- 樂天 API 不提供日本國內運費，成本試算需手動輸入
- 爬蟲需手動執行，尚未設定自動排程
- 尚無台灣市場價格資料，無法直接驗證台日價差

## 未來規劃

- 加入自動排程與執行紀錄
- 預警加上樣本數門檻與時間窗，並保存成可追溯的紀錄
- 加入台灣市場價格（手動匯入或其他來源），比較台日價差
- 依人氣、稀有度、造型等特徵計算加權推薦分數

最初的完整構想見 [docs/proposal.md](docs/proposal.md)。
