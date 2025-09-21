import pytest

from payments_src.db.csv_db.db_initialization_ops import (
    initialize_customer_df,
    initialize_dealership_df,
    initialize_loan_df,
    initialize_payments_df,
    initialize_potential_customers_df,
)
from payments_src.domain.borrowers import Borrower
from payments_src.domain.dealerships import Dealership
from payments_src.domain.loans import Loan
from payments_src.domain.payments import Payment
from payments_src.domain.potential_borrowers import PotentialBorrower


@pytest.fixture
def borrower_fields():
    return Borrower.model_fields


@pytest.fixture
def dealership_fields():
    return Dealership.model_fields


@pytest.fixture
def loan_fields():
    return Loan.model_fields


@pytest.fixture
def payment_fields():
    return Payment.model_fields


@pytest.fixture
def potential_customer_fields():
    return PotentialBorrower.model_fields


def test_initialize_customer_df(borrower_fields):
    df = initialize_customer_df()
    assert df.columns.tolist() == list(borrower_fields.keys())


def test_initialize_dealership_df(dealership_fields):
    df = initialize_dealership_df()
    assert df.columns.tolist() == list(dealership_fields.keys())


def test_initialize_loan_df(loan_fields):
    df = initialize_loan_df()
    assert df.columns.tolist() == list(loan_fields.keys())


def test_initialize_payments_df(payment_fields):
    df = initialize_payments_df()
    assert df.columns.tolist() == list(payment_fields.keys())


def test_initialize_potential_customers_df(potential_customer_fields):
    df = initialize_potential_customers_df()
    assert df.columns.tolist() == list(potential_customer_fields.keys())
