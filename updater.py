# updater.py

import time
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from loader.stock_loader import load_stock_infos
from influxdb_client import InfluxDBClient, Point, WritePrecision

# 설정
NULL = "N/A"
SHOW_TABLE = os.getenv("SHOW_TABLE", "true").lower() == "true"

# 조건부 rich import
if SHOW_TABLE:
    from rich.console import Console
    from rich.table import Table
    console = Console()

# InfluxDB 환경 변수 설정
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "watchcat")

def print_env_info():
    token_display = (
        INFLUXDB_TOKEN[:4] + "*" * (len(INFLUXDB_TOKEN) - 8) + INFLUXDB_TOKEN[-4:]
        if len(INFLUXDB_TOKEN) >= 8 else "****"
    )
    if SHOW_TABLE:
        console.rule("[bold green]Watchcat Updater 시작[/bold green]")
        console.print("[bold cyan]InfluxDB 설정[/bold cyan]")
        console.print(f"[yellow]URL     :[/yellow] {INFLUXDB_URL}")
        console.print(f"[yellow]ORG     :[/yellow] {INFLUXDB_ORG}")
        console.print(f"[yellow]BUCKET  :[/yellow] {INFLUXDB_BUCKET}")
        console.print(f"[yellow]TOKEN   :[/yellow] {token_display}")
        console.rule()

# InfluxDB 클라이언트 초기화
client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = client.write_api()


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


def fetch_data(infos: dict):
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
            write_to_influx(name, prev, open_, current)
            time.sleep(0.3)
        except Exception as e:
            rows.append([name, NULL, NULL, NULL])
            if SHOW_TABLE:
                console.print(f"[red]{name} - 수집 실패: {e}[/red]")
    return rows


def write_to_influx(name, prev, open_, current):
    try:
        point = (
            Point("stock_price")
            .tag("name", name)
            .field("prev", float(prev.replace(",", "")))
            .field("open", float(open_.replace(",", "")))
            .field("current", float(current.replace(",", "")))
            .time(datetime.now(timezone.utc), WritePrecision.NS)
        )
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
    except Exception as e:
        if SHOW_TABLE:
            console.print(f"[red]InfluxDB 기록 실패 - {name}: {e}[/red]")


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
    print()


def is_market_open():
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST).time()
    return now >= datetime.strptime("09:00", "%H:%M").time() and \
           now <= datetime.strptime("15:30", "%H:%M").time()


def main():
    print_env_info()
    infos, _ = load_stock_infos("data/stocks.yml")
    while True:
        if is_market_open():
            rows = fetch_data(infos)
            if SHOW_TABLE:
                render_table(rows)
        else:
            if SHOW_TABLE:
                KST = timezone(timedelta(hours=9))
                now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"[bold yellow]{now_str} - 시장이 열려있지 않습니다.[/bold yellow]")
                print()
        time.sleep(60)


if __name__ == "__main__":
    main()
