import streamlit as st

from payments_src.frontend.enums.enums_sidebar import SidebarOptions, SidebarTitle


def create_main_sidebar():
    st.sidebar.title(SidebarTitle.TITLE.value)
    selected_option = st.sidebar.radio("Selecciona una opción", SidebarOptions.list(), index=0, key="sidebar_option")

    return selected_option
