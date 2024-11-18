import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from streamlit_home import streamlit_home_page
from streamlit_about import streamlit_about_display
from streamlit_model import streamlit_model_display
from streamlit_prices import streamlit_prices_display
from streamlit_pairs import streamlit_pairs_trading_display


# Layout
st.set_page_config(page_title="Trading Application", layout="wide", initial_sidebar_state="expanded")
count = st_autorefresh(interval=60000, limit=100000000, key="fizzbuzzcounter")

# CSS file
@st.cache_resource
def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

local_css(r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\config\CustomStyle.css")


# Options menu
with st.sidebar:
    selected = option_menu("Main Menu", ['Home', 'Information', 'Pairs Trading', 'About'],
                           icons=['house', '1-square', '2-square', 'info-circle'],
                           menu_icon="list", default_index=1)

# Page Routing
if selected == "Home":
    streamlit_home_page()
elif selected == "Information":
    streamlit_prices_display()
elif selected =="Pairs Trading":
    streamlit_pairs_trading_display()
elif selected == "Models":
    streamlit_model_display()
elif selected == "About":
    streamlit_about_display()
