import pandas as pd
import streamlit as st


def load_ohlc_data(timeframe):
    data_paths = {
        "Minute": r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data\pickle\historical_data_minute.pkl",
        "Hourly": r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data\pickle\historical_data_hour.pkl",
        "Daily": r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data\pickle\historical_data_day.pkl"
    }

    try:
        ohlc_data = pd.read_pickle(data_paths[timeframe])
        tickers = ohlc_data['symbol'].unique()
        return ohlc_data, tickers
    except FileNotFoundError:
        st.warning("Please download the pickled data first")
        return None, []