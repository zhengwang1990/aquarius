from .common import *
from typing import Optional


class NoopProcessor(Processor):

    def __init__(self):
        super().__init__()

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['AAPL', 'AMZN', 'FB', 'GOOG', 'MSFT']

    def handle_data(self, context: Context) -> Optional[Action]:
        if context.current_time.time() == datetime.time(9, 30):
            return Action('MSFT', ActionType.BUY_TO_OPEN, 0.5, 200)
        if context.current_time.time() == datetime.time(12, 0):
            return Action('MSFT', ActionType.SELL_TO_CLOSE, 1, 201)
        return None


class NoopProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self, *args, **kwargs) -> NoopProcessor:
        return NoopProcessor()
