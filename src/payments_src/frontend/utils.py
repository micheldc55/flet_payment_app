import streamlit as st


def add_n_line_jumps(n: int):
    for _ in range(n):
        st.write("")