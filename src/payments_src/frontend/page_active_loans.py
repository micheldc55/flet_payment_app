import streamlit as st

from payments_src.frontend.enums.enums_active_loans import ActiveLoansActions
from payments_src.db.csv_db.db_operations import parse_and_expand_loan_object, read_and_expand_loans_table
from payments_src.domain.loans_enums import LoanStatus
from payments_src.domain.loans import Loan
from payments_src.frontend.page_potential_borrowers import pretty_print_object
from payments_src.frontend.utils import add_n_line_jumps


def active_loans_page():
    st.title("Préstamos Activos")

    short_col, _ = st.columns([1, 3])

    selected_action = short_col.selectbox(
        "Selecciona una acción", ActiveLoansActions.list(), index=0, key="active_loans_action"
    )

    if selected_action == ActiveLoansActions.LIST_LOANS.value:
        active_loans_df = read_and_expand_loans_table(LoanStatus.APPROVED)
        active_loans_df = parse_and_expand_loan_object(active_loans_df)

        st.dataframe(active_loans_df)   

    elif selected_action == ActiveLoansActions.VIEW_LOAN.value:
        active_loans_df = read_and_expand_loans_table(LoanStatus.APPROVED)
        active_loans_df["display_name"] = active_loans_df.apply(
            lambda x: str(x["loan_id"]) + " - " + x["loan_readable_code"] + " - " + x["borrower"].nombre_cliente + f' ({x["car"].marca_auto} {x["car"].modelo_auto})',
            axis=1
        )

        subject_display_names = active_loans_df["display_name"]

        add_n_line_jumps(2)
        st.header("Selecciona un préstamo")
        st.write("Debajo se muestran los detalles de la financiación seleccionada")
        
        short_col, _ = st.columns([1, 2])
        active_loan_name = short_col.selectbox("Selecciona un préstamo", subject_display_names, label_visibility="collapsed")

        mapping_borrower_id_to_display_name = dict(zip(subject_display_names, active_loans_df["loan_id"]))

        loan_id = mapping_borrower_id_to_display_name[active_loan_name]
        loan = active_loans_df[active_loans_df["loan_id"] == loan_id].iloc[0]
        loan_obj = Loan(**loan.to_dict())

        add_n_line_jumps(1)
        st.subheader("Cliente")
        pretty_print_object(loan_obj.borrower)
        st.subheader("Vehiculo")
        pretty_print_object(loan_obj.car)
        st.subheader("Automotora")
        pretty_print_object(loan_obj.dealership)
        st.subheader("Financiación")
        pretty_print_object(loan_obj.payment_list)

        

    elif selected_action == ActiveLoansActions.VIEW_MONTHLY_PAYMENTS.value:
        pass
    elif selected_action == ActiveLoansActions.VIEW_LOAN_PAYMENTS.value:
        pass
