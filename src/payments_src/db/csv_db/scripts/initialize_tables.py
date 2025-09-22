import argparse
import os

from payments_src.db.csv_db.db_constants import CSVTable
from payments_src.db.csv_db.db_initialization_ops import (
    initialize_customer_df,
    initialize_dealership_df,
    initialize_loan_df,
    initialize_payments_df,
)
from payments_src.db.csv_db.db_operations import (
    write_customers_table,
    write_dealership_table,
    write_loan_table,
    write_payments_table,
)

parser = argparse.ArgumentParser(description="Initialize tables")

parser.add_argument("--customer", action="store_true", help="Initialize customer table")
parser.add_argument("--dealership", action="store_true", help="Initialize dealership table")
parser.add_argument("--loan", action="store_true", help="Initialize loan table")
parser.add_argument("--payments", action="store_true", help="Initialize payments table")
parser.add_argument("--customer_files", action="store_true", help="Initialize customer files table")
parser.add_argument("--overwrite", action="store_true", default=False, help="Overwrite existing tables")

args = parser.parse_args()


def initialize_tables(args: argparse.Namespace) -> None:
    tables_dir = CSVTable.PATH.value
    os.makedirs(tables_dir, exist_ok=True)

    if args.customer:
        customer_df = initialize_customer_df()
        write_customers_table(customer_df, args.overwrite)
        print("Customer table initialized")

    if args.dealership:
        dealership_df = initialize_dealership_df()
        write_dealership_table(dealership_df, args.overwrite)
        print("Dealership table initialized")

    if args.loan:
        loan_df = initialize_loan_df()
        write_loan_table(loan_df, args.overwrite)
        print("Loan table initialized")

    if args.payments:
        payments_df = initialize_payments_df()
        write_payments_table(payments_df, args.overwrite)
        print("Payments table initialized")

    if args.customer_files:
        try:
            os.makedirs(CSVTable.CUSTOMER_FILES_PATH.value, exist_ok=False)
        except FileExistsError:
            print(f"Customer files directory already exists at {CSVTable.CUSTOMER_FILES_PATH.value}")
        else:
            print("Customer files directory initialized")


if __name__ == "__main__":
    initialize_tables(args)

# Example usage: (Initializes all tables)
# python src/payments_src/db/csv_db/scripts/initialize_tables.py --customer --dealership --loan --payments

# Example usage (uv): (Initializes all tables)
# uv run python src/payments_src/db/csv_db/scripts/initialize_tables.py --customer --overwrite --dealership --loan --payments
