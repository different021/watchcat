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