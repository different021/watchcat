import os
import psycopg2
from urllib.parse import quote_plus

DB_USER = os.getenv("DB_USER", "mcesos")
DB_PASS = quote_plus(os.getenv("DB_PASS", "mcesos2024@"))
DB_HOST = os.getenv("DB_HOST", "10.2.0.24")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gisdb")

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=os.getenv("DB_PASS", "mcesos2024@"),  # raw 값 필요
        host=DB_HOST,
        port=DB_PORT
    )
