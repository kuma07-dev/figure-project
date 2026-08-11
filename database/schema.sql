CREATE DATABASE IF NOT EXISTS ichiban_price_monitor
CHARACTER SET utf8mb4      -- 遇到一些罕見字、日文漢字
COLLATE utf8mb4_unicode_ci;  -- 排序規則，不區分英文大小寫

USE ichiban_price_monitor;

CREATE TABLE tracked_items (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, -- 設定主鍵
    anime_title VARCHAR(100) NOT NULL,          -- 作品名稱 一定要填
    series_name VARCHAR(100) NOT NULL,              -- 系列名稱 一定要填
    character_name VARCHAR(100) NOT NULL,       -- 角色名稱
    search_keyword VARCHAR(255) NOT NULL,       -- 搜尋關鍵字
    prize_rank VARCHAR(20) NULL,                -- 賞別，可不填
    
    -- 五大特徵評分 (1-5星)
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
    product_url VARCHAR(1000) NOT NULL,
    image_url VARCHAR(1000) NULL,
    first_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_listing_url UNIQUE (product_url),

    CONSTRAINT fk_listings_tracked_item
        FOREIGN KEY (tracked_item_id)
        REFERENCES tracked_items(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


SHOW WARNINGS;