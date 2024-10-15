import streamlit as st
import sys


def streamlit_home_page():
    st.title('Welcome to Trading Analysis')
    # Get the current Python interpreter path
    st.write(f"Current Python interpreter: {sys.executable}")

