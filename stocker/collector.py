import FinanceDataReader as fdr
from db_insert import insert_quotes
from datetime import datetime
import time
from dbpool import create_pool

from datetime import datetime
import FinanceDataReader as fdr

def fetch_all_quotes():
    df = fdr.StockListing("KRX")
    now = datetime.now()
    records = []
    failed_symbols = []

    for _, row in df.iterrows():
        try:
            record = (
                row["Code"],                  # symbol
                now,                          # ts
                float(row["Close"]),          # price
                row["ChangeCode"],            # rise_fall
                float(row["Changes"]),        # change
                float(row["ChagesRatio"]),    # change_rate
                int(row["Volume"]),           # volume
                int(row["Amount"]),           # 거래대금
                int(row["Marcap"]),           # 시가총액
            )
            records.append(record)
        except Exception as e:
            failed_symbols.append((row.get("Code"), str(e)))

    if failed_symbols:
        # 필요한 경우 사용자 정의 예외로 전달 가능
        raise RuntimeError(f"총 {len(failed_symbols)}개 종목 변환 실패: {failed_symbols[:5]}...")

    return records


from datetime import datetime
import time

def main():
    pool = create_pool()

    while True:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{now}] 수집 루프 시작")

        quotes = []
        try:
            t0 = time.time()
            quotes = fetch_all_quotes()
            t1 = time.time()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 수집 완료: {len(quotes)}건 ({t1 - t0:.2f}초)")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [수집 실패] {e}")

        if quotes:
            try:
                t2 = time.time()
                insert_quotes(pool, quotes)
                t3 = time.time()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 저장 완료 ({t3 - t2:.2f}초)")
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [저장 실패] {e}")

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 다음 루프까지 대기... (60초)")
        time.sleep(60)

if __name__ == "__main__":
    main()