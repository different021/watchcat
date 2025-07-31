import FinanceDataReader as fdr
from db import get_connection
from datetime import datetime
import time

def fetch_all_quotes():
    print("📥 종목 데이터 수집 시작")
    df = fdr.StockListing("KRX")
    now = datetime.now()
    records = []

    for _, row in df.iterrows():
        try:
            record = (
                row['Code'],
                now,
                float(row['Close']),
                row['ChangeCode'],
                float(row['Changes']),
                float(row['ChagesRatio']),
                int(row['Volume']),
                int(row['Amount']),
                int(row['Marcap'])
            )
            records.append(record)
        except Exception as e:
            print(f"[{row['Code']}] 변환 실패: {e}")
    
    print(f"✅ 수집 완료: {len(records)}건")
    return records

def insert_quotes(records):
    if not records:
        print("⚠ 저장할 데이터가 없습니다.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            placeholders = ', '.join(['(' + ', '.join(['%s'] * 9) + ', NULL, NULL)' for _ in records])
            flat_values = [item for rec in records for item in rec]

            query = f"""
                INSERT INTO realtime.quotes (
                    symbol, ts, price, rise_fall, change,
                    change_rate, volume, amount, marcap,
                    nav, earning_rate
                ) VALUES {placeholders}
            """

            cur.execute(query, flat_values)
        conn.commit()
        print(f"💾 한 쿼리로 {len(records)}건 삽입 완료")
    finally:
        conn.close()

def main():
    while True:
        try:
            quotes = fetch_all_quotes()
            insert_quotes(quotes)
        except Exception as e:
            print(f"🚨 수집 또는 저장 실패: {e}")
        print("⏳ 대기 중... (60초)")
        time.sleep(60)

if __name__ == "__main__":
    main()
