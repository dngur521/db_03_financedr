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
    add_all_holdings(con)


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
                {
                    "account_id": 4,
                    "account_name": "위탁계좌 (아주 아주 아주 아주 아주 공격형)",
                    "brokerage": "한국투자",
                },
            ]
        )
        repo.save_accounts(con, df)
    else:
        print(f"[INFO] 계좌 데이터 개수: {count}")


def get_accounts(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return repo.find_all_accounts(con)


# endregion


# =========================================================================
# region: holding
# =========================================================================
def add_all_holdings(con: duckdb.DuckDBPyConnection):
    count = repo.get_holdings_count(con)
    if count <= 0:
        df = pd.DataFrame(
            [
                {
                    "ticker": "005930",
                    "account_id": 3,
                    "quantity": 1,
                    "avg_buy_price": 59000,
                },
                {
                    "ticker": "0162Z0",
                    "account_id": 2,
                    "quantity": 10,
                    "avg_buy_price": 13500,
                },
                {
                    "ticker": "360750",
                    "account_id": 1,
                    "quantity": 5,
                    "avg_buy_price": 27000,
                },
                {
                    "ticker": "379810",
                    "account_id": 1,
                    "quantity": 5,
                    "avg_buy_price": 29415,
                },
            ]
        )
        repo.save_holdings(con, df)
    else:
        print(f"[INFO] 보유 데이터 개수: {count}")


def get_holdings(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return repo.find_all_holdings(con)


# endregion
