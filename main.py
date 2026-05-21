import duckdb
import FinanceDataReader as fdr
import flet as ft
import pandas as pd


# =========================================================================
# region: DuckDB Database Operations
# =========================================================================
def create_table(con: duckdb.DuckDBPyConnection):
    """
    DuckDB 테이블 생성
    """
    print("[INFO] DuckDB 테이블 생성 시작")

    query = """
        -- 1. account 테이블 생성
        CREATE TABLE IF NOT EXISTS account
        (
            account_id   INTEGER NOT NULL PRIMARY KEY, -- [후보키] 계좌 대리 키 (Surrogate Key)
            account_name VARCHAR UNIQUE,               -- [후보키] 계좌 이름 (예, ISA, 연금저축)
            brokerage    VARCHAR                       -- 증권사 (예, 한국투자증권, 미래에셋증권)
        );

        -- 2. asset 테이블 생성
        CREATE TABLE IF NOT EXISTS asset
        (
            ticker VARCHAR NOT NULL PRIMARY KEY, -- 티커
            name   VARCHAR,                      -- 종목 이름
            type   VARCHAR,                      -- 주식 또는 ETF
            country VARCHAR                      -- 국가
        );

        -- 3. daily_price 테이블 생성
        CREATE TABLE IF NOT EXISTS daily_price
        (
            ticker VARCHAR NOT NULL, -- 티커
            date   DATE    NOT NULL, -- 날짜
            open   DOUBLE,           -- 시작가
            high   DOUBLE,           -- 최고가
            low    DOUBLE,           -- 최저가
            close  DOUBLE,           -- 종가
            volume BIGINT,           -- 거래량
            PRIMARY KEY (ticker, date),
            FOREIGN KEY (ticker) REFERENCES asset (ticker)
        );

        -- 4. holding 테이블 생성
        CREATE TABLE IF NOT EXISTS holding
        (
            ticker        VARCHAR NOT NULL, -- 티커
            account_id    INTEGER NOT NULL, -- 계좌 대리 키
            quantity      INTEGER,          -- 보유 주식 수
            avg_buy_price DOUBLE,           -- 매입 평균가
            PRIMARY KEY (ticker, account_id),
            FOREIGN KEY (ticker) REFERENCES asset (ticker),
            FOREIGN KEY (account_id) REFERENCES account (account_id)
        );
    """
    con.execute(query)

    print("[INFO] DuckDB 테이블 생성 완료")


def get_assets_count(con: duckdb.DuckDBPyConnection) -> int:
    """
    테이블의 Cardinality (tuple 개수) 반환
    """
    return con.execute("SELECT COUNT(*) FROM asset").fetchone()[0]


def save_assets(con: duckdb.DuckDBPyConnection, df: pd.DataFrame):
    """
    주식 및 ETF 저장
    """
    print("[INFO] asset 저장 시작")
    con.execute("INSERT OR IGNORE INTO asset SELECT * FROM df")
    print("[INFO] asset 저장 완료")


def find_assets_by_keyword(
    con: duckdb.DuckDBPyConnection, keyword: str
) -> pd.DataFrame:
    """
    주식 및 ETF 검색. keyword 없으면 전체 결과 반환
    """
    # strip() 함수는 양쪽 공백 제거
    # 빈 문자열("")은 False이므로, not ""은 True
    if not keyword or not keyword.strip():
        return con.execute("""
            SELECT * 
            FROM asset
            ORDER BY country, name
            LIMIT 200
        """).df()

    query = """
        SELECT * FROM asset 
        WHERE name ILIKE ?
        OR ticker ILIKE ?
        LIMIT 200
    """
    search_str = f"%{keyword}%"
    return con.execute(
        query,
        [
            search_str,
            search_str,
        ],
    ).df()


# endregion


# =========================================================================
# region: Finance Data Reader
# =========================================================================
def fetch_asset_list() -> pd.DataFrame:
    """
    asset (주식 및 ETF) 리스트 얻어옴
    """
    print("[INFO] FDR asset (주식 및 ETF) 리스트 가져오기 시작")

    results = []

    # 한국 주식 (KOSPI, KOSDAQ, KONEX)
    # 컬럼명이 Code임(나머지는 Symbol)
    kr_stocks = fdr.StockListing("KRX")[["Code", "Name"]]
    kr_stocks["country"] = "KR"
    kr_stocks["type"] = "Stock"

    # 순서 변경
    kr_stocks = kr_stocks[["Code", "Name", "type", "country"]]
    # 컬럼명 변경 (DB의 asset 테이블과 맞춤)
    kr_stocks.columns = ["ticker", "name", "type", "country"]

    results.append(kr_stocks)

    markets = [
        ("ETF/KR", "KR", "ETF"),
        ("NASDAQ", "US", "Stock"),
        ("NYSE", "US", "Stock"),
        ("ETF/US", "US", "ETF"),
    ]

    for market, country, type in markets:
        print(f">>> FDR asset ({country}, {market}, {type}) 가져오기 시작 ")

        df = fdr.StockListing(market)[["Symbol", "Name"]]
        df["country"] = country
        df["type"] = type

        # 순서 변경
        df = df[["country", "Symbol", "Name", "type"]]
        # 컬럼명 변경 (DB의 asset 테이블과 맞춤)
        df.columns = ["country", "ticker", "name", "type"]

        results.append(df)

    print("[INFO] FDR asset (주식 및 ETF) 리스트 가져오기 완료")

    # 모든 데이터 병합
    df_assets = pd.concat(results, ignore_index=True)
    # print(df_assets.head())
    return df_assets


# endregion


# =========================================================================
# region: Service (Business Logic)
# =========================================================================
def add_all_assets(con: duckdb.DuckDBPyConnection):
    count = get_assets_count(con)
    if count <= 0:
        df = fetch_asset_list()
        save_assets(con, df)
    else:
        print(f"[INFO] 종목 데이터 개수: {count}")


# endregion


# =========================================================================
# region: Main
# =========================================================================
def main(page: ft.Page):
    # region [Page Setup]
    page.title = "Finance Database"
    page.padding = 16
    page.window.width = 700
    page.window.height = 500
    page.scroll = ft.ScrollMode.ADAPTIVE
    # endregion

    con = duckdb.connect("data/finance.db")

    create_table(con)
    add_all_assets(con)

    # df = find_assets_by_keyword(con, None)
    df = find_assets_by_keyword(con, "하이닉스")

    table_assets = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(str.upper(col))) for col in df.columns],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(value))) for value in row])
            for row in df.values
        ],
    )

    page.add(
        table_assets,
    )


if __name__ == "__main__":
    ft.run(main)

# endregion
