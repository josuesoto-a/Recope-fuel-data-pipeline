import json 
from pathlib import Path 
import logging

from scripts.transform.clean_plantel_prices import clean_plantel_prices


def test_valid_plantel_data_cleans_correctly(tmp_path: Path):
    raw_data = [
        {
            "fecha": "20260101",
            "nomprod": "Diesel Industrial (Plantel)",
            "preciototal": "800.50",
            "impuesto": "80.00",
            "precsinimp": "720.50",
            "tipo": "KG",
            "id": "3",
            "fechaupd": "2026/01/02",
        }
    ]

    input_path = tmp_path / "plantel_raw.json"
    output_path = tmp_path / "plantel_cleaned.json"    

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(raw_data, file)
        
    clean_plantel_prices(input_path,output_path)

    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8") as file: 
        cleaned_data = json.load(file)

    assert len(cleaned_data) == 1

    record = cleaned_data[0]


    assert record["date"] == "2026-01-01"
    assert record["product"] == "Diesel Industrial"
    assert record["price_crc"] == 800.50
    assert isinstance(record["price_crc"], float)
    assert record["tax_crc"] == 80.00
    assert record["base_price_crc"] == 720.50
    assert record["unit"] == "KG"
    assert record["product_id"] == "3"
    assert record["update_date"] == "2026-01-02"
    assert record["source"] == "plantel"
    assert "ingestion_timestamp" in record




def test_malformed_plantel_record_is_skipped(tmp_path: Path, caplog):


    raw_data = [
        {
            "fecha": "20260101",
            "nomprod": "Diesel Industrial (Plantel)",
            "preciototal": "800.50",
            "impuesto": "80.00",
            "precsinimp": "720.50",
            "tipo": "KG",
            "id": "3",
            "fechaupd": "2026/01/02",
        },
        {
            "fecha": "20260102",
            "nomprod": "Gasolina Regular (Plantel)",
            "preciototal": "invalid-price",
            "impuesto": "90.00",
            "precsinimp": "810.00",
            "tipo": "L",
            "id": "4",
            "fechaupd": "2026/01/03",
        },
        {
            "fecha": "20260103",
            "nomprod": "Gasolina Súper (Plantel)",
            "preciototal": "950.75",
            "impuesto": "95.00",
            "precsinimp": "855.75",
            "tipo": "L",
            "id": "5",
            "fechaupd": "2026/01/04",
        },
    ]
     
    
    input_path = tmp_path / "plantel_raw.json"
    output_path = tmp_path / "plantel_cleaned.json"

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(raw_data,file)

    caplog.set_level(logging.WARNING)

    clean_plantel_prices(input_path, output_path)

    with open(output_path, "r", encoding="utf-8") as file:
        cleaned_data = json.load(file)

        assert len(cleaned_data) == 2 

        assert cleaned_data[0]["product"] == "Diesel Industrial"
        assert cleaned_data[1]["product"] == "Gasolina Súper"

        assert "Record skipped" in caplog.text
        assert "index=1" in caplog.text


        
