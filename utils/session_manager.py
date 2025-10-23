import streamlit as st

def init_session_state():
    if "entry_values" not in st.session_state:
        st.session_state.entry_values = {}
    if "connection" not in st.session_state:
        st.session_state.connection = "VK-правое"
    if "radiator_type" not in st.session_state:
        st.session_state.radiator_type = "10"
    if "bracket_type" not in st.session_state:
        st.session_state.bracket_type = "Настенные кронштейны"
    if "radiator_discount" not in st.session_state:
        st.session_state.radiator_discount = 0.0
    if "bracket_discount" not in st.session_state:
        st.session_state.bracket_discount = 0.0