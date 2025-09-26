import streamlit as st

from payments_src.frontend.sidebar import create_main_sidebar
from payments_src.frontend.enums.enums_sidebar import SidebarOptions
from payments_src.frontend.page_inicio import inicio_page
from payments_src.frontend.page_active_loans import active_loans_page
from payments_src.frontend.page_monthly_payment_calculation import monthly_payment_calculation_page
from payments_src.frontend.page_potential_borrowers import potential_borrowers_page
from payments_src.frontend.page_dealership_management import dealership_management_page


def main():
    st.set_page_config(page_title="RDJ - Pagos", page_icon=":money_with_wings:", layout="wide")
    
    selected_option = create_main_sidebar()

    if selected_option == SidebarOptions.INICIO.value:
        inicio_page()

    elif selected_option == SidebarOptions.CALCULADORA_DE_PAGOS.value:
        monthly_payment_calculation_page()

    elif selected_option == SidebarOptions.CREDITOS_POTENCIALES.value:
        potential_borrowers_page()

    elif selected_option == SidebarOptions.CREDITOS_ACTIVOS.value:
        active_loans_page()

    elif selected_option == SidebarOptions.PAYMENT_MANAGEMENT.value:
        # payment_management_page()
        pass

    elif selected_option == SidebarOptions.ESTADISTICAS.value:
        pass

    elif selected_option == SidebarOptions.GESTION_AUTOMOTORAS.value:
        dealership_management_page()

if __name__ == "__main__":
    main()