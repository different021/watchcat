import FinanceDataReader as fdr
from datetime import datetime

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
