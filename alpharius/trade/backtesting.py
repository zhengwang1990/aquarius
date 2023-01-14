import collections
import datetime
import difflib
import functools
import math
import os
import signal
import time
from concurrent import futures
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import alpaca_trade_api as tradeapi
import git
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import tabulate
from alpharius.utils import TIME_ZONE, Transaction, compute_risks, compute_drawdown
from .common import (
    Action, ActionType, Context, Position, Processor, ProcessorFactory, TimeInterval,
    TradingFrequency, Mode, BASE_DIR, DATETIME_TYPE, MARKET_OPEN, MARKET_CLOSE, OUTPUT_DIR,
    DEFAULT_DATA_SOURCE, INTERDAY_LOOKBACK_LOAD, BID_ASK_SPREAD, SHORT_RESERVE_RATIO,
    logging_config, timestamp_to_index, get_unique_actions, get_header, get_processor_name)
from .data_loader import load_cached_daily_data, load_tradable_history

_MAX_WORKERS = 20


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
        self._processors = []
        self._positions = []
        self._daily_equity = [1]
        self._num_win, self._num_lose = 0, 0
        self._cash = 1
        self._interday_data = None

        backtesting_output_dir = os.path.join(OUTPUT_DIR, 'backtesting')
        output_num = 1
        while True:
            output_dir = os.path.join(backtesting_output_dir,
                                      datetime.datetime.now().strftime('%m-%d'),
                                      f'{output_num:02d}')
            if not os.path.exists(output_dir):
                self._output_dir = output_dir
                os.makedirs(output_dir, exist_ok=True)
                break
            output_num += 1

        self._details_log = logging_config(os.path.join(
            self._output_dir, 'details.txt'), detail=False, name='details')
        self._summary_log = logging_config(os.path.join(
            self._output_dir, 'summary.txt'), detail=False, name='summary')

        alpaca = tradeapi.REST()
        calendar = alpaca.get_calendar(start=self._start_date.strftime('%F'),
                                       end=(self._end_date - datetime.timedelta(days=1)).strftime('%F'))
        self._market_dates = [market_day.date for market_day in calendar
                              if market_day.date < self._end_date]
        signal.signal(signal.SIGINT, self._safe_exit)

        self._run_start_time = None
        self._interday_load_time = 0
        self._intraday_load_time = 0
        self._stock_universe_load_time = 0
        self._context_prep_time = 0
        self._data_process_time = 0

    def _safe_exit(self, signum, frame) -> None:
        self._close()
        exit(1)

    def _close(self):
        self._print_profile()
        self._print_summary()
        self._plot_summary()
        for processor in self._processors:
            processor.teardown()

    def _init_processors(self, history_start) -> None:
        self._processors = []
        for factory in self._processor_factories:
            processor = factory.create(lookback_start_date=history_start,
                                       lookback_end_date=self._end_date,
                                       data_source=DEFAULT_DATA_SOURCE,
                                       output_dir=self._output_dir)
            self._processors.append(processor)

    def _record_diff(self):
        repo = git.Repo(BASE_DIR)
        html = ''
        max_num_line = 0
        for item in repo.head.commit.diff(None):
            old_content, new_content = [], []
            if item.change_type != 'A':
                old_content = item.a_blob.data_stream.read().decode('utf-8').split('\n')
            if item.change_type != 'D':
                with open(os.path.join(BASE_DIR, item.b_path), 'r') as f:
                    new_content = f.read().split('\n')
            max_num_line = max(max_num_line, len(old_content), len(new_content))
            html_diff = difflib.HtmlDiff(wrapcolumn=120)
            html += f'<div><h1>{item.b_path}</h1>'
            html += html_diff.make_table(old_content, new_content, context=True)
            html += '</div>'
        if html:
            template_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'html', 'diff.html')
            header_width = (int(np.log10(max_num_line)) + 1) * 7 + 6
            with open(template_file, 'r') as f:
                template = f.read()
            with open(os.path.join(self._output_dir, 'diff.html'), 'w') as f:
                f.write(template.format(header_width=header_width, html=html))

    def run(self) -> List[Transaction]:
        self._run_start_time = time.time()
        try:
            self._record_diff()
        except (git.GitError, ValueError) as e:
            # Git doesn't work in some circumstances
            self._summary_log.warning(f'Diff can not be generated: {e}')
        history_start = self._start_date - datetime.timedelta(days=INTERDAY_LOOKBACK_LOAD)
        self._interday_data = load_tradable_history(
            history_start, self._end_date, DEFAULT_DATA_SOURCE)
        self._interday_load_time += time.time() - self._run_start_time
        self._init_processors(history_start)
        transactions = []
        for day in self._market_dates:
            executed_closes = self._process(day)
            transactions.extend(executed_closes)
        self._close()
        return transactions

    def _load_stock_universe(self,
                             day: DATETIME_TYPE) -> Tuple[Dict[str, List[str]], Dict[TradingFrequency, Set[str]]]:
        load_stock_universe_start = time.time()
        processor_stock_universes = dict()
        stock_universe = collections.defaultdict(set)
        for processor in self._processors:
            processor_name = get_processor_name(processor)
            processor_stock_universe = processor.get_stock_universe(day)
            processor_stock_universes[processor_name] = processor_stock_universe
            stock_universe[processor.get_trading_frequency()].update(
                processor_stock_universe)
        self._stock_universe_load_time += time.time() - load_stock_universe_start
        return processor_stock_universes, stock_universe

    def _process_data(self,
                      contexts: Dict[str, Context],
                      stock_universes: Dict[str, List[str]],
                      processors: List[Processor]) -> List[Action]:
        data_process_start = time.time()

        actions = []
        for processor in processors:
            processor_name = get_processor_name(processor)
            processor_stock_universe = stock_universes[processor_name]
            processor_contexts = []
            for symbol in processor_stock_universe:
                context = contexts.get(symbol)
                if context:
                    processor_contexts.append(context)
            processor_actions = processor.process_all_data(processor_contexts)
            actions.extend([Action(pa.symbol, pa.type, pa.percent,
                                   contexts[pa.symbol].current_price,
                                   processor_name)
                            for pa in processor_actions])

        self._data_process_time += time.time() - data_process_start
        return actions

    @functools.lru_cache()
    def _prepare_interday_lookback(self, day: DATETIME_TYPE, symbol: str) -> Optional[pd.DataFrame]:
        if symbol not in self._interday_data:
            return
        interday_data = self._interday_data[symbol]
        interday_ind = timestamp_to_index(interday_data.index, day)
        if interday_ind is None:
            return
        interday_lookback = interday_data.iloc[:interday_ind]
        return interday_lookback

    @staticmethod
    def _prepare_intraday_lookback(current_interval_start: DATETIME_TYPE, symbol: str,
                                   intraday_datas: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
        intraday_data = intraday_datas[symbol]
        intraday_ind = timestamp_to_index(intraday_data.index, current_interval_start)
        if intraday_ind is None:
            return
        intraday_lookback = intraday_data.iloc[:intraday_ind + 1]
        return intraday_lookback

    def _load_intraday_data(self,
                            day: DATETIME_TYPE,
                            stock_universe: Dict[TradingFrequency, Set[str]]) -> Dict[str, pd.DataFrame]:
        load_intraday_start = time.time()
        intraday_datas = dict()
        tasks = dict()
        unique_stock_universe = set()
        for _, symbols in stock_universe.items():
            unique_stock_universe.update(symbols)
        with futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            for symbol in unique_stock_universe:
                t = pool.submit(load_cached_daily_data, symbol,
                                day, TimeInterval.FIVE_MIN, DEFAULT_DATA_SOURCE)
                tasks[symbol] = t
            for symbol, t in tasks.items():
                intraday_datas[symbol] = t.result()
        self._intraday_load_time += time.time() - load_intraday_start
        return intraday_datas

    def _process(self, day: DATETIME_TYPE) -> List[Transaction]:
        for processor in self._processors:
            processor.setup(self._positions, day)

        processor_stock_universes, stock_universe = self._load_stock_universe(
            day)

        intraday_datas = self._load_intraday_data(day, stock_universe)

        market_open = pd.to_datetime(pd.Timestamp.combine(
            day.date(), MARKET_OPEN)).tz_localize(TIME_ZONE)
        market_close = pd.to_datetime(pd.Timestamp.combine(
            day.date(), MARKET_CLOSE)).tz_localize(TIME_ZONE)
        current_interval_start = market_open

        executed_actions = []
        while current_interval_start < market_close:
            current_time = current_interval_start + datetime.timedelta(minutes=5)

            frequency_to_process = [TradingFrequency.FIVE_MIN]
            if current_interval_start == market_open:
                frequency_to_process = [TradingFrequency.FIVE_MIN,
                                        TradingFrequency.CLOSE_TO_OPEN]
            elif current_time == market_close:
                frequency_to_process = [TradingFrequency.FIVE_MIN,
                                        TradingFrequency.CLOSE_TO_OPEN,
                                        TradingFrequency.CLOSE_TO_CLOSE]

            prep_context_start = time.time()
            contexts = dict()
            unique_symbols = set()
            for frequency, symbols in stock_universe.items():
                if frequency in frequency_to_process:
                    unique_symbols.update(symbols)
            for symbol in unique_symbols:
                intraday_lookback = self._prepare_intraday_lookback(
                    current_interval_start, symbol, intraday_datas)
                if intraday_lookback is None or len(intraday_lookback) == 0:
                    continue
                interday_lookback = self._prepare_interday_lookback(day, symbol)
                if interday_lookback is None or len(interday_lookback) == 0:
                    continue
                current_price = intraday_lookback['Close'][-1]
                context = Context(symbol=symbol,
                                  current_time=current_time,
                                  current_price=current_price,
                                  interday_lookback=interday_lookback,
                                  intraday_lookback=intraday_lookback,
                                  mode=Mode.BACKTEST)
                contexts[symbol] = context
            self._context_prep_time += time.time() - prep_context_start

            processors = []
            for processor in self._processors:
                if processor.get_trading_frequency() in frequency_to_process:
                    processors.append(processor)
            actions = self._process_data(
                contexts, processor_stock_universes, processors)
            current_executed_actions = self._process_actions(current_time, actions)
            executed_actions.extend(current_executed_actions)

            current_interval_start += datetime.timedelta(minutes=5)

        for processor in self._processors:
            processor.teardown()

        self._log_day(day, executed_actions)
        return executed_actions

    def _process_actions(self, current_time: DATETIME_TYPE, actions: List[Action]) -> List[List[Any]]:
        unique_actions = get_unique_actions(actions)

        close_actions = [action for action in unique_actions
                         if action.type in [ActionType.BUY_TO_CLOSE, ActionType.SELL_TO_CLOSE]]
        executed_closes = self._close_positions(current_time, close_actions)

        open_actions = [action for action in unique_actions
                        if action.type in [ActionType.BUY_TO_OPEN, ActionType.SELL_TO_OPEN]]
        self._open_positions(current_time, open_actions)

        return executed_closes

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

    def _close_positions(self, current_time: DATETIME_TYPE, actions: List[Action]) -> List[Transaction]:
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
            if abs(new_qty) > 1E-7:
                self._positions.append(Position(symbol, new_qty,
                                                current_position.entry_price,
                                                current_position.entry_time))
            spread_adjust = (1 - BID_ASK_SPREAD
                             if action.type == ActionType.SELL_TO_CLOSE else 1 + BID_ASK_SPREAD)
            adjusted_action_price = action.price * spread_adjust
            self._cash += adjusted_action_price * qty
            profit = adjusted_action_price / current_position.entry_price - 1
            if action.type == ActionType.BUY_TO_CLOSE:
                profit *= -1
            if profit > 0:
                self._num_win += 1
            else:
                self._num_lose += 1
            executed_actions.append(
                Transaction(symbol, action.type == ActionType.SELL_TO_CLOSE, action.processor,
                            current_position.entry_price, action.price, current_position.entry_time,
                            current_time, qty, profit * qty * current_position.entry_price,
                            profit, None, None))
        return executed_actions

    def _open_positions(self, current_time: DATETIME_TYPE, actions: List[Action]) -> None:
        tradable_cash = self._cash
        for position in self._positions:
            if position.qty < 0:
                tradable_cash += position.entry_price * position.qty * (1 + SHORT_RESERVE_RATIO)
        for action in actions:
            assert action.type in [ActionType.BUY_TO_OPEN, ActionType.SELL_TO_OPEN]
            symbol = action.symbol
            cash_to_trade = min(tradable_cash / len(actions),
                                tradable_cash * action.percent)
            if abs(cash_to_trade) < 1E-7:
                cash_to_trade = 0
            qty = cash_to_trade / action.price
            if action.type == ActionType.SELL_TO_OPEN:
                qty = -qty
            old_position = self._get_current_position(symbol)
            if old_position is None:
                entry_price = action.price
                new_qty = qty
            else:
                self._pop_current_position(symbol)
                if old_position.qty == 0:
                    entry_price = action.price
                else:
                    entry_price = (old_position.entry_price * old_position.qty +
                                   action.price * qty) / (old_position.qty + qty)
                new_qty = qty + old_position.qty
            new_position = Position(symbol, new_qty, entry_price, current_time)
            self._positions.append(new_position)
            self._cash -= action.price * qty

    def _log_day(self,
                 day: DATETIME_TYPE,
                 executed_closes: List[Transaction]) -> None:
        outputs = [get_header(day.date())]
        if executed_closes:
            table_list = [[t.symbol, t.processor, t.entry_time.time(), t.exit_time.time(),
                           'long' if t.is_long else 'short', f'{t.qty:.2g}', t.entry_price, t.exit_price,
                           f'{t.gl_pct * 100:+.2f}%'] for t in executed_closes]
            trade_info = tabulate.tabulate(table_list,
                                           headers=['Symbol', 'Processor', 'Entry Time', 'Exit Time', 'Side',
                                                    'Qty', 'Entry Price', 'Exit Price', 'Gain/Loss'],
                                           tablefmt='grid',
                                           disable_numparse=True)
            outputs.append('[ Trades ]')
            outputs.append(trade_info)

        if self._positions:
            position_info = []
            for position in self._positions:
                interday_data = self._interday_data[position.symbol]
                interday_ind = timestamp_to_index(interday_data.index, day)
                close_price, daily_change = None, None
                if interday_ind is not None:
                    close_price = interday_data['Close'][interday_ind]
                    if interday_ind > 0:
                        daily_change = (close_price / interday_data['Close'][interday_ind - 1] - 1) * 100
                change = (close_price / position.entry_price - 1) * 100 if close_price is not None else None
                value = close_price * position.qty if close_price is not None else None
                position_info.append([position.symbol, f'{position.qty:.2g}', position.entry_price,
                                      close_price,
                                      f'{value:.2g}',
                                      f'{daily_change:+.2f}%' if daily_change is not None else None,
                                      f'{change:+.2f}%' if change is not None else None])
            outputs.append('[ Positions ]')
            outputs.append(tabulate.tabulate(position_info,
                                             headers=['Symbol', 'Qty', 'Entry Price', 'Current Price',
                                                      'Current Value', 'Daily Change', 'Change'],
                                             tablefmt='grid',
                                             disable_numparse=True))

        equity = self._cash
        for position in self._positions:
            interday_data = self._interday_data[position.symbol]
            close_price = interday_data.loc[day]['Close'] if day in interday_data.index else position.entry_price
            equity += position.qty * close_price
        profit_pct = equity / self._daily_equity[-1] - 1 if self._daily_equity[-1] else 0
        self._daily_equity.append(equity)
        total_profit_pct = equity / self._daily_equity[0] - 1
        stats = [['Total Gain/Loss',
                  f'{total_profit_pct * 100:+.2f}%' if total_profit_pct < 10 else f'{total_profit_pct:+.4g}',
                  'Daily Gain/Loss', f'{profit_pct * 100:+.2f}%']]

        outputs.append('[ Stats ]')
        outputs.append(tabulate.tabulate(stats, tablefmt='grid', disable_numparse=True))

        if not executed_closes and not self._positions:
            return
        self._details_log.info('\n'.join(outputs))

    def _print_summary(self) -> None:
        def _profit_to_str(profit_num: float) -> str:
            return f'{profit_num * 100:+.2f}%' if profit_num < 10 else f'{profit_num:+.4g}'

        outputs = [get_header('Summary')]
        n_trades = self._num_win + self._num_lose
        success_rate = self._num_win / n_trades if n_trades > 0 else 0
        market_dates = self._market_dates[:len(self._daily_equity) - 1]
        if not market_dates:
            return
        summary = [['Time Range', f'{market_dates[0].date()} ~ {market_dates[-1].date()}'],
                   ['Success Rate', f'{success_rate * 100:.2f}%'],
                   ['Num of Trades', f'{n_trades} ({n_trades / len(market_dates):.2f} per day)'],
                   ['Output Dir', os.path.relpath(self._output_dir, BASE_DIR)]]
        outputs.append(tabulate.tabulate(summary, tablefmt='grid'))

        print_symbols = ['QQQ', 'SPY', 'TQQQ']
        market_symbol = 'SPY'
        stats = [['', 'My Portfolio'] + print_symbols]
        current_year = self._start_date.year
        current_start = 0
        for i, date in enumerate(market_dates):
            if i != len(market_dates) - 1 and market_dates[i + 1].year != current_year + 1:
                continue
            year_market_last_day_index = timestamp_to_index(
                self._interday_data[market_symbol].index, date)
            year_market_values = self._interday_data[market_symbol]['Close'][
                                 year_market_last_day_index - (i - current_start) - 1:year_market_last_day_index + 1]
            year_profit_number = self._daily_equity[i + 1] / self._daily_equity[current_start] - 1
            year_profit = [f'{current_year} Gain/Loss', _profit_to_str(year_profit_number)]
            _, _, year_sharpe_ratio = compute_risks(
                self._daily_equity[current_start: i + 2], year_market_values)
            year_sharpe = [f'{current_year} Sharpe Ratio',
                           f'{year_sharpe_ratio:.2f}' if not math.isnan(year_sharpe_ratio) else 'N/A']
            for symbol in print_symbols:
                if symbol not in self._interday_data:
                    continue
                last_day_index = timestamp_to_index(
                    self._interday_data[symbol].index, date)
                symbol_values = list(self._interday_data[symbol]['Close'][
                                     last_day_index - (i - current_start) - 1:last_day_index + 1])
                symbol_profit_pct = (symbol_values[-1] / symbol_values[0] - 1) * 100
                _, _, symbol_sharpe = compute_risks(
                    symbol_values, year_market_values)
                year_profit.append(f'{symbol_profit_pct:+.2f}%')
                year_sharpe.append(f'{symbol_sharpe:.2f}' if not math.isnan(symbol_sharpe) else 'N/A')
            stats.append(year_profit)
            stats.append(year_sharpe)
            current_start = i
            current_year += 1
        total_profit_number = self._daily_equity[-1] / self._daily_equity[0] - 1
        total_profit = ['Total Gain/Loss', _profit_to_str(total_profit_number)]
        market_first_day_index = timestamp_to_index(
            self._interday_data[market_symbol].index, market_dates[0])
        market_last_day_index = timestamp_to_index(
            self._interday_data[market_symbol].index, market_dates[-1])
        market_values = self._interday_data[market_symbol]['Close'][
                        market_first_day_index - 1:market_last_day_index + 1]
        my_alpha, my_beta, my_sharpe_ratio = compute_risks(self._daily_equity, market_values)
        my_drawdown, my_hi, my_li = compute_drawdown(self._daily_equity)
        my_drawdown_start = market_dates[max(my_hi - 1, 0)]
        my_drawdown_end = market_dates[max(my_li - 1, 0)]
        alpha_row = ['Alpha', f'{my_alpha * 100:.2f}%' if not math.isnan(my_alpha) else 'N/A']
        beta_row = ['Beta', f'{my_beta:.2f}' if not math.isnan(my_beta) else 'N/A']
        sharpe_ratio_row = ['Sharpe Ratio',
                            f'{my_sharpe_ratio:.2f}' if not math.isnan(my_sharpe_ratio) else 'N/A']
        drawdown_row = ['Drawdown', f'{my_drawdown * 100:+.2f}%']
        drawdown_start_row = ['Drawdown Start', my_drawdown_start.strftime('%F')]
        drawdown_end_row = ['Drawdown End', my_drawdown_end.strftime('%F')]
        for symbol in print_symbols:
            first_day_index = timestamp_to_index(
                self._interday_data[symbol].index, market_dates[0])
            last_day_index = timestamp_to_index(
                self._interday_data[symbol].index, market_dates[-1])
            symbol_values = self._interday_data[symbol]['Close'][first_day_index -
                                                                 1:last_day_index + 1]
            symbol_total_profit_pct = (symbol_values[-1] / symbol_values[0] - 1) * 100
            total_profit.append(f'{symbol_total_profit_pct:+.2f}%')
            symbol_alpha, symbol_beta, symbol_sharpe_ratio = compute_risks(
                symbol_values, market_values)
            alpha_row.append(
                f'{symbol_alpha * 100:.2f}%' if not math.isnan(symbol_alpha) else 'N/A')
            beta_row.append(
                f'{symbol_beta:.2f}' if not math.isnan(symbol_beta) else 'N/A')
            sharpe_ratio_row.append(f'{symbol_sharpe_ratio:.2f}'
                                    if not math.isnan(symbol_sharpe_ratio) else 'N/A')
            symbol_drawdown, symbol_hi, symbol_li = compute_drawdown(symbol_values)
            symbol_drawdown_start = market_dates[max(symbol_hi - 1, 0)]
            symbol_drawdown_end = market_dates[max(symbol_li - 1, 0)]
            drawdown_row.append(f'{symbol_drawdown * 100:+.2f}%')
            drawdown_start_row.append(symbol_drawdown_start.strftime('%F'))
            drawdown_end_row.append(symbol_drawdown_end.strftime('%F'))
        stats.append(total_profit)
        stats.append(alpha_row)
        stats.append(beta_row)
        stats.append(sharpe_ratio_row)
        stats.append(drawdown_row)
        stats.append(drawdown_start_row)
        stats.append(drawdown_end_row)
        outputs.append(tabulate.tabulate(stats, tablefmt='grid', disable_numparse=True))
        self._summary_log.info('\n'.join(outputs))

    def _plot_summary(self) -> None:
        pd.plotting.register_matplotlib_converters()
        plot_symbols = ['QQQ', 'SPY', 'TQQQ']
        color_map = {'QQQ': '#78d237', 'SPY': '#FF6358', 'TQQQ': '#aa46be'}
        formatter = mdates.DateFormatter('%m-%d')
        current_year = self._start_date.year
        current_start = 0
        dates, values = [], [1]
        market_dates = self._market_dates[:len(self._daily_equity) - 1]
        for i, date in enumerate(market_dates):
            dates.append(date)
            values.append(self._daily_equity[i + 1] / self._daily_equity[current_start])
            if i != len(market_dates) - 1 and market_dates[i + 1].year != current_year + 1:
                continue
            dates = [dates[0] - datetime.timedelta(days=1)] + dates
            profit_pct = (self._daily_equity[i + 1] / self._daily_equity[current_start] - 1) * 100
            plt.figure(figsize=(10, 4))
            plt.plot(dates, values,
                     label=f'My Portfolio ({profit_pct:+.2f}%)',
                     color='#28b4c8')
            yscale = 'linear'
            for symbol in plot_symbols:
                if symbol not in self._interday_data:
                    continue
                last_day_index = timestamp_to_index(
                    self._interday_data[symbol].index, date)
                symbol_values = list(self._interday_data[symbol]['Close'][
                                     last_day_index + 1 - len(dates):last_day_index + 1])
                for j in range(len(symbol_values) - 1, -1, -1):
                    symbol_values[j] /= symbol_values[0]
                if symbol == 'TQQQ':
                    if abs(symbol_values[-1] - 1) > 2 * abs(values[-1] - 1):
                        continue
                    elif abs(values[-1] - 1) > 3 * abs(symbol_values[-1] - 1):
                        yscale = 'log'
                plt.plot(dates, symbol_values,
                         label=f'{symbol} ({(symbol_values[-1] - 1) * 100:+.2f}%)',
                         color=color_map[symbol])
            text_kwargs = {'family': 'monospace'}
            plt.xlabel('Date', **text_kwargs)
            plt.ylabel('Normalized Value', **text_kwargs)
            plt.title(f'{current_year} History', **text_kwargs, y=1.15)
            plt.grid(linestyle='--', alpha=0.5)
            plt.legend(ncol=len(plot_symbols) + 1, bbox_to_anchor=(0, 1),
                       loc='lower left', prop=text_kwargs)
            ax = plt.gca()
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.xaxis.set_major_formatter(formatter)
            plt.yscale(yscale)
            plt.tight_layout()
            plt.savefig(os.path.join(self._output_dir, f'{current_year}.png'))
            plt.close()

            dates, values = [], [1]
            current_start = i
            current_year += 1

    def _print_profile(self):
        if self._run_start_time is None:
            return
        txt_output = os.path.join(self._output_dir, 'profile.txt')
        total_time = max(time.time() - self._run_start_time, 1E-7)
        outputs = [get_header('Profile')]
        profile = [
            ['Stage', 'Time Cost (s)', 'Percentage'],
            ['Total', f'{total_time:.0f}', '100%'],
            ['Interday Data Load', f'{self._interday_load_time:.0f}',
             f'{self._interday_load_time / total_time * 100:.0f}%'],
            ['Intraday Data Load', f'{self._intraday_load_time:.0f}',
             f'{self._intraday_load_time / total_time * 100:.0f}%'],
            ['Stock Universe Load', f'{self._stock_universe_load_time:.0f}',
             f'{self._stock_universe_load_time / total_time * 100:.0f}%'],
            ['Context Prepare', f'{self._context_prep_time:.0f}',
             f'{self._context_prep_time / total_time * 100:.0f}%'],
            ['Data Process', f'{self._data_process_time:.0f}',
             f'{self._data_process_time / total_time * 100:.0f}%'],
        ]
        outputs.append(tabulate.tabulate(profile, tablefmt='grid'))
        with open(txt_output, 'w') as f:
            f.write('\n'.join(outputs))
