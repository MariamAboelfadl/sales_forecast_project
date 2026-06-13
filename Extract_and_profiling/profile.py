import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

def data_profile(data: dict, max_value_counts: int = 10) -> None:
    """
    Print a data quality profile for each DataFrame in the dict.

    Parameters
    ----------
    data             : dict of {name: DataFrame}
    max_value_counts : how many top values to show per column (default 10)
                       
    """
    for df_name, df in data.items():
        logging.info(f"{'='*50}")
        logging.info(f"Profiling: {df_name}  |  shape: {df.shape}")

        # Data types
        logging.info("--- Data types ---")
        print(df.dtypes.to_string())

        # Null counts
        logging.info("--- Null counts ---")
        null_counts = df.isnull().sum()
        print(null_counts[null_counts > 0].to_string() or "  No nulls found.")

        # Duplicates
        logging.info("--- Duplicate rows ---")
        dup_count = df.duplicated().sum()
        print(f"  {df_name}: {dup_count} duplicate rows")
        if dup_count > 0:
            #  show sample of duplicates 
            print(df[df.duplicated()].head(5).to_string())

        # Descriptive statistics (numeric columns only)
        logging.info("--- Descriptive statistics ---")
        numeric_cols = df.select_dtypes(include='number')
        if not numeric_cols.empty:
            print(numeric_cols.describe().round(2).to_string())

        # top unique value for all columns
        logging.info(f"--- Top {max_value_counts} value counts per column ---")
        for col in df.columns:
            counts = df[col].value_counts().head(max_value_counts)
            print(f"\n  [{col}]  ({df[col].nunique()} unique values)")
            print(counts.to_string())

    logging.info("Profiling complete.")
