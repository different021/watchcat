import time
from datetime import datetime
from typing import List, Tuple
from zoneinfo import ZoneInfo

import FinanceDataReader as fdr
from dbpool import create_pool


def fetch_symbol_metadata(symbols: List[str]) -> List[Tuple[str, str, str, str, str, int, str]]:
    """KRX 종목 코드 리스트를 받아서 meta.symbols 테이블에 필요한 정보들을 반환함."""
    df = fdr.StockListing("KRX")
    df = df[df["Code"].isin(symbols)]

    result = []
    for _, row in df.iterrows():
        try:
            record = (
                row["Code"],         # symbol
                row["Name"],         # name
                row["ISU_CD"],       # isu_cd
                row["Market"],       # market (KOSPI, KOSDAQ 등)
                row["Dept"],         # dept (세부 분류)
                int(row["Stocks"]),  # stocks (발행주식 수)
                row["MarketId"],     # market_id (STK, KSQ 등)
            )
            result.append(record)
        except Exception:
            continue

    return result


def update_symbols_if_new():
    pool = create_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT symbol FROM meta.symbols")
            existing = set(row[0] for row in cur.fetchall())

        all_symbols_df = fdr.StockListing("KRX")
        new_symbols = [s for s in all_symbols_df["Code"] if s not in existing]

        if not new_symbols:
            print("✅ 신규 종목 없음")
            return

        records = fetch_symbol_metadata(new_symbols)
        with conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO meta.symbols (
                    symbol, name, isu_cd, market, dept, stocks, market_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, records)
        conn.commit()
        print(f"🆕 신규 종목 {len(records)}건 추가됨")
        for r in records:
            print(f"    - {r[0]}: {r[1]}")  # r[0]=symbol, r[1]=name

    finally:
        pool.putconn(conn)


def is_weekday_859(now: datetime) -> bool:
    """한국 시간 기준 평일 오전 8:59"""
    return now.weekday() < 5 and now.hour == 8 and now.minute == 59


def main():
    print("📌 [meta_updater] 종목 메타 업데이트 프로세스 시작")

    # 최초 1회 실행
    update_symbols_if_new()

    already_ran_today = False

    while True:
        now = datetime.now(ZoneInfo("Asia/Seoul")).replace(tzinfo=None)

        if is_weekday_859(now):
            if not already_ran_today:
                print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⏰ 오전 8:59 실행 조건 충족")
                update_symbols_if_new()
                already_ran_today = True
        else:
            # 08:59을 지나고 나면 다음날을 기다리기 위해 플래그 초기화
            already_ran_today = False

        time.sleep(30)


if __name__ == "__main__":
    main()
