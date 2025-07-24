import time
from rich.console import Console
from core2.market_clock import MarketClock
from loader.stock_loader import load_stock_infos
from core2.fetcher import fetch_data, render_table


class MarketUpdater:
    def __init__(self):
        self.clock = MarketClock()  # ✅ 외부 주입 없이 직접 생성
        self.console = Console()
        self._printed_open = None
        self._printed_close = None
        self._printed_1530 = None
        self.infos, _ = load_stock_infos("data/stocks.yml")

    def run(self):
        while True:
            self.process_events()
            time.sleep(60)

    def process_events(self):
        """하루 동안 출력해야 할 이벤트를 순차적으로 판단하고 처리"""
        today = self.clock.today_str()

        if self._should_announce_open(today):
            self._announce_open(today)

        if self.clock.is_market_open_time():
            self._print_market_snapshot()

        if self._should_announce_1530(today):
            self._announce_1530(today)

        if self._should_announce_close(today):
            self._announce_close(today)

    # ==== 판단 + 실행 ====

    def _should_announce_open(self, today: str) -> bool:
        return self.clock.is_market_open_time() and self._printed_open != today

    def _should_announce_1530(self, today: str) -> bool:
        return self.clock.time_now() >= self.clock.market_close_time() and self._printed_1530 != today

    def _should_announce_close(self, today: str) -> bool:
        return self.clock.is_after_close() and self._printed_close != today

    def _announce_open(self, today: str):
        self.console.rule("[bold green]📈 장이 열렸습니다")
        self.console.print(f"[green]장 시작 시각: {self.clock.formatted_now()}")
        self._printed_open = today

    def _announce_1530(self, today: str):
        rows = fetch_data(self.infos)
        render_table(rows)
        self._printed_1530 = today

    def _announce_close(self, today: str):
        self.console.rule("[bold red]📉 장이 종료되었습니다")
        self.console.print(f"[red]장 종료 시각: {self.clock.formatted_now()}")
        self._printed_close = today

    # ==== 실시간 시세 출력 ====

    def _print_market_snapshot(self):
        rows = fetch_data(self.infos)
        render_table(rows)
