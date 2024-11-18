import os
import subprocess
import dotenv
from src.data.data_loader import AlpacaDataLoader
from src.utils.helper import print_with_timestamp
from src.data.cointegration import PairAnalysis
from src.data.database_connectivity import DatabaseConnection


def run_trading_analysis():
    dotenv_path = r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\config\.env"
    stock_file = r"src\config\stocks.txt"
    trading_system = AlpacaDataLoader(dotenv_path)
    trading_system.run(stock_file)  # Remove start_date parameter

def run_pair_analysis():
    db_params = {
        'user': 'postgres',
        'password': 'nishant',
        'host': 'localhost',
        'port': '5432',
        'database': 'pairs_trading'
    }
    db_connection = DatabaseConnection(db_params)
    pair_analysis = PairAnalysis(db_connection, table_name='alpaca_data_hourly')
    pair_analysis.analyze_pairs()


if __name__ == '__main__':
    try:
        print_with_timestamp("Starting the Alpaca Trading System...")
        run_trading_analysis()
        print_with_timestamp("Alpaca Trading System completed successfully.")

        print_with_timestamp("Starting Pair Analysis...")
        run_pair_analysis()
        print_with_timestamp("Pair Analysis completed successfully.")

    except Exception as e:
        print(e)