from .common import *
from .data import load_cached_daily_data, load_tradable_history, get_header
from typing import Dict, List, Union
import datetime
import logging
import pandas as pd
import pandas_market_calendars as mcal

_DATA_SOURCE = DataSource.POLYGON
_TIME_INTERVAL = TimeInterval.FIVE_MIN
_MARKET_OPEN = datetime.time(9, 30)
_MARKET_CLOSE = datetime.time(16, 0)


class Backtesting:

    def __init__(self,
                 start_date: Union[DATETIME_TYPE, str],
                 end_date: Union[DATETIME_TYPE, str],
                 processor_factories: List[ProcessorFactory]) -> None:
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        self._start_date = start_date
        self._end_date = end_date
        self._processor_factories = processor_factories
        self._positions = []

    def _init_processors(self):
        processors = []
        for factory in self._processor_factories:
            processors.append(factory.create(lookback_start_date=self._start_date,
                                             lookback_end_date=self._end_date,
                                             datasource=_DATA_SOURCE))
        return processors

    def run(self) -> None:
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=self._start_date, end_date=self._end_date)
        market_dates = [pd.to_datetime(d.date()) for d in mcal.date_range(schedule, frequency='1D')]
        history_start = self._start_date - datetime.timedelta(days=CALENDAR_DAYS_IN_A_MONTH)
        interday_datas = load_tradable_history(history_start, self._end_date, _DATA_SOURCE)
        processors = self._init_processors()

        for day in market_dates:
            self._process_day(day, processors, interday_datas)

    def _process_day(self, day: DATETIME_TYPE, processors: List[Processor],
                     interday_datas: Dict[str, pd.DataFrame]) -> None:
        stock_universes = {}
        for processor in processors:
            processor_name = type(processor).__name__
            stock_universes[processor_name] = processor.get_stock_universe(day)
        intraday_datas = {}
        for processor_name, symbols in stock_universes.items():
            for symbol in symbols:
                if symbol in intraday_datas:
                    continue
                intraday_datas[symbol] = load_cached_daily_data(symbol, day, _TIME_INTERVAL, _DATA_SOURCE)
        market_open = pd.to_datetime(pd.Timestamp.combine(day.date(), _MARKET_OPEN)).tz_localize(TIME_ZONE)
        market_close = pd.to_datetime(pd.Timestamp.combine(day.date(), _MARKET_CLOSE)).tz_localize(TIME_ZONE)
        current_time = market_open

        while current_time < market_close:
            for processor in processors:
                processor_name = type(processor).__name__
                stock_universe = stock_universes[processor_name]
                for symbol in stock_universe:
                    intraday_data = intraday_datas[symbol]
                    intraday_ind = timestamp_to_index(intraday_data.index, current_time)
                    intraday_lookback = intraday_data.iloc[:intraday_ind]
                    interday_data = interday_datas[symbol]
                    interday_ind = timestamp_to_index(interday_data.index, day.date())
                    interday_lookback = interday_data.iloc[interday_ind - DAYS_IN_A_MONTH:interday_ind]
                    context = Context(symbol=symbol, current_time=current_time,
                                      interday_lookback=interday_lookback,
                                      intraday_lookback=intraday_lookback)
                    action = processor.handle_data(context)
                    self._process_action(action)

            current_time += datetime.timedelta(minutes=5)

        self._log_day(day)

    def _process_action(self, action: Optional[Action]) -> None:
        if action is None:
            return

    def _log_day(self, day: DATETIME_TYPE) -> None:
        day_info = get_header(day.date())
        logging.info(day_info)
