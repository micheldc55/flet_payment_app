import streamlit as st

from payments_src.frontend.utils import add_n_line_jumps
from payments_src.operations.payments.payment_operations import calculate_monthly_payment
from payments_src.domain.payment_enums import Currency


def monthly_payment_calculation_page():
    st.title("Calculadora de Pagos Mensuales")

    add_n_line_jumps(2)

    st.write("Ingrese los datos del préstamo para calcular el pago mensual teórico")

    short_col1, short_col2, _ = st.columns([1, 1, 4])

    moneda = short_col1.selectbox("Moneda", Currency.list())
    amount = short_col2.number_input("Monto del préstamo", min_value=0, value=1000, step=1)
    interest_rate_perc = short_col1.number_input("Tasa de interés (%)", min_value=0.0, value=2.0, step=0.5)
    interest_rate = interest_rate_perc / 100
    num_payments = short_col2.number_input("Número de pagos", min_value=0, value=12, step=1)

    if st.button("Calcular"):
        monthly_payment = calculate_monthly_payment(amount, num_payments, interest_rate)

        add_n_line_jumps(1)
        st.write(f"#### El pago mensual calculado es: **{moneda} {monthly_payment:.2f}**")