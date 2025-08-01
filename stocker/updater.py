import time
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

from dbpool import create_pool
from db_insert import insert_quotes  # InsertResult 포함되어 있다고 가정
from collector import fetch_all_quotes

print("📈 주식 데이터 수집 및 저장 프로그램 시작")

def is_market_open(now: datetime) -> bool:
    """현재 시간이 한국 주식 시장 개장 시간인지 여부를 반환"""
    kst_now = datetime.now(ZoneInfo("Asia/Seoul")).replace(tzinfo=None)
    is_weekday = kst_now.weekday() < 5  # 월=0, ..., 금=4
    market_start = dtime(9, 0)
    market_end = dtime(15, 30)
    return is_weekday and market_start <= kst_now.time() <= market_end

def main():
    pool = create_pool()
    print(f"[{datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')}] 데이터 수집 시작")

    while True:
        now = datetime.now(ZoneInfo("Asia/Seoul")).replace(tzinfo=None)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        if is_market_open(now):
            print(f"\n[{timestamp}] 수집 루프 시작")

            try:
                t0 = time.time()
                quotes = fetch_all_quotes()
                t1 = time.time()
                print(f"[{timestamp}] 수집 완료: {len(quotes)}건 ({t1 - t0:.2f}초)")

                t2 = time.time()
                result = insert_quotes(pool, quotes)
                t3 = time.time()

                if result.success:
                    print(f"[{timestamp}] 저장 완료 ({t3 - t2:.2f}초)")
                else:
                    print(f"[{timestamp}] 저장 실패: {result.error_code} - {result.reason}")

            except Exception as e:
                print(f"[{timestamp}] 예외 발생: {e}")

        else:
            print(f"[{timestamp}] 장시간 외 - 수집 생략")

        print(f"[{timestamp}] 다음 루프까지 대기... (60초)")
        time.sleep(60)

if __name__ == "__main__":
    main()
