import FinanceDataReader as fdr

# 모든 시장 데이터를 dict에 저장
stock_lists = {
    "KRX": fdr.StockListing("KRX"),           # 한국거래소 전체 (주식 + ETF + REIT)
    "KOSPI": fdr.StockListing("KOSPI"),       # 유가증권시장 (주식 중심)
    "KOSDAQ": fdr.StockListing("KOSDAQ"),     # 코스닥시장
    "ETF/KR": fdr.StockListing("ETF/KR"),     # 한국 ETF
    "NASDAQ": fdr.StockListing("NASDAQ"),     # 미국 나스닥
    "NYSE": fdr.StockListing("NYSE"),         # 미국 뉴욕증권거래소
    "S&P500": fdr.StockListing("S&P500")      # 미국 S&P500 구성 종목
}

def main():
    # 예시: ETF 상위 5개 출력
    print("📌 한국 ETF 상위 5개:")
    print(stock_lists["ETF/KR"].head())

    # 예시: 미국 나스닥 상장 수
    print(f"\n총 나스닥 종목 수: {len(stock_lists['NASDAQ'])}")

if __name__ == "__main__":
    main()