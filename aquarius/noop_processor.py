from .common import *
from typing import Optional


class NoopProcessor(Processor):

    def __init__(self):
        super().__init__()

    def get_stock_universe(self, view_time: DATETIME_TYPE) -> List[str]:
        return ['AAPL', 'AMZN', 'FB', 'GOOG', 'MSFT']

    def handle_data(self, context: Context) -> Optional[Action]:
        return


class NoopProcessorFactory(ProcessorFactory):

    def __init__(self):
        super().__init__()

    def create(self, *args, **kwargs) -> NoopProcessor:
        return NoopProcessor()
