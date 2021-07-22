import aquarius
import pandas as pd
import pprint


data = aquarius.HistoricalData(aquarius.TimeInterval.FIVE_MIN, aquarius.DataSource.POLYGON)

timestamp = pd.to_datetime('2021-07-19 16:00').tz_localize(tz='US/Eastern')

print(data.get_daily_data('MSFT', timestamp))