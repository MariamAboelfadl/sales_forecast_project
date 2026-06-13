import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',   
    force=True
)

def load_csv(data: dict, output_base: str = "output") -> str:
    """
    Export all DataFrames in `data` to timestamped CSV files.

    Parameters
    ----------
    data        : dict of {table_name: DataFrame}
    output_base : base directory for output (default: "output")

    Returns
    -------
    str : the full output directory path
    """
    run_id     = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_base, run_id)

    
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Could not create output directory {output_dir}: {e}")
        raise

    logging.info(f"Exporting {len(data)} tables to: {output_dir}")

    for name, df in data.items():
        file_path = os.path.join(output_dir, f"{name}.csv")
        try:
            df.to_csv(file_path, index=False)
            logging.info(f"   {name}.csv  ({len(df):,} rows)")
        except Exception as e:
            
            logging.error(f"  Failed to export {name}.csv: {e}")
            raise

    logging.info("All tables exported successfully.")
    return output_dir
