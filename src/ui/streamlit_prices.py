# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 15:33:22 2024

@author: nisha
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 15:33:22 2024

@author: nisha
"""

import streamlit as st
from streamlit_utils import load_ohlc_data, convert_now, plot_ohlc_chart
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

def streamlit_prices_display():
    price_tab1, price_tab2 = st.tabs(["Charts", "Historical Data"])

    with price_tab1:
        st.header("Price Charts")
        price_tab1_col1, price_tab1_col2 = st.columns(2)

        with price_tab1_col1:
            timeframe = ['Daily', 'Hourly', 'Minute']
            selected_timeframe = st.selectbox("Select a timeframe", timeframe)

        with price_tab1_col2:
            # Check if 'ohlc_data' and 'tickers' are already in session_state
            if 'ohlc_data' not in st.session_state or 'tickers' not in st.session_state:
                # Load the data and store in session state
                ohlc_data, tickers = load_ohlc_data(selected_timeframe)
                if ohlc_data is not None:
                    st.session_state['ohlc_data'] = ohlc_data
                    st.session_state['tickers'] = tickers
            else:
                # Retrieve cached data from session state
                ohlc_data = st.session_state['ohlc_data']
                tickers = st.session_state['tickers']

            if ohlc_data is not None:
                selected_ticker = st.selectbox("Select a ticker", tickers)

        # Display the chart
        if 'ohlc_data' in st.session_state:
            display = f"<span style='color: red; font-weight: bold;'>{selected_timeframe} price chart for ticker {selected_ticker}</span>"
            st.markdown(display, unsafe_allow_html=True)
            plot_ohlc_chart(ohlc_data, selected_ticker, selected_timeframe)

        st.divider()

        # Container for cache management
        price_tab_cache_container = st.container()
        with price_tab_cache_container:
            # Create two columns
            column_button, column_message = st.columns(2)

            # Column 1: Button to refresh data
            with column_button:
                if st.button('Refresh data', help='This will reload the latest data available'):
                    load_ohlc_data.clear()  # Clear the cache
                    ohlc_data, tickers = load_ohlc_data(selected_timeframe)  # Load data again
                    if ohlc_data is not None:
                        st.session_state['ohlc_data'] = ohlc_data
                        st.session_state['tickers'] = tickers
                    st.session_state.last_reloaded_time = convert_now()  # Update last reloaded time
                    st.success("Data reloaded successfully.")

            # Column 2: Display current time or cached message
            with column_message:
                current_time = st.session_state.get('last_reloaded_time', "N/A")
                st.write('Last data reload time:', current_time)

    with price_tab2:
        st.header("Price Historical Data")
        expander_heading = "**Key Terms Explained**"  # Simple Markdown bold

        with st.expander(expander_heading, icon=":material/help:"):
            st.markdown('''
            |Attribute|Description|
            |-|-|
            |***Open***|The price of the stock when the market opens for trading at the beginning of the day.|
            |***High***|The highest price the stock reached during the day.|
            |***Low***|The lowest price the stock dropped to during the day.|
            |***Close***|The price of the stock when the market closes for trading at the end of the day.|
            |***Volume***|Total number of shares traded during a specific period.|
            |***Trade Count***|Total number of individual trades that happened during a given time period.|
            |***VWAP (Volume Weighted Average Price)***|The average price of a stock over a specific period, weighted by the volume of trades.|
            |***Symbol***|A short code used to identify a company’s stock on the market.|
            ''')

        # Display historical data based on selected ticker
        ohlc_data_selected = ohlc_data[ohlc_data['symbol'] == selected_ticker]

        if not ohlc_data_selected.empty:
            display = f"<span style='color: red; font-weight: bold;'>{selected_timeframe} Data for ticker {selected_ticker}</span>"
            st.markdown(display, unsafe_allow_html=True)

            # Options for AgGrid
            gb = GridOptionsBuilder.from_dataframe(ohlc_data_selected)
            gb.configure_pagination(enabled=True, paginationPageSize=10)
            gb.configure_side_bar()
            gb.configure_column("trade_count", hide=True)
            gb.configure_column("vwap", hide=True)
            gridoptions_table = gb.build()
            AgGrid(ohlc_data_selected, gridOptions=gridoptions_table, enable_enterprise_modules=True, use_container_width=True)
        else:
            st.warning(f"No data available for {selected_ticker} in {selected_timeframe}.")

                
