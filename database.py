import sqlite3
import pandas as pd

DATABASE_NAME = "investment_platform.db"


# ----------------------------------
# Create Company Table
# ----------------------------------

def create_company_table():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            ticker TEXT,
            sector TEXT,
            country TEXT
        )
    """)

    connection.commit()
    connection.close()


# ----------------------------------
# Insert Companies
# ----------------------------------

def insert_companies_from_csv():

    connection = sqlite3.connect(DATABASE_NAME)

    dataframe = pd.read_csv("data/companies.csv")

    dataframe.to_sql(
        "companies",
        connection,
        if_exists="append",
        index=False
    )

    connection.close()


# ----------------------------------
# Get Companies
# ----------------------------------

def get_companies():

    connection = sqlite3.connect(DATABASE_NAME)

    data = pd.read_sql(
        "SELECT * FROM companies",
        connection
    )

    connection.close()

    # Remove Tata Motors from dropdown
    data = data[
        ~data["company_name"].str.contains(
            "Tata",
            case=False,
            na=False
        )
    ]

    return data


# ----------------------------------
# Company -> Ticker Mapping
# ----------------------------------

def get_company_ticker_mapping():

    connection = sqlite3.connect(DATABASE_NAME)

    data = pd.read_sql(
        "SELECT company_name, ticker FROM companies",
        connection
    )

    connection.close()

    # Remove Tata Motors
    data = data[
        ~data["company_name"].str.contains(
            "Tata",
            case=False,
            na=False
        )
    ]

    company_dict = dict(
        zip(
            data["company_name"],
            data["ticker"]
        )
    )

    return company_dict
