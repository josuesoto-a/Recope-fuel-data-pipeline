from pathlib import Path

import duckdb
import pandas as pd
import pytest

from scripts.analytics.export_modeled_to_parquet import export_modeled_to_parquet


def test_export_modeled_to_parquet_creates_parquet_file(tmp_path: Path):
    """
    Verifies that a modeled CSV can be correctly exported to Parquet.
    """

    input_csv_path = tmp_path / "prices_modeled.csv"
    output_parquet_path = tmp_path / "prices_modeled.parquet"

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

    modeled_data.to_csv(input_csv_path, index=False)

    result_path = export_modeled_to_parquet(input_csv_path, output_parquet_path)

    assert result_path == output_parquet_path
    assert output_parquet_path.exists()

    result = duckdb.sql(
        f"""
        SELECT
            source,
            COUNT(*) AS total_rows
        FROM read_parquet('{output_parquet_path.as_posix()}')
        GROUP BY source
        ORDER BY source
        """
    ).df()

    assert len(result) == 2
    assert set(result["source"]) == {"consumer", "international"}

    consumer_rows = result[result["source"] == "consumer"]["total_rows"].iloc[0]
    international_rows = result[result["source"] == "international"]["total_rows"].iloc[0]

    assert consumer_rows == 1
    assert international_rows == 1


def test_export_modeled_to_parquet_missing_input_raises_error(tmp_path: Path):
    """
    Verifica que la función falle si el CSV modelado no existe.
    """

    input_csv_path = tmp_path / "missing_prices_modeled.csv"
    output_parquet_path = tmp_path / "prices_modeled.parquet"

    with pytest.raises(FileNotFoundError, match="Input CSV file not found"):
        export_modeled_to_parquet(input_csv_path, output_parquet_path)

    assert not output_parquet_path.exists()