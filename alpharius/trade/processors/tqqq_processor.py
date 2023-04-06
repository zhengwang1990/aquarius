import datetime
from typing import List, Optional

import numpy as np
from ..common import (
    ProcessorAction, ActionType, Context, Processor, ProcessorFactory, TradingFrequency,
    Position, DATETIME_TYPE, DAYS_IN_A_MONTH)


class TqqqProcessor(Processor):

    def __init__(self,
                 output_dir: str) -> None:
        super().__init__(output_dir)
        self._positions = dict()
        self._memo = dict()

    def get_trading_frequency(self) -> TradingFrequency:
        return TradingFrequency.FIVE_MIN

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['TQQQ']

    def setup(self, hold_positions: List[Position], current_time: Optional[DATETIME_TYPE]) -> None:
        self._memo = dict()

    def process_data(self, context: Context) -> Optional[ProcessorAction]:
        if context.symbol in self._positions:
            return self._close_position(context)
        else:
            return self._open_position(context)

    def _get_h2l(self, context: Context) -> float:
        h2l_key = 'h2l:' + context.current_time.strftime('%F')
        if h2l_key in self._memo:
            h2l_avg = self._memo[h2l_key]
        else:
            interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
            interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
            h2l = [l / h - 1 for h, l in zip(interday_highs, interday_lows)]
            h2l_avg = np.average(h2l)
            self._memo[h2l_key] = h2l_avg
        return h2l_avg

    def _get_l2h(self, context: Context) -> float:
        l2h_key = 'l2h:' + context.current_time.strftime('%F')
        if l2h_key in self._memo:
            l2h_avg = self._memo[l2h_key]
        else:
            interday_highs = context.interday_lookback['High'][-DAYS_IN_A_MONTH:]
            interday_lows = context.interday_lookback['Low'][-DAYS_IN_A_MONTH:]
            l2h = [h / l - 1 for h, l in zip(interday_highs, interday_lows)]
            l2h_avg = np.average(l2h)
            self._memo[l2h_key] = l2h_avg
        return l2h_avg

    def _open_position(self, context: Context) -> Optional[ProcessorAction]:
        action = self._last_hour_momentum(context)
        if action:
            return action
        action = self._mean_reversion(context)
        if action:
            return action

    def _mean_reversion(self, context: Context) -> Optional[ProcessorAction]:
        t = context.current_time.time()
        if t <= datetime.time(11, 15) or t >= datetime.time(15, 0):
            return
        interday_closes = context.interday_lookback['Close']
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        # short
        l2h = self._get_l2h(context)
        short_t = 26
        if (interday_closes[-1] < np.max(interday_closes[-DAYS_IN_A_MONTH:]) * 0.9
                and len(intraday_closes) >= short_t):
            change = intraday_closes[-1] / intraday_closes[-short_t] - 1
            if change > 0.8 * l2h:
                self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                                   f'Side: short. Change: {change * 100:.2f}%. Threshold: {l2h * 100:.2f}%.')
            if change > l2h:
                self._positions[context.symbol] = {'side': 'short',
                                                   'strategy': 'mean_reversion',
                                                   'entry_time': context.current_time}
                return ProcessorAction(context.symbol, ActionType.SELL_TO_OPEN, 1)
        # long
        h2l = self._get_h2l(context)
        long_t = 19
        if len(intraday_closes) >= long_t:
            change = intraday_closes[-1] / intraday_closes[-long_t] - 1
            if change < 0.8 * h2l:
                self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                                   f'Side: long. Change: {change * 100:.2f}%. Threshold: {h2l * 100:.2f}%.')
            if change < h2l:
                self._positions[context.symbol] = {'side': 'long',
                                                   'strategy': 'mean_reversion',
                                                   'entry_time': context.current_time}
                return ProcessorAction(context.symbol, ActionType.BUY_TO_OPEN, 1)

    def _last_hour_momentum(self, context: Context) -> Optional[ProcessorAction]:
        def _open_position(side: str) -> ProcessorAction:
            self._positions[context.symbol] = {'side': side,
                                               'strategy': 'last_hour_momentum',
                                               'entry_time': context.current_time}
            action_type = ActionType.SELL_TO_OPEN if side == 'short' else ActionType.BUY_TO_OPEN
            return ProcessorAction(context.symbol, action_type, 1)
        t = context.current_time.time()
        if t <= datetime.time(15, 0) or t >= datetime.time(15, 30):
            return
        interday_closes = context.interday_lookback['Close']
        if interday_closes[-1] > np.max(interday_closes[-DAYS_IN_A_MONTH:]) * 0.9:
            return
        market_open_index = context.market_open_index
        if market_open_index is None:
            return
        intraday_opens = context.intraday_lookback['Open'][market_open_index:]
        change_from_open = context.current_price / intraday_opens[0] - 1
        change_from_close = context.current_price / context.prev_day_close - 1
        h2l = self._get_h2l(context)
        if change_from_open < 0.7 * h2l or change_from_close < 2 * h2l:
            return _open_position('short')
        l2h = self._get_l2h(context)
        intraday_closes = context.intraday_lookback['Close'][market_open_index:]
        change_from_min = context.current_price / np.min(intraday_closes) - 1
        if change_from_min > 1.2 * l2h and intraday_closes[-1] < intraday_closes[-2]:
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] Change from min '
                               f'[{change_from_min * 100:.2f}%] exceeds threshold [{1.2 * l2h * 100:.2f}%]')
            return _open_position('long')
        if intraday_opens[0] < context.prev_day_close:
            for i in range(-25, -len(intraday_closes), -24):
                if intraday_closes[i + 24] / intraday_closes[i] - 1 < l2h * 0.15:
                    break
            else:
                self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] Continuous up trend.')
                return _open_position('long')
        if change_from_open > 0.7 * l2h:
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] Change from open '
                               f'[{change_from_open * 100:.2f}%] exceeds threshold [{0.7 * l2h * 100:.2f}%]')
            return _open_position('long')
        if change_from_close > 1.5 * l2h:
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] Change from close '
                               f'[{change_from_close * 100:.2f}%] exceeds threshold [{1.5 * l2h * 100:.2f}%]')
            return _open_position('long')

    def _close_position(self, context: Context) -> Optional[ProcessorAction]:
        def exit_position():
            self._logger.debug(f'[{context.current_time.strftime("%F %H:%M")}] [{context.symbol}] '
                               f'Closing position. Current price {context.current_price}.')
            self._positions.pop(context.symbol)
            return action
        position = self._positions[context.symbol]
        action_type = ActionType.SELL_TO_CLOSE if position['side'] == 'long' else ActionType.BUY_TO_CLOSE
        action = ProcessorAction(context.symbol, action_type, 1)
        strategy = position['strategy']
        if strategy == 'last_hour_momentum':
            if context.current_time.time() == datetime.time(16, 0):
                return exit_position()
        if strategy == 'mean_reversion':
            if context.current_time >= position['entry_time'] + datetime.timedelta(minutes=60):
                return exit_position()


class TqqqProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self,
               output_dir: str,
               *args, **kwargs) -> TqqqProcessor:
        return TqqqProcessor(output_dir)
