import logging
import os
import shutil
from pathlib import Path


def clear_all_csv_tables() -> None:
    """
    Clears all CSV files and the customer_files directory from the tables directory.
    Preserves the tables directory itself.
    """
    tables_dir = Path("src/payments_src/db/csv_db/tables")
    
    if not tables_dir.exists():
        logging.warning(f"Tables directory does not exist: {tables_dir}")
        return
    
    try:
        # Remove all CSV files
        csv_files = list(tables_dir.glob("*.csv"))
        for csv_file in csv_files:
            csv_file.unlink()
            logging.info(f"Removed CSV file: {csv_file}")
        
        # Remove customer_files directory if it exists
        customer_files_dir = tables_dir / "customer_files"
        if customer_files_dir.exists():
            shutil.rmtree(customer_files_dir)
            logging.info(f"Removed customer_files directory: {customer_files_dir}")
        
        logging.info("Successfully cleared all tables")
        
    except Exception as e:
        logging.error(f"Error clearing tables: {e}")
        raise