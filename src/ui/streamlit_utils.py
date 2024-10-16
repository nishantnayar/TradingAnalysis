import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go


@st.cache_data(show_spinner=True,ttl=3600, max_entries=5)
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


def plot_ohlc_chart(ohlc_data, selected_ticker, selected_timeframe):
    ohlc_data_selected = ohlc_data[ohlc_data['symbol'] == selected_ticker]

    time_buttons = {
        "Hourly": [{'step': 'all', 'label': 'All'}, {'count': 1, 'step': 'hour', 'label': '1 hour'}],
        "Minute": [{'step': 'all', 'label': 'All'}, {'count': 30, 'step': 'minute', 'label': '30 Mins'}],
        "Daily": [{'step': 'all', 'label': 'All'}, {'count': 30, 'step': 'day', 'label': '30 Days'}]
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

    #TODO: fix caching
