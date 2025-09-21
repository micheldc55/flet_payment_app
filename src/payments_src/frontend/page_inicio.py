import streamlit as st

from payments_src.frontend.enums.enums_inicio import InicioTitle
from payments_src.frontend.utils import add_n_line_jumps


def inicio_page():
    st.title(InicioTitle.TITLE.value)
    st.subheader(InicioTitle.SUBTITLE.value)

    add_n_line_jumps(2)

    st.write("En algun momento van a haber graficos aca...")
    st.write("Tasa de rechazo de prestamos / Tasa de aprobacion de prestamos")

    add_n_line_jumps(2)
