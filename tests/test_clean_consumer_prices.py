import pandas as pd
import pytest
import json
from pathlib import Path
import tempfile
from datetime import datetime

from scripts.transform.clean_consumer_prices import clean_consumer_prices


def test_valid_consumer_data_cleans_correctly():
    """
    Verifica que datos válidos se limpian correctamente.
    
    En data engineering, la limpieza es donde ocurren las transformaciones críticas.
    Si falla aquí, TODO lo demás está mal.
    """
    # Datos RAW (tal como vienen del API de RECOPE)
    raw_data = [
        {
            "fecha": "20260101",  # Formato YYYYMMDD
            "nomprod": "Gasolina Regular (Regular)",  # Con paréntesis
            "preciototal": "1000.50",  # String con decimales
            "impuesto": "100.00",
            "precsinimp": "900.50",
            "margenpromedio": "50.00",
            "fechaupd": "2026/01/01",  # Formato YYYY/MM/DD
            "id": "1"
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "raw.json"
        output_path = Path(temp_dir) / "cleaned.json"
        
        # Escribe datos RAW
        with open(input_path, "w") as f:
            json.dump(raw_data, f)
        
        # Ejecuta limpieza
        clean_consumer_prices(input_path, output_path)
        
        # Lee resultado limpio
        with open(output_path, "r") as f:
            cleaned_data = json.load(f)
        
        # Verifica que se limpió correctamente
        assert len(cleaned_data) == 1, "Debería haber 1 registro"
        
        record = cleaned_data[0]
        
        # Verifica transformaciones específicas
        assert record["date"] == "2026-01-01", f"Fecha incorrecto: {record['date']}"
        assert record["product"] == "Gasolina Regular", f"Producto incorrecto: {record['product']}"
        assert record["price_crc"] == 1000.50, f"Precio incorrecto: {record['price_crc']}"
        assert record["tax_crc"] == 100.0, f"Tax incorrecto: {record['tax_crc']}"
        assert record["base_price_crc"] == 900.50, f"Base price incorrecto: {record['base_price_crc']}"
        assert record["update_date"] == "2026-01-01", f"Update date incorrecto: {record['update_date']}"
        assert record["product_id"] == "1", f"Product ID incorrecto: {record['product_id']}"
        assert "ingestion_timestamp" in record, "Falta ingestion_timestamp"


def test_date_parsing_multiple_formats():
    """
    Verifica que se parsean correctamente DOS FORMATOS DE FECHA DIFERENTES.
    
    fecha: YYYYMMDD
    fechaupd: YYYY/MM/DD
    
    Si el parsing falla, TODO el análisis temporal está corrupto.
    """
    raw_data = [
        {
            "fecha": "20261201",  # Diciembre 2026
            "nomprod": "Diesel",
            "preciototal": "950.00",
            "impuesto": "95.00",
            "precsinimp": "855.00",
            "margenpromedio": "47.50",
            "fechaupd": "2026/12/15",  # Formato diferente
            "id": "2"
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "raw.json"
        output_path = Path(temp_dir) / "cleaned.json"
        
        with open(input_path, "w") as f:
            json.dump(raw_data, f)
        
        clean_consumer_prices(input_path, output_path)
        
        with open(output_path, "r") as f:
            cleaned_data = json.load(f)
        
        record = cleaned_data[0]
        
        # Verifica ambos formatos parseados correctamente
        assert record["date"] == "2026-12-01", f"Fecha parsing incorrecto: {record['date']}"
        assert record["update_date"] == "2026-12-15", f"Update date parsing incorrecto: {record['update_date']}"


def test_malformed_record_skipped():
    """
    Verifica que registros con errores se saltan (skip) sin romper el pipeline.
    
    En data engineering REAL, los datos son SUCIO. Necesitas skip elegante de registros malos.
    """
    raw_data = [
        # Registro VÁLIDO
        {
            "fecha": "20260101",
            "nomprod": "Gasolina Regular",
            "preciototal": "1000.50",
            "impuesto": "100.00",
            "precsinimp": "900.50",
            "margenpromedio": "50.00",
            "fechaupd": "2026/01/01",
            "id": "1"
        },
        # Registro MALO (falta fecha)
        {
            # "fecha": FALTA ESTA COLUMNA
            "nomprod": "Diesel",
            "preciototal": "950.00",
            "impuesto": "95.00",
            "precsinimp": "855.00",
            "margenpromedio": "47.50",
            "fechaupd": "2026/01/02",
            "id": "2"
        },
        # Registro VÁLIDO
        {
            "fecha": "20260102",
            "nomprod": "Gasolina Premium",
            "preciototal": "1100.00",
            "impuesto": "110.00",
            "precsinimp": "990.00",
            "margenpromedio": "55.00",
            "fechaupd": "2026/01/02",
            "id": "3"
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "raw.json"
        output_path = Path(temp_dir) / "cleaned.json"
        
        with open(input_path, "w") as f:
            json.dump(raw_data, f)
        
        clean_consumer_prices(input_path, output_path)
        
        with open(output_path, "r") as f:
            cleaned_data = json.load(f)
        
        # CRÍTICO: Input tiene 3 registros, pero output tiene 2
        # El registro malo fue SKIPPEADO
        assert len(cleaned_data) == 2, f"Debería haber 2 registros (1 fue skipped), pero tiene {len(cleaned_data)}"
        
        # Verifica que los registros válidos están presentes
        products = [r["product"] for r in cleaned_data]
        assert "Gasolina Regular" in products, "Falta Gasolina Regular"
        assert "Gasolina Premium" in products, "Falta Gasolina Premium"


def test_numeric_conversion_to_float():
    """
    Verifica que strings numéricos se convierten a floats correctamente.
    
    Muchos APIs retornan precios como strings "1000.50".
    Si NO los conviertes a float, los cálculos dan error.
    """
    raw_data = [
        {
            "fecha": "20260101",
            "nomprod": "Test Product",
            "preciototal": "1234.56",  # String
            "impuesto": "123.45",       # String
            "precsinimp": "1111.11",    # String
            "margenpromedio": "222.22", # String
            "fechaupd": "2026/01/01",
            "id": "1"
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "raw.json"
        output_path = Path(temp_dir) / "cleaned.json"
        
        with open(input_path, "w") as f:
            json.dump(raw_data, f)
        
        clean_consumer_prices(input_path, output_path)
        
        with open(output_path, "r") as f:
            cleaned_data = json.load(f)
        
        record = cleaned_data[0]
        
        # CRÍTICO: Verifica que son FLOATS, no strings
        assert isinstance(record["price_crc"], float), f"price_crc no es float: {type(record['price_crc'])}"
        assert isinstance(record["tax_crc"], float), f"tax_crc no es float: {type(record['tax_crc'])}"
        assert isinstance(record["base_price_crc"], float), f"base_price_crc no es float: {type(record['base_price_crc'])}"
        assert isinstance(record["margin"], float), f"margin no es float: {type(record['margin'])}"
        
        # Verifica valores exactos
        assert record["price_crc"] == 1234.56, f"price_crc valor incorrecto"
        assert record["tax_crc"] == 123.45, f"tax_crc valor incorrecto"