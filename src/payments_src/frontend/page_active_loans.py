import streamlit as st

from payments_src.frontend.enums.enums_active_loans import ActiveLoansActions


def active_loans_page():
    st.title("Préstamos Activos")

    short_col, _ = st.columns([1, 4])

    selected_action = short_col.selectbox(
        "Selecciona una acción", ActiveLoansActions.list(), index=0, key="active_loans_action"
    )

    if selected_action == ActiveLoansActions.VIEW_LOAN_PAYMENTS.value:
        pass  # need to edit the way we move loans from potential to active
    elif selected_action == ActiveLoansActions.VIEW_MONTHLY_PAYMENTS.value:
        pass
    elif selected_action == ActiveLoansActions.VIEW_LOAN.value:
        pass
