from .common import *
from .data import load_tradable_history, HistoricalDataLoader
from concurrent import futures
import alpaca_trade_api as tradeapi
import datetime
import time
import pandas as pd
import retrying

_DATA_SOURCE = DataSource.POLYGON
_MAX_WORKERS = 20


class Trading:

    def __init__(self, processor_factories: List[ProcessorFactory]) -> None:
        self._output_dir = os.path.join(OUTPUT_ROOT, 'trading', datetime.datetime.now().strftime('%F'))
        os.makedirs(self._output_dir, exist_ok=True)
        logging_config(os.path.join(self._output_dir, 'log.txt'), detail_info=True)
        self._equity, self._cash = 0, 0
        self._today = pd.to_datetime(
            pd.Timestamp.combine(datetime.datetime.today().date(), datetime.time(0, 0))).tz_localize(TIME_ZONE)
        self._processor_factories = processor_factories
        self._alpaca = tradeapi.REST()
        self._update_account()
        self._update_positions()
        self._processors = []
        self._processor_stock_universes = {}
        self._stock_universe = []
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

    def _update_positions(self) -> None:
        self._positions = self._list_positions()

    def _init_processors(self, history_start: DATETIME_TYPE) -> None:
        self._processors = []
        for factory in self._processor_factories:
            self._processors.append(factory.create(lookback_start_date=history_start,
                                                   lookback_end_date=self._today,
                                                   data_source=_DATA_SOURCE))
        for processor in self._processors:
            processor.setup(self._positions)

    def _init_stock_universe(self) -> None:
        stock_universe = []
        for processor in self._processors:
            processor_name = type(processor).__name__
            processor_stock_universe = processor.get_stock_universe(self._today)
            self._processor_stock_universes[processor_name] = processor_stock_universe
            stock_universe.extend(processor_stock_universe)
        self._stock_universe = list(set(stock_universe))
        logging.info('Stock universe of the day: %s', self._stock_universe)

    def run(self) -> None:
        # Initialize
        history_start = self._today - datetime.timedelta(days=CALENDAR_DAYS_IN_A_MONTH)
        self._interday_data = load_tradable_history(history_start, self._today, _DATA_SOURCE)
        self._init_processors(history_start)
        self._init_stock_universe()

        # Wait for market open
        while time.time() < self._market_open:
            time.sleep(10)

        # Process
        processed = []
        while time.time() < self._market_close:
            current_time = pd.to_datetime(datetime.datetime.fromtimestamp(time.time())).tz_localize(TIME_ZONE)
            next_minute = current_time + datetime.timedelta(minutes=1)
            if int(current_time.minute) % 5 == 4:
                checkpoint_time = pd.to_datetime(
                    pd.Timestamp.combine(self._today.date(),
                                         datetime.time(next_minute.hour,
                                                       next_minute.minute))).tz_localize(TIME_ZONE)
                trigger_seconds = 40
                if checkpoint_time.time() == MARKET_CLOSE:
                    trigger_seconds -= 40
                if current_time.second > trigger_seconds and checkpoint_time not in processed:
                    self._process(checkpoint_time)
                processed.append(checkpoint_time)
                time.sleep(5)

    def _process(self, checkpoint_time: DATETIME_TYPE) -> None:
        logging.info('Process starts for [%s]', checkpoint_time)
        self._update_intraday_data()

        contexts = {}
        for symbol in self._stock_universe:
            intraday_lookback = self._intraday_data[symbol]
            interday_lookback = self._interday_data[symbol]
            current_price = intraday_lookback['Close'][-1]
            context = Context(symbol=symbol,
                              current_time=checkpoint_time,
                              current_price=current_price,
                              interday_lookback=interday_lookback,
                              intraday_lookback=intraday_lookback)
            contexts[symbol] = context

        actions = []
        for processor in self._processors:
            processor_name = type(processor).__name__
            stock_universe = self._processor_stock_universes[processor_name]
            for symbol in stock_universe:
                context = contexts.get(symbol)
                action = processor.process_data(context)
                if action is not None:
                    actions.append(action)

        self._trade(actions)

    def _update_intraday_data(self) -> None:
        update_start = time.time()
        tasks = {}
        data_loader = HistoricalDataLoader(TimeInterval.FIVE_MIN, _DATA_SOURCE)
        with futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            for symbol in self._stock_universe:
                t = pool.submit(data_loader.load_daily_data, symbol, self._today)
                tasks[symbol] = t
        for symbol, t in tasks.items():
            self._intraday_data[symbol] = t.result()
        logging.info('Intraday data updated for [%d] symbols. Time elapsed [%.2fs]',
                     len(self._stock_universe),
                     time.time() - update_start)

    def _list_positions(self) -> List[Position]:
        alpaca_positions = self._alpaca.list_positions()
        return [Position(position.symbol, position.qty, position.avg_entry_price, None)
                for position in alpaca_positions]

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
                continue
            if action.type == ActionType.BUY_TO_CLOSE and current_position.qty > 0:
                continue
            if action.type == ActionType.SELL_TO_CLOSE and current_position.qty < 0:
                continue
            qty = int(abs(current_position.qty) * action.percent)
            side = 'buy' if action.type == ActionType.BUY_TO_CLOSE else 'sell'
            self._order(symbol, qty, side, limit_price=action.price)

        self._wait_for_order_to_fill()

    def _open_positions(self, actions: List[Action]) -> None:
        """Opens positions instructed by input actions."""
        self._update_account()
        self._update_positions()
        tradable_cash = self._cash
        for position in self._positions:
            if position.qty < 0:
                tradable_cash += position.entry_price * position.qty * (1 + SHORT_RESERVE_RATIO)
        for action in actions:
            assert action.type in [ActionType.BUY_TO_OPEN, ActionType.SELL_TO_OPEN]
            symbol = action.symbol
            if self._get_position(symbol) is not None:
                continue
            cash_to_trade = min(tradable_cash / len(actions), tradable_cash * action.percent)
            qty = int(cash_to_trade / action.price)
            if qty == 0:
                continue
            side = 'buy' if action.type == ActionType.BUY_TO_OPEN else 'sell'
            self._order(symbol, qty, side, limit_price=action.price)

        self._wait_for_order_to_fill()

    @retrying.retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def _order(self, symbol: str, qty: float, side: str, limit_price: Optional[float] = None):
        if qty <= 0:
            return
        logging.info('Placing order for [%s]: side [%s]; qty [%s]; type [%s].',
                     symbol, side, qty, 'market' if limit_price is None else 'limit')
        try:
            if limit_price is not None:
                self._alpaca.submit_order(symbol, qty, side, 'limit', 'day',
                                          limit_price=str(limit_price))
            else:
                self._alpaca.submit_order(symbol, qty, side, 'market', 'day')
        except tradeapi.rest.APIError as e:
            logging.error('Failed to placer [%s] order for [%s]: %s', side, symbol, e)

    @retrying.retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000)
    def _wait_for_order_to_fill(self, timeout=10):
        orders = self._alpaca.list_orders(status='open')
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
            return

        logging.info('Replacing [%d] remaining orders.', len(orders))
        new_orders = []
        for order in orders:
            symbol = order.symbol
            qty = order.qty - order.filled_qty
            side = order.side
            try:
                self._alpaca.cancel_order(order.id)
                new_orders.append({'symbol': symbol, 'qty': qty, 'side': side})
            except tradeapi.rest.APIError as e:
                logging.error('Failed to replace [%s] order for [%s]: %s', side, symbol, e)

        orders = self._alpaca.list_orders(status='open')
        for _ in range(10):
            if not orders:
                break
            logging.info('Wait for orders to cancel. [%d] open orders remaining.', len(orders))
            time.sleep(0.5)
            orders = self._alpaca.list_orders(status='open')
        for order in new_orders:
            self._order(order['symbol'], order['qty'], order['side'])
