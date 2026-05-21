import flet as ft
import flet_datatable2 as ftd


def create_join_view(df) -> ft.Control:
    widths = [200, 120, 150, 120, 100, 200]

    return ftd.DataTable2(
        visible_horizontal_scroll_bar=True,
        fixed_top_rows=1,
        columns=[
            ftd.DataColumn2(label=ft.Text(str.upper(col)), fixed_width=widths[i])
            for i, col in enumerate(df.columns)
        ],
        rows=[
            ftd.DataRow2(cells=[ft.DataCell(ft.Text(str(value))) for value in row])
            for row in df.values
        ],
    )
