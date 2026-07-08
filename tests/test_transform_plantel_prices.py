import csv
import json
from pathlib import Path

import pytest

from scripts.transform.transform_plantel_prices import transform_plantel_prices


def test_transform_plantel_prices_creates_csv(tmp_path: Path):
    """
    Verifica que un JSON limpio de precios de plantel
    se transforme correctamente en un archivo CSV.
    """

    cleaned_data = [
        {
            "date": "2026-01-01",
            "product": "BUNKER C",
            "price_crc": 1000.5,
            "tax_crc": 100.0,
            "base_price_crc": 900.5,
            "unit": "KG",
            "product_id": "000000000000080025",
            "update_date": "2026-05-07",
            "source": "plantel",
            "ingestion_timestamp": "2026-01-01T00:00:00",
        }
    ]

    input_path = tmp_path / "plantel_prices_cleaned.json"
    output_path = tmp_path / "plantel_prices.csv"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(cleaned_data, file)

    transform_plantel_prices(input_path, output_path)

    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert reader.fieldnames == [
        "date",
        "product",
        "price_crc",
        "tax_crc",
        "base_price_crc",
        "unit",
        "product_id",
        "update_date",
        "source",
        "ingestion_timestamp",
    ]

    assert len(rows) == 1

    row = rows[0]

    assert row["date"] == "2026-01-01"
    assert row["product"] == "BUNKER C"
    assert row["price_crc"] == "1000.5"
    assert row["tax_crc"] == "100.0"
    assert row["base_price_crc"] == "900.5"
    assert row["unit"] == "KG"
    assert row["product_id"] == "000000000000080025"
    assert row["update_date"] == "2026-05-07"
    assert row["source"] == "plantel"
    assert row["ingestion_timestamp"] == "2026-01-01T00:00:00"


def test_transform_plantel_prices_empty_json_raises_error(tmp_path: Path):
    """
    Verifica que la transformación falle si el JSON limpio de plantel está vacío.
    """

    input_path = tmp_path / "plantel_prices_cleaned.json"
    output_path = tmp_path / "plantel_prices.csv"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump([], file)

    with pytest.raises(ValueError, match="No data to transform"):
        transform_plantel_prices(input_path, output_path)

    assert not output_path.exists()