from pathlib import Path

import duckdb

from scripts.utils.logger import get_logger


logger = get_logger("create_duckdb_database")


DATABASE_PATH = Path("data/processed/recope_prices.duckdb")
CREATE_TABLE_SQL_PATH = Path("sql/create_prices_table.sql")
SUMMARY_SQL_PATH = Path("sql/price_summary_by_source.sql")
QUALITY_SQL_PATH = Path("sql/source_quality_checks.sql")

SUMMARY_OUTPUT_PATH = Path("data/processed/price_summary_by_source.csv")
QUALITY_OUTPUT_PATH = Path("data/processed/source_quality_checks.csv")


def create_duckdb_database(
    database_path: Path = DATABASE_PATH,
    create_table_sql_path: Path = CREATE_TABLE_SQL_PATH,
    summary_sql_path: Path = SUMMARY_SQL_PATH,
    quality_sql_path: Path = QUALITY_SQL_PATH,
    summary_output_path: Path = SUMMARY_OUTPUT_PATH,
    quality_output_path: Path = QUALITY_OUTPUT_PATH,
):
    """
    Create a DuckDB database from the modeled prices CSV
    and export analytics outputs.
    """

    logger.info("Starting DuckDB analytics layer")

    if not create_table_sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {create_table_sql_path}")

    if not summary_sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {summary_sql_path}")

    if not quality_sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {quality_sql_path}")

    summary_output_path.parent.mkdir(parents=True, exist_ok=True)
    quality_output_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(database_path) as connection:
        create_table_sql = create_table_sql_path.read_text(encoding="utf-8")
        summary_sql = summary_sql_path.read_text(encoding="utf-8")
        quality_sql = quality_sql_path.read_text(encoding="utf-8")

        logger.info("Creating prices table")
        connection.execute(create_table_sql)

        logger.info("Running source summary query")
        summary_df = connection.execute(summary_sql).fetchdf()
        summary_df.to_csv(summary_output_path, index=False)

        logger.info("Running source quality checks query")
        quality_df = connection.execute(quality_sql).fetchdf()
        quality_df.to_csv(quality_output_path, index=False)

    logger.info(
        "DuckDB analytics layer completed | "
        f"database={database_path} | "
        f"summary_output={summary_output_path} | "
        f"quality_output={quality_output_path}"
    )


if __name__ == "__main__":
    create_duckdb_database()