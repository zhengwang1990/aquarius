import datetime
import functools
import math
import os
from typing import List, Tuple

import alpaca_trade_api as tradeapi
import pandas as pd
import pytz
import retrying
from dateutil.relativedelta import relativedelta

TIME_ZONE = pytz.timezone('America/New_York')


def get_time_vs_equity(history_equity: List[float],
                       history_time: List[int],
                       time_format: str,
                       cash_reserve: float,
                       skip_condition=None) -> Tuple[List[str], List[float]]:
    time_list = []
    equity_list = []
    n = sum([equity is not None for equity in history_equity])
    for i, (e, t) in enumerate(zip(history_equity[:n], history_time[:n])):
        dt = pd.to_datetime(t, utc=True, unit='s').tz_convert(TIME_ZONE)
        if skip_condition and skip_condition(dt) and i != n - 1:
            continue
        equity_list.append(max(e - cash_reserve, 0))
        time_list.append(dt.strftime(time_format))
    start = 0
    while start < len(equity_list) and equity_list[start] == 0:
        start += 1
    time_list = time_list[start:]
    equity_list = equity_list[start:]
    if len(time_list) > 1 and time_list[-2] == time_list[-1]:
        time_list.pop(-2)
        equity_list.pop(-2)
    return time_list, equity_list


def round_time(t: pd.Timestamp):
    if t.second < 30:
        return t.strftime('%m-%d %H:%M')
    return (t + datetime.timedelta(minutes=1)).strftime('%m-%d %H:%M')


def get_colored_value(value: str, color: str, with_arrow: bool = False):
    arrow = ''
    if with_arrow:
        if color == 'green':
            arrow = '<i class="uil uil-arrow-up"></i>'
        else:
            arrow = '<i class="uil uil-arrow-down"></i>'
    return f'<span style="color:{color};">{arrow}{value}</span>'


def get_signed_percentage(value: float, with_arrow: bool = False):
    color = 'green' if value >= 0 else 'red'
    return get_colored_value(f'{value * 100:+.2f}%', color, with_arrow)


def get_last_day():
    last_day = datetime.date.today()
    if datetime.datetime.now().time() < datetime.time(4, 0):
        last_day -= datetime.timedelta(days=1)
    return last_day


class AlpacaClient:

    def __init__(self):
        self._alpaca = tradeapi.REST()

    @functools.lru_cache(maxsize=5)
    def get_calendar(self, last_day: str):
        calendar = self._alpaca.get_calendar(
            start=(pd.to_datetime(last_day) - relativedelta(years=5)).strftime('%F'),
            end=last_day)
        return calendar

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_portfolio_histories(self):
        result = dict()
        last_day = get_last_day()
        calendar = self.get_calendar(last_day.strftime('%F'))
        result['market_close'] = calendar[-1].close.strftime('%H:%M')
        market_dates = [c.date for c in calendar]
        histories = dict()
        for start_index, timeframe in [(-1, '5Min'), (-5, '15Min'), (0, '1D')]:
            extended_hours = True if start_index == - 1 else False
            histories[timeframe] = self._alpaca.get_portfolio_history(
                date_start=market_dates[start_index].strftime('%F'),
                date_end=market_dates[-1].strftime('%F'),
                timeframe=timeframe,
                extended_hours=extended_hours)
        cash_reserve = float(os.environ.get('CASH_RESERVE', 0))
        result['time_1d'], result['equity_1d'] = get_time_vs_equity(
            histories['5Min'].equity,
            histories['5Min'].timestamp,
            '%H:%M',
            cash_reserve)
        current_equity = result['equity_1d'][-1]
        result['current_equity'] = f'{current_equity:.2f}'
        result['time_1w'], result['equity_1w'] = get_time_vs_equity(
            histories['15Min'].equity,
            histories['15Min'].timestamp,
            '%m-%d %H:%M',
            cash_reserve,
            lambda dt: dt.time() not in [
                datetime.time(9, 30), datetime.time(13, 0), datetime.time(16, 0)])
        result['time_5y'], result['equity_5y'] = get_time_vs_equity(
            histories['1D'].equity,
            histories['1D'].timestamp,
            '%F',
            cash_reserve)
        result['prev_close'] = (result['equity_5y'][-2]
                                if len(result['equity_5y']) > 2 else math.nan)
        for time_period, time_delta in [('1m', relativedelta(months=1)),
                                        ('6m', relativedelta(months=6)),
                                        ('1y', relativedelta(years=1))]:
            cut = (last_day - time_delta).strftime('%F')
            time_str = 'time_' + time_period
            equity_str = 'equity_' + time_period
            result[time_str] = result[equity_str] = []
            for i in range(len(result['time_5y'])):
                if result['time_5y'][i] > cut:
                    result[time_str] = result['time_5y'][i:]
                    result[equity_str] = result['equity_5y'][i:]
                    break
        for time_period in ['1d', '1w', '1m', '6m', '1y', '5y']:
            if time_period == '1d':
                base_value = (result['prev_close']
                              if result['prev_close'] > 0 else current_equity)
            else:
                base_value = (result['equity_' + time_period][0]
                              if result['equity_' + time_period] else current_equity)
            change = current_equity - base_value
            percent = current_equity / base_value - 1
            result['change_' + time_period] = get_colored_value(
                f'{change:+.2f} ({percent * 100:+.2f}%)',
                'green' if change > 0 else 'red',
                with_arrow=True)
            result['color_' + time_period] = 'green' if change > 0 else 'red'
        i = 0
        for j in range(len(result['time_5y'])):
            if j % 3 == 0 or j == len(result['time_5y']) - 1:
                result['time_5y'][i] = result['time_5y'][j]
                result['equity_5y'][i] = result['equity_5y'][j]
                i += 1
        result['time_5y'] = result['time_5y'][:i]
        result['equity_5y'] = result['equity_5y'][:i]
        if result['time_1d'][-1] > '09:30':
            for i in range(len(result['time_1d'])):
                if result['time_1d'][i] >= '09:30':
                    result['time_1d'] = result['time_1d'][i:]
                    result['equity_1d'] = result['equity_1d'][i:]
                    break
        return result

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_recent_orders(self):
        result = []
        last_day = get_last_day()
        calendar = self.get_calendar(last_day.strftime('%F'))
        orders = self._alpaca.list_orders(status='closed',
                                          after=calendar[-2].date.strftime('%F'),
                                          direction='desc')
        orders_used = [False] * len(orders)
        positions = self._alpaca.list_positions()
        position_symbols = set([position.symbol for position in positions])
        cut_time = calendar[-1].date.tz_localize(TIME_ZONE)
        for i in range(len(orders)):
            order = orders[i]
            if order.filled_at is None:
                continue
            filled_at = order.filled_at.tz_convert(TIME_ZONE)
            if filled_at < cut_time:
                break
            price = float(order.filled_avg_price)
            qty = float(order.filled_qty)
            order_obj = {'symbol': order.symbol,
                         'side': order.side,
                         'price': f'{price:.5g}',
                         'value': f'{price * qty:.2f}',
                         'time': round_time(filled_at)}
            if order.symbol in position_symbols:
                position_symbols.remove(order.symbol)
            elif not orders_used[i]:
                for j, prev_order in enumerate(orders):
                    if prev_order.filled_at is None or prev_order.symbol != order.symbol:
                        continue
                    prev_filled_at = prev_order.filled_at.tz_convert(TIME_ZONE)
                    if prev_filled_at < filled_at and prev_order.side != order.side:
                        entry_price = float(prev_order.filled_avg_price)
                        order_gl = price / entry_price - 1
                        if prev_order.side == 'sell':
                            order_gl *= -1
                        order_obj['gl'] = get_signed_percentage(order_gl)
                        orders_used[j] = True
                        break
            result.append(order_obj)
        return result

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_current_positions(self):
        result = []
        positions = self._alpaca.list_positions()
        infos = self.get_info_today([p.symbol for p in positions])
        for position in positions:
            symbol = position.symbol
            qty = float(position.qty)
            info = infos[symbol]
            entry_price = float(position.avg_entry_price)
            current_price = info['price']
            value = abs(qty * current_price)
            side = 'long' if qty > 0 else 'short'
            gl = current_price / entry_price - 1
            if side == 'short':
                gl *= -1
            result.append({
                'symbol': symbol,
                'current_price': f'{current_price:.4g}',
                'value': f'{value:.2f}',
                'side': side,
                'change_today': get_signed_percentage(info['change']),
                'gl': get_signed_percentage(gl),
            })
        result.sort(key=lambda p: p['symbol'])
        return result

    def get_info_today(self, symbols: List[str]):
        result = dict()
        last_day = get_last_day()
        calendar = self.get_calendar(last_day.strftime('%F'))
        trades = self._alpaca.get_latest_trades(symbols)
        current_prices = {symbol: trade.p for symbol, trade in trades.items()}
        prev_day = calendar[-2].date.strftime('%F')
        for symbol in symbols:
            bars = self._alpaca.get_bars(symbol,
                                         tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day),
                                         prev_day,
                                         prev_day)
            result[symbol] = {'price': current_prices[symbol],
                              'change': current_prices[symbol] / bars[0].c - 1}
        return result

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_market_watch(self):
        result = dict()
        watch_symbols = ['QQQ', 'SPY', 'DIA', 'TQQQ']
        infos = self.get_info_today(watch_symbols)
        for symbol, info in infos.items():
            result[symbol] = {'price': f'{info["price"]:.2f}',
                              'change': get_signed_percentage(info['change'], with_arrow=True)}
        return result
