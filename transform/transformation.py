import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

def data_transformation(data: dict) -> dict:
    """
    Clean and transform raw sales and forecast DataFrames.

    Returns a dict with keys 'sales' and 'forecast'.
    """
    
    df_sales = data['sales'].copy()
    df_forecast = data['forecast'].copy()

    # Sales
    logging.info("Transforming sales DataFrame")
    logging.info(f"  Shape before dedup: {df_sales.shape}")

   
    df_sales.drop_duplicates(inplace=True)
    logging.info(f"  Shape after dedup : {df_sales.shape}")


    df_sales['OrderDate'] = pd.to_datetime(df_sales['OrderDate'])

    # Trim whitespace on all string columns
    
    for col in df_sales.columns:
        if pd.api.types.is_string_dtype(df_sales[col]):
            df_sales[col] = df_sales[col].str.strip()

    
    cols_to_drop = [ 'Education', 'Occupation', 'Color']
    existing_drops = [c for c in cols_to_drop if c in df_sales.columns]
    if existing_drops:
        df_sales.drop(columns=existing_drops, inplace=True)
        logging.info(f"  Dropped columns: {existing_drops}")

    df_sales['Name'] = df_sales['Name'].fillna('Unknown')
    # Calculate Revenue
    df_sales['Sales Amount'] = (df_sales['Quantity'] * df_sales['Net Price']).round(4)

    
    logging.info(f"  Null counts after transform:\n{df_sales.isnull().sum()[df_sales.isnull().sum() > 0]}")
    logging.info("Sales transformation complete.")

    # Forecast 
    logging.info("Transforming forecast DataFrame")

    for col in df_forecast.columns:
        if pd.api.types.is_string_dtype(df_forecast[col]):
            df_forecast[col] = df_forecast[col].str.strip()

    logging.info("Forecast transformation complete.")

    return {'sales': df_sales, 'forecast': df_forecast}
