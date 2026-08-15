USE ichiban_price_monitor;

-- 可重複執行的測試資料；僅供本機驗證，不是正式市場資料。
INSERT INTO tracked_items (
    anime_title, series_name, character_name, search_keyword,
    popularity_score, rarity_score, quality_score, design_score
)
VALUES (
    '死神', 'BLEACH', '黑崎一護', '一番くじ BLEACH 黒崎一護', 5, 4, 4, 4
)
ON DUPLICATE KEY UPDATE
    anime_title = VALUES(anime_title),
    character_name = VALUES(character_name),
    popularity_score = VALUES(popularity_score),
    rarity_score = VALUES(rarity_score),
    quality_score = VALUES(quality_score),
    design_score = VALUES(design_score);

SELECT id INTO @ichigo_id
FROM tracked_items
WHERE search_keyword = '一番くじ BLEACH 黒崎一護';

INSERT INTO listings (
    tracked_item_id, source, title, product_url, image_url
)
VALUES (
    @ichigo_id,
    'Rakuten',
    '一番くじ BLEACH 黑崎一護 MASTERLISE 測試商品',
    'https://example.com/rakuten-ichigo-test',
    NULL
)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    last_seen_at = NOW(),
    is_active = TRUE;

SELECT id INTO @test_listing_id
FROM listings
WHERE product_url = 'https://example.com/rakuten-ichigo-test';

INSERT INTO price_snapshots (
    tracked_item_id, listing_id, price_jpy, shipping_jpy, stock_status, captured_at
)
SELECT @ichigo_id, @test_listing_id, 4800, 500, 'in_stock', '2026-08-10 21:00:00'
WHERE NOT EXISTS (
    SELECT 1
    FROM price_snapshots
    WHERE tracked_item_id = @ichigo_id
      AND listing_id = @test_listing_id
      AND captured_at = '2026-08-10 21:00:00'
);

INSERT INTO price_snapshots (
    tracked_item_id, listing_id, price_jpy, shipping_jpy, stock_status, captured_at
)
SELECT @ichigo_id, @test_listing_id, 5200, 500, 'in_stock', '2026-08-11 21:00:00'
WHERE NOT EXISTS (
    SELECT 1
    FROM price_snapshots
    WHERE tracked_item_id = @ichigo_id
      AND listing_id = @test_listing_id
      AND captured_at = '2026-08-11 21:00:00'
);
