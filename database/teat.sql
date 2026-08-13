USE ichiban_price_monitor;

SELECT
    t.character_name,
    l.title,
    p.price_jpy,
    p.captured_at
FROM price_snapshots AS p
JOIN listings AS l
    ON p.listing_id = l.id
   AND p.tracked_item_id = l.tracked_item_id
JOIN tracked_items AS t
    ON p.tracked_item_id = t.id
ORDER BY p.captured_at DESC;