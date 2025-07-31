
def insert_quotes(pool, records):
    if not records:
        print("⚠ 저장할 데이터가 없습니다.")
        return

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
        print(f"💾 한 쿼리로 {len(records)}건 삽입 완료")
    finally:
        pool.putconn(conn)