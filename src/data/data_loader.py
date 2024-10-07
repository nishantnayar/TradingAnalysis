import dotenv
import os
from dotenv import load_dotenv
import alpaca
import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pickle


class AlpacaDataLoader:
    def __init__(self, dotenv_path):
        self.delimiter = '-' * 50
        self.dotenv_path = dotenv_path
        self.api_key = None
        self.secret_key = None
        self.account_number = None
        self.trading_client = None
        self.historical_client = None
        self.all_bars_data = []

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

    def retrieve_historical_data(self, stock_symbols, start_date, timeframe):
        """Retrieve historical stock data for the provided list of symbols."""
        self.log(f"Retrieving historical data for {timeframe}")
        self.historical_client = StockHistoricalDataClient(self.api_key, self.secret_key)
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
                self.all_bars_data.append(bars_df)
            except Exception as e:
                print(f"Error retrieving historical data for {symbol}: {e}")

        if self.all_bars_data:
            all_bars_df = pd.concat(self.all_bars_data)
            print(f"Final dataframe created with {len(all_bars_df)} records")
            return all_bars_df
        else:
            print("No data retrieved.")
            return pd.DataFrame()

    def clean_data(self, all_bars_df, timeframe):
        """Clean the historical data by removing unnecessary columns and null values."""
        self.log("Starting cleaning activities")

        # Remove 'symbol' from the index and reset it
        try:
            all_bars_df = all_bars_df.reset_index(level='symbol', drop=True)
            print(f"Removed symbol column from the index.\n")
        except Exception as e:
            print(f"Error while removing symbol column")

        return all_bars_df

    def save_data(self, all_bars_df, filepath):
        """Save the cleaned data to a pickle file."""
        self.log(f"Saving data to a pickle file at {filepath}")
        with open(filepath, 'wb') as f:
            pickle.dump(all_bars_df, f)
        print(f"\nDataFrame successfully saved to {filepath}.\n")
        f.close()

    def run(self, stock_file, start_date):
        """Main method to run the entire process for both timeframes."""
        self.load_env()
        self.check_package_version()
        self.connect_trading_client()

        # Load stock symbols from file
        with open(stock_file, 'r') as file:
            stock_symbols = [line.strip() for line in file if line.strip()]

        # Run for TimeFrame.Minute
        all_bars_df_minute = self.retrieve_historical_data(stock_symbols, start_date, TimeFrame.Minute)
        if not all_bars_df_minute.empty:
            cleaned_df_minute = self.clean_data(all_bars_df_minute, TimeFrame.Minute)
            self.save_data(cleaned_df_minute, r'src/data/pickle/historical_data_minute.pkl')
        else:
            print("No data available for TimeFrame.Hour to clean and save.")

        # Run for TimeFrame.Hour
        all_bars_df_hour = self.retrieve_historical_data(stock_symbols, start_date, TimeFrame.Hour)
        if not all_bars_df_hour.empty:
            cleaned_df_hour = self.clean_data(all_bars_df_hour, TimeFrame.Hour)
            self.save_data(cleaned_df_hour, r'src/data/pickle/historical_data_hour.pkl')
        else:
            print("No data available for TimeFrame.Hour to clean and save.")

        # # Run for TimeFrame.Day
        # all_bars_df_day = self.retrieve_historical_data(stock_symbols, start_date, TimeFrame.Day)
        # if not all_bars_df_day.empty:
        #     cleaned_df_day = self.clean_data(all_bars_df_day, TimeFrame.Day)
        #     self.save_data(cleaned_df_day, r'src/data/pickle/historical_data_day.pkl')
        # else:
        #     print("No data available for TimeFrame.Day to clean and save.")


# Usage
if __name__ == "__main__":
    dotenv_path = dotenv.find_dotenv()
    stock_file = r"src\config\stocks.txt"
    start_date = "2024-10-01 00:00:00"

    trading_system = AlpacaDataLoader(dotenv_path)
    trading_system.run(stock_file, start_date)
