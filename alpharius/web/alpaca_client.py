import datetime
import functools
import math
import os

import alpaca_trade_api as tradeapi
import pandas as pd
import pytz
from dateutil.relativedelta import relativedelta

TIME_ZONE = pytz.timezone('America/New_York')


def get_time_vs_equity(history_equity, history_time, time_format, cash_reserve,
                       skip_condition=None):
    time_list = []
    equity_list = []
    n = sum([equity is not None for equity in history_equity])
    for i, (e, t) in enumerate(zip(history_equity[:n], history_time[:n])):
        dt = pd.to_datetime(t, utc=True, unit='s').tz_convert(TIME_ZONE)
        if skip_condition and skip_condition(dt) and i != n - 1:
            continue
        equity_list.append(max(e - cash_reserve, 0))
        time_list.append(dt.strftime(time_format))
    if len(time_list) > 1 and time_list[-2] == time_list[-1]:
        time_list.pop(-2)
        equity_list.pop(-2)
    return time_list, equity_list


class AlpacaClient:

    def __init__(self):
        self._alpaca = tradeapi.REST()

    @functools.lru_cache(maxsize=5)
    def get_calendar(self, last_day: str):
        calendar = self._alpaca.get_calendar(
            start=(pd.to_datetime(last_day) - relativedelta(years=5)).strftime('%F'),
            end=last_day)
        return calendar

    def get_portfolio_histories(self):
        result = dict()
        last_day = datetime.date.today()
        if datetime.datetime.now().time() < datetime.time(4, 0):
            last_day -= datetime.timedelta(days=1)
        calendar = self.get_calendar(last_day.strftime('%F'))
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
                base_value = result['prev_close']
            else:
                base_value = result['equity_' + time_period][0]
            change = current_equity - base_value
            percent = current_equity / base_value - 1
            result['change_' + time_period] = f'{change : .2f} ({percent * 100:+.2f}%)'
            result['color_' + time_period] = 'green' if change > 0 else 'red'
        return result
