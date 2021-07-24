from aquarius import *
import pandas as pd

# print(aquarius.TimeInterval.FIVE_MIN)

data = HistoricalData(TimeInterval.DAY, DataSource.POLYGON)

timestamp = pd.to_datetime('2021-07-19 16:00').tz_localize(tz='US/Eastern')

#print(data.get_daily_data('MSFT', timestamp))

#print(data.get_data_list('MSFT',
#                         pd.to_datetime('2021-04-09'),
#                         pd.to_datetime('2021-04-16')))

data_cache = HistoricalDataCache(TimeInterval.DAY, DataSource.POLYGON)
res = data_cache.load_history(['AAPL', 'MSFT', 'GOOG', 'FB', 'AMZN'],
                              pd.to_datetime('2020-01-01'), pd.to_datetime('2021-07-21'))
print(res['GOOG'])
