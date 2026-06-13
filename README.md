# Tech Products Sales — Data Analytics Assessment

## Repository Structure

```
├── etl_pipeline.py          # Python ETL script (single executable file)
├── Sales.json               # Raw input — sales transactions (298,246 rows)
├── forecast.json            # Raw input — annual brand forecast by country (33 rows)
├── output/
│   ├── dim_product.csv      # 2,495 unique products
│   ├── dim_customer.csv     # 8,868 unique customers
│   ├── dim_geography.csv    # 306 unique city/state/country combinations
│   ├── dim_date.csv         # 731 dates (2008-01-01 → 2009-12-31)
│   ├── fact_sales.csv       # 80,238 deduplicated sales transactions
│   └── fact_forecast.csv    # 33 annual forecast records (country × brand × year)
├── data_model.png           # Star schema ERD (see below for description)
└── README.md                # This file
```

---

## 1. ETL Logic

### 1a. Data Exploration Findings

| Issue | Field | Finding |
|-------|-------|---------|
| Duplicate rows | All fields | 218,008 of 298,246 rows are true duplicates (same values in all 18 columns). Each transaction is repeated between 1 and 491 times with no order-line key to distinguish them. |
| Mislabelled column | `Color` | Contains Subcategory values in 100% of rows. Color always equals Subcategory. Renamed to `Color_Raw` and documented; Subcategory is used in `dim_product`. |
| Null customer attributes | `Name`, `Education`, `Occupation` | 259 customers (out of 8,868) have no name or demographic data across all their transactions. Filled with `'Unknown'`. |
| No surrogate key | `SalesKey` | Source data had no transaction identifier. A sequential `SalesKey` is generated post-deduplication. |
| Date format | `OrderDate` | Stored as `M/D/YYYY` string. Parsed to `datetime64` and converted to integer `DateKey (YYYYMMDD)` for the date dimension join. |

### 1b. Transformation Steps

1. **Load** both JSON files into Pandas DataFrames.
2. **Rename columns** for clarity: `Net Price → UnitPrice`, `Product Name → ProductName`, `Customer Code → CustomerCode`, `Color → Color_Raw`.
3. **Strip whitespace** from all string columns.
4. **Parse `OrderDate`** from `M/D/YYYY` to `datetime64`.
5. **Fill nulls** in `Name`, `Education`, `Occupation` with `'Unknown'`.
6. **Deduplicate** — `drop_duplicates()` on all 18 columns. 218,008 rows removed; 80,238 unique rows retained.
7. **Calculate `Revenue`** = `Quantity × UnitPrice` (rounded to 4 decimal places).
8. **Add `SalesKey`** — sequential integer starting at 1.

### 1c. Dimension Extraction

| Table | Source columns | Key |
|-------|---------------|-----|
| `dim_product` | ProductKey, ProductName, Brand, Subcategory, Category | ProductKey (natural key from source) |
| `dim_customer` | CustomerKey, CustomerCode, Name, Education, Occupation | CustomerKey (natural key from source) |
| `dim_geography` | CountryRegion, Continent, State, City | GeoKey (surrogate, generated) |
| `dim_date` | Generated 2008–2009 | DateKey (YYYYMMDD integer) |

### 1d. Fact Tables

**`fact_sales`** — grain: one row per unique sales transaction  
Columns: `SalesKey, DateKey, OrderDate, ProductKey, CustomerKey, GeoKey, Quantity, UnitPrice, Revenue`

**`fact_forecast`** — grain: one row per Country × Brand × Year  
Columns: `ForecastKey, Year, CountryRegion, Brand, ForecastAmount`

---

## 2. Data Model

### Star Schema

```
                    ┌─────────────┐
                    │  dim_date   │
                    │─────────────│
                    │ DateKey  PK │
                    │ Date        │
                    │ Year        │
                    │ Quarter     │
                    │ Month       │
                    │ MonthName   │
                    │ WeekOfYear  │
                    │ DayOfWeek   │
                    │ IsWeekend   │
                    │ YearMonth   │
                    │ YearQuarter │
                    └──────┬──────┘
                           │ DateKey (active)
          ┌────────────────┼────────────────────┐
          │                │                    │
          ▼                ▼                    │
  ┌──────────────┐  ┌──────────────────┐        │
  │ dim_product  │  │   fact_sales     │        │
  │──────────────│  │──────────────────│        │
  │ ProductKey PK│◄─┤ ProductKey  FK   │        │
  │ ProductName  │  │ DateKey     FK   │        │
  │ Brand        │  │ CustomerKey FK   │        │
  │ Subcategory  │  │ GeoKey      FK   │        │
  │ Category     │  │ SalesKey    PK   │        │
  └──────────────┘  │ Quantity         │        │
                    │ UnitPrice        │        │
  ┌──────────────┐  │ Revenue          │        │
  │ dim_customer │  └──────────────────┘        │
  │──────────────│          ▲                   │
  │CustomerKey PK│◄─────────┘                   │
  │CustomerCode  │                              │
  │ Name         │                              │
  │ Education    │                              │
  │ Occupation   │                              │
  └──────────────┘                              │
                                                │
  ┌──────────────────┐                          │
  │ dim_geography    │                          │
  │──────────────────│                          │
  │ GeoKey       PK  │◄──── fact_sales.GeoKey   │
  │ CountryRegion    │                          │
  │ Continent        │                          │
  │ State            │                          │
  │ City             │                          │
  └──────────────────┘                          │
                                                │
  ┌─────────────────────────────────────────┐   │
  │           fact_forecast                 │   │
  │─────────────────────────────────────────│   │
  │ ForecastKey   PK                        │   │
  │ Year          ──── INACTIVE rel to ─────┴───┘
  │ CountryRegion ──── joins dim_geography via CountryRegion
  │ Brand         ──── joins dim_product via Brand
  │ ForecastAmount                          │
  └─────────────────────────────────────────┘
```

### Relationship Notes

| Relationship | Type | Cardinality | Notes |
|---|---|---|---|
| `dim_date` → `fact_sales` | Active | 1:many | Via `DateKey` |
| `dim_product` → `fact_sales` | Active | 1:many | Via `ProductKey` |
| `dim_customer` → `fact_sales` | Active | 1:many | Via `CustomerKey` |
| `dim_geography` → `fact_sales` | Active | 1:many | Via `GeoKey` |
| `dim_date[Year]` → `fact_forecast[Year]` | **Inactive** | 1:many | Use `USERELATIONSHIP()` in DAX for forecast vs actual comparisons |
| `dim_geography[CountryRegion]` → `fact_forecast[CountryRegion]` | Active | 1:many | Enables country-level filter on forecast |
| `dim_product[Brand]` → `fact_forecast[Brand]` | Active (separate) | 1:many | Enables brand-level filter on forecast |

**Granularity handling:** `fact_sales` is at transaction × product × customer × city level. `fact_forecast` is at Year × Country × Brand level. They must not be joined directly — all cross-fact comparisons go through shared dimensions using `CALCULATE()` and `USERELATIONSHIP()` in DAX.

---

## 3. Power BI Dashboard

### DAX Measures

```dax
-- Core Sales
Total Revenue = SUM(fact_sales[Revenue])

Total Units Sold = SUM(fact_sales[Quantity])

Avg Order Value = DIVIDE([Total Revenue], DISTINCTCOUNT(fact_sales[SalesKey]))

-- Year-over-Year Comparison (2009 vs 2008)
Sales 2008 =
CALCULATE([Total Revenue], YEAR(dim_date[Date]) = 2008)

Sales 2009 =
CALCULATE([Total Revenue], YEAR(dim_date[Date]) = 2009)

YoY Change $ =
[Sales 2009] - [Sales 2008]

YoY Change % =
DIVIDE([YoY Change $], [Sales 2008], 0)

-- Forecast vs Actual (2009 only)
Total Forecast 2009 =
CALCULATE(
    SUM(fact_forecast[ForecastAmount]),
    USERELATIONSHIP(dim_date[Year], fact_forecast[Year]),
    dim_date[Year] = 2009
)

Forecast vs Actual $ =
[Sales 2009] - [Total Forecast 2009]

Forecast vs Actual % =
DIVIDE([Forecast vs Actual $], [Total Forecast 2009], 0)

-- Product share of total
Product Revenue Share % =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL(dim_product))
)

-- Top 10 Products filter (used in visual-level filter)
Product Rank =
RANKX(ALL(dim_product[ProductName]), [Total Revenue], , DESC)

-- Top customer revenue
Top Customer Revenue =
CALCULATE(
    [Total Revenue],
    TOPN(1, ALL(dim_customer), [Total Revenue])
)
```

### Dashboard Layout (Single Page)

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Slicer: Country]   [Slicer: State]                 SALES DASHBOARD │
├──────────┬──────────┬──────────┬──────────────────────────────────────┤
│ KPI Card │ KPI Card │ KPI Card │                                      │
│ Total Rev│ 2009 YoY │ Forecast │   Line/Area Chart: Revenue by Month  │
│ $42.6M   │ vs 2008  │ vs Actual│   (2008 vs 2009, drill to quarter)   │
├──────────┴──────────┴──────────┤                                      │
│                                │                                      │
│  Bar Chart: Top 10 Products    ├──────────────────────────────────────┤
│  (Revenue + % share label)     │                                      │
│  [Drill-through enabled]       │  Stacked Bar: Forecast vs Actual     │
│                                │  by Brand (2009)                     │
├────────────────────────────────┤                                      │
│                                ├──────────────────────────────────────┤
│  Table: Top Customer Behavior  │  Map or Bar Chart: Revenue by        │
│  Name | Revenue | Top Products │  Country & State                     │
│  Timeline: purchases by month  │                                      │
└────────────────────────────────┴──────────────────────────────────────┘
```

### Chart Recommendations

| Requirement | Recommended Visual | Notes |
|-------------|-------------------|-------|
| Total sales by different granularities | Line chart + Matrix | Drill-down from Year → Quarter → Month → Day |
| 2009 vs 2008 comparison | Clustered bar / KPI card with YoY | DAX measures `Sales 2008`, `Sales 2009`, `YoY Change %` |
| Top 10 products & share | Horizontal bar chart | Add data label showing % of total; visual-level filter `Product Rank ≤ 10` |
| Forecast vs actual 2009 | Grouped bar chart (actual vs forecast) | Group by Brand, filter to 2009; use `USERELATIONSHIP` measure |
| Top customer behavior | Table + Scatter or line chart | Show monthly purchases; enable drill-through to customer detail page |
| Country & State filter | Slicers (both fields) | Sync across all visuals on the page |

### Drill-Down Configuration

- **Date hierarchy**: Year → Quarter → Month → Day (set in dim_date, use as a date hierarchy in Power BI)
- **Product hierarchy**: Category → Subcategory → Brand → ProductName
- **Geography hierarchy**: Continent → CountryRegion → State → City

---

## 4. Key Assumptions

1. **Deduplication**: 218,008 duplicate rows removed. Each unique (Customer, Product, Date, Quantity, Price) combination is treated as one sales line item. Total revenue after dedup: $42,644,968.84.

2. **Color field**: The `Color` column in `Sales.json` contains Subcategory values (not actual product colors). This appears to be a data pipeline error in the source system. The field is preserved as `Color_Raw` for traceability but not used in analysis.

3. **Forecast granularity**: Forecast data is at Year × Country × Brand level only. There is no product-level or date-level forecast. The comparison between forecast and actual is therefore rolled up to Country × Brand × Year.

4. **Revenue definition**: `Revenue = Quantity × UnitPrice`. No discounts, taxes, or shipping costs are present in the source data.

5. **Date table**: Spans 2008-01-01 to 2009-12-31, covering both years of sales data and the 2009 forecast period.

6. **Customer anonymity**: 259 customers have no demographic information in any of their transactions. These are treated as `'Unknown'` — not excluded — to preserve sales data completeness.

---

## 5. Running the ETL

```bash
# Install dependencies (standard Python data stack)
pip install pandas numpy

# Run from the repo root (where Sales.json and forecast.json live)
python etl_pipeline.py

# Output CSVs will appear in ./output/
```

Python 3.8+ required. No database installation needed — outputs are CSV files ready for Power BI import.
