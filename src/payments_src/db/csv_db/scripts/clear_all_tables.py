import argparse
import logging
import os
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description="Clear all CSV tables")

parser.add_argument("--clear_all_tables", action="store_true", help="Clear all CSV tables")

args = parser.parse_args()

clear_all_tables = args.clear_all_tables


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


if __name__ == "__main__":
    if clear_all_tables:
        approval = input("Are you sure you want to clear all tables? (y/n): ")
        if approval == "y":
            clear_all_csv_tables()
        else:
            logging.warning("No tables were cleared")
    else:
        logging.warning("No tables were cleared")