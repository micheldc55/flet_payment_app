import pandas as pd

from payments_src.domain.borrowers import Borrower
from payments_src.domain.dealerships import Dealership
from payments_src.domain.loans import Loan
from payments_src.domain.payments import Payment
from payments_src.domain.potential_borrowers import PotentialBorrower


def initialize_customer_df() -> None:
    borrower_fields = Borrower.model_fields

    df = pd.DataFrame(columns=borrower_fields.keys())

    return df


def initialize_dealership_df() -> None:
    dealership_fields = Dealership.model_fields

    df = pd.DataFrame(columns=dealership_fields.keys())

    return df


def initialize_loan_df() -> None:
    loan_fields = Loan.model_fields

    df = pd.DataFrame(columns=loan_fields.keys())

    return df


def initialize_payments_df() -> None:
    payments_fields = Payment.model_fields

    df = pd.DataFrame(columns=payments_fields.keys())

    return df
