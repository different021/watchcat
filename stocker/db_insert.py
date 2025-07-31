def insert_quotes(pool, records):
    if not records:
        raise ValueError("저장할 데이터가 없습니다.")

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
        return len(records)
    except Exception as e:
        conn.rollback()
        raise  # 호출자에게 예외 그대로 전달
    finally:
        pool.putconn(conn)
