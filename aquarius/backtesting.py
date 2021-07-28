from .common import *
from .data import load_cached_daily_data, load_tradable_history, get_header
from typing import Any, Dict, List, Union
import datetime
import logging
import pandas as pd
import pandas_market_calendars as mcal
import tabulate

_DATA_SOURCE = DataSource.POLYGON
_TIME_INTERVAL = TimeInterval.FIVE_MIN
_MARKET_OPEN = datetime.time(9, 30)
_MARKET_CLOSE = datetime.time(16, 0)
_SHORT_RESERVE_RATIO = 1


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
        self._daily_equity = [1]
        self._num_win, self._num_lose = 0, 0
        self._cash = 1

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
            break

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

        executed_actions = []
        while current_time < market_close:
            actions = []
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
                    if action is not None:
                        actions.append(action)
            current_executed_actions = self._process_actions(actions)
            executed_actions.extend([[current_time.time()] + executed_action
                                     for executed_action in current_executed_actions] )

            current_time += datetime.timedelta(minutes=5)

        self._log_day(day, executed_actions, interday_datas)

    def _process_actions(self, actions: List[Action]) -> List[List[Any]]:
        action_sets = set([(action.symbol, action.type) for action in actions])
        unique_actions = []
        for unique_action in action_sets:
            similar_actions = [action for action in actions if (action.symbol, action.type) == unique_action]
            action = similar_actions[0]
            for i in range(1, len(similar_actions)):
                if similar_actions[i].percent > action.percent:
                    action = similar_actions[i]
            unique_actions.append(action)

        close_actions = [action for action in unique_actions
                         if action.type in [ActionType.BUY_TO_CLOSE, ActionType.SELL_TO_CLOSE]]
        executed_closes = self._close_positions(close_actions)

        open_actions = [action for action in unique_actions
                        if action.type in [ActionType.BUY_TO_OPEN, ActionType.SELL_TO_OPEN]]
        executed_opens = self._open_positions(open_actions)

        return executed_closes + executed_opens

    def _pop_current_position(self, symbol: str) -> Optional[Position]:
        for ind, position in enumerate(self._positions):
            if position.symbol == symbol:
                current_position = self._positions.pop(ind)
                return current_position
        return None

    def _get_current_position(self, symbol: str) -> Optional[Position]:
        for position in self._positions:
            if position.symbol == symbol:
                return position
        return None

    def _close_positions(self, actions: List[Action]) -> List[List[Any]]:
        executed_actions = []
        for action in actions:
            assert action.type in [ActionType.BUY_TO_CLOSE, ActionType.SELL_TO_CLOSE]
            symbol = action.symbol
            current_position = self._get_current_position(symbol)
            if current_position is None:
                continue
            if action.type == ActionType.BUY_TO_CLOSE and current_position.qty > 0:
                continue
            if action.type == ActionType.SELL_TO_CLOSE and current_position.qty < 0:
                continue
            self._pop_current_position(symbol)
            qty = current_position.qty * action.percent
            new_qty = current_position.qty - qty
            if abs(new_qty - 0) > 1E-7:
                self._positions.append(Position(symbol, new_qty, current_position.entry_price))
            self._cash += action.price * qty
            profit = (action.price - current_position.entry_price) * qty
            if profit > 0:
                self._num_win += 1
            else:
                self._num_lose += 1
            profit_pct = profit / (current_position.entry_price * abs(qty)) * 100
            executed_actions.append([symbol, action.type, qty, current_position.entry_price,
                                     action.price, f'{profit:.2f}({profit_pct:+.2f}%)'])
        return executed_actions

    def _open_positions(self, actions: List[Action]) -> List[List[Any]]:
        executed_actions = []
        tradable_cash = self._cash
        for position in self._positions:
            if position.qty < 0:
                tradable_cash += position.entry_price * position.qty * (1 + _SHORT_RESERVE_RATIO)
        for action in actions:
            assert action.type in [ActionType.BUY_TO_OPEN, ActionType.SELL_TO_OPEN]
            symbol = action.symbol
            if self._get_current_position(symbol) is not None:
                continue
            cash_to_trade = min(tradable_cash / len(actions), tradable_cash * action.percent)
            if cash_to_trade == 0:
                continue
            qty = cash_to_trade / action.price
            if action.type == ActionType.SELL_TO_OPEN:
                qty = -qty
            new_position = Position(symbol, qty, action.price)
            self._positions.append(new_position)
            self._cash -= action.price * qty
            executed_actions.append([symbol, action.type, qty, action.price])
        return executed_actions

    def _log_day(self,
                 day: DATETIME_TYPE,
                 executed_actions: List[List[Any]],
                 interday_datas: Dict[str, pd.DataFrame]) -> None:
        outputs = [get_header(day.date())]
        if executed_actions:
            action_info = tabulate.tabulate(executed_actions,
                                            headers=['Time', 'Symbol', 'Action', 'Qty', 'Entry Price',
                                                     'Exit Price', 'Gain/Loss'],
                                            tablefmt='grid')
            outputs.append(action_info)
        equity = self._cash
        for position in self._positions:
            close_price = interday_datas[position.symbol].loc[day]['Close']
            equity += position.qty * close_price
        profit_pct = (equity / self._daily_equity[-1] - 1) * 100 if self._daily_equity[-1] else 0
        self._daily_equity.append(equity)
        summary = [['Current Equity', f'{equity:.3g}', 'Daily Gain/Loss', f'{profit_pct:+.2f}%']]
        outputs.append(tabulate.tabulate(summary, tablefmt='grid'))

        logging.info('\n'.join(outputs))
