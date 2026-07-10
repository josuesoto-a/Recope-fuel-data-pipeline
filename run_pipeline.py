from pathlib import Path

from scripts.utils.logger import get_logger
from scripts.quality.validate_prices import validate_prices_file

# FETCH
from scripts.fetch.fetch_consumer_prices import fetch_consumer_prices
from scripts.fetch.fetch_international_prices import fetch_international_prices
from scripts.fetch.fetch_plantel_prices import fetch_plantel_prices

# CLEAN
from scripts.transform.clean_consumer_prices import clean_consumer_prices
from scripts.transform.clean_international_prices import clean_international_prices
from scripts.transform.clean_plantel_prices import clean_plantel_prices

# TRANSFORM
from scripts.transform.transform_consumer_prices import transform_consumer_prices
from scripts.transform.transform_international_prices import transform_international_prices
from scripts.transform.transform_plantel_prices import transform_plantel_prices

# MODEL
from scripts.transform.model_prices_data import model_prices_data

# DUCKDB
from scripts.analytics.create_duckdb_database import create_duckdb_database

# PARQUET 
from scripts.analytics.export_modeled_to_parquet import export_modeled_to_parquet

logger = get_logger("run_pipeline")


# -----------------------------
# Utility: get the latest file.
# -----------------------------
def get_latest_file(directory, pattern):
    files = list(Path(directory).glob(pattern))

    if not files:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")

    return max(files, key=lambda f: f.stat().st_mtime)


# -----------------------------
# PIPELINE
# -----------------------------
def run_pipeline():

    try:
        logger.info("===== PIPELINE STARTED =====")

        # -----------------------------
        # 1. FETCH
        # -----------------------------
        logger.info("STEP 1: FETCH")

        fetch_consumer_prices()
        fetch_international_prices()
        fetch_plantel_prices()

        # -----------------------------
        # 2. CLEAN
        # -----------------------------
        logger.info("STEP 2: CLEAN")

        consumer_raw = get_latest_file("data/raw", "consumer_prices_*.json")
        international_raw = get_latest_file("data/raw", "international_prices_*.json")
        plantel_raw = get_latest_file("data/raw", "plantel_prices_*.json")

        consumer_clean = Path("data/processed/consumer_prices_cleaned.json")
        international_clean = Path("data/processed/international_prices_cleaned.json")
        plantel_clean = Path("data/processed/plantel_prices_cleaned.json")

        clean_consumer_prices(consumer_raw, consumer_clean)
        clean_international_prices(international_raw, international_clean)
        clean_plantel_prices(plantel_raw, plantel_clean)

        # -----------------------------
        # 3. TRANSFORM
        # -----------------------------
        logger.info("STEP 3: TRANSFORM")

        consumer_csv = Path("data/processed/consumer_prices.csv")
        international_csv = Path("data/processed/international_prices.csv")
        plantel_csv = Path("data/processed/plantel_prices.csv")

        transform_consumer_prices(consumer_clean, consumer_csv)
        transform_international_prices(international_clean, international_csv)
        transform_plantel_prices(plantel_clean, plantel_csv)

        # -----------------------------
        # 4. MODEL
        # -----------------------------
        logger.info("STEP 4: MODEL")

        modeled_output = Path("data/processed/prices_modeled.csv")

        model_prices_data(
            consumer_csv,
            international_csv,
            plantel_csv,
            modeled_output
        )

        # -----------------------------
        # 5. VALIDATION
        # -----------------------------
        logger.info("STEP 5: VALIDATION")

        validate_prices_file(modeled_output)

        
        # -----------------------------
        # 6. ANALYTICS OUTPUTS
        # -----------------------------
        logger.info("STEP 6: ANALYTICS OUTPUTS")

        parquet_output = Path("data/processed/prices_modeled.parquet")

        export_modeled_to_parquet(
            modeled_output,
            parquet_output
        )

        create_duckdb_database()



        logger.info("===== PIPELINE COMPLETED SUCCESSFULLY =====")

    except Exception as e:
        logger.exception(f"PIPELINE FAILED: {e}")
        raise


# -----------------------------
# ENTRYPOINT
# -----------------------------
if __name__ == "__main__":
    run_pipeline()