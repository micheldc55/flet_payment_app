import os
from enum import Enum


class CSVTable(Enum):
    _base_path = os.path.join("src", "payments_src", "db", "csv_db", "tables")
    PATH = _base_path
    CUSTOMER_PATH = os.path.join(_base_path, "customer.csv")
    DEALERSHIP_PATH = os.path.join(_base_path, "dealership.csv")
    LOAN_PATH = os.path.join(_base_path, "loan.csv")
    PAYMENTS_PATH = os.path.join(_base_path, "payments.csv")
    CUSTOMER_FILES_PATH = os.path.join(_base_path, "customer_files")
