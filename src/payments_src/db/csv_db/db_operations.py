import os

import pandas as pd

from payments_src.db.csv_db.db_constants import CSVTable
from payments_src.domain.borrowers import Borrower, BorrowerFactory
from payments_src.domain.car import Car, CarFactory
from payments_src.domain.dealerships import Dealership, DealershipFactory
from payments_src.domain.payments import PaymentList, PaymentListFactory
from payments_src.domain.loans import Loan
from payments_src.domain.loans_enums import LoanStatus
from payments_src.domain.payment_enums import Currency


def read_customers_table() -> pd.DataFrame:
    df = pd.read_csv(CSVTable.CUSTOMER_PATH.value)

    return df


def write_customers_table(df: pd.DataFrame, overwrite: bool = False) -> None:
    if (os.path.exists(CSVTable.CUSTOMER_PATH.value)) and (overwrite == False):
        raise FileExistsError(f"File {CSVTable.CUSTOMER_PATH.value} already exists")

    df.to_csv(CSVTable.CUSTOMER_PATH.value, index=False)


def append_customers_table(df: pd.DataFrame, new_borrower: Borrower) -> None:
    if new_borrower.borrower_id in df["borrower_id"].values:
        raise ValueError(f"Borrower with ID {new_borrower.borrower_id} already exists")
    
    df = pd.concat([df, pd.DataFrame([new_borrower.model_dump()])], ignore_index=True)

    return df


def edit_customers_table_record(df: pd.DataFrame, new_borrower: Borrower) -> None:
    borrower_id = new_borrower.borrower_id

    if borrower_id not in df["borrower_id"].values:
        raise ValueError(f"Borrower with ID {borrower_id} does not exist")
    
    new_df = df.loc[df["borrower_id"] != borrower_id].copy()

    return append_customers_table(new_df, new_borrower)


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
    if new_dealership.dealership_id in df["dealership_id"].values:
        raise ValueError(f"Dealership with ID {new_dealership.dealership_id} already exists")
    
    df = pd.concat([df, pd.DataFrame([new_dealership.model_dump()])], ignore_index=True)

    return df


def edit_dealership_table_record(df: pd.DataFrame, new_dealership: Dealership) -> pd.DataFrame:
    dealership_id = new_dealership.dealership_id
    
    if dealership_id not in df["dealership_id"].values:
        raise ValueError(f"Dealership with ID {dealership_id} does not exist")
    
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


def read_active_loans_table() -> pd.DataFrame:
    df = read_loan_table()
    df = df[df["status"] == LoanStatus.APPROVED.value]
    return df


def read_potential_loans_table() -> pd.DataFrame:
    df = read_loan_table()
    df = df[df["status"] == LoanStatus.POTENTIAL.value]
    return df


def read_rejected_loans_table() -> pd.DataFrame:
    df = read_loan_table()
    df = df[df["status"] == LoanStatus.REJECTED.value]
    return df


def append_loan_table(df: pd.DataFrame, new_loan: Loan) -> pd.DataFrame:
    """
    Append a new loan to the DataFrame using JSON serialization for nested objects.
    """
    if new_loan.loan_id in df["loan_id"].values:
        raise ValueError(f"Loan with ID {new_loan.loan_id} already exists")
    
    df = pd.concat([df, pd.DataFrame([new_loan.to_json_dict()])], ignore_index=True)
    return df


def edit_loan_table_record(df: pd.DataFrame, updated_loan: Loan) -> pd.DataFrame:
    """
    Edit an existing loan record in the DataFrame using JSON serialization for nested objects.
    """
    if updated_loan.loan_id not in df["loan_id"].values:
        raise ValueError(f"Loan with ID {updated_loan.loan_id} does not exist")
    
    loan_id = updated_loan.loan_id
    new_df = df.loc[df["loan_id"] != loan_id].copy()
    return append_loan_table(new_df, updated_loan)


def write_loan_table(df: pd.DataFrame, overwrite: bool = False) -> None:
    if (os.path.exists(CSVTable.LOAN_PATH.value)) and (overwrite == False):
        raise FileExistsError(f"File {CSVTable.LOAN_PATH.value} already exists")

    df.to_csv(CSVTable.LOAN_PATH.value, index=False)


def read_and_expand_loans_table(filter_type: LoanStatus = LoanStatus.POTENTIAL):
    if filter_type.value == LoanStatus.POTENTIAL.value:
        loans_table_copy = read_potential_loans_table().copy()
    elif filter_type.value == LoanStatus.APPROVED.value:
        loans_table_copy = read_active_loans_table().copy()
    elif filter_type.value == LoanStatus.REJECTED.value:
        loans_table_copy = read_rejected_loans_table().copy()
    else:
        raise ValueError(f"Invalid filter type: {filter_type}")

    loans_table_copy["payment_list"] = loans_table_copy["payment_list"].apply(PaymentListFactory.create_from_payment_list_record_str)
    loans_table_copy["borrower"] = loans_table_copy["borrower"].apply(BorrowerFactory.create_from_borrower_record_str)
    loans_table_copy["car"] = loans_table_copy["car"].apply(CarFactory.create_from_car_record_str)
    loans_table_copy["dealership"] = loans_table_copy["dealership"].apply(DealershipFactory.create_from_dealership_record_str)

    return loans_table_copy


def parse_and_expand_loan_object(loans_table_copy: pd.DataFrame) -> pd.DataFrame:
    expanded_df = loans_table_copy[["loan_id", "loan_readable_code", "status"]]

    borrower_fields = Borrower.get_fields_and_types()
    for field_name in borrower_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["borrower"].apply(lambda x: getattr(x, field_name))
    
    car_fields = Car.get_fields_and_types()
    for field_name in car_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["car"].apply(lambda x: getattr(x, field_name))
    
    dealership_fields = Dealership.get_fields_and_types()
    for field_name in dealership_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["dealership"].apply(lambda x: getattr(x, field_name))
    
    payment_list_fields = PaymentList.get_fields_and_types()
    for field_name in payment_list_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["payment_list"].apply(
            lambda x: getattr(x, field_name).value if isinstance(getattr(x, field_name), Currency) else getattr(x, field_name)
        )

    return expanded_df