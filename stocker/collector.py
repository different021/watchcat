import FinanceDataReader as fdr
from stocker.db_insert import insert_quotes
from datetime import datetime
import time
from dbpool import create_pool

def fetch_all_quotes():
    print("📥 종목 데이터 수집 시작")
    df = fdr.StockListing("KRX")
    now = datetime.now()
    records = []

    for _, row in df.iterrows():
        try:
            record = (
                row['Code'],                 # symbol
                now,                         # ts
                float(row['Close']),         # price
                row['ChangeCode'],           # rise_fall
                float(row['Changes']),       # change
                float(row['ChagesRatio']),   # change_rate
                int(row['Volume']),          # volume
                int(row['Amount']),          # 거래대금
                int(row['Marcap'])           # 시가총액
            )
            records.append(record)
        except Exception as e:
            print(f"[{row['Code']}] 변환 실패: {e}")

    print(f"✅ 수집 완료: {len(records)}건")
    return records

def main():
    pool = create_pool()

    while True:
        try:
            quotes = fetch_all_quotes()
            insert_quotes(pool, quotes)
        except Exception as e:
            print(f"🚨 수집 또는 저장 실패: {e}")
        print("⏳ 대기 중... (60초)")
        time.sleep(60)

if __name__ == "__main__":
    main()