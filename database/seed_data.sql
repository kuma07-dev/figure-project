USE ichiban_price_monitor;

-- 正式監測角色：僅在新資料庫建立後執行一次。
INSERT INTO tracked_items (
    anime_title, series_name, character_name, search_keyword, prize_rank,
    popularity_score, rarity_score, quality_score, design_score
)
VALUES
('死神', 'BLEACH', '黑崎一護', '一番くじ BLEACH 黒崎一護', NULL, 5, 4, 4, NULL),
('死神', 'BLEACH', '藍染惣右介', '一番くじ BLEACH 藍染惣右介', NULL, 5, 4, 4, NULL),
('死神', 'BLEACH', '烏爾奇奧拉', '一番くじ BLEACH ウルキオラ', NULL, 4, 4, 4, NULL),
('火影忍者', 'NARUTO', '漩渦鳴人', '一番くじ NARUTO うずまきナルト', NULL, 5, 4, 4, NULL),
('火影忍者', 'NARUTO', '宇智波佐助', '一番くじ NARUTO うちはサスケ', NULL, 5, 4, 4, NULL),
('火影忍者', 'NARUTO', '宇智波鼬', '一番くじ NARUTO うちはイタチ', NULL, 5, 5, 4, NULL),
('航海王', 'ONE PIECE', '蒙其・D・魯夫', '一番くじ ワンピース ルフィ', NULL, 5, 4, 4, NULL),
('航海王', 'ONE PIECE', '羅羅亞・索隆', '一番くじ ワンピース ゾロ', NULL, 5, 4, 4, NULL),
('航海王', 'ONE PIECE', '香吉士', '一番くじ ワンピース サンジ', NULL, 4, 3, 4, NULL);
