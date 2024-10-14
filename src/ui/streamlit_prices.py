import streamlit as st
from streamlit_utils import load_ohlc_data


def streamlit_prices_display():
    price_tab1, price_tab2 = st.tabs(["Charts", "Historical Data"])

    with price_tab1:
        st.header("Price Charts")
        price_tab1_col1, price_tab1_col2 = st.columns(2)
        with price_tab1_col1:
            timeframe = ['Hourly', 'Minute', 'Daily']
            selected_timeframe = st.selectbox("Select a timeframe", timeframe)
        with price_tab1_col2:
            # st.write(selected_timeframe)
            ohlc_data, tickers = load_ohlc_data(selected_timeframe)
            if ohlc_data is not None:
                selected_ticker = st.selectbox("Select a ticker", tickers)

    with price_tab2:
        st.header("Price Historical Data")
        if ohlc_data is not None:
            ohlc_data_selected = ohlc_data[ohlc_data['symbol'] == selected_ticker]
            st.dataframe(ohlc_data_selected)
            # TODO: Fix dataframe