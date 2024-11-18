# src/database/database_connection.py
import pandas as pd
from sqlalchemy import create_engine
from psycopg2 import connect
from psycopg2.extras import execute_values


class DatabaseConnection:
    def __init__(self, db_params):
        self.db_params = db_params
        self.connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        self.engine = create_engine(self.connection_string)

    def load_data(self, table_name):
        try:
            data = pd.read_sql(f"SELECT * FROM {table_name}", self.engine)
            return data
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None

    def insert_data(self, table_name, data):
        insert_query = f"""
        INSERT INTO {table_name} ("Asset 1", "Asset 2", "Checked", "ADF Test Statistic", "ADF p-Value", "TestDate")
        VALUES %s ON CONFLICT ("Asset 1", "Asset 2", "TestDate") DO NOTHING;
        """
        data_tuples = [tuple(row) for row in data.to_records(index=False)]
        try:
            with connect(
                    user=self.db_params['user'],
                    password=self.db_params['password'],
                    host=self.db_params['host'],
                    port=self.db_params['port'],
                    database=self.db_params['database']
            ) as conn:
                with conn.cursor() as cursor:
                    execute_values(cursor, insert_query, data_tuples)
                    conn.commit()
                    print("Data inserted successfully.")
        except Exception as e:
            print(f"Error inserting data: {e}")
