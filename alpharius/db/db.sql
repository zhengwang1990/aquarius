CREATE TABLE IF NOT EXISTS transaction (
    id varchar(25) PRIMARY KEY,
    symbol varchar(10),
    is_long boolean,
    processor varchar(50),
    entry_price real,
    exit_price real,
    entry_time timestamptz,
    exit_time timestamptz,
    qty real,
    gl real,
    gl_pct real,
    slippage real,
    slippage_pct real
);

CREATE INDEX IF NOT EXISTS transaction_exit_time ON transaction (exit_time);
CREATE INDEX IF NOT EXISTS transaction_processor ON transaction (processor);

CREATE TABLE IF NOT EXISTS aggregation (
    date date,
    processor varchar(50),
    gl real,
    avg_gl_pct real,
    slippage real,
    avg_slippage_pct real,
    count int,
    win_count int,
    lose_count int,
    slippage_count int,
    PRIMARY KEY (date, processor)
);

CREATE INDEX IF NOT EXISTS aggregation_date ON aggregation (Date);

CREATE TABLE IF NOT EXISTS log (
    date date,
    logger varchar(50),
    content text,
    PRIMARY KEY (date, logger)
);

CREATE INDEX IF NOT EXISTS log_date ON log (Date);