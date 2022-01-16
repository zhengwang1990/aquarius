import pandas as pd

NASDAQ100_SYMBOLS = [
    'ATVI', 'ADBE', 'AMD', 'ABNB', 'ALGN', 'GOOGL', 'AMZN', 'AEP', 'AMGN',
    'ADI', 'ANSS', 'AAPL', 'AMAT', 'ASML', 'TEAM', 'ADSK', 'ADP', 'BIDU', 'BIIB',
    'BKNG', 'AVGO', 'CDNS', 'CHTR', 'CTAS', 'CSCO', 'CTSH', 'CMCSA', 'CPRT', 'COST',
    'CRWD', 'CSX', 'DDOG', 'DXCM', 'DOCU', 'DLTR', 'EBAY', 'EA', 'EXC', 'FAST',
    'FISV', 'FTNT', 'GILD', 'HON', 'IDXX', 'ILMN', 'INTC', 'INTU', 'ISRG', 'JD',
    'KDP', 'KLAC', 'KHC', 'LRCX', 'LCID', 'LULU', 'MAR', 'MRVL', 'MTCH', 'MELI',
    'FB', 'MCHP', 'MU', 'MSFT', 'MRNA', 'MDLZ', 'MNST', 'NTES', 'NFLX', 'NVDA',
    'NXPI', 'ORLY', 'OKTA', 'PCAR', 'PANW', 'PAYX', 'PYPL', 'PTON', 'PEP', 'PDD',
    'QCOM', 'REGN', 'ROST', 'SGEN', 'SIRI', 'SWKS', 'SPLK', 'SBUX', 'SNPS', 'TMUS',
    'TSLA', 'TXN', 'VRSN', 'VRSK', 'VRTX', 'WBA', 'WDAY', 'XEL', 'XLNX', 'ZM', 'ZS'
]


def get_nasdaq100(view_time):
    nasdaq_set = set(NASDAQ100_SYMBOLS)
    view_date = pd.Timestamp(view_time.date())
    if view_date < pd.to_datetime('2021-12-20'):
        for symbol in ['ABNB', 'DDOG', 'FTNT', 'LCID', 'PANW', 'ZS']:
            nasdaq_set.discard(symbol)
        for symbol in ['CDW', 'CERN', 'CHKP', 'FOXA', 'INCY', 'TCOM']:
            nasdaq_set.add(symbol)
    if view_date < pd.to_datetime('2021-08-26'):
        nasdaq_set.discard('CRWD')
    if view_date < pd.to_datetime('2021-07-21'):
        nasdaq_set.discard('HON')
    if view_date < pd.to_datetime('2020-12-21'):
        for symbol in ['AEP', 'TEAM', 'MRVL', 'MTCH', 'OKTA', 'PTON']:
            nasdaq_set.discard(symbol)
        for symbol in ['BMRN', 'CTXS', 'EXPE', 'LBTYA', 'TTWO', 'ULTA']:
            nasdaq_set.add(symbol)
    if view_date < pd.to_datetime('2020-10-19'):
        nasdaq_set.discard('KDP')
        nasdaq_set.add('WD')
    if view_date < pd.to_datetime('2020-08-24'):
        nasdaq_set.discard('PDD')
        nasdaq_set.add('NTAP')
    if view_date < pd.to_datetime('2020-07-20'):
        nasdaq_set.discard('MRNA')
        nasdaq_set.add('CSGP')
    if view_date < pd.to_datetime('2020-06-22'):
        nasdaq_set.discard('DOCU')
        nasdaq_set.add('UAL')
    if view_date < pd.to_datetime('2020-04-30'):
        nasdaq_set.discard('ZM')
        nasdaq_set.add('WLTW')
    if view_date < pd.to_datetime('2020-04-20'):
        nasdaq_set.discard('DXCM')
        nasdaq_set.add('AAL')
    if view_date < pd.to_datetime('2019-12-13'):
        for symbol in ['ANSS', 'CDW', 'CPRT', 'CSGP', 'SGEN', 'SPLK']:
            nasdaq_set.discard(symbol)
        for symbol in ['HAS', 'HSIC', 'JBHT', 'NLOK', 'WYNN']:
            nasdaq_set.add(symbol)
    if view_date < pd.to_datetime('2019-11-21'):
        nasdaq_set.discard('EXC')
    if view_date < pd.to_datetime('2018-12-14'):
        for symbol in ['AMD', 'LULU', 'NTAP', 'UAL', 'VRSN', 'WLTW']:
            nasdaq_set.discard(symbol)
        for symbol in ['HOLX', 'QRTEA', 'STX', 'VOD']:
            nasdaq_set.add(symbol)
    if view_date < pd.to_datetime('2018-11-19'):
        nasdaq_set.discard('XEL')
        nasdaq_set.add('XRAY')
    if view_date < pd.to_datetime('2018-11-05'):
        nasdaq_set.discard('NXPI')
    if view_date < pd.to_datetime('2018-07-23'):
        nasdaq_set.discard('PEP')
        nasdaq_set.add('DISH')
    if view_date < pd.to_datetime('2017-12-18'):
        for symbol in ['ASML', 'CDNS', 'SNPS', 'TTWO', 'WDAY']:
            nasdaq_set.discard(symbol)
        for symbol in ['AKAM', 'DISCA', 'NCLH', 'TSCO', 'VIAC']:
            nasdaq_set.add(symbol)
    if view_date < pd.to_datetime('2017-10-23'):
        nasdaq_set.discard('ALGN')
        nasdaq_set.add('MAT')
    if view_date < pd.to_datetime('2017-06-19'):
        nasdaq_set.discard('MELI')
    if view_date < pd.to_datetime('2017-04-24'):
        nasdaq_set.discard('WYNN')
        nasdaq_set.add('TRIP')
    if view_date < pd.to_datetime('2017-03-20'):
        nasdaq_set.discard('IDXX')
        nasdaq_set.add('SPAC')
    if view_date < pd.to_datetime('2017-02-07'):
        nasdaq_set.discard('JBHT')
        nasdaq_set.add('NXPI')
    if view_date < pd.to_datetime('2016-12-19'):
        for symbol in ['CTAS', 'HAS', 'HOLX', 'KLAC']:
            nasdaq_set.discard(symbol)
        for symbol in ['BBBY', 'NTAP', 'SRCL']:
            nasdaq_set.add(symbol)
    if view_date < pd.to_datetime('2016-07-18'):
        nasdaq_set.discard('MCHP')
        nasdaq_set.add('ENDP')
    if view_date < pd.to_datetime('2016-06-20'):
        nasdaq_set.discard('XRAY')
    if view_date < pd.to_datetime('2016-03-16'):
        nasdaq_set.discard('NTES')
    if view_date < pd.to_datetime('2016-02-22'):
        nasdaq_set.discard('CSX')
        nasdaq_set.add('KLAC')
    if view_date < pd.to_datetime('2015-12-21'):
        for symbol in ['TCOM', 'ENDP', 'NCLH', 'TMUS', 'ULTA']:
            nasdaq_set.discard(symbol)
        for symbol in ['CHRW', 'EXPD', 'GRMN', 'KDP', 'VEON', 'WYNN']:
            nasdaq_set.add(symbol)
    if view_date < pd.to_datetime('2015-11-11'):
        nasdaq_set.discard('PYPL')
    if view_date < pd.to_datetime('2015-10-07'):
        nasdaq_set.discard('INCY')
    return list(nasdaq_set)


SP500_SYMBOLS = [
    'MMM', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADBE', 'AMD', 'AAP', 'AES', 'AFL',
    'A', 'APD', 'AKAM', 'ALK', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL',
    'MO', 'AMZN', 'AMCR', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK',
    'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'ADI', 'ANSS', 'ANTM', 'AON', 'AOS', 'APA',
    'AAPL', 'AMAT', 'APTV', 'ADM', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP',
    'AZO', 'AVB', 'AVY', 'BKR', 'BLL', 'BAC', 'BBWI', 'BAX', 'BDX', 'BRK.B', 'BBY',
    'BIO', 'TECH', 'BIIB', 'BLK', 'BK', 'BA', 'BKNG', 'BWA', 'BXP', 'BSX', 'BMY',
    'AVGO', 'BR', 'BRO', 'BF.B', 'CHRW', 'CDNS', 'CZR', 'CPB', 'COF', 'CAH', 'KMX',
    'CCL', 'CARR', 'CTLT', 'CAT', 'CBOE', 'CBRE', 'CDW', 'CE', 'CNC', 'CNP', 'CDAY',
    'CERN', 'CF', 'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF',
    'CTAS', 'CSCO', 'C', 'CFG', 'CTXS', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL',
    'CMCSA', 'CMA', 'CAG', 'COP', 'ED', 'STZ', 'COO', 'CPRT', 'GLW', 'CTVA', 'COST',
    'CTRA', 'CCI', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE', 'DAL',
    'XRAY', 'DVN', 'DXCM', 'FANG', 'DLR', 'DFS', 'DISCA', 'DISH', 'DG',
    'DLTR', 'D', 'DPZ', 'DOV', 'DOW', 'DTE', 'DUK', 'DRE', 'DD', 'DXC', 'EMN',
    'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'EMR', 'ENPH', 'ETR', 'EOG', 'EPAM',
    'EFX', 'EQIX', 'EQR', 'ESS', 'EL', 'ETSY', 'EVRG', 'ES', 'RE', 'EXC', 'EXPE',
    'EXPD', 'EXR', 'XOM', 'FFIV', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FE', 'FRC',
    'FISV', 'FLT', 'FMC', 'F', 'FTNT', 'FTV', 'FBHS', 'FOXA', 'FOX', 'BEN', 'FCX',
    'GPS', 'GRMN', 'IT', 'GNRC', 'GD', 'GE', 'GIS', 'GM', 'GPC', 'GILD', 'GL',
    'GPN', 'GS', 'GWW', 'HAL', 'HBI', 'HIG', 'HAS', 'HCA', 'PEAK', 'HSIC', 'HSY',
    'HES', 'HPE', 'HLT', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUM',
    'HBAN', 'HII', 'IEX', 'IDXX', 'INFO', 'ITW', 'ILMN', 'INCY', 'IR', 'INTC',
    'ICE', 'IBM', 'IP', 'IPG', 'IFF', 'INTU', 'ISRG', 'IVZ', 'IPGP', 'IQV', 'IRM',
    'JKHY', 'J', 'JBHT', 'SJM', 'JNJ', 'JCI', 'JPM', 'JNPR', 'K', 'KEY', 'KEYS',
    'KMB', 'KIM', 'KMI', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS',
    'LEG', 'LDOS', 'LEN', 'LLY', 'LNC', 'LIN', 'LYV', 'LKQ', 'LMT', 'L', 'LOW',
    'LUMN', 'LYB', 'MTB', 'MRO', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM', 'MAS', 'MA',
    'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'FB', 'MET', 'MTD', 'MGM', 'MCHP',
    'MU', 'MSFT', 'MAA', 'MRNA', 'MHK', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS',
    'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NWL', 'NEM', 'NWSA', 'NWS',
    'NEE', 'NLSN', 'NKE', 'NI', 'NSC', 'NTRS', 'NOC', 'NLOK', 'NCLH', 'NRG', 'NUE',
    'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'OKE', 'ORCL', 'OGN',
    'OTIS', 'PCAR', 'PKG', 'PH', 'PAYX', 'PAYC', 'PYPL', 'PENN', 'PNR', 'PBCT',
    'PEP', 'PKI', 'PFE', 'PM', 'PSX', 'PNW', 'PXD', 'PNC', 'POOL', 'PPG', 'PPL',
    'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PTC', 'PEG', 'PSA', 'PHM', 'PVH', 'QRVO',
    'PWR', 'QCOM', 'DGX', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG',
    'RMD', 'RHI', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB',
    'STX', 'SEE', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SNA', 'SO', 'LUV', 'SWK',
    'SBUX', 'STT', 'STE', 'SYK', 'SIVB', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW',
    'TTWO', 'TPR', 'TGT', 'TEL', 'TDY', 'TFX', 'TER', 'TSLA', 'TXN', 'TXT', 'TMO',
    'TJX', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 'TWTR', 'TYL', 'TSN', 'UDR',
    'ULTA', 'USB', 'UAA', 'UA', 'UNP', 'UAL', 'UNH', 'UPS', 'URI', 'UHS', 'VLO',
    'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VFC', 'VIAC', 'VTRS', 'V', 'VNO', 'VMC',
    'WRB', 'WAB', 'WMT', 'WBA', 'DIS', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST',
    'WDC', 'WU', 'WRK', 'WY', 'WHR', 'WMB', 'WLTW', 'WYNN', 'XEL', 'XLNX', 'XYL',
    'YUM', 'ZBRA', 'ZBH', 'ZION', 'ZTS'
]


def get_sp500(view_time):
    sp500_set = set(SP500_SYMBOLS)
    view_date = pd.Timestamp(view_time.date())
    if view_date < pd.to_datetime('December 14, 2021'):
        sp500_set.discard('EPAM')
        sp500_set.add('KSU')
    if view_date < pd.to_datetime('September 20, 2021'):
        sp500_set.discard('MTCH')
        sp500_set.add('PRGO')
    if view_date < pd.to_datetime('September 20, 2021'):
        sp500_set.discard('CDAY')
        sp500_set.add('UNM')
    if view_date < pd.to_datetime('September 20, 2021'):
        sp500_set.discard('BRO')
        sp500_set.add('NOV')
    if view_date < pd.to_datetime('August 30, 2021'):
        sp500_set.discard('TECH')
        sp500_set.add('MXIM')
    if view_date < pd.to_datetime('July 21, 2021'):
        sp500_set.discard('MRNA')
        sp500_set.add('ALXN')
    if view_date < pd.to_datetime('June 4, 2021'):
        sp500_set.add('HFC')
    if view_date < pd.to_datetime('June 3, 2021'):
        sp500_set.discard('OGN')
    if view_date < pd.to_datetime('May 14, 2021'):
        sp500_set.discard('CRL')
        sp500_set.add('FLIR')
    if view_date < pd.to_datetime('April 20, 2021'):
        sp500_set.discard('PTC')
        sp500_set.add('VAR')
    if view_date < pd.to_datetime('March 22, 2021'):
        sp500_set.discard('NXPI')
        sp500_set.add('FLS')
    if view_date < pd.to_datetime('March 22, 2021'):
        sp500_set.discard('PENN')
        sp500_set.add('SLG')
    if view_date < pd.to_datetime('March 22, 2021'):
        sp500_set.discard('GNRC')
        sp500_set.add('XRX')
    if view_date < pd.to_datetime('March 22, 2021'):
        sp500_set.discard('CZR')
        sp500_set.add('VNT')
    if view_date < pd.to_datetime('February 12, 2021'):
        sp500_set.discard('MPWR')
        sp500_set.add('FTI')
    if view_date < pd.to_datetime('January 21, 2021'):
        sp500_set.discard('TRMB')
        sp500_set.add('CXO')
    if view_date < pd.to_datetime('January 7, 2021'):
        sp500_set.discard('ENPH')
        sp500_set.add('TIF')
    if view_date < pd.to_datetime('December 21, 2020'):
        sp500_set.discard('TSLA')
        sp500_set.add('AIV')
    if view_date < pd.to_datetime('October 12, 2020'):
        sp500_set.add('NBL')
    if view_date < pd.to_datetime('October 9, 2020'):
        sp500_set.discard('VNT')
    if view_date < pd.to_datetime('October 7, 2020'):
        sp500_set.discard('POOL')
        sp500_set.add('ETFC')
    if view_date < pd.to_datetime('September 21, 2020'):
        sp500_set.discard('ETSY')
        sp500_set.add('HRB')
    if view_date < pd.to_datetime('September 21, 2020'):
        sp500_set.discard('TER')
        sp500_set.add('COTY')
    if view_date < pd.to_datetime('September 21, 2020'):
        sp500_set.discard('CTLT')
        sp500_set.add('KSS')
    if view_date < pd.to_datetime('June 22, 2020'):
        sp500_set.discard('BIO')
        sp500_set.add('ADS')
    if view_date < pd.to_datetime('June 22, 2020'):
        sp500_set.discard('TDY')
        sp500_set.add('HOG')
    if view_date < pd.to_datetime('June 22, 2020'):
        sp500_set.discard('TYL')
        sp500_set.add('JWN')
    if view_date < pd.to_datetime('May 22, 2020'):
        sp500_set.discard('WST')
        sp500_set.add('HP')
    if view_date < pd.to_datetime('May 12, 2020'):
        sp500_set.discard('DPZ')
        sp500_set.add('CPRI')
    if view_date < pd.to_datetime('May 12, 2020'):
        sp500_set.discard('DXCM')
        sp500_set.add('AGN')
    if view_date < pd.to_datetime('April 6, 2020'):
        sp500_set.add('M')
    if view_date < pd.to_datetime('April 6, 2020'):
        sp500_set.add('RTN')
    if view_date < pd.to_datetime('April 3, 2020'):
        sp500_set.discard('OTIS')
    if view_date < pd.to_datetime('April 3, 2020'):
        sp500_set.discard('CARR')
    if view_date < pd.to_datetime('April 1, 2020'):
        sp500_set.discard('HWM')
        sp500_set.add('ARNC')
    if view_date < pd.to_datetime('March 2, 2020'):
        sp500_set.discard('IR')
        sp500_set.add('XEC')
    if view_date < pd.to_datetime('January 28, 2020'):
        sp500_set.discard('PAYC')
        sp500_set.add('WCG')
    if view_date < pd.to_datetime('December 23, 2019'):
        sp500_set.discard('LYV')
        sp500_set.add('AMG')
    if view_date < pd.to_datetime('December 23, 2019'):
        sp500_set.discard('ZBRA')
        sp500_set.add('TRIP')
    if view_date < pd.to_datetime('December 23, 2019'):
        sp500_set.discard('STE')
        sp500_set.add('MAC')
    if view_date < pd.to_datetime('December 9, 2019'):
        sp500_set.discard('ODFL')
        sp500_set.add('STI')
    if view_date < pd.to_datetime('December 5, 2019'):
        sp500_set.discard('WRB')
        sp500_set.add('VIAB')
    if view_date < pd.to_datetime('November 21, 2019'):
        sp500_set.discard('NOW')
        sp500_set.add('CELG')
    if view_date < pd.to_datetime('October 3, 2019'):
        sp500_set.discard('LVS')
        sp500_set.add('NKTR')
    if view_date < pd.to_datetime('September 26, 2019'):
        sp500_set.discard('NVR')
        sp500_set.add('JEF')
    if view_date < pd.to_datetime('September 23, 2019'):
        sp500_set.discard('CDW')
        sp500_set.add('TSS')
    if view_date < pd.to_datetime('August 9, 2019'):
        sp500_set.discard('LDOS')
        sp500_set.add('APC')
    if view_date < pd.to_datetime('August 9, 2019'):
        sp500_set.discard('IEX')
        sp500_set.add('FL')
    if view_date < pd.to_datetime('July 15, 2019'):
        sp500_set.discard('TMUS')
        sp500_set.add('RHT')
    if view_date < pd.to_datetime('July 1, 2019'):
        sp500_set.discard('MKTX')
        sp500_set.add('LLL')
    if view_date < pd.to_datetime('June 7, 2019'):
        sp500_set.discard('AMCR')
        sp500_set.add('MAT')
    if view_date < pd.to_datetime('June 3, 2019'):
        sp500_set.discard('DD')
        sp500_set.add('DWDP')
    if view_date < pd.to_datetime('June 3, 2019'):
        sp500_set.discard('CTVA')
        sp500_set.add('FLR')
    if view_date < pd.to_datetime('April 2, 2019'):
        sp500_set.discard('DOW')
        sp500_set.add('BHF')
    if view_date < pd.to_datetime('February 27, 2019'):
        sp500_set.discard('WAB')
        sp500_set.add('GT')
    if view_date < pd.to_datetime('February 15, 2019'):
        sp500_set.discard('ATO')
        sp500_set.add('NFX')
    if view_date < pd.to_datetime('January 18, 2019'):
        sp500_set.discard('TFX')
        sp500_set.add('PCG')
    if view_date < pd.to_datetime('January 2, 2019'):
        sp500_set.discard('FRC')
        sp500_set.add('SCG')
    if view_date < pd.to_datetime('December 24, 2018'):
        sp500_set.discard('CE')
        sp500_set.add('ESRX')
    if view_date < pd.to_datetime('December 3, 2018'):
        sp500_set.discard('LW')
        sp500_set.add('COL')
    if view_date < pd.to_datetime('December 3, 2018'):
        sp500_set.discard('MXIM')
        sp500_set.add('AET')
    if view_date < pd.to_datetime('December 3, 2018'):
        sp500_set.discard('FANG')
        sp500_set.add('SRCL')
    if view_date < pd.to_datetime('November 13, 2018'):
        sp500_set.discard('JKHY')
        sp500_set.add('EQT')
    if view_date < pd.to_datetime('November 6, 2018'):
        sp500_set.discard('KEYS')
        sp500_set.add('CA')
    if view_date < pd.to_datetime('October 11, 2018'):
        sp500_set.discard('FTNT')
        sp500_set.add('EVHC')
    if view_date < pd.to_datetime('October 1, 2018'):
        sp500_set.discard('ROL')
        sp500_set.add('ANDV')
    if view_date < pd.to_datetime('September 14, 2018'):
        sp500_set.discard('WCG')
        sp500_set.add('XL')
    if view_date < pd.to_datetime('August 28, 2018'):
        sp500_set.discard('ANET')
        sp500_set.add('GGP')
    if view_date < pd.to_datetime('July 2, 2018'):
        sp500_set.discard('CPRT')
        sp500_set.add('DPS')
    if view_date < pd.to_datetime('June 20, 2018'):
        sp500_set.discard('FLT')
        sp500_set.add('TWX')
    if view_date < pd.to_datetime('June 18, 2018'):
        sp500_set.discard('BR')
        sp500_set.add('RRC')
    if view_date < pd.to_datetime('June 18, 2018'):
        sp500_set.discard('HFC')
        sp500_set.add('AYI')
    if view_date < pd.to_datetime('June 7, 2018'):
        sp500_set.discard('TWTR')
        sp500_set.add('MON')
    if view_date < pd.to_datetime('June 5, 2018'):
        sp500_set.discard('EVRG')
        sp500_set.add('NAVI')
    if view_date < pd.to_datetime('May 31, 2018'):
        sp500_set.discard('ABMD')
        sp500_set.add('WYN')
    if view_date < pd.to_datetime('April 4, 2018'):
        sp500_set.discard('MSCI')
        sp500_set.add('CSRA')
    if view_date < pd.to_datetime('March 19, 2018'):
        sp500_set.discard('TTWO')
        sp500_set.add('SIG')
    if view_date < pd.to_datetime('March 19, 2018'):
        sp500_set.discard('SIVB')
        sp500_set.add('PDCO')
    if view_date < pd.to_datetime('March 19, 2018'):
        sp500_set.discard('NKTR')
        sp500_set.add('CHK')
    if view_date < pd.to_datetime('March 7, 2018'):
        sp500_set.discard('IPGP')
        sp500_set.add('SNI')
    if view_date < pd.to_datetime('January 3, 2018'):
        sp500_set.discard('HII')
        sp500_set.add('BCR')
    if view_date < pd.to_datetime('October 13, 2017'):
        sp500_set.discard('NCLH')
        sp500_set.add('LVLT')
    if view_date < pd.to_datetime('September 18, 2017'):
        sp500_set.discard('CDNS')
        sp500_set.add('SPLS')
    if view_date < pd.to_datetime('September 1, 2017'):
        sp500_set.discard('DWDP')
        sp500_set.add('DOW')
    if view_date < pd.to_datetime('September 1, 2017'):
        sp500_set.discard('SBAC')
        sp500_set.add('DD')
    if view_date < pd.to_datetime('August 29, 2017'):
        sp500_set.discard('Q')
        sp500_set.add('WFM')
    if view_date < pd.to_datetime('August 8, 2017'):
        sp500_set.discard('BHF')
        sp500_set.add('AN')
    if view_date < pd.to_datetime('July 26, 2017'):
        sp500_set.discard('DRE')
        sp500_set.add('RIG')
    if view_date < pd.to_datetime('July 26, 2017'):
        sp500_set.discard('AOS')
        sp500_set.add('BBBY')
    if view_date < pd.to_datetime('July 26, 2017'):
        sp500_set.discard('PKG')
        sp500_set.add('MUR')
    if view_date < pd.to_datetime('July 26, 2017'):
        sp500_set.discard('RMD')
        sp500_set.add('MNK')
    if view_date < pd.to_datetime('July 26, 2017'):
        sp500_set.discard('MGM')
        sp500_set.add('RAI')
    if view_date < pd.to_datetime('June 19, 2017'):
        sp500_set.discard('HLT')
        sp500_set.add('YHOO')
    if view_date < pd.to_datetime('June 19, 2017'):
        sp500_set.discard('ALGN')
        sp500_set.add('TDC')
    if view_date < pd.to_datetime('June 19, 2017'):
        sp500_set.discard('ANSS')
        sp500_set.add('R')
    if view_date < pd.to_datetime('June 19, 2017'):
        sp500_set.discard('RE')
        sp500_set.add('MJN')
    if view_date < pd.to_datetime('June 2, 2017'):
        sp500_set.discard('INFO')
        sp500_set.add('TGNA')
    if view_date < pd.to_datetime('April 5, 2017'):
        sp500_set.discard('IT')
        sp500_set.add('DNB')
    if view_date < pd.to_datetime('April 4, 2017'):
        sp500_set.discard('DXC')
        sp500_set.add('SWN')
    if view_date < pd.to_datetime('March 20, 2017'):
        sp500_set.discard('AMD')
        sp500_set.add('URBN')
    if view_date < pd.to_datetime('March 20, 2017'):
        sp500_set.discard('RJF')
        sp500_set.add('FTR')
    if view_date < pd.to_datetime('March 20, 2017'):
        sp500_set.discard('ARE')
        sp500_set.add('FSLR')
    if view_date < pd.to_datetime('March 16, 2017'):
        sp500_set.discard('SNPS')
        sp500_set.add('HAR')
    if view_date < pd.to_datetime('March 13, 2017'):
        sp500_set.discard('DISH')
        sp500_set.add('LLTC')
    if view_date < pd.to_datetime('March 2, 2017'):
        sp500_set.discard('REG')
        sp500_set.add('ENDP')
    if view_date < pd.to_datetime('March 1, 2017'):
        sp500_set.discard('CBOE')
        sp500_set.add('PBI')
    if view_date < pd.to_datetime('February 28, 2017'):
        sp500_set.discard('INCY')
        sp500_set.add('SE')
    if view_date < pd.to_datetime('January 5, 2017'):
        sp500_set.discard('IDXX')
        sp500_set.add('STJ')
    if view_date < pd.to_datetime('December 2, 2016'):
        sp500_set.discard('MAA')
        sp500_set.add('OI')
    if view_date < pd.to_datetime('December 2, 2016'):
        sp500_set.discard('EVHC')
        sp500_set.add('LM')
    if view_date < pd.to_datetime('November 1, 2016'):
        sp500_set.discard('ARNC')
        sp500_set.add('AA')
    if view_date < pd.to_datetime('September 30, 2016'):
        sp500_set.discard('COTY')
        sp500_set.add('DO')
    if view_date < pd.to_datetime('September 22, 2016'):
        sp500_set.discard('COO')
        sp500_set.add('HOT')
    if view_date < pd.to_datetime('September 8, 2016'):
        sp500_set.discard('CHTR')
        sp500_set.add('EMC')
    if view_date < pd.to_datetime('September 6, 2016'):
        sp500_set.discard('MTD')
        sp500_set.add('TYC')
    if view_date < pd.to_datetime('July 5, 2016'):
        sp500_set.discard('FTV')
        sp500_set.add('CPGX')
    if view_date < pd.to_datetime('July 1, 2016'):
        sp500_set.discard('LNT')
        sp500_set.add('GAS')
    if view_date < pd.to_datetime('July 1, 2016'):
        sp500_set.discard('ALB')
        sp500_set.add('TE')
    if view_date < pd.to_datetime('June 22, 2016'):
        sp500_set.discard('FBHS')
        sp500_set.add('CVC')
    if view_date < pd.to_datetime('June 3, 2016'):
        sp500_set.discard('TDG')
        sp500_set.add('BXLT')
    if view_date < pd.to_datetime('May 31, 2016'):
        sp500_set.discard('AJG')
        sp500_set.add('CCE')
    if view_date < pd.to_datetime('May 23, 2016'):
        sp500_set.discard('LKQ')
        sp500_set.add('ARG')
    if view_date < pd.to_datetime('May 18, 2016'):
        sp500_set.discard('DLR')
        sp500_set.add('TWC')
    if view_date < pd.to_datetime('May 13, 2016'):
        sp500_set.discard('ALK')
        sp500_set.add('SNDK')
    if view_date < pd.to_datetime('May 3, 2016'):
        sp500_set.discard('AYI')
        sp500_set.add('ADT')
    if view_date < pd.to_datetime('April 25, 2016'):
        sp500_set.discard('GPN')
        sp500_set.add('GME')
    if view_date < pd.to_datetime('April 18, 2016'):
        sp500_set.discard('ULTA')
        sp500_set.add('THC')
    if view_date < pd.to_datetime('April 8, 2016'):
        sp500_set.discard('UA')
    if view_date < pd.to_datetime('April 4, 2016'):
        sp500_set.discard('FL')
        sp500_set.add('CAM')
    if view_date < pd.to_datetime('March 30, 2016'):
        sp500_set.discard('HOLX')
        sp500_set.add('POM')
    if view_date < pd.to_datetime('March 30, 2016'):
        sp500_set.discard('CNC')
        sp500_set.add('ESV')
    if view_date < pd.to_datetime('March 7, 2016'):
        sp500_set.discard('UDR')
        sp500_set.add('GMCR')
    if view_date < pd.to_datetime('March 4, 2016'):
        sp500_set.discard('AWK')
        sp500_set.add('CNX')
    if view_date < pd.to_datetime('February 22, 2016'):
        sp500_set.discard('CXO')
        sp500_set.add('PCL')
    if view_date < pd.to_datetime('February 1, 2016'):
        sp500_set.discard('CFG')
        sp500_set.add('PCP')
    if view_date < pd.to_datetime('February 1, 2016'):
        sp500_set.discard('FRT')
        sp500_set.add('BRCM')
    if view_date < pd.to_datetime('January 19, 2016'):
        sp500_set.discard('EXR')
        sp500_set.add('ACE')
    if view_date < pd.to_datetime('January 5, 2016'):
        sp500_set.discard('WLTW')
        sp500_set.add('FOSL')
    if view_date < pd.to_datetime('December 29, 2015'):
        sp500_set.discard('CHD')
        sp500_set.add('ALTR')
    if view_date < pd.to_datetime('December 15, 2015'):
        sp500_set.add('CMCSK')
    if view_date < pd.to_datetime('December 1, 2015'):
        sp500_set.discard('CSRA')
        sp500_set.add('CSC')
    if view_date < pd.to_datetime('November 19, 2015'):
        sp500_set.discard('ILMN')
        sp500_set.add('SIAL')
    if view_date < pd.to_datetime('November 18, 2015'):
        sp500_set.discard('SYF')
        sp500_set.add('GNW')
    if view_date < pd.to_datetime('November 2, 2015'):
        sp500_set.discard('HPE')
        sp500_set.add('HCBK')
    if view_date < pd.to_datetime('October 7, 2015'):
        sp500_set.discard('VRSK')
        sp500_set.add('JOY')
    if view_date < pd.to_datetime('September 18, 2015'):
        sp500_set.discard('CMCSK')
    if view_date < pd.to_datetime('September 18, 2015'):
        sp500_set.discard('FOX')
    if view_date < pd.to_datetime('September 18, 2015'):
        sp500_set.discard('NWS')
    if view_date < pd.to_datetime('September 2, 2015'):
        sp500_set.discard('UAL')
        sp500_set.add('HSP')
    if view_date < pd.to_datetime('August 28, 2015'):
        sp500_set.discard('ATVI')
        sp500_set.add('PLL')
    if view_date < pd.to_datetime('July 29, 2015'):
        sp500_set.discard('SIG')
        sp500_set.add('DTV')
    if view_date < pd.to_datetime('July 20, 2015'):
        sp500_set.discard('PYPL')
        sp500_set.add('NE')
    if view_date < pd.to_datetime('July 8, 2015'):
        sp500_set.discard('AAP')
        sp500_set.add('FDO')
    if view_date < pd.to_datetime('July 6, 2015'):
        sp500_set.discard('KHC')
        sp500_set.add('KRFT')
    if view_date < pd.to_datetime('July 2, 2015'):
        sp500_set.discard('CPGX')
        sp500_set.add('ATI')
    if view_date < pd.to_datetime('July 1, 2015'):
        sp500_set.discard('JBHT')
        sp500_set.add('TEG')
    if view_date < pd.to_datetime('July 1, 2015'):
        sp500_set.discard('BXLT')
        sp500_set.add('QEP')
    if view_date < pd.to_datetime('June 11, 2015'):
        sp500_set.discard('QRVO')
        sp500_set.add('LO')
    if view_date < pd.to_datetime('April 7, 2015'):
        sp500_set.discard('O')
        sp500_set.add('WIN')
    if view_date < pd.to_datetime('March 23, 2015'):
        sp500_set.discard('AAL')
        sp500_set.add('AGN')
    if view_date < pd.to_datetime('March 23, 2015'):
        sp500_set.discard('EQIX')
        sp500_set.add('DNR')
    if view_date < pd.to_datetime('March 23, 2015'):
        sp500_set.discard('SLG')
        sp500_set.add('NBR')
    if view_date < pd.to_datetime('March 23, 2015'):
        sp500_set.discard('HBI')
        sp500_set.add('AVP')
    if view_date < pd.to_datetime('March 18, 2015'):
        sp500_set.discard('HSIC')
        sp500_set.add('CFN')
    if view_date < pd.to_datetime('March 12, 2015'):
        sp500_set.discard('SWKS')
        sp500_set.add('PETM')
    if view_date < pd.to_datetime('January 27, 2015'):
        sp500_set.discard('HCA')
        sp500_set.add('SWY')
    if view_date < pd.to_datetime('January 27, 2015'):
        sp500_set.discard('ENDP')
        sp500_set.add('COV')
    if view_date < pd.to_datetime('December 5, 2014'):
        sp500_set.discard('RCL')
        sp500_set.add('BMS')
    if view_date < pd.to_datetime('November 5, 2014'):
        sp500_set.discard('LVLT')
        sp500_set.add('JBL')
    if view_date < pd.to_datetime('September 20, 2014'):
        sp500_set.discard('URI')
        sp500_set.add('BTU')
    if view_date < pd.to_datetime('September 20, 2014'):
        sp500_set.discard('UHS')
        sp500_set.add('GHC')
    if view_date < pd.to_datetime('August 18, 2014'):
        sp500_set.discard('MNK')
        sp500_set.add('RDC')
    if view_date < pd.to_datetime('August 6, 2014'):
        sp500_set.discard('DISCK')
    if view_date < pd.to_datetime('July 2, 2014'):
        sp500_set.discard('MLM')
        sp500_set.add('X')
    if view_date < pd.to_datetime('July 1, 2014'):
        sp500_set.discard('AMG')
        sp500_set.add('FRX')
    if view_date < pd.to_datetime('June 20, 2014'):
        sp500_set.discard('XEC')
        sp500_set.add('IGT')
    if view_date < pd.to_datetime('May 8, 2014'):
        sp500_set.discard('AVGO')
        sp500_set.add('LSI')
    if view_date < pd.to_datetime('May 1, 2014'):
        sp500_set.discard('UAA')
        sp500_set.add('BEAM')
    if view_date < pd.to_datetime('May 1, 2014'):
        sp500_set.discard('NAVI')
        sp500_set.add('SLM')
    if view_date < pd.to_datetime('April 3, 2014'):
        sp500_set.discard('GOOGL')
    if view_date < pd.to_datetime('April 2, 2014'):
        sp500_set.discard('ESS')
        sp500_set.add('CLF')
    if view_date < pd.to_datetime('March 21, 2014'):
        sp500_set.discard('GMCR')
        sp500_set.add('WPX')
    if view_date < pd.to_datetime('January 24, 2014'):
        sp500_set.discard('TSCO')
        sp500_set.add('LIFE')
    if view_date < pd.to_datetime('December 23, 2013'):
        sp500_set.discard('ADS')
        sp500_set.add('ANF')
    if view_date < pd.to_datetime('December 23, 2013'):
        sp500_set.discard('MHK')
        sp500_set.add('JDSU')
    if view_date < pd.to_datetime('December 23, 2013'):
        sp500_set.discard('FB')
        sp500_set.add('TER')
    if view_date < pd.to_datetime('December 10, 2013'):
        sp500_set.discard('GGP')
        sp500_set.add('MOLX')
    if view_date < pd.to_datetime('December 2, 2013'):
        sp500_set.discard('ALLE')
        sp500_set.add('JCP')
    if view_date < pd.to_datetime('November 13, 2013'):
        sp500_set.discard('KORS')
        sp500_set.add('NYX')
    if view_date < pd.to_datetime('October 29, 2013'):
        sp500_set.discard('RIG')
        sp500_set.add('DELL')
    if view_date < pd.to_datetime('September 20, 2013'):
        sp500_set.discard('VRTX')
        sp500_set.add('AMD')
    if view_date < pd.to_datetime('September 20, 2013'):
        sp500_set.discard('AME')
        sp500_set.add('SAI')
    if view_date < pd.to_datetime('September 10, 2013'):
        sp500_set.discard('DAL')
        sp500_set.add('BMC')
    if view_date < pd.to_datetime('July 8, 2013'):
        sp500_set.discard('NLSN')
        sp500_set.add('S')
    if view_date < pd.to_datetime('June 28, 2013'):
        sp500_set.discard('FOXA')
        sp500_set.add('APOL')
    if view_date < pd.to_datetime('June 21, 2013'):
        sp500_set.discard('ZTS')
        sp500_set.add('FHN')
    if view_date < pd.to_datetime('June 6, 2013'):
        sp500_set.discard('GM')
        sp500_set.add('HNZ')
    if view_date < pd.to_datetime('May 23, 2013'):
        sp500_set.discard('KSU')
        sp500_set.add('DF')
    if view_date < pd.to_datetime('May 8, 2013'):
        sp500_set.discard('MAC')
        sp500_set.add('CVH')
    if view_date < pd.to_datetime('April 30, 2013'):
        sp500_set.discard('REGN')
        sp500_set.add('PCS')
    if view_date < pd.to_datetime('February 15, 2013'):
        sp500_set.discard('PVH')
        sp500_set.add('BIG')
    if view_date < pd.to_datetime('December 31, 2012'):
        sp500_set.discard('ABBV')
        sp500_set.add('FII')
    if view_date < pd.to_datetime('December 21, 2012'):
        sp500_set.discard('DLPH')
        sp500_set.add('TIE')
    if view_date < pd.to_datetime('December 11, 2012'):
        sp500_set.discard('GRMN')
        sp500_set.add('RRD')
    if view_date < pd.to_datetime('December 3, 2012'):
        sp500_set.discard('DG')
        sp500_set.add('CBE')
    if view_date < pd.to_datetime('October 10, 2012'):
        sp500_set.discard('PETM')
        sp500_set.add('SUN')
    if view_date < pd.to_datetime('October 2, 2012'):
        sp500_set.discard('KRFT')
        sp500_set.add('ANR')
    if view_date < pd.to_datetime('October 1, 2012'):
        sp500_set.discard('ADT')
        sp500_set.add('LXK')
    if view_date < pd.to_datetime('October 1, 2012'):
        sp500_set.discard('PNR')
        sp500_set.add('DV')
    if view_date < pd.to_datetime('September 5, 2012'):
        sp500_set.discard('LYB')
        sp500_set.add('SHLD')
    if view_date < pd.to_datetime('July 31, 2012'):
        sp500_set.discard('ESV')
        sp500_set.add('GR')
    if view_date < pd.to_datetime('July 2, 2012'):
        sp500_set.discard('STX')
        sp500_set.add('PGN')
    if view_date < pd.to_datetime('June 29, 2012'):
        sp500_set.discard('MNST')
        sp500_set.add('SLE')
    if view_date < pd.to_datetime('June 5, 2012'):
        sp500_set.discard('LRCX')
        sp500_set.add('NVLS')
    if view_date < pd.to_datetime('May 21, 2012'):
        sp500_set.discard('ALXN')
        sp500_set.add('MMI')
    if view_date < pd.to_datetime('May 17, 2012'):
        sp500_set.discard('KMI')
        sp500_set.add('EP')
    if view_date < pd.to_datetime('April 23, 2012'):
        sp500_set.discard('PSX')
        sp500_set.add('SVU')
    if view_date < pd.to_datetime('April 3, 2012'):
        sp500_set.discard('FOSL')
        sp500_set.add('MHS')
    if view_date < pd.to_datetime('March 13, 2012'):
        sp500_set.discard('CCI')
        sp500_set.add('CEG')
    if view_date < pd.to_datetime('December 31, 2011'):
        sp500_set.discard('WPX')
        sp500_set.add('CPWR')
    if view_date < pd.to_datetime('December 20, 2011'):
        sp500_set.discard('TRIP')
        sp500_set.add('TLAB')
    if view_date < pd.to_datetime('December 16, 2011'):
        sp500_set.discard('BWA')
        sp500_set.add('AKS')
    if view_date < pd.to_datetime('December 16, 2011'):
        sp500_set.discard('PRGO')
        sp500_set.add('MWW')
    if view_date < pd.to_datetime('December 16, 2011'):
        sp500_set.discard('DLTR')
        sp500_set.add('WFR')
    if view_date < pd.to_datetime('December 12, 2011'):
        sp500_set.discard('GAS')
        sp500_set.add('GAS')
    if view_date < pd.to_datetime('November 18, 2011'):
        sp500_set.discard('CBE')
        sp500_set.add('JNS')
    if view_date < pd.to_datetime('October 31, 2011'):
        sp500_set.discard('XYL')
        sp500_set.add('ITT')
    if view_date < pd.to_datetime('October 14, 2011'):
        sp500_set.discard('TEL')
        sp500_set.add('CEPH')
    if view_date < pd.to_datetime('September 23, 2011'):
        sp500_set.discard('MOS')
        sp500_set.add('NSM')
    if view_date < pd.to_datetime('July 5, 2011'):
        sp500_set.discard('ACN')
        sp500_set.add('MI')
    if view_date < pd.to_datetime('June 30, 2011'):
        sp500_set.discard('MPC')
        sp500_set.add('RSH')
    if view_date < pd.to_datetime('June 1, 2011'):
        sp500_set.discard('ANR')
        sp500_set.add('MEE')
    if view_date < pd.to_datetime('April 27, 2011'):
        sp500_set.discard('CMG')
        sp500_set.add('NOVL')
    if view_date < pd.to_datetime('April 1, 2011'):
        sp500_set.discard('BLK')
        sp500_set.add('GENZ')
    if view_date < pd.to_datetime('March 31, 2011'):
        sp500_set.discard('EW')
        sp500_set.add('Q')
    if view_date < pd.to_datetime('February 28, 2011'):
        sp500_set.discard('COV')
        sp500_set.add('MFE')
    if view_date < pd.to_datetime('February 25, 2011'):
        sp500_set.discard('JOY')
        sp500_set.add('AYE')
    if view_date < pd.to_datetime('December 17, 2010'):
        sp500_set.discard('CVC')
        sp500_set.add('KG')
    if view_date < pd.to_datetime('December 17, 2010'):
        sp500_set.discard('FFIV')
        sp500_set.add('EK')
    if view_date < pd.to_datetime('December 17, 2010'):
        sp500_set.discard('NFLX')
        sp500_set.add('ODP')
    if view_date < pd.to_datetime('December 17, 2010'):
        sp500_set.discard('NFX')
        sp500_set.add('NYT')
    if view_date < pd.to_datetime('November 17, 2010'):
        sp500_set.discard('IR')
        sp500_set.add('PTV')
    if view_date < pd.to_datetime('August 26, 2010'):
        sp500_set.discard('TYC')
        sp500_set.add('SII')
    if view_date < pd.to_datetime('July 14, 2010'):
        sp500_set.discard('CB')
        sp500_set.add('MIL')
    if view_date < pd.to_datetime('June 30, 2010'):
        sp500_set.discard('QEP')
        sp500_set.add('STR')
    if view_date < pd.to_datetime('June 28, 2010'):
        sp500_set.discard('KMX')
        sp500_set.add('XTO')
    if view_date < pd.to_datetime('April 29, 2010'):
        sp500_set.discard('CERN')
        sp500_set.add('BJS')
    if view_date < pd.to_datetime('February 26, 2010'):
        sp500_set.discard('HP')
        sp500_set.add('RX')
    if view_date < pd.to_datetime('December 18, 2009'):
        sp500_set.discard('V')
        sp500_set.add('CIEN')
    if view_date < pd.to_datetime('December 18, 2009'):
        sp500_set.discard('MJN')
        sp500_set.add('DYN')
    if view_date < pd.to_datetime('December 18, 2009'):
        sp500_set.discard('CLF')
        sp500_set.add('KBH')
    if view_date < pd.to_datetime('December 18, 2009'):
        sp500_set.discard('SAI')
        sp500_set.add('CVG')
    if view_date < pd.to_datetime('December 18, 2009'):
        sp500_set.discard('ROST')
        sp500_set.add('MBI')
    if view_date < pd.to_datetime('November 3, 2009'):
        sp500_set.discard('PCLN')
        sp500_set.add('SGP')
    if view_date < pd.to_datetime('September 28, 2009'):
        sp500_set.discard('ARG')
        sp500_set.add('CBE')
    if view_date < pd.to_datetime('March 3, 2009'):
        sp500_set.discard('HRL')
        sp500_set.add('ACAS')
    if view_date < pd.to_datetime('March 3, 2009'):
        sp500_set.discard('VTR')
        sp500_set.add('JNY')
    if view_date < pd.to_datetime('December 31, 2008'):
        sp500_set.discard('OI')
        sp500_set.add('WB')
    if view_date < pd.to_datetime('September 16, 2008'):
        sp500_set.discard('HRS')
        sp500_set.add('LEH')
    if view_date < pd.to_datetime('September 12, 2008'):
        sp500_set.discard('CRM')
        sp500_set.add('FRE')
    if view_date < pd.to_datetime('September 12, 2008'):
        sp500_set.discard('FAST')
        sp500_set.add('FNM')
    if view_date < pd.to_datetime('June 10, 2008'):
        sp500_set.discard('LO')
        sp500_set.add('ABK')
    if view_date < pd.to_datetime('December 20, 2007'):
        sp500_set.discard('RRC')
        sp500_set.add('TRB')
    if view_date < pd.to_datetime('December 13, 2007'):
        sp500_set.discard('GME')
        sp500_set.add('DJ')
    if view_date < pd.to_datetime('October 26, 2007'):
        sp500_set.discard('JEC')
        sp500_set.add('AV')
    if view_date < pd.to_datetime('October 2, 2007'):
        sp500_set.discard('EXPE')
        sp500_set.add('SLR')
    if view_date < pd.to_datetime('October 1, 2007'):
        sp500_set.discard('TDC')
        sp500_set.add('NCR')
    if view_date < pd.to_datetime('September 27, 2007'):
        sp500_set.discard('TSO')
        sp500_set.add('MXIM')
    if view_date < pd.to_datetime('September 26, 2007'):
        sp500_set.discard('ICE')
        sp500_set.add('FDC')
    if view_date < pd.to_datetime('August 24, 2007'):
        sp500_set.discard('LUK')
        sp500_set.add('KSE')
    if view_date < pd.to_datetime('March 30, 2007'):
        sp500_set.discard('KFT')
        sp500_set.add('TSG')
    if view_date < pd.to_datetime('January 10, 2007'):
        sp500_set.discard('AVB')
        sp500_set.add('SBL')
    if view_date < pd.to_datetime('June 2, 2006'):
        sp500_set.discard('JNPR')
        sp500_set.add('ABS')
    if view_date < pd.to_datetime('November 18, 2005'):
        sp500_set.discard('AMZN')
        sp500_set.add('T')
    if view_date < pd.to_datetime('July 1, 2005'):
        sp500_set.discard('STZ')
        sp500_set.add('GLK')
    if view_date < pd.to_datetime('September 25, 2003'):
        sp500_set.discard('ESRX')
        sp500_set.add('QTRN')
    if view_date < pd.to_datetime('December 5, 2000'):
        sp500_set.discard('INTU')
        sp500_set.add('BS')
    if view_date < pd.to_datetime('December 5, 2000'):
        sp500_set.discard('SBL')
        sp500_set.add('OI')
    if view_date < pd.to_datetime('December 5, 2000'):
        sp500_set.discard('AYE')
        sp500_set.add('GRA')
    if view_date < pd.to_datetime('December 5, 2000'):
        sp500_set.discard('ABK')
        sp500_set.add('CCK')
    if view_date < pd.to_datetime('July 27, 2000'):
        sp500_set.discard('JDSU')
        sp500_set.add('RAD')
    if view_date < pd.to_datetime('December 7, 1999'):
        sp500_set.discard('YHOO')
        sp500_set.add('LDW')
    return list(sp500_set)
