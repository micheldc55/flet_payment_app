

def calculate_total_amount_loaned(amount: float, interest_rate: float, num_payments: int) -> float:
    return amount / (num_payments * interest_rate + 1)


def total_amount_to_pay_calculator(amount_loaned: float, num_payments: int, interest_rate: float):
    total_amount_to_pay = amount_loaned * (num_payments * interest_rate + 1)
    return total_amount_to_pay


def calculate_monthly_payment(amount_loaned: float, num_payments: int, interest_rate: float):
    total_loaned = total_amount_to_pay_calculator(amount_loaned, num_payments, interest_rate)
    payment = total_loaned / num_payments
    return payment
