import flet as ft

import service
import views


def main(page: ft.Page):
    # region [Page Setup]
    page.title = "Finance Database"
    page.padding = 16
    page.window.width = 700
    page.window.height = 500
    # endregion

    con = service.connect_database("data/finance.db")

    service.initialize(con)

    df = service.get_assets(con, None)

    def search_assets(keyword: str):
        return service.get_assets(con, keyword)

    tab_assets = views.create_asset_view(df, search_assets)

    accounts_df = service.get_accounts(con)
    tab_accounts = views.create_account_view(accounts_df)

    holdings_df = None
    tab_holdings = views.create_holding_view(holdings_df)

    prices_df = None
    tab_prices = views.create_price_view(prices_df)

    join_df = None
    tab_join = views.create_join_view(join_df)

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
