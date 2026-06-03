import pandas as pd 
import pytest


from scripts.quality.validate_prices import validate_prices_df


def test_valid_data_passes():
    df = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "source": "consumer",
            "price": 1000.0,
            "currency": "CRC",
            "price_crc": 1000.0,
            "product_id": "1"
        }
    ])

    validate_prices_df(df)


def test_null_price_raises_error():
    df = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "source": "consumer",
            "price": None,
            "currency": "CRC",
            "price_crc": 1000.0,
            "product_id": "1"
        }
    ])

    with pytest.raises(ValueError):
        validate_prices_df(df)    


def test_negative_price_raises_error():
    df = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "source": "consumer",
            "price": -500.0,
            "currency": "CRC",
            "price_crc": -500.0,
            "product_id": "1"
        }
    ])

    with pytest.raises(ValueError):
        validate_prices_df(df)        


def test_missing_required_column_raises_error():
    df = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "source": "consumer",
            "price": 1000.0,
            "currency": "CRC",
            "product_id": "1"
            # Falta "price_crc"
        }
    ])

    with pytest.raises(ValueError):
        validate_prices_df(df)        


def test_multiple_valid_rows_pass():
    df = pd.DataFrame([
        {
            "date": "2026-01-01",
            "product": "Gasolina Regular",
            "source": "consumer",
            "price": 1000.0,
            "currency": "CRC",
            "price_crc": 1000.0,
            "product_id": "1"
        },
        {
            "date": "2026-01-02",
            "product": "Diesel",
            "source": "consumer",
            "price": 950.0,
            "currency": "CRC",
            "price_crc": 950.0,
            "product_id": "2"
        },
        {
            "date": "2026-01-03",
            "product": "Gasolina Premium",
            "source": "international",
            "price": 100.0,
            "currency": "USD",
            "price_crc": 54000.0,
            "product_id": "3"
        }
    ])

    validate_prices_df(df)        