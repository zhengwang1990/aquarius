import os
from typing import Dict, List, Optional

import pandas as pd
import retrying
from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestTradeRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from .base import DATA_COLUMNS, Data, TimeInterval
from alpharius.utils import TIME_ZONE

_ALPACA_API_KEY_ENV = 'APCA_API_KEY_ID'
_ALPACA_SECRET_KEY_ENV = 'APCA_API_SECRET_KEY'


class AlpacaData(Data):

    def __init__(self,
                 api_key: Optional[str] = None,
                 secret_key: Optional[str] = None) -> None:
        """Instantiates an Alpaca Data Client.

        Parameters:
            api_key: Alpaca API key.
            secret_key: Alpaca API secret key.
        """
        api_key = api_key or os.environ[_ALPACA_API_KEY_ENV]
        secret_key = secret_key or os.environ[_ALPACA_SECRET_KEY_ENV]
        self._client = StockHistoricalDataClient(api_key=api_key, secret_key=secret_key)

    @retrying.retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def get_data(self,
                 symbol: str,
                 start_time: pd.Timestamp,
                 end_time: pd.Timestamp,
                 time_interval: TimeInterval) -> pd.DataFrame:
        """Loads data with specified start and end time."""
        if not start_time.tzinfo:
            start_time = start_time.tz_localize(TIME_ZONE)
        if not end_time.tzinfo:
            end_time = end_time.tz_localize(TIME_ZONE)
        if time_interval == TimeInterval.FIVE_MIN:
            timeframe = TimeFrame(5, TimeFrameUnit.Minute)
        elif time_interval == TimeInterval.HOUR:
            timeframe = TimeFrame(1, TimeFrameUnit.Hour)
        elif time_interval == TimeInterval.DAY:
            timeframe = TimeFrame(1, TimeFrameUnit.Day)
        else:
            raise ValueError(f'time_interval {time_interval} not supported')
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            start=start_time.to_pydatetime(),
            end=end_time.to_pydatetime(),
            timeframe=timeframe,
            adjustment=Adjustment.SPLIT,
        )
        try:
            bars = self._client.get_stock_bars(request).data[symbol]
            bars.sort(key=lambda b: b.timestamp)
        except AttributeError:
            bars = []
        index = pd.DatetimeIndex([pd.Timestamp(b.timestamp).tz_convert(TIME_ZONE) for b in bars])
        data = [[b.open, b.high, b.low, b.close, b.volume] for b in bars]
        return pd.DataFrame(data, index=index, columns=DATA_COLUMNS)

    @retrying.retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def get_last_trades(self, symbols: List[str]) -> Dict[str, float]:
        """Gets the last trade prices of a list of symbols."""
        request = StockLatestTradeRequest(symbol_or_symbols=symbols)
        trades = self._client.get_stock_latest_trade(request)
        return {symbol: t.price for symbol, t in trades.items()}
