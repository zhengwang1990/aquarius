CREATE TABLE IF NOT EXISTS Transaction (
    Id varchar(25) PRIMARY KEY,
    Symbol varchar(10),
    IsLong boolean,
    Processor varchar(50),
    EntryPrice real,
    ExitPrice real,
    EntryTime timestamp,
    ExitTime timestamp,
    Qty real,
    Gl real,
    GlPercent real,
    Slippage real,
    SlippagePercent real
);

CREATE INDEX IF NOT EXISTS TransactionExitTime ON Transaction (ExitTime);
CREATE INDEX IF NOT EXISTS TransactionProcessor ON Transaction (Processor);

CREATE TABLE IF NOT EXISTS Aggregation (
    Date date,
    Processor varchar(50),
    Gl real,
    AvgGlPercent real,
    Slippage real,
    AvgSlippagePercent real,
    Count int,
    WinCount int,
    LoseCount int,
    PRIMARY KEY (Date, Processor)
);

CREATE INDEX IF NOT EXISTS AggregationDate ON Aggregation (Date);

CREATE TABLE IF NOT EXISTS Log (
    Date date,
    Logger varchar(50),
    Content text,
    PRIMARY KEY (Date, Logger)
);