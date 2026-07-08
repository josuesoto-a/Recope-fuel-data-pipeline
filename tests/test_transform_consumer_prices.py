import csv
import json
from pathlib import Path
import pytest 

from scripts.transform.transform_consumer_prices import transform_consumer_prices

def test_transform_consumer_prices_creates_csv(tmp_path: Path):

    cleaned_data = [
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc" : 1000.5,
            "tax_crc" : 100.0,
            "base_price_crc": 900.5,
            "margin": 50.0,
            "update_date": "2026-01-02",
            "product_id" : "1",
            "ingestion_timestamp": "2026-01-01T00:00:00",



        }
    ]

    input_path = tmp_path / "consumer_prices_cleaned.json"
    output_path = tmp_path / "consumer_prices.csv"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(cleaned_data, file)

    transform_consumer_prices(input_path, output_path)


    assert output_path.exists()

    with open(output_path, 'r', encoding="utf-8",newline="") as file:
        reader =csv.DictReader(file)
        rows = list(reader)

    assert reader.fieldnames == [ 
        "date",
        "product",
        "price_crc",
        "tax_crc",
        "base_price_crc",
        "margin",
        "update_date",
        "product_id",
        "ingestion_timestamp",

    ]    

    assert len(rows) == 1 

    row = rows[0]

    assert row["date"] == "2026-01-01"
    assert row["product"] == "Gasolina Regular"
    assert row["price_crc"] == "1000.5"
    assert row["tax_crc"] == "100.0"
    assert row["base_price_crc"] == "900.5"
    assert row["margin"] == "50.0"
    assert row["update_date"] == "2026-01-02"
    assert row["product_id"] == "1"
    assert row["ingestion_timestamp"] == "2026-01-01T00:00:00"




def test_transform_consumer_prices_empty_json_raises_error(tmp_path: Path):
    """
    Verifica que la transformación falle si el JSON limpio está vacío.

    Un archivo vacío en esta etapa significa que no hay datos válidos
    para convertir a CSV, por lo tanto el pipeline debe detenerse.
    """

    input_path = tmp_path / "consumer_prices_cleaned.json"
    output_path = tmp_path / "consumer_prices.csv"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump([], file)

    with pytest.raises(ValueError, match="No data to transform"):
        transform_consumer_prices(input_path, output_path)

    assert not output_path.exists()    




