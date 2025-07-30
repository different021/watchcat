CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE meta.symbols (
    symbol         VARCHAR(6) PRIMARY KEY,  -- KRX 종목 코드 (ex: 069500)
    name           TEXT NOT NULL,           -- 종목명
    listing_date   DATE,                    -- 상장일
    settle_month   INTEGER,                 -- 결산월 (보통 12)
    sector         TEXT,                    -- 산업 구분 (ETF는 대체로 없음)
    industry       TEXT,                    -- 산업군 (ETF는 대체로 없음)
    category       INTEGER,                 -- ETF 유형 (예: 1=지수형, 4=해외지수 등)
    homepage       TEXT,                    -- 운용사 홈페이지 (optional)
    region         TEXT                     -- 지역 구분 (대개 비어있음)
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