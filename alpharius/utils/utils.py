"""Utility functions shared by multiple modules."""

import datetime
import math
import time
from typing import List, Optional, Tuple

import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd
import pytz
import recordclass

TIME_ZONE = pytz.timezone('America/New_York')
Transaction = recordclass.recordclass(
    'Transaction',
    ['symbol', 'is_long', 'processor', 'entry_price', 'exit_price', 'entry_time', 'exit_time',
     'qty', 'gl', 'gl_pct', 'slippage', 'slippage_pct'])


def get_transactions(start_date: Optional[str]) -> List[Transaction]:
    """Gets transactions from start date until today.

    params:
      start_date: The transactions after this date are fetched. Inclusive.
    """

    def round_time(t: pd.Timestamp):
        if t.second > 30:
            t = t + datetime.timedelta(minutes=1)
        return pd.to_datetime(t.strftime('%F %H:%M:00%z'))

    def get_historical_price(symbol, t) -> Optional[float]:
        timeframe = tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute)
        t_str = (t - datetime.timedelta(minutes=5)).isoformat()
        bars = alpaca.get_bars(symbol, timeframe, t_str, t.isoformat())
        if not bars or pd.to_datetime(bars[0].t).timestamp() != t.timestamp() - 300:
            return None
        return bars[0].c

    alpaca = tradeapi.REST()

    chunk_size = 500
    orders = []
    start_time_str = (pd.to_datetime(start_date) - datetime.timedelta(days=7)).tz_localize(TIME_ZONE).isoformat()
    end_time = pd.to_datetime('now', utc=True)
    check_for_more_orders = True
    order_ids = set()
    while check_for_more_orders:
        order_chunk = alpaca.list_orders(status='closed',
                                         after=start_time_str,
                                         until=end_time.isoformat(),
                                         direction='desc',
                                         limit=chunk_size)
        for order in order_chunk:
            if order.id not in order_ids:
                orders.append(order)
                order_ids.add(order.id)
        if len(order_chunk) == chunk_size:
            end_time = orders[-3].submitted_at
        else:
            check_for_more_orders = False

    positions = alpaca.list_positions()
    orders_used = [False] * len(orders)
    position_symbols = set([position.symbol for position in positions])
    cut_time = pd.to_datetime(start_date).tz_localize(TIME_ZONE)
    transactions = []
    for i in range(len(orders)):
        order = orders[i]
        used = orders_used[i]
        if order.filled_at is None or used:
            continue
        filled_at = order.filled_at.tz_convert(TIME_ZONE)
        if filled_at < cut_time:
            break
        entry_time = round_time(filled_at)
        entry_price = float(order.filled_avg_price)
        qty = float(order.filled_qty)
        exit_time = None
        exit_price = None
        gl = None
        gl_pct = None
        slippage = None
        slippage_pct = None
        is_long = order.side == 'buy'
        if order.symbol in position_symbols:
            position_symbols.remove(order.symbol)
        else:
            for j in range(i + 1, len(orders)):
                prev_order = orders[j]
                if prev_order.filled_at is None or prev_order.symbol != order.symbol:
                    continue
                prev_filled_at = prev_order.filled_at.tz_convert(TIME_ZONE)
                if prev_filled_at < filled_at and prev_order.side != order.side:
                    exit_price = entry_price
                    entry_price = float(prev_order.filled_avg_price)
                    gl = (exit_price - entry_price) * qty
                    gl_pct = exit_price / entry_price - 1
                    is_long = prev_order.side == 'buy'
                    if not is_long:
                        gl *= -1
                        gl_pct *= -1
                    exit_time = entry_time
                    entry_time = round_time(prev_filled_at)
                    theory_entry_price = get_historical_price(order.symbol, entry_time)
                    theory_exit_price = get_historical_price(order.symbol, exit_time)
                    if theory_entry_price and theory_exit_price:
                        theory_gl_pct = theory_exit_price / theory_entry_price - 1
                        if not is_long:
                            theory_gl_pct *= -1
                        slippage_pct = gl_pct - theory_gl_pct
                        slippage = slippage_pct * qty * entry_price
                    orders_used[j] = True
                    break
        transactions.append(
            Transaction(order.symbol, is_long, None, entry_price, exit_price, entry_time,
                        exit_time, qty, gl, gl_pct, slippage, slippage_pct))
    return transactions


def get_colored_value(value: str, color: str, with_arrow: bool = False) -> str:
    """Returns HTML of a value with color annotations.

    params:
      value: The string value to be colored.
      color: The color applied to the value. Can be green or red.
      with_arrow: If an arrow icon is attached to the front of the value.
    """
    arrow = ''
    if with_arrow:
        if color == 'green':
            arrow = '<i class="uil uil-arrow-up"></i>'
        else:
            arrow = '<i class="uil uil-arrow-down"></i>'
    return f'<span style="color:{color};">{arrow}{value}</span>'


def get_signed_percentage(value: float, with_arrow: bool = False) -> str:
    """Returns HTML of a percentage value with sign and color annotations.

    params:
      value: The float value to be annotated with sign and color.
      with_arrow: If an arrow icon is attached to the front of the value.
    """
    color = 'green' if value >= 0 else 'red'
    return get_colored_value(f'{value * 100:+.2f}%', color, with_arrow)


def get_current_time() -> pd.Timestamp:
    """Gets current time of NY time zone."""
    # Use time.time() instead of 'now' so that it can be mocked in test.
    return pd.to_datetime(time.time(), utc=True, unit='s').tz_convert(TIME_ZONE)


def get_today() -> pd.Timestamp:
    """Gets a datetime object of today at 00:00 NY time."""
    # Mocking time.time() will change the behavior of the method.
    return pd.to_datetime(
        pd.Timestamp.combine(get_current_time().date(),
                             datetime.time(0, 0))).tz_localize(TIME_ZONE)


def get_latest_day():
    """Gets the latest day of trading.

    If the time is before pre-market open it returns previous day.
    """
    latest_day = get_current_time()
    if latest_day.time() < datetime.time(4, 0):
        latest_day -= datetime.timedelta(days=1)
    return latest_day.date()


def compute_risks(values: List[float],
                  market_values: List[float]) -> Tuple[Optional[float], Optional[float], float]:
    """Computes alpha, beta and sharpe ratio risk factors.

    params:
      values: The values of the target.
      market_values: The market value. Typically, this is S&P 500 values.

    returns:
      A tuple consists of alpha, beta and sharpe ratio, in order.
    """
    profits = [values[k + 1] / values[k] -
               1 for k in range(len(values) - 1)]
    r = np.average(profits)
    std = np.std(profits)
    s = r / std * np.sqrt(252) if std > 0 else math.nan
    a, b = math.nan, math.nan
    if len(values) == len(market_values) and len(values) > 2:
        market_profits = [market_values[k + 1] / market_values[k] - 1
                          for k in range(len(market_values) - 1)]
        mr = np.average(market_profits)
        mvar = np.var(market_profits)
        b = np.cov(market_profits, profits, bias=True)[0, 1] / mvar
        a = (r - b * mr) * np.sqrt(252)
    return a, b, s


def compute_drawdown(values: List[float]) -> Tuple[float, int, int]:
    """Computes drawdown of the target."""
    h = values[0]
    ci = 0
    d = 0
    hi, li = 0, 0
    for i, v in enumerate(values):
        new_d = v / h - 1
        if new_d <= d:
            d = new_d
            hi = ci
            li = i
        elif v > h:
            h = v
            ci = i
    return d, hi, li


def construct_charts_link(symbol: str, date: str):
    """Constructs link to charts page for the given symbol on a given day."""
    start_date = (pd.to_datetime(date) - datetime.timedelta(days=92)).strftime('%F')
    return f'charts?date={date}&start_date={start_date}&end_date={date}&symbol={symbol}'
