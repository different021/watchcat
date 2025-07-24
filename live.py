import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.live import Live
from datetime import datetime
import time

# 종목 코드 목록
codes = [
    "006800", "003530", "005940", "071050", "039490", 
    "016360", "003540", "003470", "001720", "105560"
]

# 종목 코드 → 종목명 매핑
code_to_name = {
    "006800": "미래에셋증권",
    "003530": "한화투자증권",
    "005940": "NH투자증권",
    "071050": "한국투자금융지주",
    "039490": "키움증권",
    "016360": "삼성증권",
    "003540": "대신증권",
    "003470": "유안타증권",
    "001720": "신한금융투자",
    "105560": "KB증권",
}

NULL = "N/A"

# 전일종가, 시가 가져오기
def get_price_by_label(soup, label):
    try:
        td_tags = soup.select("table.no_info td")
        for td in td_tags:
            if label in td.text:
                value = td.select_one("span.blind")
                return value.text.strip() if value else NULL
        return NULL
    except Exception:
        return NULL

# 현재가 가져오기
def get_current_price(soup):
    try:
        return soup.select_one("p.no_today span.blind").text.strip()
    except Exception:
        return NULL

# 테이블 생성 함수
def generate_table():
    table = Table(title="증권사 시세 정보 (실시간)", title_justify="center")
    table.add_column("업데이트", justify="center", style="cyan", no_wrap=True)
    table.add_column("종목명", justify="left", style="bold")
    table.add_column("전일 종가", justify="right")
    table.add_column("금일 시가", justify="right")
    table.add_column("현재가", justify="right")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for code in codes:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            prev_close = get_price_by_label(soup, "전일")
            open_price = get_price_by_label(soup, "시가")
            current_price = get_current_price(soup)

            table.add_row(
                now,
                code_to_name.get(code, code),
                prev_close,
                open_price,
                current_price
            )

            time.sleep(0.1)  # Naver 요청 간 딜레이 (차단 방지)
        except Exception as e:
            table.add_row(now, code_to_name.get(code, code), NULL, NULL, NULL)

    return table

# 실시간 갱신 루프
console = Console()
with Live(generate_table(), console=console, refresh_per_second=0.5) as live:
    try:
        while True:
            time.sleep(60)  # 1분 간격으로 갱신
            live.update(generate_table())
    except KeyboardInterrupt:
        console.print("\n[bold red]종료합니다.[/bold red]")
