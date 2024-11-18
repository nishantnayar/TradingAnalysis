import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from sqlalchemy import create_engine


@st.cache_data(show_spinner=True, ttl=3600, max_entries=5)
def load_ohlc_data(timeframe):
    # Database connection parameters
    db_params = {
        'user': 'postgres',
        'password': 'nishant',
        'host': 'localhost',  # or your database host
        'port': '5432',       # default PostgreSQL port
        'database': 'pairs_trading'
    }

    # Create the database connection
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(connection_string)

    # Define table names based on timeframe
    table_name = {
        "Minute": "alpaca_data_min",
        "Hourly": "alpaca_data_hourly",
        "Daily": "alpaca_data_daily"
    }.get(timeframe)

    if table_name is None:
        st.warning("Invalid timeframe selected.")
        return None, []

    try:
        # Query the data from the selected table
        ohlc_data = pd.read_sql(f"SELECT * FROM {table_name}", engine)

        # Get unique tickers
        tickers = ohlc_data['symbol'].unique()

        # Ensure 'datetime' is in the correct format
        ohlc_data['timestamp'] = pd.to_datetime(ohlc_data['timestamp'], errors='coerce', utc=True)  # Parse as UTC
        
        # Check for NaT values after conversion
        if ohlc_data['timestamp'].isnull().any():
            st.warning("Some datetime values could not be parsed and will be removed.")
            ohlc_data = ohlc_data.dropna(subset=['timestamp'])

        # Convert to local timezone if needed
        ohlc_data['timestamp'] = ohlc_data['timestamp'].dt.tz_convert('America/New_York')  # Change to your desired timezone

        # Format datetime as string for display
        ohlc_data['timestamp'] = ohlc_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Reorder columns based on the timeframe
        if timeframe == "Daily":
            ohlc_data['date'] = ohlc_data['timestamp'].str[:10]  # Extract the date part
            ohlc_data = ohlc_data[['date', 'symbol', 'close', 'open', 'high', 'low', 'trade_count', 'vwap']]
        else:
            ohlc_data = ohlc_data[['timestamp', 'symbol', 'close', 'open', 'high', 'low', 'trade_count', 'vwap']]

        return ohlc_data, tickers

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, []
   

def convert_now():
    # Get the current date and time
    now = datetime.now()

    # Get the day with the appropriate suffix (st, nd, rd, th)
    day = now.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    # Format the datetime object into the desired string format
    formatted_string = now.strftime(f"{day}{suffix} %b, %Y %I:%M %p")

    return formatted_string


def plot_ohlc_chart(ohlc_data, selected_ticker, selected_timeframe):
    ohlc_data_selected = ohlc_data[ohlc_data['symbol'] == selected_ticker]

    time_buttons = {
        "Hourly": [{'step': 'all', 'label': 'All'}, {'count': 1, 'step': 'hour', 'label': '1 hour'}],
        "Minute": [{'step': 'all', 'label': 'All'}, {'count': 30, 'step': 'minute', 'label': '30 Mins'}],
        "Daily": [{'step': 'all', 'label': 'All'}, 
                  {'count': 7, 'step': 'day', 'label': '7 Days'},
                  {'count': 15, 'step': 'day', 'label': '15 Days'},
                  {'count': 30, 'step': 'day', 'label': '30 Days'}]
    }

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        # x=ohlc_data_selected.index,
        x=ohlc_data_selected.iloc[:, 0],
        open=ohlc_data_selected['open'],
        high=ohlc_data_selected['high'],
        low=ohlc_data_selected['low'],
        close=ohlc_data_selected['close'],
        name='OHLC'
    ))

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_xaxes(visible=True, rangeselector={'buttons': time_buttons[selected_timeframe]})
    st.plotly_chart(fig, use_container_width=True)


def load_correlation_data():
    # Database connection parameters
    db_params = {
        'user': 'postgres',
        'password': 'nishant',
        'host': 'localhost',  # or your database host
        'port': '5432',       # default PostgreSQL port
        'database': 'pairs_trading'
    }

    # Create the database connection
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(connection_string)
    
    try:
        # Query the data from the selected table
        query = """
        WITH distinct_test_dates AS (
            SELECT COUNT(DISTINCT "TestDate") AS total_test_dates
            FROM co_integration_test
            ),
        valid_assets AS (
            SELECT cit."Asset 1", cit."Asset 2"
            FROM co_integration_test AS cit
            WHERE cit."Checked" = 'Yes'
            AND cit."ADF p-Value" < '0.05'
            GROUP BY cit."Asset 1", cit."Asset 2"
            HAVING COUNT(DISTINCT cit."TestDate") = (SELECT total_test_dates FROM distinct_test_dates)
            )
        SELECT cit."Asset 1" as "Asset 1",
        yf1.industry as "Asset 1 Industry",
        yf1.sector as "Asset 1 Sector",
        yf1.longName as "Asset 1 Long Name",
        cit."Asset 2" as "Asset 2",
        yf2.industry as "Asset 2 Industry",
        yf2.sector as "Asset 2 Sector",
        yf2.longName as "Asset 2 Long Name",
        cit."ADF p-Value", 
        cit."TestDate"
        FROM co_integration_test AS cit
        JOIN valid_assets va
        ON cit."Asset 1" = va."Asset 1" AND cit."Asset 2" = va."Asset 2"
        JOIN yahoo_finance_info AS yf1
        ON cit."Asset 1" = yf1.symbol
        JOIN yahoo_finance_info AS yf2
        ON cit."Asset 2" = yf2.symbol
        WHERE cit."Checked" = 'Yes'
        AND cit."ADF p-Value" < '0.05'
        AND yf1.industry = yf2.industry
        ORDER BY cit."ADF p-Value" DESC
        limit 10;
        """
        coint_data = pd.read_sql(query, engine)
        return coint_data
        
    except Exception as e:
        st.error(f"Error Loading data: {e}")
        return None
    
    
def load_yahoo_data():
    # Database connection parameters
    db_params = {
        'user': 'postgres',
        'password': 'nishant',
        'host': 'localhost',  # or your database host
        'port': '5432',       # default PostgreSQL port
        'database': 'pairs_trading'
    }

    # Create the database connection
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(connection_string)
    
    try:
        # Query the data from the selected table
        query = """select * from yahoo_finance_info"""
        
        yahoo_data = pd.read_sql(query, engine)
        return yahoo_data
    except Exception as e:
        st.error(f"Error Loading data: {e}")
        return None
        

