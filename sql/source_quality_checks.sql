SELECT
    source,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN price_crc IS NULL THEN 1 ELSE 0 END) AS null_price_crc_count,
    SUM(CASE WHEN product IS NULL OR product = '' THEN 1 ELSE 0 END) AS missing_product_count,
    SUM(CASE WHEN price_crc <= 0 THEN 1 ELSE 0 END) AS non_positive_price_count,
    COUNT(DISTINCT product_id) AS distinct_product_ids
FROM prices
GROUP BY source
ORDER BY source;