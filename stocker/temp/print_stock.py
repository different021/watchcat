from rich.console import Console
from rich.table import Table

def print_stock_table(stock_dict: dict):
    table = Table(title="🔍 종목 검색 결과")

    table.add_column("종목명", style="cyan", no_wrap=True)
    table.add_column("종목코드", style="magenta")

    for name, code in stock_dict.items():
        table.add_row(name, code)

    console = Console()
    console.print(table)
