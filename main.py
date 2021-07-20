import aquarius
import pandas as pd


data = aquarius.HistoricalData(aquarius.TimeInterval.FIVE_MIN, aquarius.DataSource.POLYGON)

timestamp = pd.to_datetime('2021-07-19 13:45')

print(data.get_data_point('MSFT', timestamp))