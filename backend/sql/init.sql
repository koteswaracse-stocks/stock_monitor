CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    market_cap DOUBLE PRECISION NOT NULL,
    pe_ratio DOUBLE PRECISION,
    dividend_yield DOUBLE PRECISION,
    volume BIGINT NOT NULL,
    avg_volume BIGINT NOT NULL,
    day_change_pct DOUBLE PRECISION NOT NULL,
    week_change_pct DOUBLE PRECISION NOT NULL,
    month_change_pct DOUBLE PRECISION NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    signal VARCHAR(50) NOT NULL,
    summary TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
