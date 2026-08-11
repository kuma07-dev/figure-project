CREATE DATABASE IF NOT EXISTS ichiban_price_monitor
CHARACTER SET utf8mb4      -- 遇到一些罕見字、日文漢字
COLLATE utf8mb4_unicode_ci;  -- 排序規則，不區分英文大小寫

USE ichiban_price_monitor;

-- DROP TABLE IF EXISTS price_snapshots;
-- DROP TABLE IF EXISTS listings;
-- DROP TABLE IF EXISTS tracked_items;

CREATE TABLE tracked_items (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, -- 設定主鍵
    anime_title VARCHAR(100) NOT NULL,          -- 作品名稱 一定要填
    series_name VARCHAR(100) NULL,              -- 系列名稱 
    character_name VARCHAR(100) NOT NULL,       -- 角色名稱
    search_keyword VARCHAR(255) NOT NULL,       -- 搜尋關鍵字
    prize_rank VARCHAR(20) NULL,                -- 賞別，可不填
    
    -- 四大特徵評分 (1-5星)
    popularity_score TINYINT UNSIGNED NULL,     -- 人氣評分，不可為負數
    rarity_score TINYINT UNSIGNED NULL,         -- 稀有度評分
    quality_score TINYINT UNSIGNED NULL,        -- 品質/品相評分
    design_score TINYINT UNSIGNED NULL,         -- 造型評分
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,    -- 追蹤是否還有效？它是布林值。未來如果不想追蹤了，改成 FALSE 即可，不用刪除資料。
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 資料的「建立時間」
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP  -- 最後更新時間
        ON UPDATE CURRENT_TIMESTAMP,
        
    -- 唯一限制與效能索引    
	UNIQUE KEY uq_search_keyword (search_keyword),  -- 設定搜尋關鍵字，不能重複
    INDEX idx_active_items (is_active, id),         -- 複合索引

	-- 檢查規則，防止亂填
    CONSTRAINT chk_popularity_score  
        CHECK (popularity_score IS NULL OR popularity_score BETWEEN 1 AND 5),
    CONSTRAINT chk_rarity_score
        CHECK (rarity_score IS NULL OR rarity_score BETWEEN 1 AND 5),
    CONSTRAINT chk_quality_score
        CHECK (quality_score IS NULL OR quality_score BETWEEN 1 AND 5),
	CONSTRAINT chk_design_score
        CHECK (design_score IS NULL OR design_score BETWEEN 1 AND 5)
);



CREATE TABLE listings (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tracked_item_id INT UNSIGNED NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'Rakuten',
    title VARCHAR(500) NOT NULL,
    product_url VARCHAR(700) NOT NULL,
    image_url VARCHAR(1000) NULL,
    first_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_listing_url UNIQUE (product_url),
    
	UNIQUE KEY uq_listing_item (id, tracked_item_id),  -- 建立複合唯一鍵，開放給快照表做雙重認證參考

    CONSTRAINT fk_listings_tracked_item
        FOREIGN KEY (tracked_item_id)
        REFERENCES tracked_items(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);



CREATE TABLE price_snapshots (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tracked_item_id INT UNSIGNED NOT NULL,  -- 多存一份，用來做大數據計算與驗證
    listing_id BIGINT UNSIGNED NOT NULL,
    price_jpy INT UNSIGNED NOT NULL,
    shipping_jpy INT UNSIGNED NULL,
    stock_status VARCHAR(50) NULL,
    captured_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_snapshots_listing
        FOREIGN KEY (listing_id, tracked_item_id)
        REFERENCES listings(id, tracked_item_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        
	INDEX idx_tracked_time_price (tracked_item_id, captured_at, price_jpy),
    INDEX idx_snapshots_listing_time (listing_id, captured_at)
);

SHOW TABLES;

DESCRIBE tracked_items;
DESCRIBE listings;
DESCRIBE price_snapshots;






USE ichiban_price_monitor;


-- 測試假資料
INSERT INTO tracked_items (
    anime_title,
    series_name,
    character_name,
    search_keyword,
    popularity_score,
    rarity_score,
    quality_score,
    design_score
)
VALUES (
    'BLEACH',
    NULL,
    '黑崎一護',
    '一番くじ BLEACH 黒崎一護',
    5, 4, 4, 4
);


SELECT id, anime_title, character_name
FROM tracked_items;


-- 假設黑崎一護的 id 是 1，新增測試商品：
INSERT INTO listings (
    tracked_item_id,
    source,
    title,
    product_url,
    image_url
)
VALUES (
    1,
    'Rakuten',
    '一番くじ BLEACH 黑崎一護 MASTERLISE 測試商品',
    'https://example.com/rakuten-ichigo-test',
    NULL
);


SELECT id, tracked_item_id, title
FROM listings;


-- 假設商品 id 是 1，新增兩筆價格歷史：
INSERT INTO price_snapshots (
    tracked_item_id,
    listing_id,
    price_jpy,
    shipping_jpy,
    stock_status,
    captured_at
)
VALUES
(1, 1, 4800, 500, 'in_stock', '2026-08-10 21:00:00'),
(1, 1, 5200, 500, 'in_stock', '2026-08-11 21:00:00');


-- 最後確認三張表有成功串起來：
SELECT
    t.anime_title AS 作品,
    t.character_name AS 角色,
    l.title AS 商品名稱,
    p.price_jpy AS 日圓價格,
    p.shipping_jpy AS 日本運費,
    p.captured_at AS 抓取時間
FROM tracked_items t
JOIN listings l
    ON t.id = l.tracked_item_id
JOIN price_snapshots p
    ON l.id = p.listing_id
   AND t.id = p.tracked_item_id
ORDER BY p.captured_at;


SHOW WARNINGS;