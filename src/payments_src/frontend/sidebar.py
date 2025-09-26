import streamlit as st

from payments_src.frontend.enums.enums_sidebar import SidebarOptions, SidebarTitle, SidebarQuickAccess
from payments_src.frontend.utils import add_n_line_jumps_to_object
from payments_src.operations.payments.monthly_payment_calculations import calculate_monthly_payment


def create_main_sidebar():
    st.sidebar.title(SidebarTitle.TITLE.value)
    selected_option = st.sidebar.radio("Selecciona una opción", SidebarOptions.list(), index=0, key="sidebar_option")

    add_n_line_jumps_to_object(st.sidebar, 2)

    st.sidebar.subheader("Acceso Rápido")

    quick_access_option = st.sidebar.radio(
        label="",
        options=SidebarQuickAccess.list(),
        index=0,
        key="sidebar_quick_access",
        label_visibility="collapsed"
    )
    
    if quick_access_option == SidebarQuickAccess.CALCULADORA_DE_PAGOS.value:
        amount = st.sidebar.number_input("Monto del préstamo", min_value=0, value=1000, step=1)
        interest_rate_perc = st.sidebar.number_input("Tasa de interés (en %)", min_value=0.0, value=2.0, step=0.5)
        interest_rate = interest_rate_perc / 100
        num_payments = st.sidebar.number_input("Número de pagos", min_value=0, value=12, step=1)

        monthly_payment = calculate_monthly_payment(amount, num_payments, interest_rate)
        st.sidebar.write(f"#### COUTA: **{monthly_payment:.2f}**")
        st.sidebar.write(f"#### TOTAL A PAGAR: **{amount * (num_payments * interest_rate + 1):.2f}**")

    elif quick_access_option == SidebarQuickAccess.OCULTAR.value:
        st.sidebar.write("")
    
    return selected_option
