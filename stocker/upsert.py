# upsert.py

import pandas as pd
import FinanceDataReader as fdr
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert
from urllib.parse import quote_plus

# 🔧 PostgreSQL 접속 설정 (이 부분만 수정하시면 됩니다)
DB_USER = "mcesos"
# DB_PASS = "mcesos2024@"
DB_PASS = quote_plus("mcesos2024@")
DB_HOST = "10.2.0.24"
DB_PORT = 5432
DB_NAME = "gisdb"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?host={DB_HOST}"
engine = create_engine(DATABASE_URL)

def upsert_symbols_to_db(engine) -> None:
    print("📥 KRX 종목 목록 수집 중...")
    df = fdr.StockListing("KRX")

    print("✅ 실제 수신 컬럼:", df.columns.tolist())

    # 사용할 컬럼만 정의
    column_map = {
        "Code": "symbol",
        "Name": "name",
        "ISU_CD": "isu_cd",
        "Market": "market",
        "Dept": "dept",
        "Stocks": "stocks",
        "MarketId": "market_id",
    }


    # 유효한 컬럼만 필터링
    use_columns = list(column_map.keys())
    rename_map = {k: v for k, v in column_map.items() if k in df.columns}
    df = df[use_columns]                     # 꼭 필요한 컬럼만 남기고
    df = df.rename(columns=rename_map)       # 컬럼명 재정의
    df = df.where(pd.notnull(df), None)      # NaN -> None

    print(f"🗃️ DB에 {len(df)}건 upsert 중...")

    with engine.begin() as conn:
        for _, row in df.iterrows():
            row_data = row.to_dict()

            stmt = insert_symbol(engine).values(**row_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["symbol"],
                set_={k: getattr(stmt.excluded, k) for k in row_data if k != "symbol"}
            )
            conn.execute(stmt)

    print("✅ 메타데이터 갱신 완료")


def insert_symbol(engine):
    meta = MetaData(schema="meta")
    symbols = Table("symbols", meta, autoload_with=engine)
    return insert(symbols)


if __name__ == "__main__":
    upsert_symbols_to_db(engine)
