import FinanceDataReader as fdr
import pandas as pd


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


def fetch_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    특정 종목의 start_date부터 end_date까지의 가격 정보 얻어옴
    """
    df = fdr.DataReader(ticker, start=start_date, end=end_date)
    # print(df.head())

    # index에 있는 'Date'를 컬럼으로 변환
    df = df.reset_index()

    # 컬럼명을 소문자로 변환
    df.columns = [col.lower() for col in df.columns]

    # 필요한 컬럼 projection
    # date + ohlvc
    price_columns = ["date", "open", "high", "low", "close", "volume"]
    df = df[price_columns]
    # print(df.head())
    return df
