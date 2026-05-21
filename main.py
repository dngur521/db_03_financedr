import duckdb
import FinanceDataReader as fdr
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

    # 1. 한국 주식 (KRX) 안전하게 가져오기
    try:
        kr_stocks = fdr.StockListing("KRX")[["Code", "Name"]]
        kr_stocks["country"] = "KR"
        kr_stocks["type"] = "Stock"
        kr_stocks = kr_stocks[["Code", "Name", "type", "country"]]
        kr_stocks.columns = ["ticker", "name", "type", "country"]
        results.append(kr_stocks)
    except Exception as e:
        print(f"[WARN] KRX 데이터를 가져오는데 실패했습니다: {e}")

    # 2. 나머지 시장 루프
    markets = [
        ("ETF/KR", "KR", "ETF"),
        ("NASDAQ", "US", "Stock"),
        ("NYSE", "US", "Stock"),
        # ("ETF/US", "US", "ETF"),
        # 현재 오류 남
    ]

    for market, country, type in markets:
        print(f">>> FDR asset ({country}, {market}, {type}) 가져오기 시작 ")

        try:
            # 외부 API 호출 시 에러가 나거나 빈 데이터를 줄 때를 대비해 예외 처리
            df = fdr.StockListing(market)

            if df is None or df.empty:
                print(f"[WARN] {market} 데이터가 비어 있습니다. 건너뜁니다.")
                continue

            df = df[["Symbol", "Name"]].copy()  # SettingWithCopyWarning 방지
            df["country"] = country
            df["type"] = type

            # 순서 및 컬럼명 변경
            df = df[["Symbol", "Name", "type", "country"]]
            df.columns = ["ticker", "name", "type", "country"]

            results.append(df)

        except Exception as e:
            # 에러가 발생해도 크래시 없이 다음 시장으로 넘어가도록 처리
            print(f"[ERROR] {market} 데이터를 가져오는 중 오류 발생: {e}")
            continue

    print("[INFO] FDR asset (주식 및 ETF) 리스트 가져오기 완료")

    # 수집된 데이터가 하나도 없을 경우 빈 데이터프레임 반환
    if not results:
        print("[WARN] 수집된 자산 데이터가 전혀 없습니다.")
        return pd.DataFrame(columns=["ticker", "name", "type", "country"])

    # 안전하게 병합
    df_assets = pd.concat(results, ignore_index=True)
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
def main():
    con = duckdb.connect("data/finance.db")

    create_table(con)
    add_all_assets(con)


if __name__ == "__main__":
    main()

# endregion
