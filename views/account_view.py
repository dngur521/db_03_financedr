import flet as ft
import flet_datatable2 as ftd


def create_account_view(df) -> ft.Control:
    return ftd.DataTable2(
        fixed_top_rows=1,
        columns=[ftd.DataColumn2(ft.Text(str.upper(col))) for col in df.columns],
        rows=[
            ftd.DataRow2(cells=[ft.DataCell(ft.Text(str(value))) for value in row])
            for row in df.values
        ],
    )
