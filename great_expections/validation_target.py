import great_expectations as e 
import logging

def validation_facts (data):

    logging.info('validion for facts starting')
    
    sales_fact = data['fact_sales']
    forecast_fact = data['fact_forecast']
    sales = e.from_pandas(sales_fact )
    forecast = e.from_pandas(forecast_fact)

    # sales 
    sales.expect_column_values_to_not_be_null('ProductKey')
    sales.expect_column_values_to_not_be_null("CustomerKey")
    sales.expect_column_values_to_not_be_null("DateKey")

    sales.expect_column_values_to_be_between("Quantity", 1, 100)
    sales.expect_column_values_to_be_between("Sales Amount", 0, None)

    # forecast
    forecast.expect_column_values_to_not_be_null('BrandKey')
    forecast.expect_column_values_to_be_between("Forecast", 0, None)

    return True

def validation_dims (data):
    logging.info('validion for dims starting')
    
    dim_product = e.from_pandas(data["dim_product"])
    dim_brand = e.from_pandas(data["dim_brand"])
    dim_location = e.from_pandas(data["dim_location"])
    dim_date = e.from_pandas(data["dim_date"])

    # Product
    dim_product.expect_column_values_to_be_unique("ProductKey")
    dim_product.expect_column_values_to_not_be_null("ProductKey")

    # Brand
    dim_brand.expect_column_values_to_be_unique("BrandKey")
    dim_brand.expect_column_values_to_not_be_null("Brand")

    # Location
    dim_location.expect_column_values_to_be_unique("LocationKey")
    dim_location.expect_column_values_to_not_be_null("CountryRegion")

    # Date
    dim_date.expect_column_values_to_be_unique("DateKey")
    dim_date.expect_column_values_to_not_be_null("Date")

    return True

   