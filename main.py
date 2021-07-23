import aquarius
import pandas as pd

# print(aquarius.TimeInterval.FIVE_MIN)

data = aquarius.HistoricalData(aquarius.TimeInterval.FIVE_MIN, aquarius.DataSource.POLYGON)

timestamp = pd.to_datetime('2021-07-19 16:00').tz_localize(tz='US/Eastern')

# print(data.get_daily_data('MSFT', timestamp))

print(data.get_data_list('MSFT',
                         pd.to_datetime('2021-04-09 15:00'),
                         pd.to_datetime('2021-04-11 11:00')))
