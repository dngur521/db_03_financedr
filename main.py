import flet as ft

import service


# =========================================================================
# region: Main
# =========================================================================
def main(page: ft.Page):
    # region [Page Setup]
    page.title = "Finance Database"
    page.padding = 16
    page.window.width = 700
    page.window.height = 500
    # page.scroll = ft.ScrollMode.ADAPTIVE
    # endregion

    # Service
    # con = duckdb.connect("data/finance.db")
    con = service.connect_database("data/finance.db")

    # Service
    # repo.create_table(con)
    # add_all_assets(con)
    service.initialize(con)

    # Service
    # df = repo.find_assets_by_keyword(con, None)
    df = service.get_assets(con, None)

    # DataTable
    def create_rows(df) -> ft.DataRow:
        return [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(value))) for value in row])
            for row in df.values
        ]

    table_assets = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(str.upper(col))) for col in df.columns],
        rows=create_rows(df),
    )

    # Filtering
    def on_filter_change(e):
        # 입력된 텍스트로 asset 테이블 검색
        # Service
        # filtered_df = repo.find_assets_by_keyword(con, e.control.value)
        filtered_df = service.get_assets(con, e.control.value)

        table_assets.rows.clear()
        table_assets.rows = create_rows(filtered_df)

        page.update()

    filter_input = ft.Container(
        ft.TextField(
            label="종목 검색",
            prefix_icon=ft.Icons.SEARCH,
            hint_text="종목명을 입력하세요",
            hint_style=ft.TextStyle(color=ft.Colors.GREY_700),
            margin=16,
            expand=True,
            on_submit=on_filter_change,
        )
    )

    tab_assets = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
        controls=[filter_input, table_assets],
    )

    tab_accounts = ft.Text("계좌")
    tab_holdings = ft.Text("보유")
    tab_prices = ft.Text("시세")
    tab_join = ft.Text("Join")

    tabs = ft.Tabs(
        length=5,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="종목", icon=ft.Icons.MONETIZATION_ON_OUTLINED),
                        ft.Tab(label="계좌", icon=ft.Icons.SAVINGS_OUTLINED),
                        ft.Tab(label="보유", icon=ft.Icons.FAVORITE_BORDER_OUTLINED),
                        ft.Tab(label="시세", icon=ft.Icons.CANDLESTICK_CHART_OUTLINED),
                        ft.Tab(label="Join", icon=ft.Icons.JOIN_LEFT_OUTLINED),
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        tab_assets,
                        tab_accounts,
                        tab_holdings,
                        tab_prices,
                        tab_join,
                    ],
                ),
            ],
        ),
    )

    page.add(
        tabs,
    )


if __name__ == "__main__":
    ft.run(main)

# endregion
