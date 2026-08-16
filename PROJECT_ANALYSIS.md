# ichiban-arbitrage-system 專題健檢

> 分析日期：2026-08-16  
> 判定原則：以目前 repository 的可執行程式與 SQL 為主；README、逐字稿中的未落地內容不列為完成成果。未連接本機 MySQL 或 Rakuten API，因此「資料已成功長期累積／線上服務可用」仍待現場驗證。

## 0. 一句話定位

這是一個以 **Rakuten Ichiba（日本樂天市場）** 為單一自動資料來源的 MVP：依追蹤角色搜尋商品、保存日圓價格快照，在 Flask 網站顯示最新商品、每日中位數與簡易價格訊號，並讓使用者試算跨境購入後的成本與損益。

建議報告名稱：**台日一番賞價格監測系統**  
建議定位：**套利機會監測／可行性分析的 MVP**，不是保證套利的系統。

## 1. 問題、使用者與價值

- **問題**：同一追蹤角色在樂天可能有多筆刊登；只看單筆當下價格，無法看出整體日價格是否變動，也無法把匯率、代購費、物流與平台費一起估入。
- **使用者**：想追蹤特定一番賞角色的收藏者，或想先估算跨境購入／轉售成本的人。
- **為何值得做**：手動重複查商品與手算成本容易漏資料；保留快照後，才能將「當前刊登價格」轉為可觀察的時間序列。
- **必要界線**：Rakuten 資料是刊登價，不是成交價；目前沒有台灣市場自動資料，不能據此驗證台日價差、更不能證明穩定套利。

## 2. 實際完成度（程式碼可證明）

### A. 已完成或已有實作

| 功能 | 程式依據 | 報告可怎麼說 |
|---|---|---|
| Rakuten Item Search API 呼叫與 JSON 解析 | `crawler/rakuten_crawler.py` 的 `search_rakuten()` | 對每個啟用追蹤項目向 Rakuten 搜尋，解析名稱、價格、URL、圖片、商店、庫存欄位。|
| 基本商品清洗 | `clean_items()` | 排除套組、預購、福袋、合售等關鍵字，並僅保留 ¥500–¥30,000。|
| 自動追蹤清單與資料寫入 | `get_active_tracked_items()`、`upsert_listing()`、`insert_price_snapshot()` | 讀取啟用角色；以商品 URL 去重；同一追蹤項目、同一商品、同一天不重複寫入快照。|
| 人氣分數回寫 | `calculate_popularity_score()`、`update_tracked_item_popularity()` | 將 Rakuten 搜尋回傳的總件數以固定級距換算為 1–5 分，再寫回 `tracked_items`。它代表搜尋件數級距，不等同真實市場人氣。|
| Flask 網頁路由 | `app.py` | 有首頁 `/`、作品篩選 `/series/<anime_title>`、角色詳情 `/character/<id>`、成本試算 `/calculator`（GET/POST）。|
| 最新快照清單 | `get_latest_items()` | 使用 MySQL 視窗函式取得每個 listing 最新一筆價格。|
| 每日中位數與圖表資料 | `character_detail()`、`templates/character_detail.html` | 依日期分組所有快照，以 Python `median()` 算每日中位數，再由 Chart.js 折線圖呈現。|
| 簡易價格狀態 | `character_detail()` | 單筆價格相對同日中位數：≤ -15% 為「低估特價」、≥ +15% 為「溢價偏高」，其餘為「價格平穩」。|
| 兩日期中位數變動訊號 | `character_detail()` | 至少有兩個資料日，且最新／前一資料日中位數上升 ≥15%，畫面顯示「潛在漲幅預警」；否則是「正常觀察」。|
| 跨境成本／損益試算與基本防呆 | `app.py` 的 `calculator()` | 輸入價格、運費、匯率、代購費、國際運費、平台費與預估售價，算落地成本、保本售價、預估淨利與結果標示。負數、非有限數和平台費 ≥100% 會被拒絕。|
| 初始追蹤資料 | `database/seed_data.sql` | SQL 預置 3 部作品、9 個角色的追蹤關鍵字；這是追蹤設定，不是已驗證的市場樣本。|

靜態檢查結果：`app.py`、`database.py`、`crawler/`、`analyzer/`、兩個測試檔均可通過 Python 語法編譯；這**不等於**資料庫、API 或端到端流程已在本次分析中實際執行成功。

### B. README／文件宣稱，但目前不可列為完成成果

| 宣稱或文件內容 | 實際狀態 |
|---|---|
| `alerts` 資料表與預警紀錄保存 | `database/schema.sql` 只有 `tracked_items`、`listings`、`price_snapshots`；沒有 `alerts` 表。預警只在詳情請求時計算，未保存。|
| 「最近兩次或 48 小時」且「有效樣本至少 5 筆」才預警 | 現行程式只比較排序後的最後兩個資料日中位數；沒有 48 小時視窗，也沒有樣本數 ≥5 的條件。|
| 五大特徵加權推薦分數 | `analyzer/opportunity_analyzer.py` 為空；後端未計算人氣／稀有度／造型／品質／動能的加權公式。頁面僅顯示資料庫分數，所謂「綜合推薦度」若 `design_score` 無值則是三個分數的未加權平均。|
| 系列名稱自動擷取與回寫 | 有 `extract_series_name()` 與舊 `_legacy_main()` 的設計，但現行 `main()` 未呼叫它，也未更新 `series_name`。|
| 日本國內運費 | Rakuten API 解析結果未提供運費；快照寫入 `shipping_jpy = NULL`。資料表和試算器可接受運費，但爬蟲不會自動取得。|
| 固定每日排程 | repository 沒有 scheduler、cron、Docker 或部署設定。可手動執行爬蟲，但未見自動排程。|
| 台灣市場資料／台日價格領先驗證 | 沒有台灣來源、匯入程式、資料表或統計驗證。|
| 機器學習／機會推薦 | 無實作，且現有資料量也不足以合理訓練或驗證。|

### C. 合理列入 NEXT 的方向

1. 增加台灣市場資料與可比對的成交／售價資料，才可驗證台日市場關係。
2. 累積較長且更乾淨的歷史資料，補上樣本數與時間窗規則。
3. 把預警改為可保存、可追溯的事件，並加入來源、樣本數與門檻依據。
4. 加入排程與可觀測性（執行紀錄、失敗通知、資料品質檢查）。

## 3. 系統資料流程（以實作為準）

```text
tracked_items（啟用的搜尋關鍵字）
  → Rakuten Ichiba Item Search API
  → JSON 相容解析（Items / Item、圖片欄位）
  → 清洗：排除字詞、價格範圍
  → listings（商品 URL 唯一） + price_snapshots（同日去重）
  → Flask / MySQL 查詢
  → 首頁／作品篩選／角色詳情／Chart.js 折線圖／成本試算器
```

其中 `price_snapshots` 保存日圓價格、可空的日本運費、庫存狀態與抓取時間。首頁只顯示每個 listing 最新快照；詳情頁則取該角色全部快照來算每日中位數。

## 4. Database schema／資料模型

```text
tracked_items (1) ───< listings (1) ───< price_snapshots
      │                    │                    │
      │                    └── 商品 URL 唯一     └── 價格與抓取時間
      └── 作品、角色、搜尋關鍵字、人工／回寫分數
```

### `tracked_items`

- `id`、`anime_title`、`series_name`、`character_name`、`search_keyword`
- 可選的 `prize_rank`、`popularity_score`、`rarity_score`、`quality_score`、`design_score`
- `is_active` 與建立／更新時間
- `search_keyword` 唯一；各分數限制為 1–5 或 NULL。

### `listings`

- 一筆 Rakuten 刊登商品對應一個 `tracked_item_id`。
- 有 `source`（預設 Rakuten）、名稱、商品 URL、圖片 URL、首次／最後看見時間與啟用狀態。
- `product_url` 唯一，避免同一 URL 重複建商品。

### `price_snapshots`

- 每次觀測的 `tracked_item_id`、`listing_id`、`price_jpy`、`shipping_jpy`、`stock_status`、`captured_at`。
- 透過複合外鍵確保 listing 對應同一個 tracked item。
- 爬蟲 SQL 對「同一 tracked item、listing、日期」採 `NOT EXISTS`，因此設計上每件商品每日最多一筆快照。

## 5. API、前端頁面與資料來源

### 對外／網站路由（不是 REST JSON API）

| 路徑 | 方法 | 用途 |
|---|---|---|
| `/` | GET | 顯示所有啟用商品 listing 的最新快照。|
| `/series/<anime_title>` | GET | 依作品名稱篩選首頁清單。|
| `/character/<int:character_id>` | GET | 角色分數、歷史快照、每日中位數圖、兩日期變動訊號與單筆狀態。|
| `/calculator` | GET／POST | 顯示並提交跨境成本試算表單。|

前端沒有自建 JSON REST API；Chart.js 直接使用 Flask 模板注入的 `chart_labels`／`chart_prices`。

### 主要頁面

- **首頁**：多作品、角色、商品、最新日圓價格、抓取時間與 Rakuten 連結；可從導覽列篩選三部作品。
- **角色詳情**：分數卡、兩日中位數變動訊號、每日中位數折線圖、每筆快照與相對當日中位數的狀態。
- **成本試算器**：輸入與結果並列，顯示商品折算、代購費、落地成本、平台費、保本價及預估淨利。
- `templates/product.html`、`static/js/chart.js`、`static/js/calculator.js`、`static/css/style.css` 目前為空；實際樣式與圖表程式內嵌於 template。

### 資料來源

- 唯一自動來源是 Rakuten Ichiba Item Search API；程式使用環境變數 `RAKUTEN_APPLICATION_ID` 與 `RAKUTEN_ACCESS_KEY`。
- 爬蟲請求帶有 API 金鑰、User-Agent、Referer 與 Origin；本分析未讀取 `.env` 也未向外呼叫 API。
- `database/test_data.sql` 的 `example.com` 商品和兩筆日期快照明確註記為**本機驗證假資料**，不可做成 PPT 的市場成果或價格趨勢證據。

## 6. 價格分析、預警與成本公式

### 價格分析

1. 針對某角色取得所有 listing 快照。
2. 以 `captured_at` 的年月日分組。
3. 每個日期用 Python `statistics.median()` 計算所有快照的日圓中位數。
4. 用排序後日期的每日中位數畫趨勢圖。
5. 單筆 snapshot 與同日中位數相比，±15% 為狀態分類界線。

**注意**：此做法將同一角色下的所有 listing 快照合併。若同一 listing 在不同日存在，屬於不同日觀測；程式未做跨 listing 的可比性或成交價校正。

### 預警規則（現況）

```text
change_percent = (最新資料日中位數 − 前一資料日中位數) / 前一資料日中位數 × 100

若 change_percent ≥ 15%：潛在漲幅預警
否則：正常觀察
若資料日少於 2：資料不足
```

它是頁面即時計算的觀察訊號，不會寫入 alerts 表，也不含樣本數下限。

### 成本試算公式（現況）

```text
商品台幣成本 = (商品日圓價格 + 日本國內運費) × 匯率
代購費 = 商品台幣成本 × 代購費率
落地成本 = 商品台幣成本 + 代購費 + 國際運費
平台費 = 預估台灣售價 × 平台費率
預估淨利 = 預估台灣售價 − 落地成本 − 平台費
保本售價 = 落地成本 / (1 − 平台費率)
```

淨利 > 0 顯示「可觀察」、= 0 顯示「損益兩平」、< 0 顯示「不建議」。此分類只反映輸入假設下的算術結果，不代表市場一定能以預估售價成交。

## 7. 最適合的 Demo（需先確認本機 DB 有可用真實快照）

1. 首頁：展示追蹤清單、最新價格與 Rakuten 外連。
2. 點一個**已有至少兩個不同資料日**的角色：展示每日中位數圖與「正常觀察／潛在漲幅預警」。
3. 在同一頁解釋單筆商品如何相對同日中位數標記，並提醒它是刊登價。
4. 進成本試算器，以使用者當下準備的真實商品價格、匯率與物流條件計算；若沒有可核對的台灣售價，就只展示「保本售價」，不要宣稱真實利潤。

**Demo 前檢查**：確認 DB 已載入 schema、至少一個真實 Rakuten listing 的兩個資料日快照，且 `.env` 的 DB／Rakuten 設定有效。若沒有，PPT 需寫「Demo 資料待補」，不可使用 `test_data.sql` 當市場案例。

## 8. 主要限制與技術風險

- 單一資料源、單一國家，沒有台灣售價資料，無法直接跨市場比較。
- Rakuten 是刊登價，未證明成交、庫存或物流成本的真實性。
- 本次沒有驗證本機 DB 的實際資料量、爬蟲近期 API 可用性，不能報告「已累積 N 天／N 筆真實資料」。
- 無自動排程、無 alerts 持久化、無執行失敗通知；資料累積的持續性待補。
- 爬蟲雖有資料清洗，但未以「是否為目標角色」做更細緻的名稱比對；可能混入關鍵字相關但不可比的商品。
- `shipping_jpy` 寫入 NULL，故自動資料不含日本國內運費；試算器須人工輸入。
- `test_API.py` 變數先使用後宣告（且 `RRAKUTEN_APPLICATION_ID` 拼字不同），實際執行會出錯；目前沒有可用的自動化測試套件。
- `templates/index.html` 與 `templates/character_detail.html` 各保留了註解掉的舊版 HTML；不影響目前主體，但應在正式展示前整理。工作樹另有未提交的 `templates/character_detail.html` 修改，未碰觸。
- 前端文字中有「投資模型良好／投資與收藏價值」等較強用詞；報告應改說「成本試算結果」與「觀察訊號」，避免吹大。

## 9. 老師可能追問的方向（之後 Q&A 要誠實回答）

1. 為何選 Rakuten，而不是成交型平台？
2. 刊登價能否代表市場價？
3. 為何選中位數？當天樣本數多少？
4. 15% 門檻如何設定、是否做過回測？
5. 為什麼預警沒有保存？
6. 人氣分數是否等於角色人氣？
7. 台灣售價如何取得、如何證明套利？
8. 物流、匯率與平台費是即時資料還是手動假設？
9. 去重策略是否會漏掉同日價格變化？
10. 為何不用機器學習？目前資料是否足夠？

## 10. 本次檢查的檔案

- 專案說明與文件：`README.md`、`docs/口頭報告逐字稿.md`、`docs/scope.md`、`docs/data-flow.md`、`docs/wireframe.md`
- 後端與資料庫：`app.py`、`database.py`、`config/setting.py`、`database/schema.sql`、`database/seed_data.sql`、`database/test_data.sql`、`database/teat.sql`
- 爬蟲與分析：`crawler/rakuten_crawler.py`、`analyzer/opportunity_analyzer.py`
- 前端：`templates/index.html`、`templates/character_detail.html`、`templates/calculator.html`、`templates/product.html`、`static/css/style.css`、`static/js/chart.js`、`static/js/calculator.js`
- 測試與相依：`test_API.py`、`test_db.py`、`requirements.txt`、`logs/crawler.log`

## 11. 後續 PPT 建議範圍

建議製作 **10 頁、約 13–14 分鐘**：題目與定位 → 問題 → MVP 流程 → 資料模型 → 資料取得／清洗 → 每日中位數與預警 → 成本試算 → Demo 流程 → 已完成與限制 → NEXT。只有在確認真實 DB 快照或實機截圖後，才放真實商品／趨勢案例。
