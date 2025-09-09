from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt

from payments_src.domain.borrowers import Borrower, BorrowerFactory
from payments_src.domain.dealerships import Dealership, DealershipFactory
from payments_src.domain.loans_enums import LoanConstants
from payments_src.domain.payments import PaymentList, PaymentListFactory


class Loan(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    loan_id: PositiveInt
    loan_readable_code: str
    payment_list: PaymentList
    borrower: Borrower
    dealership: Dealership


class LoanFactory:
    @classmethod
    def create_loan(
        cls: "LoanFactory",
        loan_id: PositiveInt,
        loan_number: PositiveInt,
        payment_list: PaymentList,
        borrower: Borrower,
        dealership: Dealership,
    ) -> Loan:
        loan_readable_code = cls._create_loan_readable_code(dealership.dealership_code, loan_number)
        return Loan(
            loan_id=loan_id,
            loan_readable_code=loan_readable_code,
            payment_list=payment_list,
            borrower=borrower,
            dealership=dealership,
        )

    @classmethod
    def create_loan_from_dict(cls: "LoanFactory", loan_dict: dict) -> Loan:
        return Loan(
            loan_id=loan_dict["loan_id"],
            loan_readable_code=cls._create_loan_readable_code(loan_dict["dealership"]["dealership_code"], loan_dict["loan_number"]),
            payment_list=PaymentListFactory.create_payment_list(loan_dict["payment_list"]),
            borrower=BorrowerFactory.create_borrower(loan_dict["borrower"]),
            dealership=DealershipFactory.create_dealership(loan_dict["dealership"]),
        )

    @classmethod
    def create_loan_from_dict_without_ids(cls: "LoanFactory", loan_dict: dict) -> Loan:
        loan_id = hash(datetime.now())
        borrower_id = hash(datetime.now())

        loan_dict_copy = loan_dict.copy()
        loan_dict_copy["loan_id"] = loan_id
        loan_dict_copy["borrower"]["borrower_id"] = borrower_id

        return cls.create_loan_from_dict(loan_dict_copy)


    @staticmethod
    def _fill_number_with_left_zeros(number: PositiveInt, total_digits: PositiveInt) -> str:
        return str(number).zfill(total_digits)


    @classmethod
    def _create_loan_readable_code(cls: "LoanFactory", dealership_code: str, loan_number: PositiveInt) -> str:
        zeros_filled_number = cls._fill_number_with_left_zeros(loan_number, LoanConstants.LOAN_ID_TOTAL_DIGITS.value)
        return dealership_code + "-" + zeros_filled_number
