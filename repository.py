import duckdb
import pandas as pd


# =========================================================================
# region: DuckDB DDL
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


# endregion


# =========================================================================
# region: DuckDB asset
# =========================================================================
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
# region: DuckDB account
# =========================================================================
def get_accounts_count(con: duckdb.DuckDBPyConnection) -> int:
    """
    테이블의 Cardinality (tuple 개수) 반환
    """
    return con.execute("SELECT COUNT(*) FROM account").fetchone()[0]


def save_accounts(con: duckdb.DuckDBPyConnection, df: pd.DataFrame):
    """
    계좌 데이터 저장
    """
    print("[INFO] account 저장 시작")
    con.execute("INSERT OR IGNORE INTO account SELECT * FROM df")
    print("[INFO] account 저장 완료")


def find_all_accounts(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    계좌 검색
    """
    return con.execute("SELECT * FROM account ORDER BY account_id").df()


# endregion


# =========================================================================
# region: DuckDB holding
# =========================================================================
def get_holdings_count(con: duckdb.DuckDBPyConnection) -> int:
    """
    테이블의 Cardinality (tuple 개수) 반환
    """
    return con.execute("SELECT COUNT(*) FROM holding").fetchone()[0]


def save_holdings(con: duckdb.DuckDBPyConnection, df: pd.DataFrame):
    """
    보유 데이터 저장
    """
    print("[INFO] holding 저장 시작")
    con.execute("INSERT OR IGNORE INTO holding SELECT * FROM df")
    print("[INFO] holding 저장 완료")


def find_all_holdings(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    모든 보유 데이터 검색
    """
    return con.execute("SELECT * FROM holding ORDER BY quantity DESC").df()


# endregion


# =========================================================================
# region: DuckDB join
# =========================================================================
def find_all_joins(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    모든 종목-보유-계좌 join 데이터 검색
    """
    return con.execute("""
        SELECT name, s.ticker, account_name AS account, brokerage, quantity, avg_buy_price
        FROM account a
        LEFT JOIN holding h ON a.account_id = h.account_id
        LEFT JOIN asset s ON h.ticker = s.ticker
        ORDER BY a.account_id, quantity DESC
    """).df()


# endregion
