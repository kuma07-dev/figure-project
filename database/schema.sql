CREATE DATABASE IF NOT EXISTS ichiban_price_monitor
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ichiban_price_monitor;

CREATE TABLE tracked_items (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    anime_title VARCHAR(100) NOT NULL,
    series_name VARCHAR(100) NULL,
    character_name VARCHAR(100) NOT NULL,
    search_keyword VARCHAR(255) NOT NULL,
    prize_rank VARCHAR(20) NULL,
    popularity_score TINYINT UNSIGNED NULL,
    rarity_score TINYINT UNSIGNED NULL,
    quality_score TINYINT UNSIGNED NULL,
    design_score TINYINT UNSIGNED NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_search_keyword (search_keyword),
    INDEX idx_active_items (is_active, id),

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
    UNIQUE KEY uq_listing_item (id, tracked_item_id),

    CONSTRAINT fk_listings_tracked_item
        FOREIGN KEY (tracked_item_id)
        REFERENCES tracked_items(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE price_snapshots (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tracked_item_id INT UNSIGNED NOT NULL,
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
