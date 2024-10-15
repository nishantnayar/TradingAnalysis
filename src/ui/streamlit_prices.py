import streamlit as st
from streamlit_utils import load_ohlc_data
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_utils import convert_now


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

        # Create the first vertical container
        price_tab_chart_container = st.container(height=500)
        with price_tab_chart_container:
            st.write('This is where the price chart will be displayed')

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
                current_time = st.session_state.get('last_reloaded_time', 'Data is cached.')
                st.write('Data reloaded at:', current_time)

    with price_tab2:
        st.header("Price Historical Data")
        expander_heading = "**Key Terms Explained**"  # Simple Markdown bold

        with st.expander(expander_heading, icon=":material/help:"):
            st.markdown('''
            |Attribute|Description|
            |----------|--------------------------------------------------|
            |***Open***|Open Description|
            |***High***|Open Description|
            |***Low***|Open Description|
            |***Close***|Open Description|
            |***Volume***|Open Description|
            |***Trade Count***|Open Description|
            |***VWAP***|Open Description|
            |***Symbol***|Open Description|
            ''')

        display = f"<span style='color: red; font-weight: bold;'>{selected_timeframe} Data for ticker {selected_ticker}</span>"
        st.markdown(display, unsafe_allow_html=True)
        ohlc_data_selected = ohlc_data[ohlc_data['symbol'] == selected_ticker]

        # Options
        gb = GridOptionsBuilder.from_dataframe(ohlc_data_selected)

        # default column properties
        gb.configure_default_column(min_column_width=5)

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
