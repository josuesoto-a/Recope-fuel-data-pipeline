import csv
import json
from pathlib import Path

import pytest

from scripts.transform.transform_international_prices import transform_international_prices


def test_transform_international_prices_creates_csv(tmp_path: Path):
    """
    Verifica que un JSON limpio de precios internacionales
    se transforme correctamente en un archivo CSV.
    """

    cleaned_data = [
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.5,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00",
        }
    ]

    input_path = tmp_path / "international_prices_cleaned.json"
    output_path = tmp_path / "international_prices.csv"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(cleaned_data, file)

    transform_international_prices(input_path, output_path)

    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert reader.fieldnames == [
        "date_start",
        "date_end",
        "product",
        "price_usd",
        "product_id",
        "currency",
        "source",
        "ingestion_timestamp",
    ]

    assert len(rows) == 1

    row = rows[0]

    assert row["date_start"] == "2026-01-01"
    assert row["date_end"] == "2026-01-31"
    assert row["product"] == "Brent"
    assert row["price_usd"] == "85.5"
    assert row["product_id"] == "2"
    assert row["currency"] == "USD"
    assert row["source"] == "international"
    assert row["ingestion_timestamp"] == "2026-01-01T00:00:00"


def test_transform_international_prices_empty_json_raises_error(tmp_path: Path):
    """
    Verifica que la transformación falle si el JSON limpio internacional está vacío.
    """

    no_data = []

    input_path = tmp_path / "international_prices_cleaned.json"
    output_path = tmp_path / "international_prices.csv"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(no_data, file)

    with pytest.raises(ValueError, match="No data to transform"):
        transform_international_prices(input_path, output_path)

    assert not output_path.exists()