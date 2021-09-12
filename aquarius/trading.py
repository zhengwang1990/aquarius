from common import *
import alpaca_trade_api as tradeapi
import datetime

_DATA_SOURCE = DataSource.POLYGON


class Trading:

    def __init__(self, processor_factories: List[ProcessorFactory]):
        trading_output_dir = os.path.join(OUTPUT_ROOT, 'trading')
        os.makedirs(trading_output_dir, exist_ok=True)
        self._equity, self._cash = 0, 0
        self._processor_factories = processor_factories
        self._alpaca = tradeapi.REST()
        self._update_account()
        self._processors = []

    def _update_account(self):
        account = self._alpaca.get_account()
        self._equity = float(account.equity)
        self._cash = float(account.cash)

    def _init_processors(self):
        self._processors = []
        end_date = datetime.datetime.today()
        start_date = end_date - datetime.timedelta(days=CALENDAR_DAYS_IN_A_MONTH)
        for factory in self._processor_factories:
            self._processors.append(factory.create(lookback_start_date=start_date,
                                                   lookback_end_date=end_date,
                                                   data_source=_DATA_SOURCE))

    def run(self):
        self._init_processors()
