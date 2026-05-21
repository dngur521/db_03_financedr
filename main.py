import duckdb


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


# endregion


# =========================================================================
# region: Main
# =========================================================================
def main():
    con = duckdb.connect("data/finance.db")

    create_table(con)


if __name__ == "__main__":
    main()

# endregion
