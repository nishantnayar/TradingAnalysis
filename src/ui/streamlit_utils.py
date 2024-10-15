import pandas as pd
import streamlit as st
from datetime import datetime


@st.cache_data(show_spinner=True)
def load_ohlc_data(timeframe):
    data_paths = {
        "Minute": r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data\pickle\historical_data_minute.pkl",
        "Hourly": r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data\pickle\historical_data_hour.pkl",
        "Daily": r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data\pickle\historical_data_day.pkl"
    }

    try:
        ohlc_data = pd.read_pickle(data_paths[timeframe])
        tickers = ohlc_data['symbol'].unique()

        # reset Index
        ohlc_data = ohlc_data.reset_index()

        # drop one column
        ohlc_data = ohlc_data.drop(columns=['level_0'])

        # rename column level_1
        ohlc_data = ohlc_data.rename(columns={'level_1': 'datetime'})

        if timeframe == "Daily":
            ohlc_data['date'] = pd.to_datetime(ohlc_data['datetime']).dt.strftime('%Y-%m-%d')
            ohlc_data = ohlc_data.drop(columns=['datetime'])

        # reorder columns
        if timeframe == "Daily":
            ohlc_data = ohlc_data[['date', 'symbol', 'close', 'open', 'high', 'low', 'trade_count', 'vwap']]
        else:
            ohlc_data = ohlc_data[['datetime', 'symbol', 'close', 'open', 'high', 'low', 'trade_count', 'vwap']]

        return ohlc_data, tickers
    except FileNotFoundError:
        st.warning("Please download the pickled data first")
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
