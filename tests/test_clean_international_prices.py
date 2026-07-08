import json
from pathlib import Path

from scripts.transform.clean_international_prices import (
    clean_international_prices,
)


def test_valid_international_data_cleans_correctly(tmp_path: Path):
    raw_data = {
        "periodos": [
            {
                "desde": "20260101",
                "hasta": "20260131",
            }
        ],
        "materiales": [
            {
                "nomprod": "Brent (USD por barril)",
                "id": "2",
                "precios": ["85.50"],
            }
        ],
    }

    input_path = tmp_path / "international_raw.json"
    output_path = tmp_path / "international_cleaned.json"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(raw_data, file)

    clean_international_prices(input_path, output_path)

    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8") as file:
        cleaned_data = json.load(file)

    assert len(cleaned_data) == 1

    record = cleaned_data[0]

    assert record["date_start"] == "2026-01-01"
    assert record["date_end"] == "2026-01-31"
    assert record["product"] == "Brent"
    assert record["price_usd"] == 85.50
    assert isinstance(record["price_usd"], float)
    assert record["product_id"] == "2"
    assert record["currency"] == "USD"
    assert record["source"] == "international"
    assert "ingestion_timestamp" in record

def test_multiple_prices_match_their_periods(tmp_path: Path):
    raw_data = {
        "periodos": [
            {
                "desde": "20260101",
                "hasta": "20260131",
            },
            {
                "desde": "20260201",
                "hasta": "20260228",
            },
        ],
        "materiales": [
            {
                "nomprod": "Brent (USD por barril)",
                "id": "2",
                "precios": ["85.50", "87.25"],
            }
        ],
    }

    input_path = tmp_path / "international_raw.json"
    output_path = tmp_path / "international_cleaned.json"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(raw_data, file)

    clean_international_prices(input_path, output_path)

    with open(output_path, "r", encoding="utf-8") as file:
        cleaned_data = json.load(file)

    assert len(cleaned_data) == 2

    first_record = cleaned_data[0]
    second_record = cleaned_data[1]

    assert first_record["date_start"] == "2026-01-01"
    assert first_record["date_end"] == "2026-01-31"
    assert first_record["price_usd"] == 85.50

    assert second_record["date_start"] == "2026-02-01"
    assert second_record["date_end"] == "2026-02-28"
    assert second_record["price_usd"] == 87.25


def test_invalid_price_is_skipped(tmp_path: Path, caplog):
    raw_data = {
        "periodos": [
            {
                "desde": "20260101",
                "hasta": "20260131",
            },
            {
                "desde": "20260201",
                "hasta": "20260228",
            },
        ],
        "materiales": [
            {
                "nomprod": "Brent (USD por barril)",
                "id": "2",
                "precios": ["invalid-price", "87.25"],
            }
        ],
    }

    input_path = tmp_path / "international_raw.json"
    output_path = tmp_path / "international_cleaned.json"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(raw_data, file)

    clean_international_prices(input_path, output_path)

    with open(output_path, "r", encoding="utf-8") as file:
        cleaned_data = json.load(file)

    assert len(cleaned_data) == 1

    valid_record = cleaned_data[0]

    assert valid_record["date_start"] == "2026-02-01"
    assert valid_record["date_end"] == "2026-02-28"
    assert valid_record["price_usd"] == 87.25

    assert "Record skipped" in caplog.text
    assert "price_index=0" in caplog.text



def test_invalid_material_is_skipped(tmp_path: Path, caplog):
    raw_data = {
        "periodos": [
            {
                "desde": "20260101",
                "hasta": "20260131",
            }
        ],
        "materiales": [
            {
                "nomprod": "Material inválido",
                # Falta la clave obligatoria "id"
                "precios": ["70.00"],
            },
            {
                "nomprod": "Brent (USD por barril)",
                "id": "2",
                "precios": ["85.50"],
            },
        ],
    }

    input_path = tmp_path / "international_raw.json"
    output_path = tmp_path / "international_cleaned.json"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(raw_data, file)

    clean_international_prices(input_path, output_path)

    with open(output_path, "r", encoding="utf-8") as file:
        cleaned_data = json.load(file)

    assert len(cleaned_data) == 1

    valid_record = cleaned_data[0]

    assert valid_record["product"] == "Brent"
    assert valid_record["product_id"] == "2"
    assert valid_record["price_usd"] == 85.50

    assert "Material skipped" in caplog.text
    assert "index=0" in caplog.text    