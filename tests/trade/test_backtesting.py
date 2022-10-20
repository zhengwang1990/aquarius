import pandas as pd
import pytest
from alpharius import trade
from alpharius.trade import processors
from ..fakes import FakeProcessorFactory


@pytest.mark.parametrize("trading_frequency",
                         [trade.TradingFrequency.FIVE_MIN,
                          trade.TradingFrequency.CLOSE_TO_CLOSE,
                          trade.TradingFrequency.CLOSE_TO_OPEN])
def test_run_success(trading_frequency):
    fake_processor_factory = FakeProcessorFactory(trading_frequency)
    fake_processor = fake_processor_factory.processor
    backtesting = trade.Backtesting(start_date=pd.to_datetime('2021-03-17'),
                                    end_date=pd.to_datetime('2021-03-24'),
                                    processor_factories=[fake_processor_factory])

    backtesting.run()

    assert fake_processor.get_stock_universe_call_count > 0
    assert fake_processor.process_data_call_count > 0


def test_run_with_processors():
    processor_factories = [processors.OvernightProcessorFactory(),
                           processors.ZScoreProcessorFactory(),
                           processors.O2lProcessorFactory(),
                           processors.O2hProcessorFactory(),
                           processors.BearMomentumProcessorFactory(),
                           processors.HourlyReversionProcessorFactory()]
    backtesting = trade.Backtesting(start_date=pd.to_datetime('2021-03-17'),
                                    end_date=pd.to_datetime('2021-03-18'),
                                    processor_factories=processor_factories)

    backtesting.run()
