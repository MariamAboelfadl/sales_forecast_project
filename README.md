# Sales Forecast Analytics Pipeline

## Project Overview

This project demonstrates an end-to-end Data Engineering workflow for sales analytics and forecasting. The pipeline extracts raw sales and forecast data from JSON files, performs data profiling, cleaning, transformation, validation, dimensional modeling, and prepares curated datasets for business intelligence reporting in Power BI.

---

## Business Requirements

The solution addresses the following analytical requirements:

- Analyze total sales across multiple dimensions.
- Compare sales performance between 2008 and 2009.
- Identify the Top 10 products and their contribution to total sales.
- Compare forecasted sales against actual sales for 2009.
- Analyze top customer purchasing behavior and purchased products over time.
- Enable filtering by Country and State.

---

## Data Pipeline Architecture

```text
Raw JSON Files
      │
      ▼
Data Extraction
      │
      ▼
Data Profiling
      │
      ▼
Data Cleaning
      │
      ▼
Data Transformation

      │
      ▼
Dimensional Modeling
      │
      ▼
Data Validation and load layer
      │
      ▼
Power BI Dashboard
```

---

## Data Quality Improvements

### Cleaning Activities

- Removed duplicate records.
- Converted OrderDate to DateTime format.
- Standardized text columns.
- Removed unnecessary columns with high missing rates.
- Validated column data types.
- Applied business rule validation.

### Validation

Implemented data quality checks using Great Expectations:

- Null checks
- Data type validation
- Duplicate detection
- Business rule validation

---

## Data Transformation

Generated analytical attributes:

| Column | Description |
|----------|----------|
| Sales Amount | Quantity × Net Price |
| Year | Extracted from OrderDate |
| Month | Extracted from OrderDate |
| Quarter | Extracted from OrderDate |
| YearMonth | YYYY-MM format |

---

## Dimensional Data Model

### FactSales

- ProductKey
- CustomerKey
- OrderDate
- Quantity
- Net Price
- Sales Amount

### DimProduct

- ProductKey
- Product Name
- Brand
- Category
- Subcategory

### DimCustomer

- CustomerKey
- Customer Code

### DimLocation

- Continent
- CountryRegion
- State
- City

### DimDate

- Date
- Year
- Month
- Quarter

### Forecast Fact

- CountryRegion
- Brand
- Year
- Forecast

---

## Technologies

- Python
- Pandas
- Great Expectations
- Power BI
- DAX

---

## Repository Structure

```text
SALES_FORECAST_PROJECT
│
├── data
├── Extract_and_profiling
├── transform
├── modeling
├── validation
├── load
├── main.py
└── README.md
```

---

## Dashboard KPIs

- Total Sales
- Sales by Year
- Sales Growth %
- Forecast vs Actual
- Top 10 Products
- Product Contribution %
- Top Customer Analysis
- Country Performance
- State Performance

---

## Key Skills Demonstrated

- Data Extraction
- Data Profiling
- Data Cleaning
- Data Transformation
- Data Validation
- Dimensional Modeling
- ETL Development
- Data Warehousing Concepts
- Business Intelligence
- Power BI & DAX

---

