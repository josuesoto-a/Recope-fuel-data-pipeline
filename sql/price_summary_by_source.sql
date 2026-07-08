SELECT
    source,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT product) AS total_products,
    MIN(price_crc) AS min_price_crc,
    AVG(price_crc) AS avg_price_crc,
    MAX(price_crc) AS max_price_crc
FROM prices
GROUP BY source
ORDER BY source;