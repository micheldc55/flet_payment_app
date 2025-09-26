import streamlit as st


def add_n_line_jumps(n: int):
    for _ in range(n):
        st.write("")


def add_n_line_jumps_to_object(object: object, n: int):
    for _ in range(n):
        object.write("")
