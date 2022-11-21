import copy
import datetime
import functools
import math
import os
import threading
import time
from concurrent import futures
from typing import List, Tuple

import alpaca_trade_api as tradeapi
import pandas as pd
import retrying
from alpharius.utils import get_signed_percentage, get_colored_value, TIME_ZONE
from dateutil.relativedelta import relativedelta
from flask import Flask

app = Flask(__name__)

START_DATE = '2022-08-05'


def get_time_vs_equity(history_equity: List[float],
                       history_time: List[int],
                       time_format: str,
                       cash_reserve: float) -> Tuple[List[str], List[float]]:
    time_list = []
    equity_list = []
    n = sum([equity is not None for equity in history_equity])
    for i, (e, t) in enumerate(zip(history_equity[:n], history_time[:n])):
        dt = pd.to_datetime(t, utc=True, unit='s').tz_convert(TIME_ZONE)
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


def round_time(t: pd.Timestamp, time_fmt_with_year: bool):
    fmt = f'<span class="xs-hidden">{"%Y-" if time_fmt_with_year else ""}%m-%d </span>%H:%M'
    if t.second < 30:
        return t.strftime(fmt)
    return (t + datetime.timedelta(minutes=1)).strftime(fmt)


def get_last_day():
    last_day = pd.to_datetime('now', utc=True).tz_convert(TIME_ZONE)
    if last_day.time() < datetime.time(4, 0):
        last_day -= datetime.timedelta(days=1)
    return last_day.date()


class AlpacaClient:

    def __init__(self):
        self._alpaca = tradeapi.REST()
        self._pool = futures.ThreadPoolExecutor(max_workers=10)
        self._lock = threading.RLock()

    @functools.lru_cache(maxsize=5)
    def get_calendar(self, last_day: str):
        calendar = self._alpaca.get_calendar(
            start=max((pd.to_datetime(last_day) - relativedelta(years=5)).strftime('%F'),
                      START_DATE),
            end=last_day)
        return calendar

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_portfolio_histories(self):
        start = time.time()
        result = dict()
        last_day = get_last_day()
        calendar = self.get_calendar(last_day.strftime('%F'))
        result['market_close'] = calendar[-1].close.strftime('%H:%M')
        market_dates = [c.date for c in calendar]
        tasks = dict()
        for start_index, timeframe in [(-1, '5Min'), (0, '1D')]:
            extended_hours = True if start_index == - 1 else False
            tasks[timeframe] = self._pool.submit(self._alpaca.get_portfolio_history,
                                                 date_start=market_dates[start_index].strftime('%F'),
                                                 date_end=market_dates[-1].strftime('%F'),
                                                 timeframe=timeframe,
                                                 extended_hours=extended_hours)
        histories = dict()
        for timeframe in ['5Min', '1D']:
            histories[timeframe] = tasks[timeframe].result()
        cash_reserve = float(os.environ.get('CASH_RESERVE', 0))
        result['time_1d'], result['equity_1d'] = get_time_vs_equity(
            histories['5Min'].equity,
            histories['5Min'].timestamp,
            '%H:%M',
            cash_reserve)
        current_equity = result['equity_1d'][-1]
        result['current_equity'] = f'{current_equity:,.2f}'
        result['time_5y'], result['equity_5y'] = get_time_vs_equity(
            histories['1D'].equity,
            histories['1D'].timestamp,
            '%F',
            cash_reserve)
        time_points = copy.copy(result['time_5y'])
        result['equity_5y'][-1] = current_equity
        result['prev_close'] = (result['equity_5y'][-2]
                                if len(result['equity_5y']) > 2 else math.nan)
        for time_period, time_delta in [('1w', relativedelta(weeks=1)),
                                        ('1m', relativedelta(months=1)),
                                        ('6m', relativedelta(months=6)),
                                        ('1y', relativedelta(years=1))]:
            cut = (last_day - time_delta - relativedelta(days=1)).strftime('%F')
            time_str = 'time_' + time_period
            equity_str = 'equity_' + time_period
            result[time_str] = result[equity_str] = []
            for i in range(len(result['time_5y'])):
                if result['time_5y'][i] > cut and result['equity_5y'][i] > 0:
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
                'green' if change >= 0 else 'red',
                with_arrow=True)
            result['color_' + time_period] = 'green' if change >= 0 else 'red'
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
        compare_symbols = ['QQQ', 'SPY', 'TQQQ']
        for symbol in compare_symbols:
            tasks[symbol] = self._pool.submit(self.get_compare_symbol, symbol,
                                              market_dates[-1].date(), time_points, result)
        for symbol in compare_symbols:
            tasks[symbol].result()
        app.logger.info('Time cost for get_portfolio_histories: [%.2fs]', time.time() - start)
        return result

    def get_compare_symbol(self, symbol: str, last_day, time_points, portfolio_histories):
        day_bars = self._alpaca.get_bars(
            symbol,
            tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute),
            pd.Timestamp.combine(last_day, datetime.time(0, 0)).tz_localize(TIME_ZONE).isoformat(),
            pd.Timestamp.combine(last_day, datetime.time(23, 0)).tz_localize(TIME_ZONE).isoformat())
        dict_1d = dict()
        for bar in day_bars:
            t = pd.to_datetime(bar.t).tz_convert(TIME_ZONE).strftime('%H:%M')
            dict_1d[t] = bar.o
        year_bars = self._alpaca.get_bars(
            symbol,
            tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day),
            time_points[0],
            time_points[-1])
        dict_5y = dict()
        for bar in year_bars:
            t = pd.to_datetime(bar.t).tz_convert(TIME_ZONE).strftime('%F')
            dict_5y[t] = bar.c
        symbol_values = dict()
        for timeframe in ['1d', '1w', '1m', '6m', '1y', '5y']:
            symbol_values[timeframe] = []
            timeline = portfolio_histories['time_' + timeframe]
            dict_ref = dict_1d if timeframe == '1d' else dict_5y
            for t in timeline:
                symbol_values[timeframe].append(dict_ref.get(t))
            symbol_values[timeframe][-1] = day_bars[-1].c
        for timeframe in ['1d', '1w', '1m', '6m', '1y', '5y']:
            if timeframe == '1d':
                symbol_base = dict_5y[time_points[-2]]
                portfolio_base = portfolio_histories['prev_close']
            else:
                symbol_base = symbol_values[timeframe][0]
                portfolio_base = portfolio_histories['equity_' + timeframe][0]
            for i in range(len(symbol_values[timeframe])):
                if symbol_values[timeframe][i] is not None:
                    symbol_values[timeframe][i] = symbol_values[timeframe][i] / symbol_base * portfolio_base
            with self._lock:
                portfolio_histories[symbol.lower() + '_' + timeframe] = symbol_values[timeframe]

    def get_recent_orders(self):
        return self.get_orders(-1, False)

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_orders(self, calendar_index: int, time_fmt_with_year: bool):
        start = time.time()
        result = []
        last_day = get_last_day()
        calendar = self.get_calendar(last_day.strftime('%F'))
        orders = self._alpaca.list_orders(status='closed',
                                          after=calendar[calendar_index - 1].date.strftime('%F'),
                                          direction='desc')
        orders_used = [False] * len(orders)
        positions = self._alpaca.list_positions()
        position_symbols = set([position.symbol for position in positions])
        cut_time = calendar[calendar_index].date.tz_localize(TIME_ZONE)
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
                         'price': f'{price:.4g}',
                         'value': f'{price * qty:.2f}',
                         'time': round_time(filled_at, time_fmt_with_year)}
            if order.symbol in position_symbols:
                position_symbols.remove(order.symbol)
            elif not orders_used[i]:
                for j in range(i + 1, len(orders)):
                    prev_order = orders[j]
                    if prev_order.filled_at is None or prev_order.symbol != order.symbol:
                        continue
                    prev_filled_at = prev_order.filled_at.tz_convert(TIME_ZONE)
                    if prev_filled_at < filled_at and prev_order.side != order.side:
                        entry_price = float(prev_order.filled_avg_price)
                        order_gl = price / entry_price - 1
                        if prev_order.side == 'sell':
                            order_gl *= -1
                        order_obj['entry_price'] = f'{entry_price:.4g}'
                        order_obj['entry_time'] = round_time(prev_filled_at, time_fmt_with_year)
                        order_obj['gl'] = get_signed_percentage(order_gl)
                        orders_used[j] = True
                        break
            result.append(order_obj)
        app.logger.info('Time cost for get_orders: [%.2fs]', time.time() - start)
        return result

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_current_positions(self):
        start = time.time()
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
                'value': f'{value:.2f}' if value < 1000 else f'{value:.0f}',
                'side': side,
                'day_change': get_signed_percentage(info['change']),
                'gl': get_signed_percentage(gl),
            })
        result.sort(key=lambda p: p['symbol'])
        app.logger.info('Time cost for get_current_positions: [%.2fs]', time.time() - start)
        return result

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_info_today(self, symbols: List[str]):
        if not symbols:
            return dict()
        result = dict()
        last_day = get_last_day()
        calendar = self.get_calendar(last_day.strftime('%F'))
        trades = self._alpaca.get_latest_trades(symbols)
        current_prices = {symbol: trade.p for symbol, trade in trades.items()}
        prev_day = calendar[-2].date.strftime('%F')
        tasks = dict()
        for symbol in symbols:
            tasks[symbol] = self._pool.submit(self._alpaca.get_bars,
                                              symbol=symbol,
                                              timeframe=tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day),
                                              start=prev_day,
                                              end=prev_day)
        today_str = datetime.datetime.today().astimezone(TIME_ZONE).strftime('%b %d')
        trading_day = calendar[-1].date.strftime('%b %d')
        for symbol in symbols:
            bars = tasks[symbol].result()
            result[symbol] = {'price': current_prices[symbol],
                              'change': current_prices[symbol] / bars[0].c - 1,
                              'date': trading_day if trading_day != today_str else 'Today'}
        return result

    def get_market_watch(self):
        start = time.time()
        result = dict()
        watch_symbols = ['QQQ', 'SPY', 'DIA', 'TQQQ']
        infos = self.get_info_today(watch_symbols)
        for symbol, info in infos.items():
            result[symbol] = {'price': f'{info["price"]:.2f}',
                              'change': get_signed_percentage(info['change'], with_arrow=True),
                              'date': info['date']}
        app.logger.info('Time cost for get_market_watch: [%.2fs]', time.time() - start)
        return result

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_daily_prices(self):
        start = time.time()
        last_day = get_last_day()
        calendar = self.get_calendar(last_day.strftime('%F'))
        end_date = calendar[-1].date.strftime('%F')
        portfolio_task = self._pool.submit(self._alpaca.get_portfolio_history,
                                           date_start=START_DATE,
                                           date_end=end_date,
                                           timeframe='1D',
                                           extended_hours=False)
        compare_symbols = ['QQQ', 'SPY']
        tasks = dict()
        for symbol in compare_symbols:
            tasks[symbol] = self._pool.submit(self._alpaca.get_bars,
                                              symbol=symbol,
                                              timeframe=tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day),
                                              start=START_DATE,
                                              end=end_date,
                                              adjustment='split')
        portfolio_result = portfolio_task.result()
        portfolio_dates = [pd.to_datetime(t, utc=True, unit='s').tz_convert(TIME_ZONE).strftime('%F')
                           for t in portfolio_result.timestamp]
        cash_reserve = float(os.environ.get('CASH_RESERVE', 0))
        portfolio_values = [e - cash_reserve for e in portfolio_result.equity]
        start_index = 0
        while start_index < len(portfolio_values) and portfolio_values[start_index] == 0:
            start_index += 1
        result = {'dates': portfolio_dates[start_index:],
                  'symbols': ['My Portfolio'] + compare_symbols,
                  'values': [portfolio_values[start_index:]]}
        for symbol in compare_symbols:
            bars = tasks[symbol].result()
            symbol_values = [bar.c for bar in bars]
            assert len(symbol_values) == len(portfolio_values)
            result['values'].append(symbol_values[start_index:])
        app.logger.info('Time cost for get_daily_prices: [%.2fs]', time.time() - start)
        return result

    @retrying.retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
    def get_charts(self, symbol: str, date: str):
        pd_date = pd.to_datetime(date)
        start_time = pd.to_datetime(
            pd.Timestamp.combine(pd_date.date(), datetime.time(0, 0))).tz_localize(TIME_ZONE)
        end_time = pd.to_datetime(
            pd.Timestamp.combine(pd_date.date(), datetime.time(23, 59))).tz_localize(TIME_ZONE)
        bars = self._alpaca.get_bars(symbol=symbol,
                                     timeframe=tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute),
                                     start=start_time.isoformat(),
                                     end=end_time.isoformat(),
                                     adjustment='split')
        prev_day_bar = self._alpaca.get_bars(symbol=symbol,
                                             timeframe=tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day),
                                             start=(pd_date - datetime.timedelta(days=7)).strftime('%F'),
                                             end=(pd_date - datetime.timedelta(days=1)).strftime('%F'),
                                             adjustment='split')[-1]
        labels = []
        values = []
        for bar in bars:
            label = pd.to_datetime(bar.t).tz_convert(TIME_ZONE).strftime('%H:%M')
            labels.append(label)
            value = {'h': bar.h, 'l': bar.l, 'o': bar.o, 'c': bar.c, 'v': bar.v,
                     'x': label, 's': [bar.o, bar.c]}
            values.append(value)
        return {'labels': labels, 'values': values, 'prev_close': prev_day_bar.c}
