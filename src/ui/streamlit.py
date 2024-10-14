import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
import pandas as pd
#from st_aggrid import AgGrid
import plotly.graph_objects as go
from streamlit_home import streamlit_home_page
from streamlit_about import  streamlit_about_display
from streamlit_model import streamlit_model_display
from streamlit_prices import streamlit_prices_display


# Layout
st.set_page_config(page_title="Trading Application",
                   layout="wide",
                   initial_sidebar_state="expanded")
count = st_autorefresh(interval=60000, limit=100000000, key="fizzbuzzcounter")


# this is where we will create a CSS file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


local_css(r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\config\CustomStyle.css")

# options menu
with st.sidebar:
    selected = option_menu("Main Menu", ['Home', 'Prices', 'Models', 'About'],
                           icons=['house', '1-square', '2-square', 'info-circle'],
                           menu_icon="list", default_index=1)

# Home Page
if selected == "Home":
    streamlit_home_page()

# Prices Page
if selected == "Prices":
    streamlit_prices_display()
    # price_tab1, price_tab2 = st.tabs(["Charts", "Historical Data"])
    # with price_tab1:
    #     st.title("Price Charts")
    #     price_tab1_col1, price_tab1_col2 = st.columns(2)
    #
    #     with price_tab1_col1:
    #         timeframe = ['Hourly', 'Minute', 'Daily']
    #         selected_timeframe = st.selectbox("Select a timeframe", timeframe)
    #
    #         with price_tab1_col2:
    #             if selected_timeframe == "Minute":
    #                 try:
    #                     ohlc_data = pd.read_pickle(r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data"
    #                                                r"\pickle\historical_data_minute.pkl")
    #                     # create a list of unique tickers
    #                     tickers = ohlc_data['symbol'].unique()
    #                     selected_ticker = st.selectbox("Select a ticker", tickers)
    #
    #                 except FileNotFoundError:
    #                     st.warning("Please download the pickled data first")
    #
    #             if selected_timeframe == "Hourly":
    #                 try:
    #                     ohlc_data = pd.read_pickle(r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data"
    #                                                r"\pickle\historical_data_hour.pkl")
    #                     # create a list of unique tickers
    #                     tickers = ohlc_data['symbol'].unique()
    #                     selected_ticker = st.selectbox("Select a ticker", tickers)
    #                 except FileNotFoundError:
    #                     st.warning("Please download the pickled data first")
    #
    #             if selected_timeframe == "Daily":
    #                 try:
    #                     ohlc_data = pd.read_pickle(r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data"
    #                                                r"\pickle\historical_data_day.pkl")
    #                     # create a list of unique tickers
    #                     tickers = ohlc_data['symbol'].unique()
    #                     selected_ticker = st.selectbox("Select a ticker", tickers)
    #                 except FileNotFoundError:
    #                     st.warning("Please download the pickled data first")
    #
    #     # build the ohlc chart
    #     # start OHLC Chart
    #     display = f"<span style='color: red; font-weight: bold;'>{selected_timeframe} Data for ticker {selected_ticker}</span>"
    #     st.markdown(display, unsafe_allow_html=True)
    #     ohlc_data_selected = ohlc_data[ohlc_data['symbol'] == selected_ticker]
    #
    #     time_buttons_hour = [
    #         {'step': 'all', 'stepmode': 'backward', 'label': 'All'},
    #         {'count': 1, 'step': 'hour', 'stepmode': 'backward', 'label': '1 hour'},
    #         {'count': 6, 'step': 'hour', 'stepmode': 'backward', 'label': '5 hours'},
    #         {'count': 12, 'step': 'day', 'stepmode': 'backward', 'label': '12 hours'},
    #         {'count': 24, 'step': 'month', 'stepmode': 'backward', 'label': '24 hours'},
    #     ]
    #
    #     time_buttons_minute = [
    #         {'step': 'all', 'stepmode': 'backward', 'label': 'All'},
    #         {'count': 30, 'step': 'minute', 'stepmode': 'backward', 'label': '30 Mins'},
    #         {'count': 60, 'step': 'hour', 'stepmode': 'backward', 'label': '60 Mins'},
    #     ]
    #
    #     time_buttons_day = [
    #         {'step': 'all', 'stepmode': 'backward', 'label': 'All'},
    #         {'count': 30, 'step': 'day', 'stepmode': 'backward', 'label': '30 Days'},
    #         {'count': 60, 'step': 'day', 'stepmode': 'backward', 'label': '60 Days'},
    #     ]
    #
    #     # Build the chart
    #     fig = go.Figure()
    #     fig.add_trace(go.Candlestick(x=ohlc_data_selected.index,
    #                                  open=ohlc_data_selected['open'],
    #                                  high=ohlc_data_selected['high'],
    #                                  low=ohlc_data_selected['low'],
    #                                  close=ohlc_data_selected['close'],
    #                                  name='OHLC',
    #                                  showlegend=True))
    #     fig.update_layout(xaxis_rangeslider_visible=False)
    #     fig.update_xaxes(visible=True, showticklabels=False)
    #     if selected_timeframe == "Hourly":
    #         fig.update_xaxes(rangeselector={'buttons': time_buttons_hour})
    #     if selected_timeframe == "Minute":
    #         fig.update_xaxes(rangeselector={'buttons': time_buttons_minute})
    #     # if selected_timeframe == "Daily":
    #     #     fig.update_xaxes(rangeselector={'buttons': time_buttons_day})
    #     fig.update_xaxes(rangebreaks=[dict(bounds=[16, 9.30], pattern="hour"), dict(bounds=['sat', 'mon'])],
    #                      showgrid=False)
    #     st.plotly_chart(fig, use_container_width=True)
    #
    #     # end OHLC Chart
    #
    # with price_tab2:
    #     st.write('Second Tab')
    #     st.write(len(ohlc_data_selected))
    #     ohlc_data_selected.reset_index(inplace=True)
    #     st.dataframe(ohlc_data_selected)
    #     #AgGrid(ohlc_data_selected, fit_columns_on_grid_load=True)

# Models
if selected == "Models":
    streamlit_model_display()

# About
if selected == "About":
    streamlit_about_display()

# TODO: Fix daily chart
