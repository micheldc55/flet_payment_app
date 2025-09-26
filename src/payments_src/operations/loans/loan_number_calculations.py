import json
from pydantic import PositiveInt

from payments_src.domain.dealerships import Dealership
from payments_src.db.csv_db.db_operations import read_loan_table, read_customers_table


def _get_dealership_code(dealership: Dealership) -> str:
    return dealership.dealership_id


def _create_dealership(dealership_dict: dict) -> Dealership:
    return Dealership(**dealership_dict)


def _to_json(dealership_str: str) -> dict:
    return json.loads(dealership_str)


def get_next_loan_readable_number(dealership_id: str) -> PositiveInt:
    loans_df = read_loan_table()
    loans_df["dealership_id"] = (
        loans_df["dealership"]
        .map(_to_json)
        .map(_create_dealership)
        .map(_get_dealership_code)
    )
    loans_df = loans_df[loans_df["dealership_id"] == dealership_id]
    
    if len(loans_df) == 0:
        return 1
    else:
        return loans_df.shape[0] + 1


def get_next_loan_id() -> PositiveInt:
    loans_df = read_loan_table()
    return loans_df.shape[0] + 1


def get_next_borrower_id() -> PositiveInt:
    borrowers_df = read_customers_table()
    return borrowers_df.shape[0] + 1
