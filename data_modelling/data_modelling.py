import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

def data_model(data: dict) -> dict:
    """
    Build the star schema: dimension tables + fact tables.

    Returns a dict of all tables ready for loading.
    """
    
    df_sales = data['sales'].copy()
    df_forecast = data['forecast'].copy()

    
    logging.info("Creating DateKeys")

    df_sales['DateKey'] = df_sales['OrderDate'].dt.strftime('%Y%m%d').astype(int)

    df_forecast['Date'] = pd.to_datetime(df_forecast['Year'].astype(str) + '-01-01')
    df_forecast['DateKey'] = df_forecast['Date'].dt.strftime('%Y%m%d').astype(int)

    # dim_date 
    logging.info("Building dim_date")

    
    dim_date = pd.DataFrame({
        'Date': pd.date_range(start='2008-01-01', end='2009-12-31', freq='D')
    })

    dim_date['DateKey']     = dim_date['Date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['Year']        = dim_date['Date'].dt.year
    dim_date['Quarter']     = dim_date['Date'].dt.quarter
    dim_date['QuarterName'] = 'Q' + dim_date['Quarter'].astype(str)
    dim_date['Month']       = dim_date['Date'].dt.month
    dim_date['MonthName']   = dim_date['Date'].dt.strftime('%B')    
    dim_date['MonthShort']  = dim_date['Date'].dt.strftime('%b')    
    dim_date['WeekOfYear']  = dim_date['Date'].dt.isocalendar().week.astype(int)
    dim_date['DayOfWeek']   = dim_date['Date'].dt.dayofweek + 1     
    dim_date['DayName']     = dim_date['Date'].dt.strftime('%A')    
    dim_date['IsWeekend']   = dim_date['DayOfWeek'].isin([6, 7])   
    dim_date['YearMonth']   = dim_date['Date'].dt.to_period('M').astype(str)

    # dim_product 
    logging.info("Building dim_product")

    dim_product = (
        df_sales[['ProductKey', 'Product Name', 'Brand', 'Category', 'Subcategory']]
        .drop_duplicates(subset=['ProductKey'])   
        .sort_values('ProductKey')
        .reset_index(drop=True)
    )

    #  dim_customer 
    logging.info("Building dim_customer")

   
    customer_cols = ['CustomerKey', 'Customer Code','Name']
   
    dim_customer = (
        df_sales[customer_cols]
        .drop_duplicates(subset=['CustomerKey'])
        .sort_values('CustomerKey')
        .reset_index(drop=True)
    )

    # dim_location
    logging.info("Building dim_location")

    dim_location = (
        df_sales[['CountryRegion', 'Continent', 'State', 'City']]
        .drop_duplicates()
        .sort_values(['CountryRegion', 'State', 'City'])
        .reset_index(drop=True)
    )
    dim_location.insert(0, 'LocationKey', range(1, len(dim_location) + 1))

    # Merge LocationKey back into sales
    df_sales = df_sales.merge(
        dim_location[['LocationKey', 'CountryRegion', 'Continent', 'State', 'City']],
        on=['CountryRegion', 'Continent', 'State', 'City'],
        how='left'
    )

    #  dim_brand 
    
    logging.info("Building dim_brand")

    dim_brand = (
        pd.concat([df_sales[['Brand']], df_forecast[['Brand']]])
        .drop_duplicates()
        .sort_values('Brand')
        .reset_index(drop=True)
    )
    dim_brand.insert(0, 'BrandKey', range(1, len(dim_brand) + 1))

    df_forecast = df_forecast.merge(dim_brand, on='Brand', how='left')

    # fact_sales 
    logging.info("Building fact_sales")

   
    fact_sales = df_sales[[
        'ProductKey',
        'CustomerKey',
        'LocationKey',
        'DateKey',
        'Quantity',
        'Net Price',
        'Sales Amount'
    ]].copy()

    
    fact_sales.insert(0, 'SalesKey', range(1, len(fact_sales) + 1))

    # fact_forecast 
    logging.info("Building fact_forecast")

    fact_forecast = df_forecast[[
        'BrandKey',
        'DateKey',
        'CountryRegion',    
        'Forecast'
    ]].copy()

    fact_forecast.insert(0, 'ForecastKey', range(1, len(fact_forecast) + 1))

    logging.info("All tables built successfully.")

    return {
        'dim_product':  dim_product,
        'dim_customer': dim_customer,
        'dim_location': dim_location,
        'dim_brand':    dim_brand,
        'dim_date':     dim_date,
        'fact_sales':   fact_sales,
        'fact_forecast':fact_forecast
    }
