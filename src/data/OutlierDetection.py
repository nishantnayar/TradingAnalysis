import pickle
import pandas as pd


def read_pickle_file(file_path):
    """Reads a pickle file and returns its contents.

    Args:
        file_path (str): The path to the pickle file.

    Returns:
        The contents of the pickle file.
    """

    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: Pickle file '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading pickle file: {e}")
        return None


# Example usage:
file_path = r"C:\Users\nisha\Documents\PythonProjects\TradingAnalysis\src\data\pickle\historical_data_day.pkl"
data = read_pickle_file(file_path)
symbol = 'MU'
data = data[data['symbol'] == symbol]

if data is not None:
    # Process the data
    print(f'Number of rows in dataset is {len(data)}')
else:
    print("Failed to read the pickle file.")

data=data.reset_index()
data['date'] = pd.to_datetime(data['timestamp']).dt.strftime('%Y-%m-%d')
data = data[['date', 'close']]
data['date'] = pd.to_datetime(data['date'])
print(data.dtypes)
