import pandas as pd

NASDAQ100_SYMBOLS = [
    'ATVI', 'ADBE', 'AMD', 'ALGN', 'GOOGL', 'AMZN', 'AEP', 'AMGN', 'ADI', 'ANSS',
    'AAPL', 'AMAT', 'ASML', 'TEAM', 'ADSK', 'ADP', 'BIDU', 'BIIB', 'BKNG', 'AVGO',
    'CDNS', 'CDW', 'CERN', 'CHTR', 'CHKP', 'CTAS', 'CSCO', 'CTSH', 'CMCSA', 'CPRT',
    'COST', 'CRWD', 'CSX', 'DXCM', 'DOCU', 'DLTR', 'EBAY', 'EA', 'EXC', 'FAST',
    'FISV', 'FOXA', 'GILD', 'HON', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG',
    'JD', 'KDP', 'KLAC', 'KHC', 'LRCX', 'LULU', 'MAR', 'MRVL', 'MTCH', 'MELI',
    'FB', 'MCHP', 'MU', 'MSFT', 'MRNA', 'MDLZ', 'MNST', 'NTES', 'NFLX', 'NVDA',
    'NXPI', 'ORLY', 'OKTA', 'PCAR', 'PAYX', 'PYPL', 'PTON', 'PEP', 'PDD', 'QCOM',
    'REGN', 'ROST', 'SGEN', 'SIRI', 'SWKS', 'SPLK', 'SBUX', 'SNPS', 'TMUS', 'TSLA',
    'TXN', 'TCOM', 'VRSN', 'VRSK', 'VRTX', 'WBA', 'WDAY', 'XEL', 'XLNX', 'ZM',
]


def get_nasdaq100(view_time):
    nasdaq_set = set(NASDAQ100_SYMBOLS)
    if view_time < pd.to_datetime('2021-08-26'):
        nasdaq_set.remove('CRWD')
    if view_time < pd.to_datetime('2021-07-21'):
        nasdaq_set.remove('HON')
    if view_time < pd.to_datetime('2020-12-21'):
        for symbol in ['AEP', 'TEAM', 'MRVL', 'MTCH', 'OKTA', 'PTON']:
            nasdaq_set.remove(symbol)
        for symbol in ['BMRN', 'CTXS', 'EXPE', 'LBTYA', 'TTWO', 'ULTA']:
            nasdaq_set.add(symbol)
    if view_time < pd.to_datetime('2020-10-19'):
        nasdaq_set.remove('KDP')
        nasdaq_set.add('WD')
    if view_time < pd.to_datetime('2020-08-24'):
        nasdaq_set.remove('PDD')
        nasdaq_set.add('NTAP')
    if view_time < pd.to_datetime('2020-07-20'):
        nasdaq_set.remove('MRNA')
        nasdaq_set.add('CSGP')
    if view_time < pd.to_datetime('2020-06-22'):
        nasdaq_set.remove('DOCU')
        nasdaq_set.add('UAL')
    if view_time < pd.to_datetime('2020-04-30'):
        nasdaq_set.remove('ZM')
        nasdaq_set.add('WLTW')
    if view_time < pd.to_datetime('2020-04-20'):
        nasdaq_set.remove('DXCM')
        nasdaq_set.add('AAL')
    if view_time < pd.to_datetime('2019-12-13'):
        for symbol in ['ANSS', 'CDW', 'CPRT', 'CSGP', 'SGEN', 'SPLK']:
            nasdaq_set.remove(symbol)
        for symbol in ['HAS', 'HSIC', 'JBHT', 'NLOK', 'WYNN']:
            nasdaq_set.add(symbol)
    if view_time < pd.to_datetime('2019-11-21'):
        nasdaq_set.remove('EXC')
    if view_time < pd.to_datetime('2018-12-14'):
        for symbol in ['AMD', 'LULU', 'NTAP', 'UAL', 'VRSN', 'WLTW']:
            nasdaq_set.remove(symbol)
        for symbol in ['HOLX', 'QRTEA', 'STX', 'VOD']:
            nasdaq_set.add(symbol)
    if view_time < pd.to_datetime('2018-11-19'):
        nasdaq_set.remove('XEL')
        nasdaq_set.add('XRAY')
    if view_time < pd.to_datetime('2018-11-05'):
        nasdaq_set.remove('NXPI')
    if view_time < pd.to_datetime('2018-07-23'):
        nasdaq_set.remove('PEP')
        nasdaq_set.add('DISH')
    if view_time < pd.to_datetime('2017-12-18'):
        for symbol in ['ASML', 'CDNS', 'SNPS', 'TTWO', 'WDAY']:
            nasdaq_set.remove(symbol)
        for symbol in ['AKAM', 'DISCA', 'NCLH', 'TSCO', 'VIAC']:
            nasdaq_set.add(symbol)
    if view_time < pd.to_datetime('2017-10-23'):
        nasdaq_set.remove('ALGN')
        nasdaq_set.add('MAT')
    if view_time < pd.to_datetime('2017-06-19'):
        nasdaq_set.remove('MELI')
    if view_time < pd.to_datetime('2017-04-24'):
        nasdaq_set.remove('WYNN')
        nasdaq_set.add('TRIP')
    if view_time < pd.to_datetime('2017-03-20'):
        nasdaq_set.remove('IDXX')
        nasdaq_set.add('SPAC')
    if view_time < pd.to_datetime('2017-02-07'):
        nasdaq_set.remove('JBHT')
        nasdaq_set.add('NXPI')
    if view_time < pd.to_datetime('2016-12-19'):
        for symbol in ['CTAS', 'HAS', 'HOLX', 'KLAC']:
            nasdaq_set.remove(symbol)
        for symbol in ['BBBY', 'NTAP', 'SRCL']:
            nasdaq_set.add(symbol)
    if view_time < pd.to_datetime('2016-07-18'):
        nasdaq_set.remove('MCHP')
        nasdaq_set.add('ENDP')
    if view_time < pd.to_datetime('2016-06-20'):
        nasdaq_set.remove('XRAY')
    if view_time < pd.to_datetime('2016-03-16'):
        nasdaq_set.remove('NTES')
    if view_time < pd.to_datetime('2016-02-22'):
        nasdaq_set.remove('CSX')
        nasdaq_set.add('KLAC')
    if view_time < pd.to_datetime('2015-12-21'):
        for symbol in ['TCOM', 'ENDP', 'NCLH', 'TMUS', 'ULTA']:
            nasdaq_set.remove(symbol)
        for symbol in ['CHRW', 'EXPD', 'GRMN', 'KDP', 'VEON', 'WYNN']:
            nasdaq_set.add(symbol)
    if view_time < pd.to_datetime('2015-11-11'):
        nasdaq_set.remove('PYPL')
    if view_time < pd.to_datetime('2015-10-07'):
        nasdaq_set.remove('INCY')
    return list(nasdaq_set)
