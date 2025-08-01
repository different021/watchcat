import FinanceDataReader as fdr
from datetime import datetime
from typing import List, Tuple
from zoneinfo import ZoneInfo  # Python 3.9+

def fetch_all_quotes() -> List[Tuple]:
    df = fdr.StockListing("KRX")
    now = datetime.now(ZoneInfo("Asia/Seoul")).replace(tzinfo=None)

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
        raise RuntimeError(f"총 {len(failed_symbols)}개 종목 변환 실패: {failed_symbols[:5]}...")

    return records

def fetch_symbol_metadata(symbols: List[str]) -> List[Tuple[str, str, str, str, str, int, str]]:
    """
    KRX 종목 코드 리스트를 받아서 meta.symbols 테이블에 필요한 정보들을 반환함.
    실제 DB 저장은 이 함수의 책임이 아님.
    """
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
