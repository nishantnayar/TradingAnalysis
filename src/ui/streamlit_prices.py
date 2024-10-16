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
            # st.write(selected_timeframe)
            # Check if 'ohlc_data' and 'tickers' are already in session_state

            if 'ohlc_data' not in st.session_state or 'tickers' not in st.session_state:
                # If not, load the data and store in session state
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

        # Create the first vertical container
        # price_tab_chart_container = st.container(height=500)
        # with price_tab_chart_container:
        display = f"<span style='color: red; font-weight: bold;'>{selected_timeframe} price chart for ticker {selected_ticker}</span>"
        st.markdown(display, unsafe_allow_html=True)
        plot_ohlc_chart(ohlc_data, selected_ticker, selected_timeframe)

        st.divider()
        # Create the second vertical container
        price_tab_cache_container = st.container()
        with price_tab_cache_container:
            # Create two columns
            column_button, column_message = st.columns(2)

            # Column 1: Button
            with column_button:
                if st.button('Clear cache and reload', icon=":material/refresh:",
                             help='This will clear cache and reload the latest data available'):
                    load_ohlc_data.clear()  # Clear the cache
                    ohlc_data, tickers = load_ohlc_data(selected_timeframe)  # Load data
                    current_time = convert_now()  # Get current time
                    st.session_state.last_reloaded_time = current_time  # Store last reloaded time in session state

            # Column 2: Display current time or cached message
            with column_message:
                current_time = convert_now()
                current_time = st.session_state.get('Data reloaded at:', current_time)
                st.write('Data reloaded at:', current_time)

    with price_tab2:
        st.header("Price Historical Data")
        expander_heading = "**Key Terms Explained**"  # Simple Markdown bold

        with st.expander(expander_heading, icon=":material/help:"):
            st.markdown('''
            |Attribute|Description|
            |-|--------------------------------------------------|
            |***Open***|The price of the stock when the market opens for trading at the beginning of the day.|
            |***High***|The highest price the stock reached during the day.|
            |***Low***|The lowest price the stock dropped to during the day.|
            |***Close***|The price of the stock when the market closes for trading at the end of the day.|
            |***Volume***|refers to the total number of shares of a stock that were traded (bought or sold) during a specific period, usually a single day. It gives an idea of how active a stock is in the market.|
            |***Trade Count***|This is the total number of individual trades (buying or selling transactions) that happened for a specific stock during a given time period, like a day. Each time someone buys or sells the stock, it adds to the trade count.|
            |***VWAP (Volume Weighted Average Price)***|VWAP is the average price of a stock over a specific period, weighted by the volume of trades. It shows where most trading happened during the day. In simple terms, it helps you see the “real” average price considering both price and how much trading took place at those prices.|
            |***Symbol***|A symbol is a short code used to identify a company’s stock on the market. |
            ''')

        display = f"<span style='color: red; font-weight: bold;'>{selected_timeframe} Data for ticker {selected_ticker}</span>"
        st.markdown(display, unsafe_allow_html=True)
        ohlc_data_selected = ohlc_data[ohlc_data['symbol'] == selected_ticker]

        # Options
        gb = GridOptionsBuilder.from_dataframe(ohlc_data_selected)

        # default column properties
        # gb.configure_default_column(min_column_width=5)

        # Add pagination
        gb.configure_pagination(enabled=True, paginationPageSize=10)

        # Add sidebar
        gb.configure_side_bar()

        # hide certain columns by default
        gb.configure_column("trade_count", hide=True)
        gb.configure_column("vwap", hide=True)
        gridoptions_table = gb.build()
        AgGrid(ohlc_data_selected,
               gridOptions=gridoptions_table,
               enable_enterprise_modules=True,
               use_container_width=True, )
