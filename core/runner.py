import time
from rich.console import Console
from core.market_clock import MarketClock
from loader.stock_loader import load_stock_infos
from core.fetcher import fetch_data, render_table

class WatchcatRunner:
    def __init__(self):
        self.console = Console()
        self.clock = MarketClock()
        self.infos, _ = load_stock_infos("data/stocks.yml")

    def run(self):
        while True:
            now = self.clock.now()

            self.check_market_open(now)
            self.check_market_active()
            self.check_print_1530()
            self.check_market_close(now)

            time.sleep(60)

    def check_market_open(self, now):
        if self.clock.should_open():
            self.console.rule("[bold green]📈 장이 열렸습니다")
            self.console.print(f"[bold green]오늘 장 시작: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.clock.mark_open()

    def check_market_active(self):
        if self.clock.is_market_open():
            rows = fetch_data(self.infos)
            render_table(rows)

    def check_print_1530(self):
        if self.clock.should_print_1530():
            rows = fetch_data(self.infos)
            render_table(rows)
            self.clock.mark_1530()

    def check_market_close(self, now):
        if self.clock.should_close():
            self.console.rule("[bold red]📉 장이 종료되었습니다")
            self.console.print(f"[bold red]오늘 장 종료: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.clock.mark_close()
