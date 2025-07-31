from psycopg2.pool import SimpleConnectionPool
import os
from urllib.parse import quote_plus

def create_pool():
    minconn = os.getenv("DB_MIN_CONN", 1)
    maxconn = os.getenv("DB_MAX_CONN", 5)
    db_user = os.getenv("DB_USER", "mcesos")
    db_pass = os.getenv("DB_PASS", "mcesos2024@")
    db_host = os.getenv("DB_HOST", "10.2.0.24")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "gisdb")

    return SimpleConnectionPool(
        minconn,
        maxconn,
        dbname=db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )
