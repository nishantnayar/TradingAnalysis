# import os
# import pickle
# import pandas as pd
# import psycopg2
# from dotenv import load_dotenv
# import alpaca
# from alpaca.trading.client import TradingClient
# from alpaca.data.historical.stock import StockHistoricalDataClient
# from alpaca.data.requests import StockBarsRequest
# from alpaca.data.timeframe import TimeFrame
# from psycopg2.extras import execute_values
# from datetime import datetime, timedelta
# from src.utils.helper import print_with_timestamp
#
#
# class AlpacaDataLoader:
#     def __init__(self, dotenv_path):
#         self.delimiter = '-' * 50
#         self.dotenv_path = dotenv_path
#         self.api_key = None
#         self.secret_key = None
#         self.account_number = None
#         self.trading_client = None
#         self.historical_client = None
#         self.db_params = {}
#
#     def log(self, message):
#         """Utility to print messages."""
#         print(self.delimiter)
#         print(message)
#         print(self.delimiter)
#
#     def load_env(self):
#         """Load environment variables from the specified .env file."""
#         self.log('Loading Environment variables')
#         load_dotenv(dotenv_path=self.dotenv_path)
#         self.api_key = os.getenv("APCA_API_KEY_ID")
#         self.secret_key = os.getenv("APCA_API_SECRET_KEY")
#         self.account_number = os.getenv("APCA_ACCOUNT_NUMBER")
#
#         # Load database parameters
#         self.db_params = {
#             'dbname': os.getenv('DB_NAME'),
#             'user': os.getenv('DB_USER'),
#             'password': os.getenv('DB_PASSWORD'),
#             'host': os.getenv('DB_HOST'),
#             'port': os.getenv('DB_PORT')
#         }
#
#     def check_package_version(self):
#         """Check if the Alpaca package version is compatible."""
#         print('\nChecking the package version\n')
#         print(f"We are using the Alpaca version {alpaca.__version__}")
#         try:
#             assert alpaca.__version__ >= '0.30.1', "Alpaca version must be at least 0.30.1"
#         except AssertionError as e:
#             raise Exception(f"Alpaca version requirement not met: {e}")
#
#     def connect_trading_client(self):
#         """Establish a connection to the Alpaca trading system."""
#         self.trading_client = TradingClient(api_key=self.api_key, secret_key=self.secret_key, paper=True)
#         acct = self.trading_client.get_account()
#
#         try:
#             assert acct.account_number == self.account_number, "Alpaca Account found"
#             self.log("Alpaca Account is matching. OK to proceed ahead")
#         except AssertionError as e:
#             raise Exception(f"Account number not found : {e}")
#
#     def retrieve_max_timestamp(self):
#         """Retrieve the maximum timestamp from the PostgreSQL database."""
#         conn = psycopg2.connect(**self.db_params)
#         cursor = conn.cursor()
#         cursor.execute("SELECT MAX(timestamp) FROM alpaca_data_daily;")
#         max_timestamp = cursor.fetchone()[0]
#         cursor.close()
#         conn.close()
#         return max_timestamp
#
#     def get_next_date(self):
#         """Determine the next date based on the maximum timestamp in the database."""
#         max_timestamp = self.retrieve_max_timestamp()
#         if max_timestamp is None:
#             # If there is no data in the database, start from a default date
#             return datetime(2024, 1, 1)  # Default start date
#         else:
#             # Increment the max timestamp by 1 day
#             return max_timestamp + timedelta(days=1)
#
#     def retrieve_historical_data(self, stock_symbols, start_date, timeframe):
#         """Retrieve historical stock data for the provided list of symbols."""
#         self.log(f"Retrieving historical data for {timeframe}")
#         self.historical_client = StockHistoricalDataClient(self.api_key, self.secret_key)
#         all_bars_data = []  # Create a separate list for each timeframe's data
#         for symbol in stock_symbols:
#             print(f"\nRetrieving historical data for {symbol} with {timeframe} timeframe...")
#             request_params = StockBarsRequest(
#                 symbol_or_symbols=symbol,
#                 timeframe=timeframe,
#                 start=start_date
#             )
#             try:
#                 bars = self.historical_client.get_stock_bars(request_params)
#                 bars_df = bars.df
#                 bars_df['symbol'] = symbol  # Add a column for the stock symbol
#                 all_bars_data.append(bars_df)
#             except Exception as e:
#                 print(f"Error retrieving historical data for {symbol}: {e}")
#
#         if all_bars_data:
#             all_bars_df = pd.concat(all_bars_data)
#             print(f"Final dataframe created with {len(all_bars_df)} records for {timeframe}")
#             return all_bars_df
#         else:
#             print("No data retrieved.")
#             return pd.DataFrame()
#
#     def clean_data(self, all_bars_df, timeframe):
#         """Clean the historical data by removing unnecessary columns and null values."""
#         self.log(f"Starting cleaning activities for {timeframe}")
#
#         # Remove 'symbol' from the index and reset it
#         try:
#             all_bars_df = all_bars_df.reset_index()
#             all_bars_df.drop(columns=['level_0'], inplace=True)
#             all_bars_df.rename(columns={'level_1': 'timestamp'}, inplace=True)
#             all_bars_df = all_bars_df[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']]
#             print(f"Removed symbol column from the index for {timeframe}.\n")
#         except Exception as e:
#             print(f"Error while removing symbol column for {timeframe}: {e}")
#
#         return all_bars_df
#
#     def save_data(self, all_bars_df, filepath):
#         """Save the cleaned data to a pickle file."""
#         self.log(f"Saving data to a pickle file at {filepath}")
#         with open(filepath, 'wb') as f:
#             pickle.dump(all_bars_df, f)
#         print(f"\nDataFrame successfully saved to {filepath}.\n")
#
#     def insert_ohlc_data(self, df):
#         """Insert OHLC data into PostgreSQL database."""
#         # Connect to the PostgreSQL database
#         conn = psycopg2.connect(**self.db_params)
#         cursor = conn.cursor()
#
#         # Define the insert SQL query
#         insert_query = """
#         INSERT INTO alpaca_data_daily (symbol, timestamp, open, high, low, close, volume, trade_count, vwap)
#         VALUES %s
#         ON CONFLICT (symbol, timestamp) DO NOTHING;
#         """
#
#         # Convert DataFrame to a list of tuples
#         records = df.to_records(index=False)
#         data_tuples = [tuple(row) for row in records]
#
#         # Use execute_values to bulk insert
#         execute_values(cursor, insert_query, data_tuples)
#
#         # Commit the transaction and close the connection
#         conn.commit()
#         cursor.close()
#         conn.close()
#         print_with_timestamp("Data inserted successfully.")
#
#     def run(self, stock_file):
#         """Main method to run the entire process for both timeframes."""
#         self.load_env()
#         self.check_package_version()
#         self.connect_trading_client()
#
#         # Load stock symbols from file
#         with open(stock_file, 'r') as file:
#             stock_symbols = [line.strip() for line in file if line.strip()]
#
#         # Get the next date based on max timestamp
#         start_date = self.get_next_date()
#         print(f"Starting data retrieval from: {start_date}")
#
#         # Run for TimeFrame.Day
#         all_bars_df_day = self.retrieve_historical_data(stock_symbols, start_date, TimeFrame.Day)
#         if not all_bars_df_day.empty:
#             cleaned_df_day = self.clean_data(all_bars_df_day, TimeFrame.Day)
#             # self.save_data(cleaned_df_day, r'src/data/pickle/historical_data_day.pkl')
#
#             # Save to PostgreSQL
#             self.insert_ohlc_data(cleaned_df_day)
#         else:
#             print("No data available for TimeFrame.Day to clean and save.")
#
#
# # Usage
# if __name__ == "__main__":
#     dotenv_path = dotenv.find_dotenv()
#     stock_file = r"src\config\stocks.txt"
#
#     trading_system = AlpacaDataLoader(dotenv_path)
#     trading_system.run(stock_file)


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

    def get_next_date(self):
        """Determine the next date based on the maximum timestamp in the daily database."""
        max_timestamp = self.retrieve_max_timestamp_daily()
        if max_timestamp is None:
            # If there is no data in the database, start from a default date
            return datetime(2024, 1, 1)  # Default start date
        else:
            # Increment the max timestamp by 1 day
            return max_timestamp + timedelta(days=1)

    def get_next_hour(self):
        """Determine the next hour based on the maximum timestamp in the hourly database."""
        max_timestamp = self.retrieve_max_timestamp_hourly()
        if max_timestamp is None:
            # If there is no data in the database, start from a default date
            return datetime(2024, 1, 1, 0, 0)  # Default start date with hour
        else:
            # Increment the max timestamp by 1 hour
            return max_timestamp + timedelta(hours=1)

    def retrieve_historical_data(self, stock_symbols, start_date, timeframe):
        """Retrieve historical stock data for the provided list of symbols."""
        self.log(f"Retrieving historical data for {timeframe}")
        self.historical_client = StockHistoricalDataClient(self.api_key, self.secret_key)
        all_bars_data = []  # Create a separate list for each timeframe's data
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
                bars_df['symbol'] = symbol  # Add a column for the stock symbol
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

    def save_data(self, all_bars_df, filepath):
        """Save the cleaned data to a pickle file."""
        self.log(f"Saving data to a pickle file at {filepath}")
        with open(filepath, 'wb') as f:
            pickle.dump(all_bars_df, f)
        print(f"\nDataFrame successfully saved to {filepath}.\n")

    def insert_ohlc_data(self, df, is_hourly=False):
        """Insert OHLC data into PostgreSQL database."""
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()

        # Determine the correct table based on the timeframe
        table_name = 'alpaca_data_hourly' if is_hourly else 'alpaca_data_daily'

        # Define the insert SQL query
        insert_query = f"""
        INSERT INTO {table_name} (symbol, timestamp, open, high, low, close, volume, trade_count, vwap)
        VALUES %s
        ON CONFLICT (symbol, timestamp) DO NOTHING;
        """

        # Convert DataFrame to a list of tuples
        records = df.to_records(index=False)
        data_tuples = [tuple(row) for row in records]

        # Use execute_values to bulk insert
        execute_values(cursor, insert_query, data_tuples)

        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        print_with_timestamp("Data inserted successfully.")

    def run(self, stock_file):
        """Main method to run the entire process for both timeframes."""
        self.load_env()
        self.check_package_version()
        self.connect_trading_client()

        # Load stock symbols from file
        with open(stock_file, 'r') as file:
            stock_symbols = [line.strip() for line in file if line.strip()]

        # Get the next date based on max timestamp for daily data
        start_date_daily = self.get_next_date()
        print(f"Starting daily data retrieval from: {start_date_daily}")

        # Run for TimeFrame.Day
        all_bars_df_day = self.retrieve_historical_data(stock_symbols, start_date_daily, TimeFrame.Day)
        if not all_bars_df_day.empty:
            cleaned_df_day = self.clean_data(all_bars_df_day, TimeFrame.Day)
            self.insert_ohlc_data(cleaned_df_day)  # Save to PostgreSQL
        else:
            print("No data available for TimeFrame.Day to clean and save.")

        # Get the next hour based on max timestamp for hourly data
        start_date_hourly = self.get_next_hour()
        print(f"Starting hourly data retrieval from: {start_date_hourly}")

        # Run for TimeFrame.Hour
        all_bars_df_hour = self.retrieve_historical_data(stock_symbols, start_date_hourly, TimeFrame.Hour)
        if not all_bars_df_hour.empty:
            cleaned_df_hour = self.clean_data(all_bars_df_hour, TimeFrame.Hour)
            self.insert_ohlc_data(cleaned_df_hour, is_hourly=True)  # Save to PostgreSQL
        else:
            print("No data available for TimeFrame.Hour to clean and save.")


# Usage
if __name__ == "__main__":
    dotenv_path = dotenv.find_dotenv()
    stock_file = r"src\config\stocks.txt"

    trading_system = AlpacaDataLoader(dotenv_path)
    trading_system.run(stock_file)
