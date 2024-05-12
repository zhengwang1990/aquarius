CREATE TABLE IF NOT EXISTS time_range (
    symbol TEXT PRIMARY KEY,
    time_range TEXT
);

CREATE TABLE IF NOT EXISTS chart (
    symbol TEXT,
    date TEXT,
    time TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    UNIQUE (symbol, time)
);

CREATE INDEX IF NOT EXISTS chart_time ON chart (symbol);
CREATE INDEX IF NOT EXISTS chart_time ON chart (date);
