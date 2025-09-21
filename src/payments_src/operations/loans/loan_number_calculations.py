from pydantic import PositiveInt

from payments_src.domain.dealerships import Dealership
from payments_src.db.csv_db.db_operations import read_loan_table


def _get_dealership_code(dealership: Dealership) -> str:
    return dealership.dealership_id


def _create_dealership(dealership_dict: dict) -> Dealership:
    return Dealership(**dealership_dict)


def get_next_loan_number(dealership_id: str) -> PositiveInt:
    loans_df = read_loan_table()
    loans_df["dealership_id"] = loans_df["dealership"].map(_create_dealership).map(_get_dealership_code)
    loans_df = loans_df[loans_df["dealership_id"] == dealership_id]
    
    if len(loans_df) == 0:
        return 1
    else:
        return loans_df.shape[0] + 1