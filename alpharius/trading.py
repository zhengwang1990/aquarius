from .common import *
from .data import load_tradable_history, HistoricalDataLoader
from .email import send_email
from concurrent import futures
import alpaca_trade_api as tradeapi
import collections
import datetime
import time
import os
import pandas as pd
import retrying

_DATA_SOURCE = DataSource.POLYGON
_MAX_WORKERS = 10


class Trading:

    def __init__(self, processor_factories: List[ProcessorFactory]) -> None:
        self._output_dir = os.path.join(OUTPUT_ROOT, 'trading', datetime.datetime.now().strftime('%F'))
        os.makedirs(self._output_dir, exist_ok=True)
        logging_config(os.path.join(self._output_dir, 'log.txt'), detail=True)
        self._equity, self._cash = 0, 0
        self._cash_reserve = float(os.environ.get('CASH_RESERVE', 0))
        self._today = pd.to_datetime(
            pd.Timestamp.combine(datetime.datetime.today().date(), datetime.time(0, 0))).tz_localize(TIME_ZONE)
        self._processor_factories = processor_factories
        self._alpaca = tradeapi.REST()
        self._update_account()
        self._update_positions()
        self._processors = []
        self._frequency_to_processor = collections.defaultdict(list)
        self._processor_stock_universes = {}
        self._stock_universe = collections.defaultdict(list)
        self._interday_data = {}
        self._intraday_data = {}
        clock = self._alpaca.get_clock()
        self._market_open = clock.next_open.timestamp()
        self._market_close = clock.next_close.timestamp()
        if self._market_open > self._market_close:
            self._market_open = pd.to_datetime(
                pd.Timestamp.combine(self._today.date(), MARKET_OPEN)).tz_localize(TIME_ZONE).timestamp()

    def _update_account(self) -> None:
        account = self._alpaca.get_account()
        self._equity = float(account.equity)
        self._cash = float(account.cash)
        logging.info('Account updated: equity [%s]; cash [%s].', self._equity, self._cash)

    def _update_positions(self) -> None:
        alpaca_positions = self._alpaca.list_positions()
        self._positions = [Position(position.symbol, float(position.qty),
                                    float(position.avg_entry_price), None)
                           for position in alpaca_positions]
        logging.info('Positions updated: [%d] open positions.', len(self._positions))

    def _init_processors(self, history_start: DATETIME_TYPE) -> None:
        self._processors = []
        for factory in self._processor_factories:
            processor = factory.create(lookback_start_date=history_start,
                                       lookback_end_date=self._today,
                                       data_source=_DATA_SOURCE,
                                       logging_enabled=True)
            self._processors.append(processor)
            self._frequency_to_processor[processor.get_trading_frequency()].append(processor)
        for processor in self._processors:
            processor.setup(self._positions)

    def _init_stock_universe(self) -> None:
        for processor in self._processors:
            processor_name = type(processor).__name__
            processor_stock_universe = processor.get_stock_universe(self._today)
            self._processor_stock_universes[processor_name] = processor_stock_universe
            self._stock_universe[processor.get_trading_frequency()].extend(processor_stock_universe)
        logging.info('Stock universe of the day: %s', self._stock_universe)

    def run(self) -> None:
        # Initialize
        history_start = self._today - datetime.timedelta(days=INTERDAY_LOOKBACK_LOAD)
        self._interday_data = load_tradable_history(history_start, self._today, _DATA_SOURCE)
        self._init_processors(history_start)
        self._init_stock_universe()

        # Wait for market open
        while time.time() < self._market_open:
            time.sleep(10)

        # Process
        processed = []
        while time.time() < self._market_close:
            current_time = pd.to_datetime(pd.Timestamp(int(time.time()), unit='s', tz=TIME_ZONE))
            next_minute = current_time + datetime.timedelta(minutes=1)
            if int(current_time.minute) % 5 == 4:
                checkpoint_time = pd.to_datetime(
                    pd.Timestamp.combine(self._today.date(),
                                         datetime.time(int(next_minute.hour),
                                                       int(next_minute.minute)))).tz_localize(TIME_ZONE)
                trigger_seconds = 40
                if checkpoint_time.timestamp() == self._market_close:
                    trigger_seconds -= 15
                if current_time.second > trigger_seconds and checkpoint_time not in processed:
                    self._process(checkpoint_time)
                    processed.append(checkpoint_time)
                time.sleep(5)

        # Send email
        send_email()

    def _process(self, checkpoint_time: DATETIME_TYPE) -> None:
        logging.info('Process starts for [%s]', checkpoint_time.time())
        frequency_to_process = [TradingFrequency.FIVE_MIN]
        if checkpoint_time.timestamp() == self._market_open:
            frequency_to_process = [TradingFrequency.FIVE_MIN,
                                    TradingFrequency.CLOSE_TO_OPEN]
        elif checkpoint_time.timestamp() == self._market_close:
            frequency_to_process = [TradingFrequency.FIVE_MIN,
                                    TradingFrequency.CLOSE_TO_OPEN,
                                    TradingFrequency.CLOSE_TO_CLOSE]

        self._update_intraday_data(frequency_to_process)

        contexts = {}
        for frequency, symbols in self._stock_universe.items():
            if frequency not in frequency_to_process:
                continue
            for symbol in symbols:
                intraday_lookback = self._intraday_data[symbol]
                interday_lookback = self._interday_data.get(symbol).iloc[-INTERDAY_LOOKBACK_DAYS:]
                if interday_lookback is None or len(interday_lookback) < DAYS_IN_A_MONTH:
                    continue
                if not len(intraday_lookback):
                    continue
                current_price = intraday_lookback['Close'][-1]
                context = Context(symbol=symbol,
                                  current_time=checkpoint_time,
                                  current_price=current_price,
                                  interday_lookback=interday_lookback,
                                  intraday_lookback=intraday_lookback)
                contexts[symbol] = context
        logging.info('Contexts prepared for [%s] symbols.', len(contexts))

        actions = []
        for processor in self._processors:
            if processor.get_trading_frequency() not in frequency_to_process:
                continue
            processor_name = type(processor).__name__
            stock_universe = self._processor_stock_universes[processor_name]
            processor_contexts = []
            for symbol in stock_universe:
                context = contexts.get(symbol)
                if context:
                    processor_contexts.append(context)
            actions.extend(processor.process_all_data(processor_contexts))
        logging.info('Got [%d] actions to process.', len(actions))

        self._trade(actions)

    def _update_intraday_data(self, frequency_to_process: List[TradingFrequency]) -> None:
        update_start = time.time()
        tasks = {}
        data_loader = HistoricalDataLoader(TimeInterval.FIVE_MIN, _DATA_SOURCE)
        with futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            for frequency, symbols in self._stock_universe.items():
                if frequency not in frequency_to_process:
                    continue
                for symbol in symbols:
                    t = pool.submit(data_loader.load_daily_data, symbol, self._today)
                    tasks[symbol] = t
        for symbol, t in tasks.items():
            self._intraday_data[symbol] = t.result()
        logging.info('Intraday data updated for [%d] symbols. Time elapsed [%.2fs]',
                     len(tasks),
                     time.time() - update_start)

    def _get_position(self, symbol: str) -> Optional[Position]:
        for position in self._positions:
            if symbol == position.symbol:
                return position
        return None

    def _trade(self, actions: List[Action]) -> None:
        unique_actions = get_unique_actions(actions)

        close_actions = [action for action in unique_actions
                         if action.type in [ActionType.BUY_TO_CLOSE, ActionType.SELL_TO_CLOSE]]
        self._close_positions(close_actions)

        open_actions = [action for action in unique_actions
                        if action.type in [ActionType.BUY_TO_OPEN, ActionType.SELL_TO_OPEN]]
        self._open_positions(open_actions)

    def _close_positions(self, actions: List[Action]) -> None:
        """Closes positions instructed by input actions."""
        self._update_positions()
        for action in actions:
            assert action.type in [ActionType.BUY_TO_CLOSE, ActionType.SELL_TO_CLOSE]
            symbol = action.symbol
            current_position = self._get_position(symbol)
            if current_position is None:
                logging.info('Position for [%s] does not exist. Skipping close.', symbol)
                continue
            if action.type == ActionType.BUY_TO_CLOSE and current_position.qty > 0:
                logging.info('Position for [%s] is already long-side. Skipping close.', symbol)
                continue
            if action.type == ActionType.SELL_TO_CLOSE and current_position.qty < 0:
                logging.info('Position for [%s] is already short-side. Skipping close.', symbol)
                continue
            qty = int(abs(current_position.qty) * action.percent)
            side = 'buy' if action.type == ActionType.BUY_TO_CLOSE else 'sell'
            self._place_order(symbol, side, qty=qty)

        self._wait_for_order_to_fill()

    def _open_positions(self, actions: List[Action]) -> None:
        """Opens positions instructed by input actions."""
        self._update_account()
        self._update_positions()
        tradable_cash = self._cash - self._cash_reserve
        for position in self._positions:
            if position.qty < 0:
                tradable_cash += position.entry_price * position.qty * (1 + SHORT_RESERVE_RATIO)
        for action in actions:
            assert action.type in [ActionType.BUY_TO_OPEN, ActionType.SELL_TO_OPEN]
            symbol = action.symbol
            if self._get_position(symbol) is not None:
                logging.info('Position for [%s] already exists. Skipping open.', symbol)
                continue
            cash_to_trade = min(tradable_cash / len(actions), tradable_cash * action.percent)
            if cash_to_trade < self._equity * 0.01:
                logging.info('Not enough cash to open [%s]. Skipping open.', symbol)
                continue
            side = 'buy' if action.type == ActionType.BUY_TO_OPEN else 'sell'
            self._place_order(symbol, side, notional=cash_to_trade)

        self._wait_for_order_to_fill()

    @retrying.retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def _place_order(self, symbol: str, side: str,
                     qty: Optional[float] = None,
                     notional: Optional[float] = None,
                     limit_price: Optional[float] = None) -> None:
        order_type = 'market' if limit_price is None else 'limit'
        logging.info('Placing order for [%s]: side [%s]; qty [%s]; notional [%s]; type [%s].',
                     symbol, side, notional, qty, order_type)
        try:
            self._alpaca.submit_order(symbol=symbol, qty=qty, side=side,
                                      type=order_type,
                                      time_in_force='day',
                                      notional=notional,
                                      limit_price=limit_price)
        except tradeapi.rest.APIError as e:
            logging.error('Failed to placer [%s] order for [%s]: %s', side, symbol, e)

    @retrying.retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def _wait_for_order_to_fill(self, timeout: int = 10) -> None:
        orders = self._alpaca.list_orders(status='open')
        if not orders:
            return
        wait_time = 0
        while orders:
            logging.info('Waiting for orders to fill. [%d] open orders remaining.', len(orders))
            time.sleep(2)
            wait_time += 2
            if wait_time >= timeout:
                break
            orders = self._alpaca.list_orders(status='open')
        if not orders:
            logging.info('All orders are filled')
        else:
            logging.warning('[%d] orders not filled', len(orders))
