from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import json

@dataclass
class InsertResult:
    success: bool                   # True if insert succeeded
    inserted_count: int             # Number of inserted records (0 if failed)
    error_code: Optional[str]       # 'E01', 'E05' 등 (None if success)
    reason: Optional[str]           # Raw error message (None if success)

def insert_quotes(pool, records) -> InsertResult:
    if not records:
        return InsertResult(False, 0, "E03", "저장할 데이터가 없습니다.")

    conn = pool.getconn()
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
        return InsertResult(True, len(records), None, None)

    except Exception as e:
        conn.rollback()
        msg = str(e)
        code = "E01" if "foreign key constraint" in msg else "E05"
        _log_failed_batch(pool, records, code, msg)
        return InsertResult(False, 0, code, msg)

    finally:
        pool.putconn(conn)

def _log_failed_batch(pool, records, error_code: str, reason: str):
    """ops.failed_realtime_batches에 실패 기록 삽입"""
    from datetime import datetime  # 지역 import
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            ts = records[0][1] if records and len(records[0]) > 1 else None

            # datetime → 문자열 변환
            serializable_data = [
                [v.isoformat() if isinstance(v, datetime) else v for v in rec]
                for rec in records
            ]

            cur.execute("""
                INSERT INTO ops.failed_realtime_batches (ts, error_code, reason, failed_data)
                VALUES (%s, %s, %s, %s)
            """, (ts, error_code, reason, json.dumps(serializable_data)))
        conn.commit()

        # ✅ 사용자 피드백용 출력
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 실패 배치 기록 완료: 코드={error_code}")

    finally:
        pool.putconn(conn)
