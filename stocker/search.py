import pandas as pd
import os
import requests
from io import BytesIO
from datetime import datetime
from print_stock import print_stock_table

CSV_PATH = "stocks.csv"

# 📌 KRX 서버에서 상장종목 목록 CSV 다운로드
def download_krx_stock_list() -> pd.DataFrame:
    url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
    data = {
        "mktId": "ALL",
        "trdDd": datetime.today().strftime("%Y%m%d"),
        "share": "1",
        "money": "1",
        "csvxls_isNo": "false",
        "name": "fileDown",
        "url": "dbms/MDC/STAT/standard/MDCSTAT01901"
    }

    headers = {"User-Agent": "Mozilla/5.0"}
    otp_resp = requests.post(url, data=data, headers=headers)
    otp = otp_resp.text

    download_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
    resp = requests.post(download_url, data={"code": otp}, headers=headers)

    return pd.read_csv(BytesIO(resp.content), encoding="euc-kr")

# 📌 CSV 저장
def save_krx_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False, encoding="euc-kr")
    print(f"📁 CSV 파일 저장 완료: {path}")

# 📌 종목코드 사전 로딩
def load_stock_codes(csv_path: str) -> dict:
    if not os.path.exists(csv_path):
        print("📦 CSV 파일이 없어 KRX 서버에서 다운로드합니다...")
        df = download_krx_stock_list()
        save_krx_csv(df, csv_path)

    df = pd.read_csv(csv_path, encoding="euc-kr")
    
    # ✅ KRX에서 확인된 컬럼명 사용
    name_col = "한글 종목명"
    code_col = "단축코드"

    df = df[[name_col, code_col]]
    return dict(zip(df[name_col].str.strip(), df[code_col].astype(str).str.zfill(6)))



# 📌 종목명 검색
def search_stock_code(keyword: str, stock_dict: dict) -> dict:
    keyword = keyword.strip()
    return {name: code for name, code in stock_dict.items() if keyword in name}

def main():
    stock_dict = load_stock_codes(CSV_PATH)

    while True:
        keyword = input("종목명을 입력하세요: ").strip()
        result = search_stock_code(keyword, stock_dict)
    
        if not result:
            print("🔍 검색 결과가 없습니다.")
        else:
            print_stock_table(result)

if __name__ == "__main__":
    main()
