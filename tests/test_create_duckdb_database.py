from pathlib import Path

import pandas as pd

from scripts.analytics.create_duckdb_database import create_duckdb_database


def test_create_duckdb_database_exports_analytics_outputs(tmp_path: Path):
    """
    Verifica que la capa DuckDB pueda crear una base temporal
    y exportar outputs analíticos desde un CSV modelado.
    """

    modeled_csv_path = tmp_path / "prices_modeled.csv"
    database_path = tmp_path / "recope_prices.duckdb"
    create_table_sql_path = tmp_path / "create_prices_table.sql"
    summary_sql_path = tmp_path / "price_summary_by_source.sql"
    quality_sql_path = tmp_path / "source_quality_checks.sql"
    summary_output_path = tmp_path / "price_summary_by_source.csv"
    quality_output_path = tmp_path / "source_quality_checks.csv"

    modeled_data = pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "product": "Gasolina Regular",
                "source": "consumer",
                "price": 1000.0,
                "currency": "CRC",
                "unit": "L",
                "price_unit": "CRC/L",
                "price_crc": 1000.0,
                "product_id": "1",
                "ingestion_timestamp": "2026-01-01T00:00:00",
            },
            {
                "date": "2026-01-01",
                "product": "Brent",
                "source": "international",
                "price": 85.0,
                "currency": "USD",
                "unit": "reference",
                "price_unit": "USD/reference",
                "price_crc": 45900.0,
                "product_id": "2",
                "ingestion_timestamp": "2026-01-01T00:00:00",
            },
        ]
    )

    modeled_data.to_csv(modeled_csv_path, index=False)

    create_table_sql_path.write_text(
        f"""
        CREATE OR REPLACE TABLE prices AS
        SELECT *
        FROM read_csv_auto('{modeled_csv_path.as_posix()}', HEADER = TRUE);
        """,
        encoding="utf-8",
    )

    summary_sql_path.write_text(
        """
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
        """,
        encoding="utf-8",
    )

    quality_sql_path.write_text(
        """
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
        """,
        encoding="utf-8",
    )

    create_duckdb_database(
        database_path=database_path,
        create_table_sql_path=create_table_sql_path,
        summary_sql_path=summary_sql_path,
        quality_sql_path=quality_sql_path,
        summary_output_path=summary_output_path,
        quality_output_path=quality_output_path,
    )

    assert database_path.exists()
    assert summary_output_path.exists()
    assert quality_output_path.exists()

    summary_result = pd.read_csv(summary_output_path)
    quality_result = pd.read_csv(quality_output_path)

    assert len(summary_result) == 2
    assert len(quality_result) == 2

    assert set(summary_result["source"]) == {"consumer", "international"}
    assert set(quality_result["source"]) == {"consumer", "international"}

    consumer_summary = summary_result[summary_result["source"] == "consumer"].iloc[0]

    assert consumer_summary["total_rows"] == 1
    assert consumer_summary["total_products"] == 1
    assert consumer_summary["min_price_crc"] == 1000.0
    assert consumer_summary["avg_price_crc"] == 1000.0
    assert consumer_summary["max_price_crc"] == 1000.0

    consumer_quality = quality_result[quality_result["source"] == "consumer"].iloc[0]

    assert consumer_quality["total_rows"] == 1
    assert consumer_quality["null_price_crc_count"] == 0
    assert consumer_quality["missing_product_count"] == 0
    assert consumer_quality["non_positive_price_count"] == 0
    assert consumer_quality["distinct_product_ids"] == 1