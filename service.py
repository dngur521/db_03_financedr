from datetime import timedelta

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
    add_all_prices(con)


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


# =========================================================================
# region: join
# =========================================================================
def get_joined_data(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return repo.find_all_joins(con)


# endregion


# =========================================================================
# region: price
# =========================================================================
def add_all_prices(con: duckdb.DuckDBPyConnection):
    today = pd.Timestamp.today()
    last_business_day = (
        today - pd.offsets.BDay(0 if today.dayofweek < 5 else 1)
    ).date()

    latest_date = repo.find_latest_price_date(con)
    yesterday = last_business_day - timedelta(days=1)
    print(f"[INFO] DB 최신 날짜: {latest_date}, 직전 영업일: {yesterday}")

    if not latest_date or latest_date < yesterday:
        one_year_ago = last_business_day - pd.DateOffset(years=1)

        # 시작 날짜 (None이면 1년 전, 값이 있으면 latest_date 다음날부터)
        start_date = (
            one_year_ago if not latest_date else latest_date + timedelta(days=1)
        )

        print(f"[INFO] {start_date}부터 {yesterday}까지의 시세 데이터 수집 시작")
        tickers = repo.find_all_holdings(con)["ticker"].unique()

        for ticker in tickers:
            df = data.fetch_price_data(ticker, start_date, yesterday)
            repo.save_prices(con, ticker, df)

        print("[INFO] 시세 데이터 수집 완료")
    else:
        print(f"[INFO] 최신 시세 데이터 확인 완료 (최신 날짜: {latest_date})")


def get_prices(con: duckdb.DuckDBPyConnection, ticker: str) -> pd.DataFrame:
    """
    ticker의 최근 1년간 시세 데이터를 DB로부터 얻어옴
    """
    today = pd.Timestamp.today()
    last_business_day = (
        today - pd.offsets.BDay(0 if today.dayofweek < 5 else 1)
    ).date()
    one_year_ago = (last_business_day - pd.DateOffset(years=1)).date()

    return repo.find_prices_by_date(con, ticker, one_year_ago, last_business_day)


# endregion
