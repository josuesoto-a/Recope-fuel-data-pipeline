import pandas as pd
from pathlib import Path
from scripts.utils.logger import get_logger

logger = get_logger("validate_prices")


# -----------------------------
# VALIDACIÓN CORE (DataFrame)
# -----------------------------
def validate_prices_df(df: pd.DataFrame) -> None:

    logger.info("Running data quality checks")

    if df.empty:
        raise ValueError("DataFrame is empty - no data to validate")
    

    # -----------------------------
    # 1. Columnas requeridas
    # -----------------------------
    required_columns = [
        "date",
        "product",
        "source",
        "price",
        "currency",
        "price_crc",
        "product_id"
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    # -----------------------------
    # 2. Nulls críticos
    # -----------------------------
    critical_cols = ["date", "product", "price"]

    null_counts = df[critical_cols].isnull().sum()

    if null_counts.any():
        raise ValueError(f"Null values found: {null_counts.to_dict()}")

    # -----------------------------
    # 3. Precios negativos
    # -----------------------------
    if (df["price"] < 0).any():
        raise ValueError("Negative prices detected")

    # -----------------------------
    # 4. Duplicados
    # -----------------------------
    duplicates = df.duplicated().sum()

    if duplicates > 0:
        logger.warning(f"Duplicates found: {duplicates}")

    logger.info("Data validation passed")


# -----------------------------
# ENTRYPOINT (archivo)
# -----------------------------
def validate_prices_file(input_path: Path) -> None:

    logger.info(f"Validating file: {input_path}")

    df = pd.read_csv(input_path)

    validate_prices_df(df)  # ← aquí está la separación correcta