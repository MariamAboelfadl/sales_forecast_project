import pandas as pd
import logging
import os


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)


def extract(sales_path: str = "data/Sales.json",
            forecast_path: str = "data/forecast.json") -> dict:
    """
    Load raw JSON files and return them as a dict of DataFrames.
    
    """
    
    for path in [sales_path, forecast_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input file not found: {path}")

    logging.info(f"Loading sales data from: {sales_path}")
    df_sales = pd.read_json(sales_path)

    logging.info(f"Loading forecast data from: {forecast_path}")
    df_forecast = pd.read_json(forecast_path)

    
    logging.info(f"Sales loaded    — shape: {df_sales.shape}")
    logging.info(f"Forecast loaded — shape: {df_forecast.shape}")

    return {
        'sales': df_sales,
        'forecast': df_forecast
    }

