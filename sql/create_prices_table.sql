CREATE OR REPLACE TABLE PRICES AS 
SELECT *
FROM read_csv_auto('data/processed/prices_modeled.csv', HEADER = TRUE);