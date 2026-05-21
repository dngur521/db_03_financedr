import flet as ft
import flet_charts as fch
import plotly.express as px

import service


def create_price_view(df, con) -> ft.Control:
    # print(df)
    # 첫 번째 종목의 티커를 초기 티커값으로 설정 (없다면 삼성전자)
    ticker = df["ticker"].iloc[0] if not df.empty else "005930"
    # print(ticker)

    # 차트 생성
    def generate_chart_figure(ticker_code: str, ticker_name: str) -> px.line:
        prices_df = service.get_prices(con, ticker_code)
        # print(prices_df)

        return px.line(
            prices_df,
            x="date",
            y="close",
            title=f"{ticker_name} ({ticker_code}) 시세",
            template="plotly_dark",
        )

    # 티커 선택 시 차트 업데이트
    def on_ticker_selected(e):
        selected_ticker = e.control.value
        # print(selected_ticker)

        matched_rows = df[df["ticker"] == selected_ticker]
        selected_name = matched_rows["name"].iloc[0]

        chart.figure = generate_chart_figure(selected_ticker, selected_name)
        e.page.update()

    # 드롭다운 생성
    dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option(
                key=row["ticker"], text=f"{row['name']} ({row['ticker']})"
            )
            for _, row in df.iterrows()
        ],
        expand=True,
        value=ticker,
        on_select=on_ticker_selected,
    )

    # 초기 차트 생성
    fig = generate_chart_figure(ticker, df[df["ticker"] == ticker]["name"].iloc[0])
    chart = fch.PlotlyChart(figure=fig)

    # 레이아웃 구성
    # 전체적으로 세로 방향(Column)으로 배치
    # 상단에 Text("종목 선택: ")와 드롭다운을 가로 방향(Row)으로 배치
    # 세로 방향 하단에 차트 배치
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("종목 선택: "),
                    dropdown,
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            chart,
        ]
    )
