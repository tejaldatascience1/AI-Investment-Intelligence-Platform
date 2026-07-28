import sqlite3
import pandas as pd


DATABASE_NAME = "investment_platform.db"


def create_company_table():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS companies
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            ticker TEXT,
            sector TEXT,
            country TEXT
        )
        """
    )

    connection.commit()

    connection.close()



def insert_companies_from_csv():

    connection = sqlite3.connect(DATABASE_NAME)

    dataframe = pd.read_csv(
        "data/companies.csv"
    )

    dataframe.to_sql(
        "companies",
        connection,
        if_exists="append",
        index=False
    )

    connection.close()



def get_companies():

    connection = sqlite3.connect(DATABASE_NAME)

    data = pd.read_sql(
        "SELECT * FROM companies",
        connection
    )

    connection.close()

    data = data[data["ticker"] != "TATAMOTORS.NS"]

return data



def get_company_ticker_mapping():

    connection = sqlite3.connect(DATABASE_NAME)

    data = pd.read_sql(
        "SELECT company_name, ticker FROM companies",
        connection
    )

    connection.close()


    company_dict = dict(
        zip(
            data["company_name"],
            data["ticker"]
        )
    )

    return company_dict
