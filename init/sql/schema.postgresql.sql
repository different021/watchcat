--DROP TABLE IF EXISTS 
--    realtime.quotes,
--    summary.daily_prices,
--    meta.symbols
--CASCADE;

CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE meta.symbols (
    symbol        VARCHAR(6) PRIMARY KEY,
    name          TEXT NOT NULL,
    isu_cd        TEXT,             -- KRX 내부 종목 코드
    market        TEXT,             -- KOSPI, KOSDAQ, KONEX
    dept          TEXT,             -- KRX 분류 세부 그룹
    stocks        BIGINT,           -- 발행 주식 수
    market_id     TEXT              -- STK, KSQ 등 내부 코드
);


CREATE SCHEMA IF NOT EXISTS realtime;

CREATE TABLE realtime.quotes (
    id             BIGSERIAL PRIMARY KEY,
    symbol         VARCHAR(6) NOT NULL REFERENCES meta.symbols(symbol),
    ts             TIMESTAMP WITHOUT TIME ZONE NOT NULL,  -- 수집 시각
    price          NUMERIC(12, 2),        -- 현재가
    rise_fall      SMALLINT,              -- 전일 대비 (1=상승, 2=보합, 5=하락 등)
    change         NUMERIC(12, 2),        -- 전일 대비 가격 변화량
    change_rate    NUMERIC(6, 2),         -- 등락률 (%)
    nav            NUMERIC(12, 2),        -- 순자산가치 (optional)
    earning_rate   NUMERIC(6, 2),         -- 수익률 (optional)
    volume         BIGINT,                -- 거래량
    amount         BIGINT,                -- 거래대금
    marcap         BIGINT                 -- 시가총액
);

CREATE SCHEMA IF NOT EXISTS summary;

CREATE TABLE summary.daily_prices (
    symbol         VARCHAR(6) NOT NULL REFERENCES meta.symbols(symbol),
    date           DATE NOT NULL,                      -- 거래일
    open           NUMERIC(12, 2),                     -- 시가
    close          NUMERIC(12, 2),                     -- 종가
    high           NUMERIC(12, 2),                     -- 고가
    low            NUMERIC(12, 2),                     -- 저가
    volume         BIGINT,                             -- 거래량
    amount         BIGINT,                             -- 거래대금
    PRIMARY KEY (symbol, date)
);

CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE ops.failed_realtime_batches (
    id            BIGSERIAL PRIMARY KEY,
    ts            TIMESTAMP NOT NULL,         -- 수집 타임스탬프
    error_code    TEXT NOT NULL,              -- 실패 코드 (E01 등)
    reason        TEXT,                       -- PostgreSQL 예외 메시지 등
    failed_data   JSONB,                      -- 실패한 symbol 리스트 or 전체 레코드
    created_at    TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ops.error_codes (
    code         TEXT PRIMARY KEY,     -- 예: 'E01'
    name         TEXT NOT NULL,        -- 예: 'SYMBOL_NOT_FOUND'
    description  TEXT                  -- 예: 'meta.symbols 테이블에 존재하지 않는 종목 코드'
);