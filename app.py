# app.py
import os
# Эту строку нужно добавить ДО импорта streamlit
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

import streamlit as st

st.set_page_config(
    page_title="RadiaTool Pro v2.0",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main, .block-container {
        background-color: #f8f9fa !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("RadiaTool Pro v2.0")
st.info("Используйте навигацию слева для перехода между разделами.")