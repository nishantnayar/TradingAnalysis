import os
import subprocess
import dotenv
from src.data.data_loader import AlpacaDataLoader
from src.utils.helper import print_with_timestamp


def run_trading_analysis():
    dotenv_path = r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\config\.env"
    stock_file = r"src\config\stocks.txt"
    trading_system = AlpacaDataLoader(dotenv_path)
    trading_system.run(stock_file)  # Remove start_date parameter


if __name__ == '__main__':
    try:
        print_with_timestamp("Starting the Alpaca Trading System...")
        run_trading_analysis()
        print_with_timestamp("Alpaca Trading System completed successfully.")

    except Exception as e:
        print(e)