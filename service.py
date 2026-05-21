import duckdb
import pandas as pd

import data_source as data
import repository as repo


# =========================================================================
# region: Service (Business Logic)
# =========================================================================
def connect_database(path: str) -> duckdb.DuckDBPyConnection:
    return duckdb.connect("data/finance.db")


def initialize(con: duckdb.DuckDBPyConnection):
    repo.create_table(con)
    add_all_assets(con)


def add_all_assets(con: duckdb.DuckDBPyConnection):
    count = repo.get_assets_count(con)
    if count <= 0:
        df = data.fetch_asset_list()
        repo.save_assets(con, df)
    else:
        print(f"[INFO] 종목 데이터 개수: {count}")


def get_assets(con: duckdb.DuckDBPyConnection, keyword: str) -> pd.DataFrame:
    return repo.find_assets_by_keyword(con, keyword)


# endregion
