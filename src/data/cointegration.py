# src/analysis/pair_analysis.py
import pandas as pd
import numpy as np
from itertools import combinations
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from datetime import datetime


class PairAnalysis:
    def __init__(self, db_connection, table_name, common_column='timestamp'):
        self.db_connection = db_connection
        self.table_name = table_name
        self.common_column = common_column
        # Add "Test Date" column for storing the current date of the test
        self.co_integration_test_df = pd.DataFrame(
            columns=['Asset 1', 'Asset 2', 'Checked', 'ADF Test Statistic', 'ADF p-Value', 'TestDate'])

    def analyze_pairs(self):
        data = self.db_connection.load_data(self.table_name)
        if data is None:
            return

        tickers = data['symbol'].unique()
        pair_counter = 1

        # Example hardcoded tickers for testing, can be removed
        # tickers = ['DVA', 'MMC', 'MKC', 'ALLE']

        for pair in combinations(tickers, 2):
            asset_1, asset_2 = pair
            print(f"Analyzing combination {pair_counter}: {asset_1}, {asset_2}")

            filtered_df_1 = data[data['symbol'] == asset_1]
            filtered_df_2 = data[data['symbol'] == asset_2]
            # Get the current date
            current_date = datetime.now().strftime('%Y-%m-%d')

            if abs(len(filtered_df_1) - len(filtered_df_2)) / min(len(filtered_df_1), len(filtered_df_2)) * 100 <= 5:
                self._run_cointegration_test(filtered_df_1, filtered_df_2, asset_1, asset_2)
            else:
                print(f"Skipping pair {asset_1}, {asset_2} due to length difference.")
                # Adding current_date to the DataFrame for skipped pairs as well
                self.co_integration_test_df = pd.concat([self.co_integration_test_df,
                                                         pd.DataFrame([[asset_1, asset_2, 'No', 0, 0, current_date]],
                                                                      columns=self.co_integration_test_df.columns)],
                                                        ignore_index=True)

            pair_counter += 1

        self.db_connection.insert_data('co_integration_test', self.co_integration_test_df)

    def _run_cointegration_test(self, df1, df2, asset_1, asset_2):
        df1 = df1[df1[self.common_column].isin(df2[self.common_column])]
        df2 = df2[df2[self.common_column].isin(df1[self.common_column])]

        df1 = df1.copy()
        df2 = df2.copy()
        df1['log_close'] = np.log(df1['close'])
        df2['log_close'] = np.log(df2['close'])

        X = df1['log_close'].reset_index(drop=True)
        Y = df2['log_close'].reset_index(drop=True)

        model = sm.OLS(Y, sm.add_constant(X)).fit()
        residuals = model.resid
        adf_test = adfuller(residuals)
        p_value = adf_test[1]

        # Get the current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Add the current date to the new row
        new_row = pd.DataFrame([[asset_1, asset_2, 'Yes', adf_test[0], p_value, current_date]],
                               columns=self.co_integration_test_df.columns)
        # print(new_row)
        self.co_integration_test_df = pd.concat([self.co_integration_test_df, new_row], ignore_index=True)

        print(f"ADF Test Statistic: {adf_test[0]}, p-value: {p_value}, Test Date: {current_date}")
