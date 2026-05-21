import duckdb
import pandas as pd

import data_source as data
import repository as repo


# =========================================================================
# region: Database
# =========================================================================
def connect_database(path: str) -> duckdb.DuckDBPyConnection:
    return duckdb.connect("data/finance.db")


def initialize(con: duckdb.DuckDBPyConnection):
    repo.create_table(con)
    add_all_assets(con)
    add_all_accounts(con)


# endregion


# =========================================================================
# region: asset
# =========================================================================
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


# =========================================================================
# region: account
# =========================================================================
def add_all_accounts(con: duckdb.DuckDBPyConnection):
    count = repo.get_accounts_count(con)
    if count <= 0:
        df = pd.DataFrame(
            [
                {"account_id": 1, "account_name": "ISA", "brokerage": "키움증권"},
                {
                    "account_id": 2,
                    "account_name": "연금저축펀드",
                    "brokerage": "삼성증권",
                },
                {"account_id": 3, "account_name": "위탁계좌", "brokerage": "미래에셋"},
            ]
        )
        repo.save_accounts(con, df)
    else:
        print(f"[INFO] 계좌 데이터 개수: {count}")


def get_accounts(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return repo.find_all_accounts(con)


# endregion
