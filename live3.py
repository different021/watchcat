# run_watchcat.py
import time
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from datetime import datetime, timezone, timedelta
from loader.stock_loader import load_stock_infos

NULL = "N/A"
console = Console()


def get_price_by_label(soup, label):
    try:
        for td in soup.select("table.no_info td"):
            if label in td.text:
                value = td.select_one("span.blind")
                return value.text.strip() if value else NULL
        return NULL
    except Exception:
        return NULL


def get_current_price(soup):
    try:
        return soup.select_one("p.no_today span.blind").text.strip()
    except Exception:
        return NULL


def fetch_data(infos : dict):
    rows = []
    for code, name in infos.items():
        try:
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            prev = get_price_by_label(soup, "전일")
            open_ = get_price_by_label(soup, "시가")
            current = get_current_price(soup)

            rows.append([name, prev, open_, current])
            time.sleep(0.3)  # 너무 빠르면 차단
        except Exception:
            rows.append([name, NULL, NULL, NULL])
    return rows


def render_table(rows):
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    table = Table(title=f"Watchcat: 증권사 시세 정보 ({now})", title_justify="center")
    table.add_column("종목명", justify="left", style="bold")
    table.add_column("전일 종가", justify="right")
    table.add_column("금일 시가", justify="right")
    table.add_column("현재가", justify="right")

    for row in rows:
        table.add_row(*row)

    console.print(table)
    print()  # 구분용 줄바꿈

def is_market_open():
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST).time()  # ← 꼭 `.time()`으로 잘라줘야 합니다
    return now >= datetime.strptime("09:00", "%H:%M").time() and \
           now <= datetime.strptime("15:30", "%H:%M").time()

def main():
    infos, _ = load_stock_infos("data/stocks.yml")
    last_open_date = None
    last_close_date = None
    last_1530_date = None

    while True:
        KST = timezone(timedelta(hours=9))
        now = datetime.now(KST)
        now_time = now.time()
        today_str = now.strftime("%Y-%m-%d")

        if now_time >= datetime.strptime("09:00", "%H:%M").time() and last_open_date != today_str:
            console.rule("[bold green]📈 장이 열렸습니다")
            console.print(f"[bold green]오늘 장 시작: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            last_open_date = today_str

        if is_market_open():
            rows = fetch_data(infos)
            render_table(rows)

        if now_time >= datetime.strptime("15:30", "%H:%M").time() and last_1530_date != today_str:
            rows = fetch_data(infos)
            render_table(rows)
            last_1530_date = today_str

        if now_time >= datetime.strptime("15:31", "%H:%M").time() and last_close_date != today_str:
            console.rule("[bold red]📉 장이 종료되었습니다")
            console.print(f"[bold red]오늘 장 종료: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            last_close_date = today_str

        time.sleep(60)


if __name__ == "__main__":
    main()
