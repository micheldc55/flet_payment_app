import os

import pandas as pd
from pydantic import PositiveInt

from payments_src.db.csv_db.db_constants import CSVTable
from payments_src.domain.borrowers import Borrower
from payments_src.domain.dealerships import Dealership
from payments_src.domain.loans import Loan
from payments_src.domain.potential_borrowers import PotentialBorrower


def read_customers_table() -> pd.DataFrame:
    df = pd.read_csv(CSVTable.CUSTOMER_PATH.value)

    return df


def write_customers_table(df: pd.DataFrame, overwrite: bool = False) -> None:
    if (os.path.exists(CSVTable.CUSTOMER_PATH.value)) and (overwrite == False):
        raise FileExistsError(f"File {CSVTable.CUSTOMER_PATH.value} already exists")

    df.to_csv(CSVTable.CUSTOMER_PATH.value, index=False)


def append_customers_table(df: pd.DataFrame, new_borrower: Borrower) -> None:
    df = pd.concat([df, pd.DataFrame([new_borrower.model_dump()])], ignore_index=True)

    return df


def edit_customers_table_record(df: pd.DataFrame, new_borrower: Borrower) -> None:
    borrower_id = new_borrower.borrower_id

    new_df = df.loc[df["borrower_id"] != borrower_id].copy()

    return append_potential_customers_table(new_df, new_borrower)


def read_dealership_table() -> pd.DataFrame:
    df = pd.read_csv(
        CSVTable.DEALERSHIP_PATH.value,
        dtype={
            "dealership_phone_number": str,
            "dealership_code": str,
        },
    )

    return df


def append_dealership_table(df: pd.DataFrame, new_dealership: Dealership) -> None:
    df = pd.concat([df, pd.DataFrame([new_dealership.model_dump()])], ignore_index=True)

    return df


def edit_dealership_table_record(df: pd.DataFrame, new_dealership: Dealership) -> pd.DataFrame:
    dealership_id = new_dealership.dealership_id

    new_df = df.loc[df["dealership_id"] != dealership_id].copy()

    return append_dealership_table(new_df, new_dealership)


def write_dealership_table(df: pd.DataFrame, overwrite: bool = False) -> None:
    if (os.path.exists(CSVTable.DEALERSHIP_PATH.value)) and (overwrite == False):
        raise FileExistsError(f"File {CSVTable.DEALERSHIP_PATH.value} already exists")

    df.to_csv(CSVTable.DEALERSHIP_PATH.value, index=False)


def read_payments_table() -> pd.DataFrame:
    df = pd.read_csv(CSVTable.PAYMENTS_PATH.value)

    return df


def write_payments_table(df: pd.DataFrame, overwrite: bool = False) -> None:
    if (os.path.exists(CSVTable.PAYMENTS_PATH.value)) and (overwrite == False):
        raise FileExistsError(f"File {CSVTable.PAYMENTS_PATH.value} already exists")

    df.to_csv(CSVTable.PAYMENTS_PATH.value, index=False)


def read_loan_table() -> pd.DataFrame:
    df = pd.read_csv(CSVTable.LOAN_PATH.value)

    return df


def write_loan_table(df: pd.DataFrame, overwrite: bool = False) -> None:
    if (os.path.exists(CSVTable.LOAN_PATH.value)) and (overwrite == False):
        raise FileExistsError(f"File {CSVTable.LOAN_PATH.value} already exists")

    df.to_csv(CSVTable.LOAN_PATH.value, index=False)


def append_loan_table(df: pd.DataFrame, new_loan: Loan) -> pd.DataFrame:
    """
    Append a new loan to the DataFrame using JSON serialization for nested objects.
    """
    df = pd.concat([df, pd.DataFrame([new_loan.to_json_dict()])], ignore_index=True)
    return df


def edit_loan_table_record(df: pd.DataFrame, updated_loan: Loan) -> pd.DataFrame:
    """
    Edit an existing loan record in the DataFrame using JSON serialization for nested objects.
    """
    loan_id = updated_loan.loan_id
    new_df = df.loc[df["loan_id"] != loan_id].copy()
    return append_loan_table(new_df, updated_loan)

