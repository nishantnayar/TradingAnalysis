import os
import pickle
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import alpaca
from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from src.utils.helper import print_with_timestamp


class AlpacaDataLoader:
    def __init__(self, dotenv_path):
        self.delimiter = '-' * 50
        self.dotenv_path = dotenv_path
        self.api_key = None
        self.secret_key = None
        self.account_number = None
        self.trading_client = None
        self.historical_client = None
        self.db_params = {}

    def log(self, message):
        """Utility to print messages."""
        print(self.delimiter)
        print(message)
        print(self.delimiter)

    def load_env(self):
        """Load environment variables from the specified .env file."""
        self.log('Loading Environment variables')
        load_dotenv(dotenv_path=self.dotenv_path)
        self.api_key = os.getenv("APCA_API_KEY_ID")
        self.secret_key = os.getenv("APCA_API_SECRET_KEY")
        self.account_number = os.getenv("APCA_ACCOUNT_NUMBER")

        # Load database parameters
        self.db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }

    def check_package_version(self):
        """Check if the Alpaca package version is compatible."""
        print('\nChecking the package version\n')
        print(f"We are using the Alpaca version {alpaca.__version__}")
        try:
            assert alpaca.__version__ >= '0.30.1', "Alpaca version must be at least 0.30.1"
        except AssertionError as e:
            raise Exception(f"Alpaca version requirement not met: {e}")

    def connect_trading_client(self):
        """Establish a connection to the Alpaca trading system."""
        self.trading_client = TradingClient(api_key=self.api_key, secret_key=self.secret_key, paper=True)
        acct = self.trading_client.get_account()

        try:
            assert acct.account_number == self.account_number, "Alpaca Account found"
            self.log("Alpaca Account is matching. OK to proceed ahead")
        except AssertionError as e:
            raise Exception(f"Account number not found : {e}")

    def retrieve_max_timestamp_daily(self):
        """Retrieve the maximum timestamp from the daily PostgreSQL database."""
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM alpaca_data_daily;")
        max_timestamp = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return max_timestamp

    def retrieve_max_timestamp_hourly(self):
        """Retrieve the maximum timestamp from the hourly PostgreSQL database."""
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM alpaca_data_hourly;")
        max_timestamp = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return max_timestamp

    def retrieve_max_timestamp_minute(self):
        """Retrieve the maximum timestamp from the minute PostgreSQL database."""
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM alpaca_data_min;")
        max_timestamp = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return max_timestamp

    def get_next_date(self):
        """Determine the next date based on the maximum timestamp in the daily database."""
        max_timestamp = self.retrieve_max_timestamp_daily()
        if max_timestamp is None:
            return datetime(2024, 1, 1)
        else:
            return max_timestamp + timedelta(days=1)

    def get_next_hour(self):
        """Determine the next hour based on the maximum timestamp in the hourly database."""
        max_timestamp = self.retrieve_max_timestamp_hourly()
        if max_timestamp is None:
            return datetime(2024, 1, 1, 0, 0)
        else:
            return max_timestamp + timedelta(hours=1)

    def get_next_minute(self):
        """Determine the next minute based on the maximum timestamp in the minute database."""
        max_timestamp = self.retrieve_max_timestamp_minute()
        if max_timestamp is None:
            return datetime(2024, 11, 1, 0, 0)
        else:
            return max_timestamp + timedelta(minutes=1)

    def retrieve_historical_data(self, stock_symbols, start_date, timeframe):
        """Retrieve historical stock data for the provided list of symbols."""
        self.log(f"Retrieving historical data for {timeframe}")
        self.historical_client = StockHistoricalDataClient(self.api_key, self.secret_key)
        all_bars_data = []
        for symbol in stock_symbols:
            print(f"\nRetrieving historical data for {symbol} with {timeframe} timeframe...")
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start_date
            )
            try:
                bars = self.historical_client.get_stock_bars(request_params)
                bars_df = bars.df
                bars_df['symbol'] = symbol
                all_bars_data.append(bars_df)
            except Exception as e:
                print(f"Error retrieving historical data for {symbol}: {e}")

        if all_bars_data:
            all_bars_df = pd.concat(all_bars_data)
            print(f"Final dataframe created with {len(all_bars_df)} records for {timeframe}")
            return all_bars_df
        else:
            print("No data retrieved.")
            return pd.DataFrame()

    def clean_data(self, all_bars_df, timeframe):
        """Clean the historical data by removing unnecessary columns and null values."""
        self.log(f"Starting cleaning activities for {timeframe}")

        # Remove 'symbol' from the index and reset it
        try:
            all_bars_df = all_bars_df.reset_index()
            all_bars_df.drop(columns=['level_0'], inplace=True)
            all_bars_df.rename(columns={'level_1': 'timestamp'}, inplace=True)
            all_bars_df = all_bars_df[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']]
            print(f"Removed symbol column from the index for {timeframe}.\n")
        except Exception as e:
            print(f"Error while removing symbol column for {timeframe}: {e}")

        return all_bars_df

    def insert_ohlc_data(self, df, is_hourly=False, is_minute=False):
        """Insert OHLC data into PostgreSQL database."""
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()

        table_name = 'alpaca_data_min' if is_minute else 'alpaca_data_hourly' if is_hourly else 'alpaca_data_daily'

        insert_query = f"""
        INSERT INTO {table_name} (symbol, timestamp, open, high, low, close, volume, trade_count, vwap)
        VALUES %s
        ON CONFLICT (symbol, timestamp) DO NOTHING;
        """

        records = df.to_records(index=False)
        data_tuples = [tuple(row) for row in records]
        execute_values(cursor, insert_query, data_tuples)

        conn.commit()
        cursor.close()
        conn.close()
        print_with_timestamp(f"Data inserted successfully into {table_name}.")

    def run(self, stock_file):
        """Main method to run the entire process for daily, hourly, and minute timeframes."""
        self.load_env()
        self.check_package_version()
        self.connect_trading_client()

        with open(stock_file, 'r') as file:
            stock_symbols = [line.strip() for line in file if line.strip()]

        # Daily data
        start_date_daily = self.get_next_date()
        print(f"Starting daily data retrieval from: {start_date_daily}")
        all_bars_df_day = self.retrieve_historical_data(stock_symbols, start_date_daily, TimeFrame.Day)
        if not all_bars_df_day.empty:
            cleaned_df_day = self.clean_data(all_bars_df_day, TimeFrame.Day)
            self.insert_ohlc_data(cleaned_df_day)
        else:
            print("No data available for TimeFrame.Day to clean and save.")

        # Hourly data
        start_date_hourly = self.get_next_hour()
        print(f"Starting hourly data retrieval from: {start_date_hourly}")
        all_bars_df_hour = self.retrieve_historical_data(stock_symbols, start_date_hourly, TimeFrame.Hour)
        if not all_bars_df_hour.empty:
            cleaned_df_hour = self.clean_data(all_bars_df_hour, TimeFrame.Hour)
            self.insert_ohlc_data(cleaned_df_hour, is_hourly=True)
        else:
            print("No data available for TimeFrame.Hour to clean and save.")

        # Minute data
        start_date_minute = self.get_next_minute()
        print(f"Starting minute data retrieval from: {start_date_minute}")
        all_bars_df_minute = self.retrieve_historical_data(stock_symbols, start_date_minute, TimeFrame.Minute)
        if not all_bars_df_minute.empty:
            cleaned_df_minute = self.clean_data(all_bars_df_minute, TimeFrame.Minute)
            self.insert_ohlc_data(cleaned_df_minute, is_minute=True)
        else:
            print("No data available for TimeFrame.Minute to clean and save.")

# Usage
if __name__ == "__main__":
    dotenv_path = dotenv.find_dotenv()
    stock_file = r"src\config\stocks.txt"

    trading_system = AlpacaDataLoader(dotenv_path)
    trading_system.run(stock_file)
