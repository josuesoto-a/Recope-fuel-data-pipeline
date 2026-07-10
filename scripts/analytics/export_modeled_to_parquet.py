from pathlib import Path

import duckdb

from scripts.utils.logger import get_logger


logger = get_logger("export_modeled_to_parquet")


MODELED_CSV_PATH = Path("data/processed/prices_modeled.csv")
PARQUET_OUTPUT_PATH = Path("data/processed/prices_modeled.parquet")


def export_modeled_to_parquet(
    input_csv_path: Path = MODELED_CSV_PATH,
    output_parquet_path: Path = PARQUET_OUTPUT_PATH,
):
    """
    Export the modeled prices dataset from CSV to Parquet format.
    """

    logger.info("Starting Parquet export")

    if not input_csv_path.exists():
        raise FileNotFoundError(f"Input CSV file not found: {input_csv_path}")

    output_parquet_path.parent.mkdir(parents=True, exist_ok=True)

    if output_parquet_path.exists():
        output_parquet_path.unlink()

    input_csv_sql_path = input_csv_path.as_posix().replace("'", "''")
    output_parquet_sql_path = output_parquet_path.as_posix().replace("'", "''")

    with duckdb.connect() as connection:
        connection.execute(
            f"""
            COPY (
                SELECT *
                FROM read_csv_auto('{input_csv_sql_path}', HEADER = TRUE)
            )
            TO '{output_parquet_sql_path}'
            (FORMAT PARQUET);
            """
        )

        row_count = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM read_parquet('{output_parquet_sql_path}');
            """
        ).fetchone()[0]

    logger.info(
        f"Parquet export completed | rows={row_count} | output={output_parquet_path}"
    )

    return output_parquet_path


if __name__ == "__main__":
    export_modeled_to_parquet()