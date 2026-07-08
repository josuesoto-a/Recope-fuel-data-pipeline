import pandas as pd
import pytest
from pathlib import Path

from scripts.transform.model_prices_data import model_prices_data 

import tempfile
import os




def test_model_prices_data_unifies_three_sources():
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.0,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        assert output_path.exists()
        result = pd.read_csv(output_path)
        assert len(result) == 3
        assert "price_crc" in result.columns


        




def test_currency_conversion_usd_to_crc():
    """
    Verifica que la conversión USD → CRC se aplica correctamente.
    1 USD = 540 CRC (según el código)
    """
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 100.0,  # 100 USD
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        result = pd.read_csv(output_path)
        
        # Busca la fila de Brent (international)
        brent_row = result[result["product"] == "Brent"].iloc[0]
        
        # Verifica que price_crc = price_usd * 540
        assert brent_row["price_crc"] == 54000.0  # 100 * 540 = 54000
        assert brent_row["currency"] == "USD"





def test_no_nulls_in_critical_columns():
    """
    Verifica que no hay valores nulos en columnas críticas.
    En data engineering, nulls sin controlar pueden arruinar análisis.
    """
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.0,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        result = pd.read_csv(output_path)
        
        # Columnas críticas que NO pueden tener nulls
        critical_columns = ["date", "product", "price", "price_crc"]
        
        for col in critical_columns:
            null_count = result[col].isnull().sum()
            assert null_count == 0, f"Columna {col} tiene {null_count} nulls"






def test_all_sources_present_in_output():
    """
    Verifica que el output contiene datos de las 3 fuentes.
    Si falta una fuente, significa que algo falló en la transformación.
    """
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.0,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        result = pd.read_csv(output_path)
        
        # Verifica que hay al menos 1 fila de cada fuente
        sources = result["source"].unique()
        
        assert "consumer" in sources, "Falta fuente consumer"
        assert "international" in sources, "Falta fuente international"
        assert "plantel" in sources, "Falta fuente plantel"            





def test_prices_are_positive():
    """
    Verifica que NO hay precios negativos o cero.
    Precios negativos indican datos corruptos.
    """
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.0,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        result = pd.read_csv(output_path)
        
        # Verifica que TODOS los precios son > 0
        assert (result["price"] > 0).all(), "Hay precios <= 0"
        assert (result["price_crc"] > 0).all(), "Hay precios_crc <= 0"





def test_price_unit_column_created():
    """
    Verifica que la columna price_unit se crea con formato correcto.
    price_unit = currency + "_per_" + unit
    Ej: "CRC_per_L", "USD_unknown", "CRC_per_KG"
    
    En data engineering, price_unit es crucial para análisis comparables.
    """
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.0,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        result = pd.read_csv(output_path)
        
        # Verifica que price_unit existe
        assert "price_unit" in result.columns, "Falta columna price_unit"
        
        # Verifica formato de price_unit para cada fuente
        consumer_row = result[result["product"] == "Gasolina Regular"].iloc[0]
        international_row = result[result["product"] == "Brent"].iloc[0]
        plantel_row = result[result["product"] == "Diesel Industrial"].iloc[0]
        
        assert consumer_row["price_unit"] == "CRC_per_L", f"Consumer price_unit incorrecto: {consumer_row['price_unit']}"
        assert international_row["price_unit"] == "USD_unknown", f"International price_unit incorrecto: {international_row['price_unit']}"
        assert plantel_row["price_unit"] == "CRC_per_KG", f"Plantel price_unit incorrecto: {plantel_row['price_unit']}"






def test_source_labels_correct():
    """
    Verifica que cada fila tiene el source label correcto.
    source debe ser: "consumer", "international", o "plantel"
    
    Esto es crítico para auditoría y trazabilidad de datos.
    """
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.0,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        result = pd.read_csv(output_path)
        
        # Verifica que cada producto tiene el source correcto
        consumer_row = result[result["product"] == "Gasolina Regular"].iloc[0]
        international_row = result[result["product"] == "Brent"].iloc[0]
        plantel_row = result[result["product"] == "Diesel Industrial"].iloc[0]
        
        assert consumer_row["source"] == "consumer", f"Consumer source incorrecto: {consumer_row['source']}"
        assert international_row["source"] == "international", f"International source incorrecto: {international_row['source']}"
        assert plantel_row["source"] == "plantel", f"Plantel source incorrecto: {plantel_row['source']}"        





def test_output_has_all_required_columns():
    """
    Verifica que el output tiene TODAS las 10 columnas esperadas.
    
    Si falta una columna, significa que la transformación NO funcionó
    y los analistas no tendrán los datos que esperan.
    """
    df_consumer = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "price_crc": 1000.0,
            "tax_crc": 100.0,
            "base_price_crc": 900.0,
            "product_id": "1",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_international = pd.DataFrame([
        {
            "date_start": "2026-01-01",
            "date_end": "2026-01-31",
            "product": "Brent",
            "price_usd": 85.0,
            "product_id": "2",
            "currency": "USD",
            "source": "international",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    df_plantel = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Diesel Industrial",
            "price_crc": 800.0,
            "tax_crc": 80.0,
            "base_price_crc": 720.0,
            "unit": "KG",
            "product_id": "3",
            "update_date": "2026-01-01",
            "ingestion_timestamp": "2026-01-01T00:00:00"
        }
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        consumer_path = Path(temp_dir) / "consumer.csv"
        international_path = Path(temp_dir) / "international.csv"
        plantel_path = Path(temp_dir) / "plantel.csv"
        output_path = Path(temp_dir) / "output.csv"

        df_consumer.to_csv(consumer_path, index=False)
        df_international.to_csv(international_path, index=False)
        df_plantel.to_csv(plantel_path, index=False)

        model_prices_data(consumer_path, international_path, plantel_path, output_path)

        result = pd.read_csv(output_path)
        
        # Las 10 columnas que DEBE tener el output
        required_columns = [
            "date",
            "product",
            "source",
            "price",
            "currency",
            "unit",
            "price_unit",
            "price_crc",
            "product_id",
            "ingestion_timestamp"
        ]
        
        # Verifica que TODAS existen
        missing_columns = [col for col in required_columns if col not in result.columns]
        
        assert missing_columns == [], f"Faltan columnas: {missing_columns}"        