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
    'TSLA', 'TXN', 'VRSN', 'VRSK', 'VRTX', 'WBA', 'WDAY', 'XEL', 'XLNX', 'ZM', 'ZS',
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
    'YUM', 'ZBRA', 'ZBH', 'ZION', 'ZTS',
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


COMPANY_SYMBOLS = [
    'A', 'AA', 'AAC', 'AACG', 'AACI', 'AACIW', 'AADI', 'AAIC', 'AAIN', 'AAL',
    'AAMC', 'AAME', 'AAN', 'AAOI', 'AAON', 'AAP', 'AAPL', 'AAQC', 'AAT', 'AATC',
    'AAU', 'AAWW', 'AB', 'ABB', 'ABBV', 'ABC', 'ABCB', 'ABCL', 'ABCM', 'ABEO',
    'ABEV', 'ABG', 'ABGI', 'ABIO', 'ABM', 'ABMD', 'ABNB', 'ABOS', 'ABR', 'ABSI',
    'ABST', 'ABT', 'ABTX', 'ABUS', 'ABVC', 'AC', 'ACA', 'ACAB', 'ACABU', 'ACABW',
    'ACAD', 'ACAH', 'ACAHU', 'ACAHW', 'ACAQ', 'ACAX', 'ACAXR', 'ACAXU', 'ACAXW',
    'ACB', 'ACBA', 'ACBAW', 'ACC', 'ACCD', 'ACCO', 'ACDI', 'ACEL', 'ACER', 'ACET',
    'ACEV', 'ACEVU', 'ACEVW', 'ACGL', 'ACGLN', 'ACGLO', 'ACH', 'ACHC', 'ACHL',
    'ACHR', 'ACHV', 'ACI', 'ACII', 'ACIU', 'ACIW', 'ACKIT', 'ACKIU', 'ACKIW',
    'ACLS', 'ACLX', 'ACM', 'ACMR', 'ACN', 'ACNB', 'ACON', 'ACONW', 'ACOR', 'ACP',
    'ACQR', 'ACQRU', 'ACQRW', 'ACR', 'ACRE', 'ACRO', 'ACRS', 'ACRX', 'ACST', 'ACT',
    'ACTD', 'ACTDU', 'ACTDW', 'ACTG', 'ACU', 'ACV', 'ACVA', 'ACXP', 'ADAG', 'ADAL',
    'ADALU', 'ADALW', 'ADAP', 'ADBE', 'ADC', 'ADCT', 'ADER', 'ADERU', 'ADERW',
    'ADES', 'ADEX', 'ADGI', 'ADI', 'ADIL', 'ADILW', 'ADM', 'ADMA', 'ADMP', 'ADN',
    'ADNT', 'ADNWW', 'ADOC', 'ADOCR', 'ADOCW', 'ADP', 'ADPT', 'ADRA', 'ADRT',
    'ADSE', 'ADSEW', 'ADSK', 'ADT', 'ADTH', 'ADTHW', 'ADTN', 'ADTX', 'ADUS', 'ADV',
    'ADVM', 'ADVWW', 'ADX', 'ADXN', 'AE', 'AEAC', 'AEACU', 'AEACW', 'AEAE', 'AEAEU',
    'AEAEW', 'AEE', 'AEF', 'AEFC', 'AEG', 'AEHA', 'AEHAW', 'AEHL', 'AEHR', 'AEI',
    'AEIS', 'AEL', 'AEM', 'AEMD', 'AENZ', 'AEO', 'AEP', 'AEPPZ', 'AER', 'AERC',
    'AERI', 'AES', 'AESC', 'AESE', 'AEVA', 'AEY', 'AEYE', 'AEZS', 'AFAC', 'AFACW',
    'AFAQ', 'AFAQU', 'AFAQW', 'AFB', 'AFBI', 'AFCG', 'AFG', 'AFGB', 'AFGC', 'AFGD',
    'AFGE', 'AFIB', 'AFL', 'AFMD', 'AFRM', 'AFT', 'AFTR', 'AFYA', 'AG', 'AGAC',
    'AGBA', 'AGBAR', 'AGBAW', 'AGCB', 'AGCO', 'AGD', 'AGE', 'AGEN', 'AGFS', 'AGFY',
    'AGGR', 'AGGRU', 'AGGRW', 'AGI', 'AGIL', 'AGILW', 'AGIO', 'AGL', 'AGLE', 'AGM',
    'AGMH', 'AGNC', 'AGNCM', 'AGNCN', 'AGNCO', 'AGNCP', 'AGO', 'AGR', 'AGRI',
    'AGRIW', 'AGRO', 'AGRX', 'AGS', 'AGTC', 'AGTI', 'AGX', 'AGYS', 'AHCO', 'AHG',
    'AHH', 'AHI', 'AHPA', 'AHPAU', 'AHPAW', 'AHPI', 'AHRN', 'AHRNU', 'AHRNW', 'AHT',
    'AI', 'AIB', 'AIBBR', 'AIBBU', 'AIC', 'AIF', 'AIG', 'AIH', 'AIHS', 'AIKI',
    'AIM', 'AIMAU', 'AIMC', 'AIN', 'AINC', 'AINV', 'AIO', 'AIP', 'AIR', 'AIRC',
    'AIRG', 'AIRI', 'AIRS', 'AIRT', 'AIRTP', 'AIT', 'AIU', 'AIV', 'AIZ', 'AIZN',
    'AJG', 'AJRD', 'AJX', 'AJXA', 'AKA', 'AKAM', 'AKAN', 'AKBA', 'AKIC', 'AKICU',
    'AKICW', 'AKR', 'AKRO', 'AKTS', 'AKTX', 'AKU', 'AKUS', 'AKYA', 'AL', 'ALB',
    'ALBO', 'ALC', 'ALCC', 'ALCO', 'ALDX', 'ALE', 'ALEC', 'ALEX', 'ALF', 'ALFIW',
    'ALG', 'ALGM', 'ALGN', 'ALGS', 'ALGT', 'ALHC', 'ALIM', 'ALIT', 'ALJJ', 'ALK',
    'ALKS', 'ALKT', 'ALL', 'ALLE', 'ALLG', 'ALLK', 'ALLO', 'ALLR', 'ALLT', 'ALLY',
    'ALNA', 'ALNY', 'ALOR', 'ALORU', 'ALORW', 'ALOT', 'ALPAU', 'ALPAW', 'ALPN',
    'ALPP', 'ALR', 'ALRM', 'ALRN', 'ALRS', 'ALSA', 'ALSAR', 'ALSAU', 'ALSAW',
    'ALSN', 'ALT', 'ALTG', 'ALTO', 'ALTR', 'ALTU', 'ALTUU', 'ALTUW', 'ALV', 'ALVR',
    'ALX', 'ALXO', 'ALYA', 'ALZN', 'AM', 'AMAL', 'AMAM', 'AMAO', 'AMAOU', 'AMAOW',
    'AMAT', 'AMBA', 'AMBC', 'AMBO', 'AMBP', 'AMC', 'AMCI', 'AMCIU', 'AMCIW', 'AMCR',
    'AMCX', 'AMD', 'AME', 'AMED', 'AMEH', 'AMG', 'AMGN', 'AMH', 'AMK', 'AMKR',
    'AMLX', 'AMN', 'AMNB', 'AMOT', 'AMOV', 'AMP', 'AMPE', 'AMPG', 'AMPGW', 'AMPH',
    'AMPI', 'AMPL', 'AMPS', 'AMPY', 'AMR', 'AMRC', 'AMRK', 'AMRN', 'AMRS', 'AMRX',
    'AMS', 'AMSC', 'AMSF', 'AMST', 'AMSWA', 'AMT', 'AMTB', 'AMTD', 'AMTI', 'AMTX',
    'AMWD', 'AMWL', 'AMX', 'AMYT', 'AMZN', 'AN', 'ANAB', 'ANAC', 'ANDE', 'ANEB',
    'ANET', 'ANF', 'ANGH', 'ANGHW', 'ANGI', 'ANGN', 'ANGO', 'ANIK', 'ANIP', 'ANIX',
    'ANNX', 'ANPC', 'ANSS', 'ANTE', 'ANTM', 'ANTX', 'ANVS', 'ANY', 'ANZU', 'ANZUU',
    'ANZUW', 'AOD', 'AOGO', 'AOGOU', 'AOGOW', 'AOMR', 'AON', 'AORT', 'AOS', 'AOSL',
    'AOUT', 'AP', 'APA', 'APAC', 'APACU', 'APACW', 'APAM', 'APCA', 'APCX', 'APCXW',
    'APD', 'APDN', 'APEI', 'APEN', 'APG', 'APGB', 'APH', 'API', 'APLD', 'APLE',
    'APLS', 'APLT', 'APM', 'APMI', 'APMIW', 'APN', 'APO', 'APOG', 'APP', 'APPF',
    'APPH', 'APPHW', 'APPN', 'APPS', 'APRE', 'APRN', 'APSG', 'APT', 'APTM', 'APTMU',
    'APTMW', 'APTO', 'APTS', 'APTV', 'APTX', 'APVO', 'APWC', 'APXI', 'APXIU',
    'APXIW', 'APYX', 'AQB', 'AQMS', 'AQN', 'AQNA', 'AQNB', 'AQNU', 'AQST', 'AQUA',
    'AR', 'ARAV', 'ARAY', 'ARBE', 'ARBEW', 'ARBG', 'ARBGU', 'ARBGW', 'ARBK',
    'ARBKL', 'ARC', 'ARCB', 'ARCC', 'ARCE', 'ARCH', 'ARCK', 'ARCKU', 'ARCKW',
    'ARCO', 'ARCT', 'ARDC', 'ARDS', 'ARDX', 'ARE', 'AREB', 'AREBW', 'AREC', 'AREN',
    'ARES', 'ARGD', 'ARGO', 'ARGU', 'ARGUU', 'ARGUW', 'ARGX', 'ARHS', 'ARI', 'ARIS',
    'ARIZ', 'ARIZR', 'ARIZU', 'ARIZW', 'ARKO', 'ARKOW', 'ARKR', 'ARL', 'ARLO',
    'ARLP', 'ARMK', 'ARMP', 'ARNC', 'AROC', 'AROW', 'ARQQ', 'ARQQW', 'ARQT', 'ARR',
    'ARRW', 'ARRWU', 'ARRWW', 'ARRY', 'ARTE', 'ARTEW', 'ARTL', 'ARTLW', 'ARTNA',
    'ARTW', 'ARVL', 'ARVN', 'ARW', 'ARWR', 'ARYD', 'ARYE', 'ASA', 'ASAI', 'ASAN',
    'ASAQ', 'ASAX', 'ASAXU', 'ASAXW', 'ASB', 'ASC', 'ASCA', 'ASCAR', 'ASCBU', 'ASG',
    'ASGI', 'ASGN', 'ASH', 'ASIX', 'ASLE', 'ASLN', 'ASM', 'ASMB', 'ASML', 'ASND',
    'ASNS', 'ASO', 'ASPA', 'ASPAU', 'ASPAW', 'ASPC', 'ASPCU', 'ASPCW', 'ASPN',
    'ASPS', 'ASPU', 'ASR', 'ASRT', 'ASRV', 'ASTC', 'ASTE', 'ASTL', 'ASTLW', 'ASTR',
    'ASTS', 'ASTSW', 'ASUR', 'ASX', 'ASXC', 'ASYS', 'ASZ', 'ATA', 'ATAI', 'ATAK',
    'ATAKR', 'ATAKU', 'ATAKW', 'ATAQ', 'ATAX', 'ATC', 'ATCO', 'ATCOL', 'ATCX',
    'ATEC', 'ATEK', 'ATEN', 'ATER', 'ATEX', 'ATGE', 'ATHA', 'ATHE', 'ATHM', 'ATHX',
    'ATI', 'ATIF', 'ATIP', 'ATKR', 'ATLC', 'ATLCL', 'ATLCP', 'ATLO', 'ATNF',
    'ATNFW', 'ATNI', 'ATNM', 'ATNX', 'ATO', 'ATOM', 'ATOS', 'ATR', 'ATRA', 'ATRC',
    'ATRI', 'ATRO', 'ATSG', 'ATTO', 'ATUS', 'ATVC', 'ATVCW', 'ATVI', 'ATXI', 'ATXS',
    'ATY', 'AU', 'AUB', 'AUBAP', 'AUBN', 'AUD', 'AUDC', 'AUGX', 'AUID', 'AUMN',
    'AUPH', 'AUR', 'AURA', 'AURC', 'AURCU', 'AURCW', 'AUROW', 'AUS', 'AUST', 'AUTL',
    'AUTO', 'AUUD', 'AUUDW', 'AUVI', 'AUVIP', 'AUY', 'AVA', 'AVAC', 'AVACU',
    'AVACW', 'AVAH', 'AVAL', 'AVAN', 'AVAV', 'AVB', 'AVCO', 'AVCT', 'AVCTW', 'AVD',
    'AVDL', 'AVDX', 'AVEO', 'AVGO', 'AVGOP', 'AVGR', 'AVHI', 'AVHIU', 'AVHIW',
    'AVID', 'AVIR', 'AVK', 'AVLR', 'AVNS', 'AVNT', 'AVNW', 'AVO', 'AVPT', 'AVPTW',
    'AVRO', 'AVT', 'AVTE', 'AVTR', 'AVTX', 'AVXL', 'AVY', 'AVYA', 'AWF', 'AWH',
    'AWI', 'AWK', 'AWP', 'AWR', 'AWRE', 'AWX', 'AX', 'AXAC', 'AXDX', 'AXGN', 'AXH',
    'AXL', 'AXLA', 'AXNX', 'AXON', 'AXP', 'AXR', 'AXS', 'AXSM', 'AXTA', 'AXTI',
    'AXU', 'AY', 'AYI', 'AYLA', 'AYRO', 'AYTU', 'AYX', 'AZ', 'AZEK', 'AZN', 'AZO',
    'AZPN', 'AZRE', 'AZTA', 'AZUL', 'AZYO', 'AZZ', 'B', 'BA', 'BABA', 'BAC', 'BACA',
    'BAFN', 'BAH', 'BAK', 'BALL', 'BALY', 'BAM', 'BAMH', 'BAMI', 'BAMR', 'BANC',
    'BAND', 'BANF', 'BANFP', 'BANR', 'BANX', 'BAOS', 'BAP', 'BARK', 'BASE', 'BATL',
    'BATRA', 'BATRK', 'BAX', 'BB', 'BBAI', 'BBAR', 'BBBY', 'BBCP', 'BBD', 'BBDC',
    'BBDO', 'BBGI', 'BBI', 'BBIG', 'BBIGV', 'BBIO', 'BBLG', 'BBLGW', 'BBLN', 'BBN',
    'BBQ', 'BBSI', 'BBU', 'BBUC', 'BBVA', 'BBW', 'BBWI', 'BBY', 'BC', 'BCAB',
    'BCAC', 'BCACU', 'BCACW', 'BCAT', 'BCBP', 'BCC', 'BCDA', 'BCDAW', 'BCE', 'BCEL',
    'BCH', 'BCLI', 'BCML', 'BCO', 'BCOR', 'BCOV', 'BCOW', 'BCPC', 'BCRX', 'BCS',
    'BCSA', 'BCSAU', 'BCSAW', 'BCSF', 'BCTX', 'BCTXW', 'BCV', 'BCX', 'BCYC', 'BDC',
    'BDJ', 'BDL', 'BDN', 'BDR', 'BDSX', 'BDTX', 'BDX', 'BDXB', 'BE', 'BEAM', 'BEAT',
    'BEATW', 'BECN', 'BEDU', 'BEEM', 'BEEMW', 'BEKE', 'BELFA', 'BELFB', 'BEN',
    'BENE', 'BENER', 'BENEU', 'BENEW', 'BEP', 'BEPC', 'BEPH', 'BEPI', 'BERY',
    'BEST', 'BFAC', 'BFAM', 'BFC', 'BFH', 'BFI', 'BFIIW', 'BFIN', 'BFK', 'BFLY',
    'BFRI', 'BFRIW', 'BFS', 'BFST', 'BFZ', 'BG', 'BGB', 'BGCP', 'BGFV', 'BGH',
    'BGI', 'BGNE', 'BGR', 'BGRY', 'BGRYW', 'BGS', 'BGSF', 'BGSX', 'BGT', 'BGX',
    'BGXX', 'BGY', 'BH', 'BHAC', 'BHACW', 'BHAT', 'BHB', 'BHC', 'BHE', 'BHF',
    'BHFAL', 'BHFAM', 'BHFAN', 'BHFAO', 'BHFAP', 'BHG', 'BHIL', 'BHK', 'BHLB',
    'BHP', 'BHR', 'BHSE', 'BHSEW', 'BHV', 'BHVN', 'BIDU', 'BIG', 'BIGC', 'BIGZ',
    'BIIB', 'BILI', 'BILL', 'BIMI', 'BIO', 'BIOC', 'BIOL', 'BIOR', 'BIOS', 'BIOSU',
    'BIOSW', 'BIOT', 'BIOTU', 'BIOTW', 'BIOX', 'BIP', 'BIPC', 'BIPH', 'BIPI',
    'BIRD', 'BIT', 'BITE', 'BITF', 'BIVI', 'BJ', 'BJDX', 'BJRI', 'BK', 'BKCC',
    'BKD', 'BKE', 'BKEP', 'BKEPP', 'BKH', 'BKI', 'BKKT', 'BKN', 'BKNG', 'BKR',
    'BKSC', 'BKSY', 'BKT', 'BKTI', 'BKU', 'BKYI', 'BL', 'BLBD', 'BLBX', 'BLCM',
    'BLCO', 'BLCT', 'BLD', 'BLDE', 'BLDEW', 'BLDP', 'BLDR', 'BLE', 'BLEU', 'BLEUR',
    'BLEUU', 'BLEUW', 'BLFS', 'BLFY', 'BLI', 'BLIN', 'BLK', 'BLKB', 'BLMN', 'BLND',
    'BLNG', 'BLNGW', 'BLNK', 'BLNKW', 'BLPH', 'BLRX', 'BLSA', 'BLTE', 'BLTS',
    'BLTSW', 'BLU', 'BLUA', 'BLUE', 'BLW', 'BLX', 'BLZE', 'BMA', 'BMAC', 'BMAQ',
    'BMAQR', 'BMAQU', 'BMAQW', 'BMBL', 'BME', 'BMEA', 'BMEZ', 'BMI', 'BMO', 'BMRA',
    'BMRC', 'BMRN', 'BMTX', 'BMY', 'BNED', 'BNFT', 'BNGO', 'BNGOW', 'BNIXR',
    'BNIXW', 'BNL', 'BNNR', 'BNNRU', 'BNNRW', 'BNOX', 'BNR', 'BNRG', 'BNS', 'BNSO',
    'BNTC', 'BNTX', 'BNY', 'BOAC', 'BOAS', 'BOC', 'BOCN', 'BOCNU', 'BOCNW', 'BODY',
    'BOE', 'BOH', 'BOKF', 'BOLT', 'BON', 'BOOM', 'BOOT', 'BORR', 'BOSC', 'BOTJ',
    'BOWL', 'BOX', 'BOXD', 'BOXL', 'BP', 'BPAC', 'BPACU', 'BPACW', 'BPMC', 'BPOP',
    'BPOPM', 'BPRN', 'BPT', 'BPTH', 'BPTS', 'BPYPM', 'BPYPN', 'BPYPO', 'BPYPP',
    'BQ', 'BR', 'BRAC', 'BRACR', 'BRACU', 'BRAG', 'BRBR', 'BRBS', 'BRC', 'BRCC',
    'BRCN', 'BRD', 'BRDG', 'BRDS', 'BREZ', 'BREZR', 'BREZW', 'BRFH', 'BRFS', 'BRG',
    'BRID', 'BRIV', 'BRIVU', 'BRIVW', 'BRKH', 'BRKHU', 'BRKHW', 'BRKL', 'BRKR',
    'BRLI', 'BRLIR', 'BRLIU', 'BRLIW', 'BRLT', 'BRMK', 'BRN', 'BRO', 'BROG',
    'BROGW', 'BROS', 'BRP', 'BRPM', 'BRPMU', 'BRPMW', 'BRQS', 'BRSP', 'BRT', 'BRTX',
    'BRW', 'BRX', 'BRY', 'BRZE', 'BSAC', 'BSAQ', 'BSBK', 'BSBR', 'BSET', 'BSFC',
    'BSGA', 'BSGAR', 'BSGM', 'BSIG', 'BSKY', 'BSKYU', 'BSKYW', 'BSL', 'BSM', 'BSMX',
    'BSQR', 'BSRR', 'BST', 'BSTZ', 'BSVN', 'BSX', 'BSY', 'BTA', 'BTAI', 'BTB',
    'BTBD', 'BTBDW', 'BTBT', 'BTCM', 'BTCS', 'BTCY', 'BTG', 'BTI', 'BTN', 'BTO',
    'BTOG', 'BTRS', 'BTT', 'BTTR', 'BTTX', 'BTU', 'BTWN', 'BTWNU', 'BTWNW', 'BTX',
    'BTZ', 'BUD', 'BUI', 'BUR', 'BURL', 'BUSE', 'BV', 'BVH', 'BVN', 'BVS', 'BVXV',
    'BW', 'BWA', 'BWAC', 'BWACU', 'BWACW', 'BWAQ', 'BWAQR', 'BWAY', 'BWB', 'BWBBP',
    'BWC', 'BWCAU', 'BWCAW', 'BWEN', 'BWFG', 'BWG', 'BWMN', 'BWMX', 'BWNB', 'BWSN',
    'BWV', 'BWXT', 'BX', 'BXC', 'BXMT', 'BXMX', 'BXP', 'BXRX', 'BXSL', 'BY', 'BYD',
    'BYFC', 'BYM', 'BYN', 'BYND', 'BYNO', 'BYNOU', 'BYRN', 'BYSI', 'BYTS', 'BYTSU',
    'BYTSW', 'BZ', 'BZFD', 'BZFDW', 'BZH', 'BZUN', 'C', 'CAAP', 'CAAS', 'CABA',
    'CABO', 'CAC', 'CACC', 'CACI', 'CADE', 'CADL', 'CAE', 'CAF', 'CAG', 'CAH',
    'CAJ', 'CAKE', 'CAL', 'CALA', 'CALB', 'CALM', 'CALT', 'CALX', 'CAMP', 'CAMT',
    'CAN', 'CANF', 'CANG', 'CANO', 'CAPD', 'CAPL', 'CAPR', 'CAR', 'CARA', 'CARE',
    'CARG', 'CARR', 'CARS', 'CARV', 'CAS', 'CASA', 'CASH', 'CASI', 'CASS', 'CASY',
    'CAT', 'CATC', 'CATO', 'CATY', 'CB', 'CBAN', 'CBAT', 'CBAY', 'CBD', 'CBFV',
    'CBH', 'CBIO', 'CBL', 'CBNK', 'CBOE', 'CBRE', 'CBRG', 'CBRGU', 'CBRGW', 'CBRL',
    'CBSH', 'CBT', 'CBTX', 'CBU', 'CBZ', 'CC', 'CCAI', 'CCAIU', 'CCAIW', 'CCAP',
    'CCB', 'CCBG', 'CCCC', 'CCCS', 'CCD', 'CCEL', 'CCEP', 'CCF', 'CCI', 'CCJ',
    'CCK', 'CCL', 'CCLP', 'CCM', 'CCMP', 'CCNC', 'CCNE', 'CCNEP', 'CCO', 'CCOI',
    'CCRD', 'CCRN', 'CCS', 'CCSI', 'CCTS', 'CCTSU', 'CCU', 'CCV', 'CCVI', 'CCXI',
    'CCZ', 'CD', 'CDAK', 'CDAQ', 'CDAQU', 'CDAQW', 'CDAY', 'CDE', 'CDEV', 'CDK',
    'CDLX', 'CDMO', 'CDNA', 'CDNS', 'CDR', 'CDRE', 'CDRO', 'CDROW', 'CDTX', 'CDW',
    'CDXC', 'CDXS', 'CDZI', 'CDZIP', 'CE', 'CEA', 'CEAD', 'CEADW', 'CECE', 'CEE',
    'CEG', 'CEI', 'CEIX', 'CELC', 'CELH', 'CELU', 'CELUW', 'CELZ', 'CEM', 'CEMI',
    'CEN', 'CENN', 'CENQ', 'CENQU', 'CENQW', 'CENT', 'CENTA', 'CENX', 'CEPU',
    'CEQP', 'CERE', 'CERN', 'CERS', 'CERT', 'CET', 'CETX', 'CETXP', 'CEV', 'CEVA',
    'CF', 'CFB', 'CFBK', 'CFFE', 'CFFEU', 'CFFEW', 'CFFI', 'CFFN', 'CFFS', 'CFFSW',
    'CFG', 'CFIV', 'CFIVU', 'CFIVW', 'CFLT', 'CFMS', 'CFR', 'CFRX', 'CFSB', 'CFVI',
    'CFVIU', 'CFVIW', 'CG', 'CGA', 'CGABL', 'CGAU', 'CGBD', 'CGC', 'CGEM', 'CGEN',
    'CGNT', 'CGNX', 'CGO', 'CGRN', 'CGTX', 'CHAA', 'CHCI', 'CHCO', 'CHCT', 'CHD',
    'CHDN', 'CHE', 'CHEAU', 'CHEF', 'CHEK', 'CHEKZ', 'CHGG', 'CHH', 'CHI', 'CHK',
    'CHKEL', 'CHKEW', 'CHKEZ', 'CHKP', 'CHMG', 'CHMI', 'CHN', 'CHNG', 'CHNGU',
    'CHNR', 'CHPT', 'CHRA', 'CHRB', 'CHRS', 'CHRW', 'CHS', 'CHSCL', 'CHSCM',
    'CHSCN', 'CHSCO', 'CHSCP', 'CHT', 'CHTR', 'CHUY', 'CHW', 'CHWA', 'CHWAU',
    'CHWAW', 'CHWY', 'CHX', 'CHY', 'CI', 'CIA', 'CIB', 'CIDM', 'CIEN', 'CIF',
    'CIFR', 'CIFRW', 'CIG', 'CIGI', 'CIH', 'CII', 'CIIG', 'CIIGU', 'CIIGW', 'CIK',
    'CIM', 'CINC', 'CINF', 'CING', 'CINGW', 'CINT', 'CIO', 'CION', 'CIR', 'CISO',
    'CITE', 'CITEU', 'CIVB', 'CIVI', 'CIX', 'CIXX', 'CIZN', 'CJJD', 'CKPT', 'CKX',
    'CL', 'CLAA', 'CLAQ', 'CLAQR', 'CLAQW', 'CLAR', 'CLAS', 'CLAY', 'CLAYU',
    'CLAYW', 'CLB', 'CLBK', 'CLBR', 'CLBS', 'CLBT', 'CLBTW', 'CLDT', 'CLDX', 'CLEU',
    'CLF', 'CLFD', 'CLGN', 'CLH', 'CLIM', 'CLINR', 'CLINU', 'CLINW', 'CLIR', 'CLLS',
    'CLM', 'CLMT', 'CLNE', 'CLNN', 'CLNNW', 'CLOE', 'CLOER', 'CLOEU', 'CLOV',
    'CLPR', 'CLPS', 'CLPT', 'CLR', 'CLRB', 'CLRCU', 'CLRM', 'CLRMU', 'CLRMW',
    'CLRO', 'CLS', 'CLSD', 'CLSK', 'CLSN', 'CLST', 'CLVR', 'CLVRW', 'CLVS', 'CLVT',
    'CLW', 'CLWT', 'CLX', 'CLXT', 'CM', 'CMA', 'CMAX', 'CMBM', 'CMC', 'CMCA',
    'CMCAU', 'CMCAW', 'CMCL', 'CMCM', 'CMCO', 'CMCSA', 'CMCT', 'CME', 'CMG', 'CMI',
    'CMLS', 'CMMB', 'CMP', 'CMPI', 'CMPO', 'CMPOW', 'CMPR', 'CMPS', 'CMPX', 'CMRA',
    'CMRAW', 'CMRE', 'CMRX', 'CMS', 'CMSA', 'CMSC', 'CMSD', 'CMT', 'CMTG', 'CMTL',
    'CMU', 'CNA', 'CNC', 'CNCE', 'CND', 'CNDA', 'CNDB', 'CNDT', 'CNET', 'CNEY',
    'CNF', 'CNFR', 'CNFRL', 'CNGL', 'CNGLU', 'CNGLW', 'CNHI', 'CNI', 'CNK', 'CNM',
    'CNMD', 'CNNB', 'CNNE', 'CNO', 'CNOB', 'CNOBP', 'CNP', 'CNQ', 'CNR', 'CNS',
    'CNSL', 'CNSP', 'CNTA', 'CNTB', 'CNTG', 'CNTQ', 'CNTQU', 'CNTQW', 'CNTX',
    'CNTY', 'CNVY', 'CNX', 'CNXC', 'CNXN', 'CO', 'COCO', 'COCP', 'CODA', 'CODI',
    'CODX', 'COE', 'COF', 'COFS', 'COGT', 'COHN', 'COHR', 'COHU', 'COIN', 'COKE',
    'COLB', 'COLD', 'COLI', 'COLIU', 'COLIW', 'COLL', 'COLM', 'COMM', 'COMP',
    'COMS', 'COMSP', 'COMSW', 'CONN', 'CONX', 'CONXU', 'CONXW', 'COO', 'COOK',
    'COOL', 'COOLU', 'COOLW', 'COOP', 'COP', 'CORR', 'CORS', 'CORT', 'CORZ',
    'CORZW', 'COSM', 'COST', 'COTY', 'COUP', 'COUR', 'COVA', 'COVAU', 'COVAW',
    'COWN', 'COWNL', 'CP', 'CPA', 'CPAA', 'CPAAW', 'CPAC', 'CPAQ', 'CPAR', 'CPARU',
    'CPARW', 'CPB', 'CPE', 'CPF', 'CPG', 'CPHC', 'CPHI', 'CPIX', 'CPK', 'CPLP',
    'CPNG', 'CPOP', 'CPRI', 'CPRT', 'CPRX', 'CPS', 'CPSH', 'CPSI', 'CPSS', 'CPT',
    'CPTAG', 'CPTAL', 'CPTK', 'CPTN', 'CPTNW', 'CPUH', 'CPZ', 'CQP', 'CR', 'CRAI',
    'CRBP', 'CRBU', 'CRC', 'CRCT', 'CRDF', 'CRDL', 'CRDO', 'CREC', 'CRECU', 'CRECW',
    'CREG', 'CRESW', 'CRESY', 'CREX', 'CREXW', 'CRF', 'CRGE', 'CRGY', 'CRH', 'CRHC',
    'CRI', 'CRIS', 'CRK', 'CRKN', 'CRL', 'CRM', 'CRMD', 'CRMT', 'CRNC', 'CRNT',
    'CRNX', 'CRON', 'CROX', 'CRS', 'CRSP', 'CRSR', 'CRT', 'CRTD', 'CRTDW', 'CRTO',
    'CRTX', 'CRU', 'CRUS', 'CRVL', 'CRVS', 'CRWD', 'CRWS', 'CRXT', 'CRXTW', 'CRZN',
    'CRZNW', 'CS', 'CSAN', 'CSBR', 'CSCO', 'CSCW', 'CSGP', 'CSGS', 'CSII', 'CSIQ',
    'CSL', 'CSLM', 'CSLMR', 'CSPI', 'CSQ', 'CSR', 'CSSE', 'CSSEN', 'CSSEP', 'CSTA',
    'CSTE', 'CSTL', 'CSTM', 'CSTR', 'CSV', 'CSWC', 'CSWI', 'CSX', 'CTAQ', 'CTAQU',
    'CTAQW', 'CTAS', 'CTBB', 'CTBI', 'CTDD', 'CTEK', 'CTG', 'CTGO', 'CTHR', 'CTIB',
    'CTIC', 'CTKB', 'CTLP', 'CTLT', 'CTMX', 'CTO', 'CTOS', 'CTR', 'CTRA', 'CTRE',
    'CTRM', 'CTRN', 'CTS', 'CTSH', 'CTSO', 'CTT', 'CTV', 'CTVA', 'CTXR', 'CTXRW',
    'CTXS', 'CUBA', 'CUBB', 'CUBE', 'CUBI', 'CUE', 'CUEN', 'CUENW', 'CUK', 'CULL',
    'CULP', 'CURI', 'CURIW', 'CURO', 'CURV', 'CUTR', 'CUZ', 'CVAC', 'CVBF', 'CVCO',
    'CVCY', 'CVE', 'CVEO', 'CVET', 'CVGI', 'CVGW', 'CVI', 'CVII', 'CVLG', 'CVLT',
    'CVLY', 'CVM', 'CVNA', 'CVR', 'CVRX', 'CVS', 'CVT', 'CVV', 'CVX', 'CW', 'CWAN',
    'CWBC', 'CWBR', 'CWCO', 'CWEN', 'CWH', 'CWK', 'CWST', 'CWT', 'CX', 'CXAC',
    'CXDO', 'CXE', 'CXH', 'CXM', 'CXW', 'CYAD', 'CYAN', 'CYBE', 'CYBN', 'CYBR',
    'CYCC', 'CYCCP', 'CYCN', 'CYD', 'CYH', 'CYN', 'CYRN', 'CYRX', 'CYT', 'CYTH',
    'CYTHW', 'CYTK', 'CYTO', 'CYXT', 'CZNC', 'CZOO', 'CZR', 'CZWI', 'D', 'DAC',
    'DADA', 'DAIO', 'DAKT', 'DAL', 'DALN', 'DALS', 'DAN', 'DAO', 'DAOO', 'DAOOU',
    'DAOOW', 'DAR', 'DARE', 'DASH', 'DATS', 'DATSW', 'DAVA', 'DAVE', 'DAVEW',
    'DAWN', 'DB', 'DBD', 'DBGI', 'DBGIW', 'DBI', 'DBL', 'DBRG', 'DBTX', 'DBVT',
    'DBX', 'DC', 'DCBO', 'DCF', 'DCFC', 'DCFCW', 'DCGO', 'DCGOW', 'DCI', 'DCO',
    'DCOM', 'DCOMP', 'DCP', 'DCPH', 'DCRD', 'DCRDU', 'DCRDW', 'DCT', 'DCTH', 'DCUE',
    'DD', 'DDD', 'DDF', 'DDI', 'DDL', 'DDOG', 'DDS', 'DDT', 'DE', 'DEA', 'DECAU',
    'DECK', 'DEI', 'DELL', 'DEN', 'DENN', 'DEO', 'DERM', 'DESP', 'DEX', 'DFFN',
    'DFH', 'DFIN', 'DFP', 'DFS', 'DG', 'DGHI', 'DGICA', 'DGICB', 'DGII', 'DGLY',
    'DGNU', 'DGX', 'DH', 'DHAC', 'DHACU', 'DHACW', 'DHBC', 'DHBCU', 'DHBCW', 'DHC',
    'DHCA', 'DHCAU', 'DHCAW', 'DHCNI', 'DHCNL', 'DHF', 'DHHC', 'DHHCW', 'DHI',
    'DHIL', 'DHR', 'DHT', 'DHX', 'DHY', 'DIAX', 'DIBS', 'DICE', 'DIDI', 'DILAU',
    'DILAW', 'DIN', 'DINO', 'DIOD', 'DIS', 'DISA', 'DISAU', 'DISAW', 'DISH', 'DIT',
    'DJCO', 'DK', 'DKDCA', 'DKDCU', 'DKL', 'DKNG', 'DKS', 'DLA', 'DLB', 'DLCA',
    'DLCAU', 'DLCAW', 'DLHC', 'DLNG', 'DLO', 'DLPN', 'DLR', 'DLTH', 'DLTR', 'DLX',
    'DLY', 'DM', 'DMA', 'DMAC', 'DMAQ', 'DMB', 'DMF', 'DMLP', 'DMO', 'DMRC', 'DMS',
    'DMTK', 'DMYS', 'DNA', 'DNAA', 'DNAB', 'DNAC', 'DNAD', 'DNAY', 'DNB', 'DNLI',
    'DNMR', 'DNN', 'DNOW', 'DNP', 'DNUT', 'DNZ', 'DO', 'DOC', 'DOCN', 'DOCS',
    'DOCU', 'DOGZ', 'DOLE', 'DOMA', 'DOMO', 'DOOO', 'DOOR', 'DORM', 'DOUG', 'DOV',
    'DOW', 'DOX', 'DOYU', 'DPCSW', 'DPG', 'DPRO', 'DPSI', 'DPZ', 'DQ', 'DRAY',
    'DRAYU', 'DRAYW', 'DRCT', 'DRCTW', 'DRD', 'DRE', 'DRH', 'DRI', 'DRIO', 'DRMA',
    'DRMAW', 'DRQ', 'DRRX', 'DRTS', 'DRTSW', 'DRTT', 'DRUG', 'DRVN', 'DS', 'DSAC',
    'DSACU', 'DSACW', 'DSAQ', 'DSEY', 'DSGN', 'DSGR', 'DSGX', 'DSKE', 'DSL', 'DSM',
    'DSP', 'DSS', 'DSU', 'DSWL', 'DSX', 'DT', 'DTB', 'DTC', 'DTE', 'DTEA', 'DTF',
    'DTG', 'DTIL', 'DTM', 'DTOC', 'DTOCW', 'DTP', 'DTRT', 'DTRTU', 'DTRTW', 'DTSS',
    'DTST', 'DTSTW', 'DTW', 'DUET', 'DUETU', 'DUK', 'DUKB', 'DUNE', 'DUNEU',
    'DUNEW', 'DUO', 'DUOL', 'DUOT', 'DV', 'DVA', 'DVAX', 'DVN', 'DWAC', 'DWACU',
    'DWACW', 'DWIN', 'DWSN', 'DX', 'DXC', 'DXCM', 'DXF', 'DXLG', 'DXPE', 'DXR',
    'DXYN', 'DY', 'DYAI', 'DYFN', 'DYN', 'DYNS', 'DYNT', 'DZSI', 'E', 'EA', 'EAC',
    'EACPU', 'EAD', 'EAF', 'EAI', 'EAR', 'EARN', 'EAST', 'EAT', 'EB', 'EBACU',
    'EBAY', 'EBC', 'EBET', 'EBF', 'EBIX', 'EBMT', 'EBON', 'EBR', 'EBS', 'EBTC',
    'EC', 'ECAT', 'ECCC', 'ECCV', 'ECCW', 'ECCX', 'ECF', 'ECL', 'ECOR', 'ECPG',
    'ECVT', 'ED', 'EDAP', 'EDBL', 'EDBLW', 'EDD', 'EDF', 'EDI', 'EDIT', 'EDN',
    'EDNC', 'EDNCU', 'EDR', 'EDRY', 'EDSA', 'EDTK', 'EDTX', 'EDTXU', 'EDTXW', 'EDU',
    'EDUC', 'EE', 'EEA', 'EEFT', 'EEIQ', 'EEX', 'EFC', 'EFL', 'EFOI', 'EFR', 'EFSC',
    'EFSCP', 'EFT', 'EFTR', 'EFTRW', 'EFX', 'EGAN', 'EGBN', 'EGF', 'EGGF', 'EGHT',
    'EGLE', 'EGLX', 'EGO', 'EGP', 'EGRX', 'EGY', 'EH', 'EHC', 'EHI', 'EHTH', 'EIC',
    'EICA', 'EIG', 'EIGR', 'EIM', 'EIX', 'EJFA', 'EJFAU', 'EJFAW', 'EJH', 'EKSO',
    'EL', 'ELA', 'ELAN', 'ELAT', 'ELBM', 'ELC', 'ELDN', 'ELEV', 'ELF', 'ELLO',
    'ELMD', 'ELMS', 'ELMSW', 'ELOX', 'ELP', 'ELS', 'ELSE', 'ELTK', 'ELVT', 'ELY',
    'ELYM', 'ELYS', 'EM', 'EMAN', 'EMBC', 'EMBK', 'EMBKW', 'EMCF', 'EMD', 'EME',
    'EMF', 'EMKR', 'EML', 'EMLD', 'EMLDU', 'EMLDW', 'EMN', 'EMO', 'EMP', 'EMR',
    'EMX', 'ENB', 'ENBA', 'ENCP', 'ENCPU', 'ENCPW', 'ENDP', 'ENER', 'ENERR',
    'ENERU', 'ENERW', 'ENFN', 'ENG', 'ENIA', 'ENIC', 'ENJ', 'ENJY', 'ENJYW', 'ENLC',
    'ENLV', 'ENO', 'ENOB', 'ENOV', 'ENPC', 'ENPH', 'ENR', 'ENS', 'ENSC', 'ENSG',
    'ENSV', 'ENTA', 'ENTF', 'ENTFU', 'ENTFW', 'ENTG', 'ENTX', 'ENTXW', 'ENV',
    'ENVA', 'ENVB', 'ENVX', 'ENX', 'ENZ', 'EOCW', 'EOD', 'EOG', 'EOI', 'EOLS',
    'EOS', 'EOSE', 'EOSEW', 'EOT', 'EP', 'EPAC', 'EPAM', 'EPC', 'EPD', 'EPHY',
    'EPHYU', 'EPHYW', 'EPIX', 'EPM', 'EPR', 'EPRT', 'EPSN', 'EPWR', 'EPZM', 'EQ',
    'EQBK', 'EQC', 'EQD', 'EQH', 'EQIX', 'EQNR', 'EQOS', 'EQR', 'EQRX', 'EQRXW',
    'EQS', 'EQT', 'EQX', 'ERAS', 'ERC', 'ERES', 'ERESU', 'ERESW', 'ERF', 'ERH',
    'ERIC', 'ERIE', 'ERII', 'ERJ', 'ERO', 'ERYP', 'ES', 'ESAB', 'ESAC', 'ESACU',
    'ESACW', 'ESCA', 'ESE', 'ESEA', 'ESGC', 'ESGR', 'ESGRO', 'ESGRP', 'ESI', 'ESLT',
    'ESM', 'ESMT', 'ESNT', 'ESOA', 'ESP', 'ESPR', 'ESQ', 'ESRT', 'ESS', 'ESSA',
    'ESSC', 'ESSCW', 'ESTA', 'ESTC', 'ESTE', 'ET', 'ETAC', 'ETACU', 'ETACW', 'ETB',
    'ETD', 'ETG', 'ETJ', 'ETN', 'ETNB', 'ETO', 'ETON', 'ETR', 'ETRN', 'ETSY',
    'ETTX', 'ETV', 'ETW', 'ETWO', 'ETY', 'EUCR', 'EUCRW', 'EURN', 'EVA', 'EVAX',
    'EVBG', 'EVBN', 'EVC', 'EVCM', 'EVE', 'EVER', 'EVEX', 'EVF', 'EVFM', 'EVG',
    'EVGN', 'EVGO', 'EVGOW', 'EVGR', 'EVGRU', 'EVH', 'EVI', 'EVK', 'EVLO', 'EVLV',
    'EVLVW', 'EVM', 'EVN', 'EVO', 'EVOJ', 'EVOJU', 'EVOJW', 'EVOK', 'EVOP', 'EVR',
    'EVRG', 'EVRI', 'EVT', 'EVTC', 'EVTL', 'EVV', 'EW', 'EWBC', 'EWCZ', 'EWTX',
    'EXAI', 'EXAS', 'EXC', 'EXD', 'EXEL', 'EXFY', 'EXG', 'EXK', 'EXLS', 'EXN',
    'EXP', 'EXPD', 'EXPE', 'EXPI', 'EXPO', 'EXPR', 'EXR', 'EXTN', 'EXTR', 'EYE',
    'EYEN', 'EYES', 'EYESW', 'EYPT', 'EZFL', 'EZGO', 'EZPW', 'F', 'FA', 'FACA',
    'FACT', 'FAF', 'FAM', 'FAMI', 'FANG', 'FANH', 'FARM', 'FARO', 'FAST', 'FAT',
    'FATBB', 'FATBP', 'FATE', 'FATH', 'FATP', 'FATPW', 'FAX', 'FB', 'FBC', 'FBHS',
    'FBIO', 'FBIOP', 'FBIZ', 'FBK', 'FBMS', 'FBNC', 'FBP', 'FBRT', 'FBRX', 'FC',
    'FCAP', 'FCAX', 'FCBC', 'FCCO', 'FCEL', 'FCF', 'FCFS', 'FCN', 'FCNCA', 'FCNCO',
    'FCNCP', 'FCO', 'FCPT', 'FCRD', 'FCRX', 'FCT', 'FCUV', 'FCX', 'FDBC', 'FDEU',
    'FDMT', 'FDP', 'FDS', 'FDUS', 'FDX', 'FE', 'FEAM', 'FEDU', 'FEIM', 'FELE',
    'FEMY', 'FEN', 'FENC', 'FENG', 'FEO', 'FERG', 'FET', 'FEXD', 'FEXDR', 'FEXDU',
    'FEXDW', 'FF', 'FFA', 'FFBC', 'FFBW', 'FFC', 'FFHL', 'FFIC', 'FFIE', 'FFIEW',
    'FFIN', 'FFIV', 'FFNW', 'FFWM', 'FGB', 'FGBI', 'FGBIP', 'FGEN', 'FGF', 'FGFPP',
    'FGI', 'FGIWW', 'FGMC', 'FGMCU', 'FHB', 'FHI', 'FHLT', 'FHLTU', 'FHLTW', 'FHN',
    'FHS', 'FHTX', 'FIAC', 'FIACU', 'FIACW', 'FIBK', 'FICO', 'FICV', 'FICVU',
    'FICVW', 'FIF', 'FIGS', 'FINM', 'FINMU', 'FINMW', 'FINS', 'FINV', 'FINW', 'FIS',
    'FISI', 'FISV', 'FITB', 'FITBI', 'FITBO', 'FITBP', 'FIVE', 'FIVN', 'FIX',
    'FIXX', 'FIZZ', 'FKWL', 'FL', 'FLAC', 'FLACU', 'FLACW', 'FLAG', 'FLC', 'FLEX',
    'FLGC', 'FLGT', 'FLIC', 'FLL', 'FLME', 'FLMN', 'FLMNW', 'FLNC', 'FLNG', 'FLNT',
    'FLO', 'FLR', 'FLS', 'FLT', 'FLUX', 'FLWS', 'FLXS', 'FLYA', 'FLYW', 'FMAO',
    'FMBH', 'FMC', 'FMIV', 'FMIVU', 'FMIVW', 'FMN', 'FMNB', 'FMS', 'FMTX', 'FMX',
    'FMY', 'FN', 'FNA', 'FNB', 'FNCB', 'FNCH', 'FND', 'FNF', 'FNGR', 'FNHC', 'FNKO',
    'FNLC', 'FNV', 'FNVT', 'FNVTU', 'FNVTW', 'FNWB', 'FNWD', 'FOA', 'FOCS', 'FOF',
    'FOLD', 'FONR', 'FOR', 'FORA', 'FORD', 'FORG', 'FORM', 'FORR', 'FORTY', 'FOSL',
    'FOSLL', 'FOUN', 'FOUNU', 'FOUNW', 'FOUR', 'FOX', 'FOXA', 'FOXF', 'FOXW',
    'FOXWW', 'FPAC', 'FPAY', 'FPF', 'FPH', 'FPI', 'FPL', 'FR', 'FRA', 'FRAF',
    'FRBA', 'FRBK', 'FRBN', 'FRBNU', 'FRBNW', 'FRC', 'FRD', 'FREE', 'FREEW', 'FREQ',
    'FREY', 'FRG', 'FRGAP', 'FRGE', 'FRGI', 'FRHC', 'FRLA', 'FRLAU', 'FRLAW',
    'FRLN', 'FRME', 'FRMEP', 'FRO', 'FROG', 'FRON', 'FRONU', 'FRONW', 'FRPH',
    'FRPT', 'FRSG', 'FRSGU', 'FRSGW', 'FRSH', 'FRST', 'FRSX', 'FRT', 'FRW', 'FRWAU',
    'FRWAW', 'FRXB', 'FSBC', 'FSBW', 'FSD', 'FSEA', 'FSFG', 'FSI', 'FSK', 'FSLR',
    'FSLY', 'FSM', 'FSNB', 'FSP', 'FSR', 'FSRD', 'FSRDW', 'FSRX', 'FSRXU', 'FSRXW',
    'FSS', 'FSSI', 'FSSIW', 'FST', 'FSTR', 'FSTX', 'FSV', 'FT', 'FTAA', 'FTAAU',
    'FTAAW', 'FTAI', 'FTAIN', 'FTAIO', 'FTAIP', 'FTCH', 'FTCI', 'FTCV', 'FTCVU',
    'FTCVW', 'FTDR', 'FTEK', 'FTEV', 'FTF', 'FTFT', 'FTHM', 'FTHY', 'FTI', 'FTII',
    'FTIIU', 'FTIIW', 'FTK', 'FTNT', 'FTPA', 'FTPAW', 'FTRP', 'FTS', 'FTV', 'FTVI',
    'FTVIU', 'FTVIW', 'FUBO', 'FUL', 'FULC', 'FULT', 'FULTP', 'FUN', 'FUNC', 'FUND',
    'FURY', 'FUSB', 'FUSN', 'FUTU', 'FUV', 'FVAM', 'FVCB', 'FVIV', 'FVRR', 'FVT',
    'FWAC', 'FWBI', 'FWONA', 'FWONK', 'FWP', 'FWRD', 'FWRG', 'FXCO', 'FXCOR',
    'FXCOW', 'FXLV', 'FXNC', 'FYBR', 'FZT', 'G', 'GAB', 'GABC', 'GACQ', 'GACQU',
    'GACQW', 'GAIA', 'GAIN', 'GAINN', 'GAINZ', 'GALT', 'GAM', 'GAMB', 'GAMC',
    'GAMCW', 'GAME', 'GAN', 'GANX', 'GAPA', 'GAQ', 'GASS', 'GATE', 'GATEU', 'GATEW',
    'GATO', 'GATX', 'GAU', 'GB', 'GBAB', 'GBBKU', 'GBCI', 'GBDC', 'GBIO', 'GBL',
    'GBLI', 'GBNH', 'GBNY', 'GBOX', 'GBR', 'GBRG', 'GBRGR', 'GBRGW', 'GBS', 'GBT',
    'GBX', 'GCBC', 'GCI', 'GCMG', 'GCMGW', 'GCO', 'GCP', 'GCTK', 'GCV', 'GD',
    'GDDY', 'GDEN', 'GDL', 'GDNR', 'GDNRU', 'GDNRW', 'GDO', 'GDOT', 'GDRX', 'GDS',
    'GDST', 'GDSTR', 'GDSTU', 'GDSTW', 'GDV', 'GDYN', 'GE', 'GECC', 'GECCM',
    'GECCN', 'GECCO', 'GEEX', 'GEEXU', 'GEEXW', 'GEF', 'GEG', 'GEHI', 'GEL', 'GENC',
    'GENE', 'GENI', 'GENQ', 'GENQU', 'GENQW', 'GEO', 'GEOS', 'GER', 'GERN', 'GES',
    'GET', 'GEVO', 'GF', 'GFAI', 'GFAIW', 'GFF', 'GFGD', 'GFGDR', 'GFGDU', 'GFGDW',
    'GFI', 'GFL', 'GFLU', 'GFOR', 'GFS', 'GFX', 'GGAA', 'GGAAU', 'GGAAW', 'GGAL',
    'GGB', 'GGE', 'GGG', 'GGGV', 'GGGVR', 'GGMC', 'GGMCW', 'GGN', 'GGPI', 'GGPIU',
    'GGPIW', 'GGR', 'GGROW', 'GGT', 'GGZ', 'GH', 'GHAC', 'GHACU', 'GHACW', 'GHC',
    'GHG', 'GHIX', 'GHIXU', 'GHL', 'GHLD', 'GHM', 'GHRS', 'GHSI', 'GHY', 'GIA',
    'GIAC', 'GIACW', 'GIB', 'GIC', 'GIFI', 'GIGM', 'GIII', 'GIIX', 'GIIXU', 'GIIXW',
    'GIL', 'GILD', 'GILT', 'GIM', 'GIPR', 'GIPRW', 'GIS', 'GIW', 'GIWWU', 'GIWWW',
    'GJH', 'GJO', 'GJS', 'GKOS', 'GL', 'GLAD', 'GLAQ', 'GLAQU', 'GLAQW', 'GLBE',
    'GLBL', 'GLBLU', 'GLBLW', 'GLBS', 'GLBZ', 'GLDD', 'GLDG', 'GLEE', 'GLEEU',
    'GLEEW', 'GLG', 'GLHA', 'GLHAU', 'GLHAW', 'GLLI', 'GLLIR', 'GLLIW', 'GLMD',
    'GLNG', 'GLO', 'GLOB', 'GLOP', 'GLP', 'GLPG', 'GLPI', 'GLQ', 'GLRE', 'GLS',
    'GLSI', 'GLSPT', 'GLSPU', 'GLSPW', 'GLT', 'GLTA', 'GLTO', 'GLU', 'GLUE', 'GLV',
    'GLW', 'GLYC', 'GM', 'GMAB', 'GMBL', 'GMBLP', 'GMBLW', 'GMBLZ', 'GMDA', 'GME',
    'GMED', 'GMFI', 'GMFIW', 'GMGI', 'GMRE', 'GMS', 'GMTX', 'GMVD', 'GMVDW', 'GNAC',
    'GNACU', 'GNACW', 'GNCA', 'GNE', 'GNFT', 'GNK', 'GNL', 'GNLN', 'GNPX', 'GNRC',
    'GNS', 'GNSS', 'GNT', 'GNTA', 'GNTX', 'GNTY', 'GNUS', 'GNW', 'GO', 'GOAC',
    'GOBI', 'GOCO', 'GOED', 'GOEV', 'GOEVW', 'GOF', 'GOGL', 'GOGN', 'GOGO', 'GOL',
    'GOLD', 'GOLF', 'GOOD', 'GOODN', 'GOODO', 'GOOG', 'GOOGL', 'GOOS', 'GORO',
    'GOSS', 'GOTU', 'GOVX', 'GOVXW', 'GP', 'GPAC', 'GPACU', 'GPACW', 'GPC', 'GPCO',
    'GPCOW', 'GPI', 'GPJA', 'GPK', 'GPL', 'GPMT', 'GPN', 'GPOR', 'GPP', 'GPRE',
    'GPRK', 'GPRO', 'GPS', 'GRAB', 'GRABW', 'GRAY', 'GRBK', 'GRC', 'GRCL', 'GRCY',
    'GRCYU', 'GRCYW', 'GREE', 'GREEL', 'GRF', 'GRFS', 'GRIL', 'GRIN', 'GRMN',
    'GRNA', 'GRNAW', 'GRNQ', 'GROM', 'GROMW', 'GROW', 'GROY', 'GRPH', 'GRPN',
    'GRTS', 'GRTX', 'GRVI', 'GRVY', 'GRWG', 'GRX', 'GS', 'GSAQ', 'GSAQU', 'GSAQW',
    'GSAT', 'GSBC', 'GSBD', 'GSEV', 'GSEVU', 'GSEVW', 'GSHD', 'GSIT', 'GSK', 'GSL',
    'GSLD', 'GSM', 'GSMG', 'GSMGW', 'GSQB', 'GSQD', 'GSRM', 'GSRMR', 'GSRMU',
    'GSRMW', 'GSV', 'GT', 'GTAC', 'GTACU', 'GTACW', 'GTBP', 'GTE', 'GTEC', 'GTES',
    'GTH', 'GTHX', 'GTIM', 'GTLB', 'GTLS', 'GTN', 'GTPA', 'GTPAU', 'GTPAW', 'GTPB',
    'GTPBU', 'GTPBW', 'GTX', 'GTXAP', 'GTY', 'GTYH', 'GUG', 'GURE', 'GUT', 'GVA',
    'GVCI', 'GVCIU', 'GVCIW', 'GVP', 'GWH', 'GWII', 'GWIIW', 'GWRE', 'GWRS', 'GWW',
    'GXII', 'GXIIW', 'GXO', 'GYRO', 'H', 'HA', 'HAAC', 'HAACU', 'HAACW', 'HAE',
    'HAFC', 'HAIA', 'HAIAU', 'HAIAW', 'HAIN', 'HAL', 'HALL', 'HALO', 'HAPP', 'HARP',
    'HAS', 'HASI', 'HAYN', 'HAYW', 'HBAN', 'HBANM', 'HBANP', 'HBB', 'HBCP', 'HBI',
    'HBIO', 'HBM', 'HBNC', 'HBT', 'HCA', 'HCAR', 'HCARU', 'HCARW', 'HCAT', 'HCC',
    'HCCI', 'HCDI', 'HCDIP', 'HCDIW', 'HCDIZ', 'HCI', 'HCIC', 'HCICU', 'HCICW',
    'HCII', 'HCIIW', 'HCKT', 'HCM', 'HCMA', 'HCMAU', 'HCMAW', 'HCNE', 'HCNEU',
    'HCNEW', 'HCP', 'HCSG', 'HCTI', 'HCVI', 'HCVIW', 'HCWB', 'HCXY', 'HD', 'HDB',
    'HDSN', 'HE', 'HEAR', 'HEES', 'HEI', 'HELE', 'HEP', 'HEPA', 'HEPS', 'HEQ',
    'HERA', 'HERAU', 'HERAW', 'HES', 'HESM', 'HEXO', 'HFBL', 'HFFG', 'HFRO', 'HFWA',
    'HGBL', 'HGEN', 'HGLB', 'HGTY', 'HGV', 'HHC', 'HHGC', 'HHGCW', 'HHLA', 'HHS',
    'HI', 'HIBB', 'HIE', 'HIFS', 'HIG', 'HIGA', 'HIHO', 'HII', 'HIII', 'HIIIU',
    'HIIIW', 'HIL', 'HILS', 'HIMS', 'HIMX', 'HIO', 'HIPO', 'HITI', 'HIVE', 'HIW',
    'HIX', 'HL', 'HLAH', 'HLAHU', 'HLAHW', 'HLBZ', 'HLBZW', 'HLF', 'HLG', 'HLGN',
    'HLI', 'HLIO', 'HLIT', 'HLLY', 'HLMN', 'HLNE', 'HLT', 'HLTH', 'HLVX', 'HLX',
    'HMA', 'HMC', 'HMCO', 'HMCOU', 'HMCOW', 'HMLP', 'HMN', 'HMNF', 'HMPT', 'HMST',
    'HMTV', 'HMY', 'HNGR', 'HNI', 'HNNA', 'HNNAZ', 'HNP', 'HNRA', 'HNRG', 'HNST',
    'HNVR', 'HNW', 'HOFT', 'HOFV', 'HOFVW', 'HOG', 'HOLI', 'HOLX', 'HOMB', 'HON',
    'HONE', 'HOOD', 'HOOK', 'HOPE', 'HORI', 'HOTH', 'HOUR', 'HOV', 'HOVNP', 'HOWL',
    'HP', 'HPE', 'HPF', 'HPI', 'HPK', 'HPKEW', 'HPLT', 'HPLTW', 'HPP', 'HPQ', 'HPS',
    'HPX', 'HQH', 'HQI', 'HQL', 'HQY', 'HR', 'HRB', 'HRI', 'HRL', 'HRMY', 'HROW',
    'HROWL', 'HRT', 'HRTG', 'HRTX', 'HRZN', 'HSAQ', 'HSBC', 'HSC', 'HSDT', 'HSIC',
    'HSII', 'HSKA', 'HSON', 'HST', 'HSTM', 'HSTO', 'HSY', 'HT', 'HTA', 'HTAQ',
    'HTBI', 'HTBK', 'HTCR', 'HTD', 'HTFB', 'HTGC', 'HTGM', 'HTH', 'HTHT', 'HTIA',
    'HTIBP', 'HTLD', 'HTLF', 'HTLFP', 'HTOO', 'HTOOW', 'HTPA', 'HTY', 'HTZ',
    'HTZWW', 'HUBB', 'HUBG', 'HUBS', 'HUDI', 'HUGE', 'HUGS', 'HUIZ', 'HUM', 'HUMA',
    'HUMAW', 'HUN', 'HURC', 'HURN', 'HUSA', 'HUSN', 'HUT', 'HUYA', 'HVBC', 'HVT',
    'HWBK', 'HWC', 'HWCPZ', 'HWELW', 'HWKN', 'HWKZ', 'HWM', 'HXL', 'HY', 'HYAC',
    'HYACW', 'HYB', 'HYFM', 'HYI', 'HYLN', 'HYMC', 'HYMCL', 'HYMCW', 'HYMCZ',
    'HYPR', 'HYRE', 'HYT', 'HYW', 'HYZN', 'HYZNW', 'HZN', 'HZNP', 'HZO', 'HZON',
    'IAA', 'IAC', 'IACC', 'IAE', 'IAF', 'IAG', 'IART', 'IAS', 'IAUX', 'IBA', 'IBCP',
    'IBER', 'IBEX', 'IBIO', 'IBKR', 'IBM', 'IBN', 'IBOC', 'IBP', 'IBRX', 'IBTX',
    'ICAD', 'ICCC', 'ICCH', 'ICCM', 'ICD', 'ICE', 'ICFI', 'ICHR', 'ICL', 'ICLK',
    'ICLR', 'ICMB', 'ICNC', 'ICPT', 'ICUI', 'ICVX', 'ID', 'IDA', 'IDAI', 'IDBA',
    'IDCC', 'IDE', 'IDEX', 'IDN', 'IDR', 'IDRA', 'IDT', 'IDW', 'IDXX', 'IDYA',
    'IEA', 'IEAWW', 'IEP', 'IESC', 'IEX', 'IFBD', 'IFF', 'IFIN', 'IFN', 'IFRX',
    'IFS', 'IGA', 'IGAC', 'IGACU', 'IGACW', 'IGC', 'IGD', 'IGI', 'IGIC', 'IGMS',
    'IGNY', 'IGNYU', 'IGNYW', 'IGR', 'IGT', 'IGTA', 'IGTAR', 'IGTAW', 'IH', 'IHD',
    'IHG', 'IHIT', 'IHRT', 'IHS', 'IHT', 'IHTA', 'IIF', 'III', 'IIII', 'IIIIU',
    'IIIIW', 'IIIN', 'IIIV', 'IIM', 'IINN', 'IINNW', 'IIPR', 'IIVI', 'IIVIP',
    'IKNA', 'IKT', 'ILMN', 'ILPT', 'IMAB', 'IMAC', 'IMACW', 'IMAQ', 'IMAQR',
    'IMAQU', 'IMAQW', 'IMAX', 'IMBI', 'IMBIL', 'IMCC', 'IMCR', 'IMGN', 'IMGO',
    'IMH', 'IMKTA', 'IMMP', 'IMMR', 'IMMX', 'IMNM', 'IMO', 'IMOS', 'IMPL', 'IMPP',
    'IMPPP', 'IMPX', 'IMRA', 'IMRN', 'IMRNW', 'IMRX', 'IMTE', 'IMTX', 'IMTXW',
    'IMUX', 'IMV', 'IMVT', 'IMXI', 'INAB', 'INBK', 'INBKZ', 'INBX', 'INCR', 'INCY',
    'INDB', 'INDI', 'INDIW', 'INDO', 'INDP', 'INDT', 'INFA', 'INFI', 'INFN', 'INFU',
    'INFY', 'ING', 'INGN', 'INGR', 'INKA', 'INKAU', 'INKAW', 'INKT', 'INM', 'INMB',
    'INMD', 'INN', 'INNV', 'INO', 'INOD', 'INPX', 'INSE', 'INSG', 'INSI', 'INSM',
    'INSP', 'INST', 'INSW', 'INT', 'INTA', 'INTC', 'INTEU', 'INTEW', 'INTG', 'INTT',
    'INTU', 'INTZ', 'INUV', 'INVA', 'INVE', 'INVH', 'INVO', 'INVZ', 'INVZW', 'INZY',
    'IOAC', 'IOACU', 'IOACW', 'IOBT', 'IONM', 'IONQ', 'IONS', 'IOR', 'IOSP', 'IOT',
    'IOVA', 'IP', 'IPA', 'IPAR', 'IPAX', 'IPAXU', 'IPAXW', 'IPDN', 'IPG', 'IPGP',
    'IPHA', 'IPI', 'IPOD', 'IPOF', 'IPSC', 'IPVA', 'IPVF', 'IPVI', 'IPVIU', 'IPVIW',
    'IPW', 'IPWR', 'IQ', 'IQI', 'IQMD', 'IQMDU', 'IQMDW', 'IQV', 'IR', 'IRBT',
    'IRCP', 'IRDM', 'IREN', 'IRIX', 'IRL', 'IRM', 'IRMD', 'IRNT', 'IROQ', 'IRRX',
    'IRS', 'IRT', 'IRTC', 'IRWD', 'IS', 'ISAA', 'ISD', 'ISDR', 'ISEE', 'ISIG',
    'ISLE', 'ISLEW', 'ISO', 'ISPC', 'ISPO', 'ISPOW', 'ISR', 'ISRG', 'ISSC', 'ISTR',
    'ISUN', 'IT', 'ITAQ', 'ITAQU', 'ITCB', 'ITCI', 'ITGR', 'ITHX', 'ITHXU', 'ITHXW',
    'ITI', 'ITIC', 'ITOS', 'ITP', 'ITQ', 'ITQRU', 'ITQRW', 'ITRG', 'ITRI', 'ITRM',
    'ITRN', 'ITT', 'ITUB', 'ITW', 'IVA', 'IVAC', 'IVC', 'IVCAU', 'IVCB', 'IVCBU',
    'IVCBW', 'IVCP', 'IVCPU', 'IVCPW', 'IVDA', 'IVH', 'IVR', 'IVT', 'IVZ', 'IX',
    'IXAQ', 'IXAQU', 'IXAQW', 'IXHL', 'IZEA', 'J', 'JACK', 'JAGX', 'JAKK', 'JAMF',
    'JAN', 'JANX', 'JAQC', 'JAQCU', 'JAQCW', 'JATT', 'JAZZ', 'JBGS', 'JBHT', 'JBI',
    'JBK', 'JBL', 'JBLU', 'JBSS', 'JBT', 'JCE', 'JCI', 'JCIC', 'JCICU', 'JCICW',
    'JCSE', 'JCTCF', 'JD', 'JEF', 'JELD', 'JEMD', 'JEQ', 'JFIN', 'JFR', 'JFU', 'JG',
    'JGGC', 'JGGCR', 'JGGCU', 'JGGCW', 'JGH', 'JHAA', 'JHG', 'JHI', 'JHS', 'JHX',
    'JILL', 'JJSF', 'JKHY', 'JKS', 'JLL', 'JLS', 'JMAC', 'JMACU', 'JMACW', 'JMIA',
    'JMM', 'JMSB', 'JNCE', 'JNJ', 'JNPR', 'JOAN', 'JOB', 'JOBY', 'JOE', 'JOF',
    'JOFF', 'JOFFU', 'JOFFW', 'JOUT', 'JP', 'JPC', 'JPI', 'JPM', 'JPS', 'JPT',
    'JQC', 'JRI', 'JRO', 'JRS', 'JRSH', 'JRVR', 'JSD', 'JSM', 'JSPR', 'JSPRW', 'JT',
    'JUGGU', 'JUGGW', 'JUN', 'JUPW', 'JUPWW', 'JVA', 'JWAC', 'JWACR', 'JWEL', 'JWN',
    'JWSM', 'JXN', 'JYAC', 'JYNT', 'JZXN', 'K', 'KACL', 'KACLU', 'KACLW', 'KAHC',
    'KAI', 'KAII', 'KAIIU', 'KAIIW', 'KAIR', 'KAIRU', 'KAIRW', 'KALA', 'KALU',
    'KALV', 'KAMN', 'KAR', 'KARO', 'KAVL', 'KB', 'KBAL', 'KBH', 'KBNT', 'KBNTW',
    'KBR', 'KC', 'KCGI', 'KD', 'KDNY', 'KDP', 'KE', 'KELYA', 'KELYB', 'KEN', 'KEP',
    'KEQU', 'KERN', 'KERNW', 'KEX', 'KEY', 'KEYS', 'KF', 'KFFB', 'KFRC', 'KFS',
    'KFY', 'KGC', 'KHC', 'KIDS', 'KIII', 'KIIIU', 'KIIIW', 'KIM', 'KIND', 'KINS',
    'KINZ', 'KINZU', 'KINZW', 'KIO', 'KIQ', 'KIRK', 'KKR', 'KKRS', 'KLAC', 'KLAQ',
    'KLAQU', 'KLAQW', 'KLIC', 'KLR', 'KLTR', 'KLXE', 'KMB', 'KMDA', 'KMF', 'KMI',
    'KMPB', 'KMPH', 'KMPR', 'KMT', 'KMX', 'KN', 'KNBE', 'KNDI', 'KNOP', 'KNSA',
    'KNSL', 'KNSW', 'KNTE', 'KNTK', 'KNX', 'KO', 'KOD', 'KODK', 'KOF', 'KOP',
    'KOPN', 'KORE', 'KOS', 'KOSS', 'KPLT', 'KPLTW', 'KPRX', 'KPTI', 'KR', 'KRBP',
    'KRC', 'KREF', 'KRG', 'KRKR', 'KRMD', 'KRNL', 'KRNLU', 'KRNLW', 'KRNT', 'KRNY',
    'KRO', 'KRON', 'KROS', 'KRP', 'KRT', 'KRTX', 'KRUS', 'KRYS', 'KSCP', 'KSI',
    'KSICU', 'KSICW', 'KSM', 'KSPN', 'KSS', 'KT', 'KTB', 'KTCC', 'KTF', 'KTH',
    'KTN', 'KTOS', 'KTRA', 'KTTA', 'KTTAW', 'KUKE', 'KULR', 'KURA', 'KVHI', 'KVSA',
    'KVSC', 'KW', 'KWAC', 'KWR', 'KXIN', 'KYCH', 'KYCHR', 'KYCHU', 'KYCHW', 'KYMR',
    'KYN', 'KZIA', 'KZR', 'L', 'LAAA', 'LAAAW', 'LAB', 'LABP', 'LAC', 'LAD', 'LADR',
    'LAKE', 'LAMR', 'LANC', 'LAND', 'LANDM', 'LANDO', 'LARK', 'LASR', 'LATG',
    'LATGU', 'LATGW', 'LAUR', 'LAW', 'LAX', 'LAXXR', 'LAXXU', 'LAXXW', 'LAZ',
    'LAZR', 'LAZY', 'LBAI', 'LBBB', 'LBBBR', 'LBBBU', 'LBBBW', 'LBC', 'LBPH',
    'LBPS', 'LBPSW', 'LBRDA', 'LBRDK', 'LBRDP', 'LBRT', 'LBTYA', 'LBTYB', 'LBTYK',
    'LC', 'LCA', 'LCAA', 'LCAAU', 'LCAAW', 'LCAHW', 'LCFY', 'LCFYW', 'LCI', 'LCID',
    'LCII', 'LCNB', 'LCTX', 'LCUT', 'LDHA', 'LDHAU', 'LDHAW', 'LDI', 'LDOS', 'LDP',
    'LE', 'LEA', 'LEAP', 'LECO', 'LEDS', 'LEE', 'LEG', 'LEGA', 'LEGAU', 'LEGAW',
    'LEGH', 'LEGN', 'LEJU', 'LEN', 'LEO', 'LESL', 'LEU', 'LEV', 'LEVI', 'LEXX',
    'LEXXW', 'LFAC', 'LFACU', 'LFACW', 'LFC', 'LFG', 'LFLY', 'LFLYW', 'LFMD',
    'LFMDP', 'LFST', 'LFT', 'LFTR', 'LFTRW', 'LFUS', 'LFVN', 'LGAC', 'LGACU',
    'LGACW', 'LGHL', 'LGHLW', 'LGI', 'LGIH', 'LGL', 'LGMK', 'LGND', 'LGO', 'LGST',
    'LGSTU', 'LGSTW', 'LGTO', 'LGTOU', 'LGTOW', 'LGV', 'LGVC', 'LGVCU', 'LGVN',
    'LH', 'LHAA', 'LHC', 'LHCG', 'LHDX', 'LHX', 'LI', 'LIAN', 'LIBY', 'LIBYU',
    'LIBYW', 'LICY', 'LIDR', 'LIDRW', 'LIFE', 'LII', 'LILA', 'LILAK', 'LILM',
    'LILMW', 'LIN', 'LINC', 'LIND', 'LINK', 'LION', 'LIONW', 'LIQT', 'LITB', 'LITE',
    'LITM', 'LITT', 'LITTU', 'LITTW', 'LIVB', 'LIVBU', 'LIVBW', 'LIVE', 'LIVN',
    'LIXT', 'LIXTW', 'LIZI', 'LJAQ', 'LJAQU', 'LJAQW', 'LJPC', 'LKCO', 'LKFN',
    'LKQ', 'LL', 'LLAP', 'LLL', 'LLNW', 'LLY', 'LMACA', 'LMACU', 'LMACW', 'LMAO',
    'LMAOW', 'LMAT', 'LMB', 'LMDX', 'LMDXW', 'LMFA', 'LMND', 'LMNL', 'LMNR', 'LMPX',
    'LMST', 'LMT', 'LNC', 'LND', 'LNDC', 'LNFA', 'LNG', 'LNN', 'LNSR', 'LNT',
    'LNTH', 'LNW', 'LOAN', 'LOB', 'LOCC', 'LOCL', 'LOCO', 'LODE', 'LOGC', 'LOGI',
    'LOKM', 'LOMA', 'LOOP', 'LOPE', 'LOTZ', 'LOTZW', 'LOV', 'LOVE', 'LOW', 'LPCN',
    'LPG', 'LPI', 'LPL', 'LPLA', 'LPRO', 'LPSN', 'LPTH', 'LPTX', 'LPX', 'LQDA',
    'LQDT', 'LRCX', 'LRFC', 'LRMR', 'LRN', 'LSAK', 'LSBK', 'LSCC', 'LSEA', 'LSEAW',
    'LSF', 'LSI', 'LSPD', 'LSPR', 'LSPRW', 'LSTR', 'LSXMA', 'LSXMB', 'LSXMK',
    'LTBR', 'LTC', 'LTCH', 'LTCHW', 'LTH', 'LTHM', 'LTRN', 'LTRPA', 'LTRPB', 'LTRX',
    'LTRY', 'LTRYW', 'LU', 'LUB', 'LUCD', 'LULU', 'LUMN', 'LUMO', 'LUNA', 'LUNG',
    'LUV', 'LUXA', 'LUXAU', 'LUXAW', 'LVAC', 'LVACU', 'LVACW', 'LVLU', 'LVO',
    'LVOX', 'LVOXW', 'LVRA', 'LVRAU', 'LVRAW', 'LVS', 'LVTX', 'LW', 'LWAY', 'LWLG',
    'LX', 'LXEH', 'LXFR', 'LXP', 'LXRX', 'LXU', 'LYB', 'LYEL', 'LYFT', 'LYG', 'LYL',
    'LYLT', 'LYRA', 'LYTS', 'LYV', 'LZ', 'LZB', 'M', 'MA', 'MAA', 'MAAQ', 'MAAQR',
    'MAAQU', 'MAAQW', 'MAC', 'MACA', 'MACAU', 'MACAW', 'MACC', 'MACK', 'MAG',
    'MAIN', 'MAN', 'MANH', 'MANT', 'MANU', 'MAPS', 'MAPSW', 'MAQC', 'MAQCW', 'MAR',
    'MARA', 'MARK', 'MARPS', 'MAS', 'MASI', 'MASS', 'MAT', 'MATW', 'MATX', 'MAV',
    'MAX', 'MAXN', 'MAXR', 'MAYS', 'MBAC', 'MBCN', 'MBI', 'MBII', 'MBIN', 'MBINN',
    'MBINO', 'MBINP', 'MBIO', 'MBNKP', 'MBOT', 'MBRX', 'MBSC', 'MBTC', 'MBTCR',
    'MBTCU', 'MBUU', 'MBWM', 'MC', 'MCAA', 'MCAAU', 'MCAAW', 'MCACU', 'MCAE',
    'MCAER', 'MCAF', 'MCAFR', 'MCAG', 'MCAGU', 'MCB', 'MCBC', 'MCBS', 'MCD', 'MCFT',
    'MCG', 'MCHP', 'MCHX', 'MCI', 'MCK', 'MCLD', 'MCLDW', 'MCN', 'MCO', 'MCR',
    'MCRB', 'MCRI', 'MCS', 'MCW', 'MCY', 'MD', 'MDB', 'MDC', 'MDGL', 'MDGS',
    'MDGSW', 'MDH', 'MDIA', 'MDJH', 'MDLZ', 'MDNA', 'MDRR', 'MDRRP', 'MDRX', 'MDT',
    'MDU', 'MDV', 'MDVL', 'MDWD', 'MDWT', 'MDXG', 'MDXH', 'ME', 'MEAC', 'MEACU',
    'MEACW', 'MEC', 'MED', 'MEDP', 'MEDS', 'MEG', 'MEGI', 'MEI', 'MEIP', 'MEKA',
    'MELI', 'MEOA', 'MEOAU', 'MEOAW', 'MEOH', 'MERC', 'MESA', 'MESO', 'MET', 'METC',
    'METCL', 'METX', 'METXW', 'MF', 'MFA', 'MFC', 'MFD', 'MFG', 'MFGP', 'MFH',
    'MFIN', 'MFM', 'MFV', 'MG', 'MGA', 'MGEE', 'MGF', 'MGI', 'MGIC', 'MGLD', 'MGM',
    'MGNI', 'MGNX', 'MGPI', 'MGR', 'MGRB', 'MGRC', 'MGRD', 'MGTA', 'MGTX', 'MGU',
    'MGY', 'MGYR', 'MHD', 'MHF', 'MHH', 'MHI', 'MHK', 'MHLA', 'MHLD', 'MHN', 'MHNC',
    'MHO', 'MHUA', 'MIC', 'MICS', 'MICT', 'MIDD', 'MIGI', 'MILE', 'MILEW', 'MIMO',
    'MIN', 'MIND', 'MINDP', 'MINM', 'MIO', 'MIR', 'MIRM', 'MIRO', 'MIST', 'MIT',
    'MITA', 'MITC', 'MITK', 'MITO', 'MITQ', 'MITT', 'MIXT', 'MIY', 'MKC', 'MKD',
    'MKFG', 'MKL', 'MKSI', 'MKTW', 'MKTWW', 'MKTX', 'ML', 'MLAB', 'MLAC', 'MLACU',
    'MLACW', 'MLAI', 'MLAIU', 'MLAIW', 'MLCO', 'MLI', 'MLKN', 'MLM', 'MLNK', 'MLP',
    'MLR', 'MLSS', 'MLTX', 'MLVF', 'MMAT', 'MMC', 'MMD', 'MMI', 'MMLP', 'MMM',
    'MMMB', 'MMP', 'MMS', 'MMSI', 'MMT', 'MMU', 'MMX', 'MMYT', 'MN', 'MNDO', 'MNDT',
    'MNDY', 'MNKD', 'MNMD', 'MNOV', 'MNP', 'MNPR', 'MNRL', 'MNRO', 'MNSB', 'MNSBP',
    'MNSO', 'MNST', 'MNTK', 'MNTN', 'MNTS', 'MNTSW', 'MNTV', 'MNTX', 'MO', 'MOBQ',
    'MOBQW', 'MOD', 'MODD', 'MODN', 'MODV', 'MOFG', 'MOGO', 'MOGU', 'MOH', 'MOHO',
    'MOLN', 'MOMO', 'MON', 'MOR', 'MORF', 'MORN', 'MOS', 'MOTS', 'MOV', 'MOVE',
    'MOXC', 'MP', 'MPA', 'MPAA', 'MPAC', 'MPACR', 'MPACU', 'MPACW', 'MPB', 'MPC',
    'MPLN', 'MPLX', 'MPRAU', 'MPRAW', 'MPV', 'MPW', 'MPWR', 'MPX', 'MQ', 'MQT',
    'MQY', 'MRAI', 'MRAM', 'MRBK', 'MRC', 'MRCC', 'MRCY', 'MREO', 'MRIN', 'MRK',
    'MRKR', 'MRM', 'MRNA', 'MRNS', 'MRO', 'MRSN', 'MRTN', 'MRTX', 'MRUS', 'MRVI',
    'MRVL', 'MS', 'MSA', 'MSAC', 'MSACW', 'MSB', 'MSBI', 'MSC', 'MSCI', 'MSD',
    'MSDA', 'MSDAU', 'MSDAW', 'MSEX', 'MSFT', 'MSGE', 'MSGM', 'MSGS', 'MSI', 'MSM',
    'MSN', 'MSP', 'MSPR', 'MSPRV', 'MSPRZ', 'MSSAU', 'MSTR', 'MSVB', 'MT', 'MTA',
    'MTAC', 'MTACU', 'MTACW', 'MTAL', 'MTB', 'MTBC', 'MTBCO', 'MTBCP', 'MTC',
    'MTCH', 'MTCN', 'MTCR', 'MTD', 'MTDR', 'MTEK', 'MTEKW', 'MTEM', 'MTEX', 'MTG',
    'MTH', 'MTLS', 'MTMT', 'MTN', 'MTNB', 'MTOR', 'MTP', 'MTR', 'MTRN', 'MTRX',
    'MTRY', 'MTRYU', 'MTRYW', 'MTSI', 'MTTR', 'MTVC', 'MTW', 'MTX', 'MTZ', 'MU',
    'MUA', 'MUC', 'MUDS', 'MUDSU', 'MUDSW', 'MUE', 'MUFG', 'MUI', 'MUJ', 'MULN',
    'MUR', 'MURF', 'MURFU', 'MURFW', 'MUSA', 'MUX', 'MVBF', 'MVF', 'MVIS', 'MVO',
    'MVST', 'MVSTW', 'MVT', 'MWA', 'MX', 'MXC', 'MXCT', 'MXE', 'MXF', 'MXL', 'MYD',
    'MYE', 'MYFW', 'MYGN', 'MYI', 'MYMD', 'MYN', 'MYNA', 'MYNZ', 'MYO', 'MYOV',
    'MYPS', 'MYPSW', 'MYRG', 'MYSZ', 'MYTE', 'NAAC', 'NAACU', 'NAACW', 'NABL',
    'NAC', 'NAD', 'NAII', 'NAK', 'NAN', 'NAOV', 'NAPA', 'NARI', 'NAT', 'NATH',
    'NATI', 'NATR', 'NAUT', 'NAVB', 'NAVI', 'NAZ', 'NBB', 'NBEV', 'NBH', 'NBHC',
    'NBIX', 'NBN', 'NBO', 'NBR', 'NBRV', 'NBSE', 'NBST', 'NBSTU', 'NBSTW', 'NBTB',
    'NBTX', 'NBW', 'NBXG', 'NBY', 'NC', 'NCA', 'NCAC', 'NCACU', 'NCACW', 'NCLH',
    'NCMI', 'NCNA', 'NCNO', 'NCR', 'NCSM', 'NCTY', 'NCV', 'NCZ', 'NDAC', 'NDACU',
    'NDACW', 'NDAQ', 'NDLS', 'NDMO', 'NDP', 'NDRA', 'NDSN', 'NE', 'NEA', 'NECB',
    'NEE', 'NEGG', 'NEM', 'NEN', 'NEO', 'NEOG', 'NEON', 'NEP', 'NEPH', 'NEPT',
    'NERV', 'NESR', 'NESRW', 'NET', 'NETC', 'NETI', 'NEU', 'NEV', 'NEWP', 'NEWR',
    'NEWT', 'NEWTL', 'NEWTZ', 'NEX', 'NEXA', 'NEXI', 'NEXT', 'NFBK', 'NFE', 'NFG',
    'NFGC', 'NFJ', 'NFLX', 'NFNT', 'NFYS', 'NG', 'NGC', 'NGD', 'NGG', 'NGL', 'NGM',
    'NGMS', 'NGS', 'NGVC', 'NGVT', 'NH', 'NHC', 'NHI', 'NHIC', 'NHICW', 'NHS',
    'NHTC', 'NHWK', 'NI', 'NIC', 'NICE', 'NICK', 'NID', 'NIE', 'NILE', 'NIM',
    'NIMC', 'NINE', 'NIO', 'NIQ', 'NISN', 'NIU', 'NJR', 'NKE', 'NKG', 'NKLA',
    'NKSH', 'NKTR', 'NKTX', 'NKX', 'NL', 'NLIT', 'NLITU', 'NLITW', 'NLOK', 'NLS',
    'NLSN', 'NLSP', 'NLSPW', 'NLTX', 'NLY', 'NM', 'NMAI', 'NMCO', 'NMFC', 'NMG',
    'NMI', 'NMIH', 'NML', 'NMM', 'NMMC', 'NMMCU', 'NMMCW', 'NMR', 'NMRD', 'NMRK',
    'NMS', 'NMT', 'NMTC', 'NMTR', 'NMZ', 'NN', 'NNAVW', 'NNBR', 'NNDM', 'NNI',
    'NNN', 'NNOX', 'NNVC', 'NNY', 'NOA', 'NOAC', 'NOACU', 'NOACW', 'NOAH', 'NOC',
    'NODK', 'NOG', 'NOK', 'NOM', 'NOMD', 'NOTV', 'NOV', 'NOVA', 'NOVN', 'NOVT',
    'NOVVR', 'NOVVU', 'NOVVW', 'NOW', 'NP', 'NPABU', 'NPABW', 'NPCE', 'NPCT',
    'NPFD', 'NPK', 'NPO', 'NPTN', 'NPV', 'NQP', 'NR', 'NRAC', 'NRACU', 'NRACW',
    'NRBO', 'NRC', 'NRDS', 'NRDY', 'NREF', 'NRG', 'NRGV', 'NRGX', 'NRIM', 'NRIX',
    'NRK', 'NRO', 'NRP', 'NRSN', 'NRSNW', 'NRT', 'NRUC', 'NRXP', 'NRXPW', 'NRZ',
    'NS', 'NSA', 'NSC', 'NSEC', 'NSIT', 'NSL', 'NSP', 'NSPR', 'NSR', 'NSS', 'NSSC',
    'NSTB', 'NSTC', 'NSTD', 'NSTG', 'NSTS', 'NSYS', 'NTAP', 'NTB', 'NTCO', 'NTCT',
    'NTES', 'NTG', 'NTGR', 'NTIC', 'NTIP', 'NTLA', 'NTNX', 'NTR', 'NTRA', 'NTRB',
    'NTRBW', 'NTRS', 'NTRSO', 'NTST', 'NTUS', 'NTWK', 'NTZ', 'NU', 'NUBIU', 'NUBIW',
    'NUE', 'NUO', 'NURO', 'NUS', 'NUTX', 'NUV', 'NUVA', 'NUVB', 'NUVL', 'NUW',
    'NUWE', 'NUZE', 'NVAC', 'NVACW', 'NVAX', 'NVCN', 'NVCR', 'NVCT', 'NVDA', 'NVEC',
    'NVEE', 'NVEI', 'NVFY', 'NVG', 'NVGS', 'NVIV', 'NVMI', 'NVNO', 'NVO', 'NVOS',
    'NVR', 'NVRO', 'NVS', 'NVSA', 'NVSAU', 'NVSAW', 'NVST', 'NVT', 'NVTA', 'NVTS',
    'NVVE', 'NVVEW', 'NVX', 'NWBI', 'NWE', 'NWFL', 'NWG', 'NWL', 'NWLI', 'NWN',
    'NWPX', 'NWS', 'NWSA', 'NX', 'NXC', 'NXDT', 'NXE', 'NXGL', 'NXGLW', 'NXGN',
    'NXJ', 'NXN', 'NXP', 'NXPI', 'NXPL', 'NXPLW', 'NXRT', 'NXST', 'NXTC', 'NXTP',
    'NYC', 'NYCB', 'NYMT', 'NYMTL', 'NYMTM', 'NYMTN', 'NYMTZ', 'NYMX', 'NYT',
    'NYXH', 'NZF', 'O', 'OACB', 'OAS', 'OB', 'OBCI', 'OBE', 'OBLG', 'OBNK', 'OBSV',
    'OBT', 'OC', 'OCA', 'OCAX', 'OCAXU', 'OCAXW', 'OCC', 'OCCI', 'OCCIN', 'OCCIO',
    'OCDX', 'OCFC', 'OCFCP', 'OCFT', 'OCG', 'OCGN', 'OCN', 'OCSL', 'OCUL', 'OCUP',
    'OCX', 'ODC', 'ODFL', 'ODP', 'OEC', 'OEG', 'OEPW', 'OEPWU', 'OEPWW', 'OESX',
    'OFC', 'OFED', 'OFG', 'OFIX', 'OFLX', 'OFS', 'OG', 'OGE', 'OGEN', 'OGI', 'OGN',
    'OGS', 'OHAA', 'OHAAW', 'OHI', 'OHPA', 'OHPAU', 'OHPAW', 'OI', 'OIA', 'OII',
    'OIIM', 'OIS', 'OKE', 'OKTA', 'OKYO', 'OLB', 'OLED', 'OLIT', 'OLITW', 'OLK',
    'OLLI', 'OLMA', 'OLN', 'OLO', 'OLP', 'OLPX', 'OM', 'OMAB', 'OMC', 'OMCL',
    'OMEG', 'OMER', 'OMEX', 'OMF', 'OMGA', 'OMI', 'OMIC', 'OMQS', 'ON', 'ONB',
    'ONBPO', 'ONBPP', 'ONCR', 'ONCS', 'ONCT', 'ONCY', 'ONDS', 'ONEM', 'ONEW', 'ONL',
    'ONON', 'ONTF', 'ONTO', 'ONTX', 'ONVO', 'ONYX', 'ONYXU', 'ONYXW', 'OOMA', 'OP',
    'OPA', 'OPAD', 'OPBK', 'OPCH', 'OPEN', 'OPFI', 'OPGN', 'OPHC', 'OPI', 'OPINL',
    'OPK', 'OPNT', 'OPOF', 'OPP', 'OPRA', 'OPRT', 'OPRX', 'OPT', 'OPTN', 'OPTT',
    'OPY', 'OR', 'ORA', 'ORAN', 'ORC', 'ORCC', 'ORCL', 'ORGN', 'ORGNW', 'ORGO',
    'ORGS', 'ORI', 'ORIAW', 'ORIC', 'ORLA', 'ORLY', 'ORMP', 'ORN', 'ORRF', 'ORTX',
    'OSBC', 'OSCR', 'OSG', 'OSH', 'OSI', 'OSIS', 'OSK', 'OSPN', 'OSS', 'OST',
    'OSTK', 'OSTR', 'OSTRU', 'OSTRW', 'OSUR', 'OSW', 'OTEC', 'OTECU', 'OTECW',
    'OTEX', 'OTIC', 'OTIS', 'OTLK', 'OTLY', 'OTMO', 'OTMOW', 'OTRK', 'OTRKP',
    'OTTR', 'OUST', 'OUT', 'OVBC', 'OVID', 'OVLY', 'OVV', 'OWL', 'OWLT', 'OXAC',
    'OXACW', 'OXBR', 'OXBRW', 'OXLC', 'OXLCL', 'OXLCM', 'OXLCO', 'OXLCP', 'OXLCZ',
    'OXM', 'OXSQ', 'OXSQG', 'OXSQL', 'OXSQZ', 'OXUS', 'OXUSU', 'OXUSW', 'OXY',
    'OYST', 'OZ', 'OZK', 'OZKAP', 'PAA', 'PAAS', 'PAC', 'PACB', 'PACI', 'PACK',
    'PACW', 'PACX', 'PACXU', 'PACXW', 'PAFO', 'PAFOR', 'PAFOU', 'PAG', 'PAGP',
    'PAGS', 'PAHC', 'PAI', 'PALI', 'PALT', 'PAM', 'PANL', 'PANW', 'PAQC', 'PAQCU',
    'PAQCW', 'PAR', 'PARA', 'PARAA', 'PARAP', 'PARR', 'PASG', 'PATH', 'PATI',
    'PATK', 'PAVM', 'PAVMZ', 'PAX', 'PAXS', 'PAY', 'PAYA', 'PAYC', 'PAYO', 'PAYOW',
    'PAYS', 'PAYX', 'PB', 'PBA', 'PBAX', 'PBAXU', 'PBBK', 'PBF', 'PBFS', 'PBFX',
    'PBH', 'PBHC', 'PBI', 'PBIP', 'PBLA', 'PBPB', 'PBR', 'PBT', 'PBTS', 'PBYI',
    'PCAR', 'PCB', 'PCCT', 'PCCTU', 'PCCTW', 'PCF', 'PCG', 'PCGU', 'PCH', 'PCK',
    'PCM', 'PCN', 'PCOM', 'PCOR', 'PCPC', 'PCQ', 'PCRX', 'PCSA', 'PCSB', 'PCT',
    'PCTI', 'PCTTU', 'PCTTW', 'PCTY', 'PCVX', 'PCX', 'PCXCU', 'PCXCW', 'PCYG',
    'PCYO', 'PD', 'PDCE', 'PDCO', 'PDD', 'PDEX', 'PDFS', 'PDI', 'PDLB', 'PDM',
    'PDO', 'PDOT', 'PDS', 'PDSB', 'PDT', 'PEAK', 'PEAR', 'PEARW', 'PEB', 'PEBK',
    'PEBO', 'PECO', 'PED', 'PEG', 'PEGA', 'PEGR', 'PEGRU', 'PEGRW', 'PEGY', 'PEI',
    'PEN', 'PENN', 'PEO', 'PEP', 'PEPG', 'PEPL', 'PEPLU', 'PEPLW', 'PERI', 'PESI',
    'PETQ', 'PETS', 'PETV', 'PETVW', 'PETZ', 'PFBC', 'PFC', 'PFD', 'PFDR', 'PFDRW',
    'PFE', 'PFG', 'PFGC', 'PFH', 'PFHC', 'PFHD', 'PFIE', 'PFIN', 'PFIS', 'PFL',
    'PFLT', 'PFMT', 'PFN', 'PFO', 'PFS', 'PFSI', 'PFSW', 'PFTA', 'PFTAU', 'PFTAW',
    'PFX', 'PFXNL', 'PFXNZ', 'PG', 'PGC', 'PGEN', 'PGNY', 'PGP', 'PGR', 'PGRE',
    'PGRU', 'PGRW', 'PGRWU', 'PGRWW', 'PGSS', 'PGTI', 'PGZ', 'PH', 'PHAR', 'PHAS',
    'PHAT', 'PHCF', 'PHD', 'PHG', 'PHGE', 'PHI', 'PHIC', 'PHICU', 'PHICW', 'PHIO',
    'PHK', 'PHM', 'PHR', 'PHT', 'PHUN', 'PHUNW', 'PHVS', 'PHX', 'PHYT', 'PI',
    'PIAI', 'PICC', 'PII', 'PIII', 'PIIIW', 'PIK', 'PIM', 'PINC', 'PINE', 'PING',
    'PINS', 'PIPP', 'PIPR', 'PIRS', 'PIXY', 'PJT', 'PK', 'PKBK', 'PKE', 'PKG',
    'PKI', 'PKOH', 'PKX', 'PL', 'PLAB', 'PLAG', 'PLAN', 'PLAO', 'PLAOU', 'PLAY',
    'PLBC', 'PLBY', 'PLCE', 'PLD', 'PLG', 'PLL', 'PLM', 'PLMI', 'PLMIU', 'PLMIW',
    'PLMR', 'PLNT', 'PLOW', 'PLPC', 'PLRX', 'PLSE', 'PLTK', 'PLTR', 'PLUG', 'PLUS',
    'PLX', 'PLXP', 'PLXS', 'PLYA', 'PLYM', 'PM', 'PMCB', 'PMD', 'PME', 'PMF',
    'PMGM', 'PMGMU', 'PMGMW', 'PML', 'PMM', 'PMO', 'PMT', 'PMTS', 'PMVC', 'PMVP',
    'PMX', 'PNACU', 'PNBK', 'PNC', 'PNF', 'PNFP', 'PNFPP', 'PNI', 'PNM', 'PNNT',
    'PNR', 'PNRG', 'PNT', 'PNTG', 'PNTM', 'PNW', 'POAI', 'PODD', 'POET', 'POLA',
    'POLY', 'POND', 'PONO', 'PONOU', 'PONOW', 'POOL', 'POR', 'PORT', 'POSH', 'POST',
    'POW', 'POWI', 'POWL', 'POWRU', 'POWRW', 'POWW', 'POWWP', 'PPBI', 'PPBT', 'PPC',
    'PPG', 'PPHP', 'PPHPR', 'PPHPU', 'PPHPW', 'PPIH', 'PPL', 'PPSI', 'PPT', 'PPTA',
    'PPYA', 'PPYAU', 'PPYAW', 'PRA', 'PRAA', 'PRAX', 'PRBM', 'PRCH', 'PRCT', 'PRDO',
    'PRDS', 'PRE', 'PRENW', 'PRFT', 'PRFX', 'PRG', 'PRGO', 'PRGS', 'PRI', 'PRIM',
    'PRK', 'PRLB', 'PRLD', 'PRLH', 'PRM', 'PRMW', 'PRO', 'PROC', 'PROCW', 'PROF',
    'PROV', 'PRPB', 'PRPC', 'PRPH', 'PRPL', 'PRPO', 'PRQR', 'PRS', 'PRSO', 'PRSR',
    'PRSRU', 'PRSRW', 'PRT', 'PRTA', 'PRTC', 'PRTG', 'PRTH', 'PRTK', 'PRTS', 'PRTY',
    'PRU', 'PRVA', 'PRVB', 'PSA', 'PSAG', 'PSAGU', 'PSAGW', 'PSB', 'PSEC', 'PSF',
    'PSFE', 'PSHG', 'PSMT', 'PSN', 'PSNL', 'PSO', 'PSPC', 'PSTG', 'PSTH', 'PSTI',
    'PSTL', 'PSTV', 'PSTX', 'PSX', 'PT', 'PTA', 'PTC', 'PTCT', 'PTE', 'PTEN',
    'PTGX', 'PTIC', 'PTICU', 'PTICW', 'PTIX', 'PTIXW', 'PTLO', 'PTMN', 'PTN',
    'PTNR', 'PTOC', 'PTOCW', 'PTON', 'PTPI', 'PTR', 'PTRA', 'PTRS', 'PTSI', 'PTVE',
    'PTY', 'PUBM', 'PUCK', 'PUCKU', 'PUCKW', 'PUK', 'PULM', 'PUMP', 'PUYI', 'PV',
    'PVBC', 'PVH', 'PVL', 'PW', 'PWFL', 'PWOD', 'PWP', 'PWPPW', 'PWR', 'PWSC',
    'PWUP', 'PWUPU', 'PWUPW', 'PX', 'PXD', 'PXLW', 'PXS', 'PXSAP', 'PXSAW', 'PYCR',
    'PYN', 'PYPD', 'PYPL', 'PYR', 'PYS', 'PYT', 'PYXS', 'PZC', 'PZG', 'PZN', 'PZZA',
    'QCOM', 'QCRH', 'QD', 'QDEL', 'QFIN', 'QFTA', 'QGEN', 'QH', 'QIPT', 'QK',
    'QLGN', 'QLI', 'QLYS', 'QMCO', 'QNGY', 'QNRX', 'QNST', 'QQQX', 'QRHC', 'QRTEA',
    'QRTEB', 'QRTEP', 'QRVO', 'QS', 'QSI', 'QSIAW', 'QSR', 'QTEK', 'QTEKW', 'QTNT',
    'QTRX', 'QTT', 'QTWO', 'QUAD', 'QUBT', 'QUIK', 'QUMU', 'QUOT', 'QURE', 'QVCC',
    'QVCD', 'R', 'RA', 'RAAS', 'RACB', 'RACE', 'RACY', 'RACYU', 'RACYW', 'RAD',
    'RADA', 'RADI', 'RAIL', 'RAIN', 'RAM', 'RAMMU', 'RAMMW', 'RAMP', 'RAND', 'RANI',
    'RAPT', 'RARE', 'RAVE', 'RBA', 'RBAC', 'RBB', 'RBBN', 'RBCAA', 'RBCN', 'RBKB',
    'RBLX', 'RBOT', 'RC', 'RCA', 'RCAC', 'RCACU', 'RCACW', 'RCAT', 'RCB', 'RCC',
    'RCEL', 'RCFA', 'RCG', 'RCHG', 'RCHGU', 'RCHGW', 'RCI', 'RCII', 'RCKT', 'RCKY',
    'RCL', 'RCLF', 'RCLFW', 'RCM', 'RCMT', 'RCON', 'RCOR', 'RCRT', 'RCRTW', 'RCS',
    'RCUS', 'RDBX', 'RDBXW', 'RDCM', 'RDFN', 'RDHL', 'RDI', 'RDIB', 'RDN', 'RDNT',
    'RDUS', 'RDVT', 'RDW', 'RDWR', 'RDY', 'RE', 'REAL', 'REAX', 'REDU', 'REE',
    'REEAW', 'REED', 'REFI', 'REFR', 'REG', 'REGI', 'REGN', 'REI', 'REKR', 'RELI',
    'RELIW', 'RELL', 'RELX', 'RELY', 'RENEU', 'RENN', 'RENO', 'RENT', 'REPL',
    'REPX', 'RERE', 'RES', 'RETA', 'RETO', 'REV', 'REVB', 'REVBU', 'REVBW', 'REVE',
    'REVEU', 'REVEW', 'REVG', 'REVH', 'REVHU', 'REVHW', 'REX', 'REXR', 'REYN',
    'REZI', 'RF', 'RFAC', 'RFACR', 'RFACU', 'RFACW', 'RFI', 'RFIL', 'RFL', 'RFM',
    'RFMZ', 'RFP', 'RGA', 'RGC', 'RGCO', 'RGEN', 'RGF', 'RGLD', 'RGLS', 'RGNX',
    'RGP', 'RGR', 'RGS', 'RGT', 'RGTI', 'RGTIW', 'RH', 'RHE', 'RHI', 'RHP', 'RIBT',
    'RICK', 'RICO', 'RICOU', 'RICOW', 'RIDE', 'RIG', 'RIGL', 'RILY', 'RILYG',
    'RILYK', 'RILYL', 'RILYM', 'RILYN', 'RILYO', 'RILYP', 'RILYT', 'RILYZ', 'RIO',
    'RIOT', 'RIV', 'RIVN', 'RJAC', 'RJF', 'RKDA', 'RKLB', 'RKLY', 'RKT', 'RKTA',
    'RL', 'RLAY', 'RLGT', 'RLGY', 'RLI', 'RLJ', 'RLMD', 'RLTY', 'RLX', 'RLYB', 'RM',
    'RMAX', 'RMBI', 'RMBL', 'RMBS', 'RMCF', 'RMD', 'RMED', 'RMGC', 'RMGCU', 'RMGCW',
    'RMI', 'RMM', 'RMMZ', 'RMNI', 'RMO', 'RMR', 'RMT', 'RMTI', 'RNA', 'RNAZ',
    'RNDB', 'RNER', 'RNERU', 'RNERW', 'RNG', 'RNGR', 'RNLX', 'RNP', 'RNR', 'RNST',
    'RNW', 'RNWK', 'RNWWW', 'RNXT', 'ROAD', 'ROC', 'ROCAR', 'ROCAU', 'ROCC', 'ROCG',
    'ROCGU', 'ROCGW', 'ROCK', 'ROCL', 'ROCLU', 'ROCLW', 'ROG', 'ROIC', 'ROIV',
    'ROIVW', 'ROK', 'ROKU', 'ROL', 'ROLL', 'ROLLP', 'RONI', 'ROOT', 'ROP', 'ROSE',
    'ROSEU', 'ROSEW', 'ROSS', 'ROST', 'ROVR', 'RPAY', 'RPD', 'RPHM', 'RPID', 'RPM',
    'RPRX', 'RPT', 'RPTX', 'RQI', 'RRAC', 'RRBI', 'RRC', 'RRGB', 'RRR', 'RRX', 'RS',
    'RSF', 'RSG', 'RSI', 'RSKD', 'RSLS', 'RSSS', 'RSVR', 'RSVRW', 'RTL', 'RTLPO',
    'RTLPP', 'RTLR', 'RTX', 'RUBY', 'RUN', 'RUSHA', 'RUSHB', 'RUTH', 'RVAC',
    'RVACW', 'RVLP', 'RVLV', 'RVMD', 'RVNC', 'RVP', 'RVPH', 'RVPHW', 'RVSB', 'RVSN',
    'RVSNW', 'RVT', 'RWAY', 'RWLK', 'RWOD', 'RWODU', 'RWT', 'RXDX', 'RXRA', 'RXRAU',
    'RXRAW', 'RXRX', 'RXST', 'RXT', 'RY', 'RYAAY', 'RYAM', 'RYAN', 'RYI', 'RYN',
    'RYTM', 'RZA', 'RZB', 'RZLT', 'S', 'SA', 'SABR', 'SABRP', 'SABS', 'SABSW',
    'SACC', 'SACH', 'SAFE', 'SAFM', 'SAFT', 'SAGA', 'SAGAR', 'SAGAU', 'SAGE', 'SAH',
    'SAI', 'SAIA', 'SAIC', 'SAIL', 'SAITW', 'SAK', 'SAL', 'SALM', 'SAM', 'SAMA',
    'SAMAU', 'SAMAW', 'SAMG', 'SAN', 'SANA', 'SANB', 'SANBU', 'SANBW', 'SANG',
    'SANM', 'SANW', 'SAP', 'SAR', 'SASI', 'SASR', 'SAT', 'SATL', 'SATLW', 'SATS',
    'SAVA', 'SAVE', 'SB', 'SBAC', 'SBBA', 'SBCF', 'SBET', 'SBEV', 'SBFG', 'SBFM',
    'SBFMW', 'SBGI', 'SBH', 'SBI', 'SBII', 'SBLK', 'SBNY', 'SBNYP', 'SBOW', 'SBR',
    'SBRA', 'SBS', 'SBSI', 'SBSW', 'SBT', 'SBTX', 'SBUX', 'SCAQU', 'SCAQW', 'SCCB',
    'SCCC', 'SCCD', 'SCCE', 'SCCF', 'SCCO', 'SCD', 'SCHL', 'SCHN', 'SCHW', 'SCI',
    'SCKT', 'SCL', 'SCLE', 'SCLEU', 'SCLEW', 'SCM', 'SCMA', 'SCMAW', 'SCOA',
    'SCOAU', 'SCOAW', 'SCOB', 'SCOBW', 'SCOR', 'SCPH', 'SCPL', 'SCPS', 'SCRM',
    'SCRMU', 'SCRMW', 'SCS', 'SCSC', 'SCTL', 'SCU', 'SCUA', 'SCVL', 'SCWX', 'SCX',
    'SCYX', 'SD', 'SDAC', 'SDACU', 'SDACW', 'SDC', 'SDGR', 'SDH', 'SDHY', 'SDIG',
    'SDPI', 'SE', 'SEAC', 'SEAS', 'SEAT', 'SEATW', 'SEB', 'SECO', 'SEDG', 'SEE',
    'SEED', 'SEEL', 'SEER', 'SEIC', 'SELB', 'SELF', 'SEM', 'SEMR', 'SENEA', 'SENEB',
    'SENS', 'SERA', 'SES', 'SESN', 'SEV', 'SEVN', 'SF', 'SFB', 'SFBC', 'SFBS',
    'SFE', 'SFET', 'SFIX', 'SFL', 'SFM', 'SFNC', 'SFST', 'SFT', 'SG', 'SGA', 'SGBX',
    'SGC', 'SGEN', 'SGFY', 'SGH', 'SGHC', 'SGHL', 'SGHLU', 'SGHT', 'SGII', 'SGIIW',
    'SGLY', 'SGMA', 'SGML', 'SGMO', 'SGRP', 'SGRY', 'SGTX', 'SGU', 'SHAC', 'SHACU',
    'SHACW', 'SHAK', 'SHAP', 'SHBI', 'SHC', 'SHCA', 'SHCAU', 'SHCAW', 'SHCR',
    'SHCRW', 'SHEL', 'SHEN', 'SHG', 'SHI', 'SHIP', 'SHLS', 'SHLX', 'SHO', 'SHOO',
    'SHOP', 'SHPW', 'SHQA', 'SHQAU', 'SHQAW', 'SHUA', 'SHUAU', 'SHUAW', 'SHW',
    'SHYF', 'SI', 'SIBN', 'SID', 'SIDU', 'SIEB', 'SIEN', 'SIER', 'SIERU', 'SIERW',
    'SIF', 'SIFY', 'SIG', 'SIGA', 'SIGI', 'SIGIP', 'SII', 'SILC', 'SILK', 'SILV',
    'SIM', 'SIMO', 'SINT', 'SIOX', 'SIRE', 'SIRI', 'SISI', 'SITC', 'SITE', 'SITM',
    'SIVB', 'SIVBP', 'SIX', 'SJ', 'SJI', 'SJIJ', 'SJIV', 'SJM', 'SJR', 'SJT', 'SJW',
    'SKE', 'SKIL', 'SKIN', 'SKLZ', 'SKM', 'SKT', 'SKX', 'SKY', 'SKYA', 'SKYAU',
    'SKYAW', 'SKYH', 'SKYT', 'SKYW', 'SKYX', 'SLAB', 'SLAC', 'SLAM', 'SLAMU',
    'SLAMW', 'SLB', 'SLCA', 'SLCR', 'SLCRW', 'SLDB', 'SLDP', 'SLDPW', 'SLF', 'SLG',
    'SLGC', 'SLGCW', 'SLGG', 'SLGL', 'SLGN', 'SLHG', 'SLHGP', 'SLI', 'SLM', 'SLMBP',
    'SLN', 'SLNG', 'SLNH', 'SLNHP', 'SLNO', 'SLP', 'SLQT', 'SLRC', 'SLRX', 'SLS',
    'SLVM', 'SLVR', 'SLVRU', 'SLVRW', 'SM', 'SMAP', 'SMAPU', 'SMAPW', 'SMAR',
    'SMBC', 'SMBK', 'SMCI', 'SMED', 'SMFG', 'SMFL', 'SMFR', 'SMFRW', 'SMG', 'SMHI',
    'SMID', 'SMIH', 'SMIHU', 'SMIHW', 'SMIT', 'SMLP', 'SMLR', 'SMM', 'SMMF', 'SMMT',
    'SMP', 'SMPL', 'SMR', 'SMRT', 'SMSI', 'SMTC', 'SMTI', 'SMTS', 'SMWB', 'SNA',
    'SNAP', 'SNAX', 'SNAXW', 'SNBR', 'SNCE', 'SNCR', 'SNCRL', 'SNCY', 'SND', 'SNDA',
    'SNDL', 'SNDR', 'SNDX', 'SNES', 'SNEX', 'SNFCA', 'SNGX', 'SNMP', 'SNN', 'SNOA',
    'SNOW', 'SNP', 'SNPO', 'SNPS', 'SNPX', 'SNRH', 'SNRHU', 'SNRHW', 'SNSE', 'SNT',
    'SNTG', 'SNV', 'SNX', 'SNY', 'SO', 'SOBR', 'SOFI', 'SOFO', 'SOHO', 'SOHOB',
    'SOHON', 'SOHOO', 'SOHU', 'SOI', 'SOJC', 'SOJD', 'SOJE', 'SOL', 'SOLN', 'SOLO',
    'SOLOW', 'SON', 'SOND', 'SONDW', 'SONM', 'SONN', 'SONO', 'SONX', 'SONY', 'SOPA',
    'SOPH', 'SOR', 'SOS', 'SOTK', 'SOUN', 'SOUNW', 'SOVO', 'SP', 'SPB', 'SPCB',
    'SPCE', 'SPCM', 'SPCMU', 'SPCMW', 'SPE', 'SPFI', 'SPG', 'SPGI', 'SPGS', 'SPH',
    'SPI', 'SPIR', 'SPK', 'SPKB', 'SPKBU', 'SPKBW', 'SPLK', 'SPLP', 'SPNE', 'SPNS',
    'SPNT', 'SPOK', 'SPOT', 'SPPI', 'SPR', 'SPRB', 'SPRC', 'SPRO', 'SPSC', 'SPT',
    'SPTK', 'SPTKW', 'SPTN', 'SPWH', 'SPWR', 'SPXC', 'SPXX', 'SQ', 'SQFT', 'SQFTP',
    'SQFTW', 'SQL', 'SQLLW', 'SQM', 'SQNS', 'SQSP', 'SQZ', 'SR', 'SRAD', 'SRAX',
    'SRC', 'SRCE', 'SRCL', 'SRDX', 'SRE', 'SREA', 'SREV', 'SRG', 'SRGA', 'SRI',
    'SRL', 'SRLP', 'SRNE', 'SRPT', 'SRRA', 'SRRK', 'SRSA', 'SRSAU', 'SRSAW', 'SRT',
    'SRTS', 'SRV', 'SRZN', 'SRZNW', 'SSAA', 'SSAAW', 'SSB', 'SSBI', 'SSBK', 'SSD',
    'SSIC', 'SSKN', 'SSL', 'SSNC', 'SSNT', 'SSP', 'SSRM', 'SSSS', 'SSSSL', 'SST',
    'SSTI', 'SSTK', 'SSU', 'SSY', 'SSYS', 'ST', 'STAA', 'STAB', 'STAF', 'STAG',
    'STBA', 'STC', 'STCN', 'STE', 'STEM', 'STEP', 'STER', 'STET', 'STEW', 'STG',
    'STGW', 'STIM', 'STK', 'STKL', 'STKS', 'STLA', 'STLD', 'STM', 'STN', 'STNE',
    'STNG', 'STOK', 'STON', 'STOR', 'STRA', 'STRC', 'STRCW', 'STRE', 'STRL', 'STRM',
    'STRN', 'STRNW', 'STRO', 'STRR', 'STRRP', 'STRS', 'STRT', 'STRY', 'STSA',
    'STSS', 'STSSW', 'STT', 'STTK', 'STVN', 'STWD', 'STX', 'STXS', 'STZ', 'SU',
    'SUAC', 'SUI', 'SUM', 'SUMO', 'SUMR', 'SUN', 'SUNL', 'SUNW', 'SUP', 'SUPN',
    'SUPV', 'SURF', 'SURG', 'SURGW', 'SUZ', 'SVC', 'SVFA', 'SVFAU', 'SVFAW', 'SVFB',
    'SVFC', 'SVFD', 'SVM', 'SVNA', 'SVNAU', 'SVNAW', 'SVRA', 'SVT', 'SVVC', 'SWAG',
    'SWAGU', 'SWAGW', 'SWAV', 'SWBI', 'SWCH', 'SWET', 'SWETU', 'SWETW', 'SWI',
    'SWIM', 'SWIR', 'SWK', 'SWKH', 'SWKS', 'SWM', 'SWN', 'SWSS', 'SWSSU', 'SWSSW',
    'SWT', 'SWTX', 'SWVL', 'SWVLW', 'SWX', 'SWZ', 'SXC', 'SXI', 'SXT', 'SXTC', 'SY',
    'SYBT', 'SYBX', 'SYF', 'SYK', 'SYN', 'SYNA', 'SYNH', 'SYNL', 'SYPR', 'SYRS',
    'SYTA', 'SYTAW', 'SYY', 'SZC', 'SZZL', 'SZZLU', 'SZZLW', 'T', 'TA', 'TAC',
    'TACA', 'TACT', 'TAIT', 'TAK', 'TAL', 'TALK', 'TALKW', 'TALO', 'TALS', 'TANH',
    'TANNI', 'TANNL', 'TANNZ', 'TAOP', 'TAP', 'TARA', 'TARO', 'TARS', 'TASK',
    'TAST', 'TATT', 'TAYD', 'TBB', 'TBBK', 'TBC', 'TBCP', 'TBCPU', 'TBCPW', 'TBI',
    'TBK', 'TBKCP', 'TBLA', 'TBLAW', 'TBLD', 'TBLT', 'TBLTW', 'TBNK', 'TBPH',
    'TBSA', 'TBSAW', 'TC', 'TCAC', 'TCACU', 'TCACW', 'TCBC', 'TCBI', 'TCBIO',
    'TCBK', 'TCBP', 'TCBPW', 'TCBS', 'TCBX', 'TCDA', 'TCFC', 'TCI', 'TCMD', 'TCN',
    'TCOA', 'TCOM', 'TCON', 'TCPC', 'TCRR', 'TCRT', 'TCRX', 'TCS', 'TCVA', 'TCX',
    'TD', 'TDC', 'TDCX', 'TDF', 'TDG', 'TDOC', 'TDS', 'TDUP', 'TDW', 'TDY', 'TEAF',
    'TEAM', 'TECH', 'TECK', 'TECTP', 'TEDU', 'TEF', 'TEI', 'TEKK', 'TEKKU', 'TEKKW',
    'TEL', 'TELA', 'TELL', 'TELZ', 'TEN', 'TENB', 'TENX', 'TEO', 'TER', 'TERN',
    'TESS', 'TETC', 'TETCU', 'TETCW', 'TETE', 'TETEU', 'TEVA', 'TEX', 'TFC', 'TFFP',
    'TFII', 'TFSA', 'TFSL', 'TFX', 'TG', 'TGA', 'TGAA', 'TGAAU', 'TGAAW', 'TGAN',
    'TGB', 'TGH', 'TGI', 'TGLS', 'TGNA', 'TGR', 'TGS', 'TGT', 'TGTX', 'TGVC',
    'TGVCU', 'TGVCW', 'TH', 'THAC', 'THACU', 'THACW', 'THC', 'THCA', 'THCAW',
    'THCP', 'THCPU', 'THCPW', 'THFF', 'THG', 'THM', 'THMO', 'THO', 'THQ', 'THR',
    'THRM', 'THRN', 'THRX', 'THRY', 'THS', 'THTX', 'THW', 'THWWW', 'TIG', 'TIGO',
    'TIGR', 'TIL', 'TILE', 'TIMB', 'TINV', 'TIOA', 'TIOAW', 'TIPT', 'TIRX', 'TISI',
    'TITN', 'TIVC', 'TIXT', 'TJX', 'TK', 'TKAT', 'TKC', 'TKLF', 'TKNO', 'TKR',
    'TLGA', 'TLGY', 'TLGYU', 'TLGYW', 'TLIS', 'TLK', 'TLRY', 'TLS', 'TLSA', 'TLYS',
    'TM', 'TMAC', 'TMBR', 'TMC', 'TMCI', 'TMCWW', 'TMDI', 'TMDX', 'TME', 'TMHC',
    'TMKR', 'TMKRU', 'TMKRW', 'TMO', 'TMP', 'TMPMW', 'TMQ', 'TMST', 'TMUS', 'TMX',
    'TNC', 'TNDM', 'TNET', 'TNGX', 'TNK', 'TNL', 'TNON', 'TNP', 'TNXP', 'TNYA',
    'TOAC', 'TOACU', 'TOACW', 'TOI', 'TOIIW', 'TOL', 'TOMZ', 'TOPS', 'TOST', 'TOUR',
    'TOWN', 'TPB', 'TPBAW', 'TPC', 'TPG', 'TPGY', 'TPH', 'TPHS', 'TPIC', 'TPL',
    'TPR', 'TPST', 'TPTA', 'TPTX', 'TPVG', 'TPX', 'TPZ', 'TR', 'TRAQ', 'TRC',
    'TRCA', 'TRDA', 'TREC', 'TREE', 'TREX', 'TRGP', 'TRHC', 'TRI', 'TRIB', 'TRIN',
    'TRIP', 'TRIS', 'TRKA', 'TRKAW', 'TRMB', 'TRMD', 'TRMK', 'TRMR', 'TRN', 'TRNO',
    'TRNS', 'TRON', 'TRONU', 'TRONW', 'TROO', 'TROW', 'TROX', 'TRP', 'TRQ', 'TRS',
    'TRST', 'TRT', 'TRTL', 'TRTN', 'TRTX', 'TRU', 'TRUE', 'TRUP', 'TRV', 'TRVG',
    'TRVI', 'TRVN', 'TRX', 'TS', 'TSAT', 'TSBK', 'TSC', 'TSCAP', 'TSCBP', 'TSCO',
    'TSE', 'TSEM', 'TSHA', 'TSI', 'TSIB', 'TSIBU', 'TSIBW', 'TSLA', 'TSLX', 'TSM',
    'TSN', 'TSP', 'TSPQ', 'TSQ', 'TSRI', 'TSVT', 'TT', 'TTC', 'TTCF', 'TTD', 'TTE',
    'TTEC', 'TTEK', 'TTGT', 'TTI', 'TTM', 'TTMI', 'TTNP', 'TTOO', 'TTP', 'TTSH',
    'TTWO', 'TU', 'TUEM', 'TUFN', 'TUP', 'TURN', 'TUSK', 'TUYA', 'TV', 'TVC', 'TVE',
    'TVTX', 'TVTY', 'TW', 'TWCB', 'TWCBW', 'TWI', 'TWIN', 'TWKS', 'TWLO', 'TWLV',
    'TWLVU', 'TWLVW', 'TWN', 'TWND', 'TWNI', 'TWNK', 'TWO', 'TWOA', 'TWOU', 'TWST',
    'TWTR', 'TX', 'TXG', 'TXMD', 'TXN', 'TXRH', 'TXT', 'TY', 'TYDEV', 'TYG', 'TYL',
    'TYME', 'TYRA', 'TZOO', 'TZPS', 'TZPSW', 'U', 'UA', 'UAA', 'UAL', 'UAMY', 'UAN',
    'UAVS', 'UBA', 'UBCP', 'UBER', 'UBFO', 'UBOH', 'UBP', 'UBS', 'UBSI', 'UBX',
    'UCBI', 'UCBIO', 'UCL', 'UCTT', 'UDMY', 'UDR', 'UE', 'UEC', 'UEIC', 'UFAB',
    'UFCS', 'UFI', 'UFPI', 'UFPT', 'UG', 'UGI', 'UGIC', 'UGP', 'UGRO', 'UHAL',
    'UHS', 'UHT', 'UI', 'UIHC', 'UIS', 'UK', 'UKOMW', 'UL', 'ULBI', 'ULCC', 'ULH',
    'ULTA', 'UMBF', 'UMC', 'UMH', 'UMPQ', 'UNAM', 'UNB', 'UNCY', 'UNF', 'UNFI',
    'UNH', 'UNIT', 'UNM', 'UNMA', 'UNP', 'UNTY', 'UNVR', 'UONE', 'UONEK', 'UP',
    'UPC', 'UPH', 'UPLD', 'UPS', 'UPST', 'UPTD', 'UPTDU', 'UPTDW', 'UPWK', 'URBN',
    'URG', 'URGN', 'URI', 'UROY', 'USA', 'USAC', 'USAK', 'USAP', 'USAS', 'USAU',
    'USB', 'USCB', 'USCT', 'USCTU', 'USCTW', 'USDP', 'USEG', 'USER', 'USFD', 'USIO',
    'USLM', 'USM', 'USNA', 'USPH', 'USWS', 'USWSW', 'USX', 'UTAA', 'UTAAU', 'UTAAW',
    'UTF', 'UTG', 'UTHR', 'UTI', 'UTL', 'UTMD', 'UTME', 'UTRS', 'UTSI', 'UTZ',
    'UUU', 'UUUU', 'UVE', 'UVSP', 'UVV', 'UWMC', 'UXIN', 'UZD', 'UZE', 'UZF', 'V',
    'VABK', 'VAC', 'VACC', 'VAL', 'VALE', 'VALN', 'VALU', 'VAPO', 'VAQC', 'VATE',
    'VAXX', 'VBF', 'VBFC', 'VBIV', 'VBLT', 'VBNK', 'VBOC', 'VBOCU', 'VBOCW', 'VBTX',
    'VC', 'VCEL', 'VCIF', 'VCKA', 'VCKAU', 'VCKAW', 'VCNX', 'VCSA', 'VCTR', 'VCV',
    'VCXA', 'VCXAU', 'VCXAW', 'VCXB', 'VCYT', 'VEC', 'VECO', 'VECT', 'VEDU', 'VEEE',
    'VEEV', 'VEL', 'VELO', 'VELOU', 'VELOW', 'VENA', 'VENAR', 'VENAU', 'VENAW',
    'VEON', 'VERA', 'VERB', 'VERBW', 'VERI', 'VERO', 'VERU', 'VERV', 'VERX', 'VERY',
    'VET', 'VEV', 'VFC', 'VFF', 'VFL', 'VG', 'VGFC', 'VGI', 'VGII', 'VGM', 'VGR',
    'VGZ', 'VHAQ', 'VHC', 'VHI', 'VHNA', 'VHNAW', 'VIA', 'VIAO', 'VIASP', 'VIAV',
    'VICI', 'VICR', 'VIEW', 'VIEWW', 'VIGL', 'VII', 'VIIAU', 'VIIAW', 'VINC',
    'VINE', 'VINO', 'VINP', 'VIOT', 'VIPS', 'VIR', 'VIRC', 'VIRI', 'VIRT', 'VIRX',
    'VISL', 'VIST', 'VITL', 'VIV', 'VIVE', 'VIVK', 'VIVO', 'VJET', 'VKI', 'VKQ',
    'VKTX', 'VLAT', 'VLATU', 'VLATW', 'VLCN', 'VLD', 'VLDR', 'VLDRW', 'VLGEA',
    'VLN', 'VLNS', 'VLO', 'VLON', 'VLRS', 'VLT', 'VLTA', 'VLY', 'VLYPO', 'VLYPP',
    'VMAR', 'VMC', 'VMCA', 'VMCAU', 'VMCAW', 'VMD', 'VMEO', 'VMGA', 'VMGAU',
    'VMGAW', 'VMI', 'VMO', 'VMW', 'VNCE', 'VNDA', 'VNET', 'VNO', 'VNOM', 'VNRX',
    'VNT', 'VNTR', 'VOC', 'VOD', 'VOR', 'VORB', 'VORBW', 'VOXX', 'VOYA', 'VPCB',
    'VPCBW', 'VPG', 'VPV', 'VQS', 'VRA', 'VRAR', 'VRAY', 'VRCA', 'VRDN', 'VRE',
    'VREX', 'VRM', 'VRME', 'VRMEW', 'VRNA', 'VRNS', 'VRNT', 'VRPX', 'VRRM', 'VRSK',
    'VRSN', 'VRT', 'VRTS', 'VRTV', 'VRTX', 'VS', 'VSAC', 'VSACU', 'VSAT', 'VSCO',
    'VSEC', 'VSH', 'VSSYW', 'VST', 'VSTA', 'VSTM', 'VSTO', 'VTAQ', 'VTAQR', 'VTAQU',
    'VTAQW', 'VTEX', 'VTGN', 'VTIQ', 'VTIQU', 'VTIQW', 'VTN', 'VTNR', 'VTOL', 'VTR',
    'VTRS', 'VTRU', 'VTSI', 'VTVT', 'VTYX', 'VUZI', 'VVI', 'VVNT', 'VVOS', 'VVPR',
    'VVR', 'VVV', 'VWE', 'VWEWW', 'VXRT', 'VYGG', 'VYGR', 'VYNE', 'VYNT', 'VZ',
    'VZIO', 'VZLA', 'W', 'WAB', 'WABC', 'WAFD', 'WAFDP', 'WAFU', 'WAL', 'WALD',
    'WALDU', 'WALDW', 'WARR', 'WASH', 'WAT', 'WATT', 'WAVC', 'WAVD', 'WAVE', 'WAVS',
    'WAVSW', 'WB', 'WBA', 'WBD', 'WBEV', 'WBS', 'WBT', 'WBX', 'WCC', 'WCN', 'WD',
    'WDAY', 'WDC', 'WDFC', 'WDH', 'WDI', 'WE', 'WEA', 'WEAV', 'WEBR', 'WEC', 'WEJO',
    'WEJOW', 'WEL', 'WELL', 'WEN', 'WERN', 'WES', 'WETF', 'WEX', 'WEYS', 'WF',
    'WFC', 'WFCF', 'WFG', 'WFRD', 'WGO', 'WH', 'WHD', 'WHF', 'WHG', 'WHLM', 'WHLR',
    'WHLRD', 'WHLRL', 'WHLRP', 'WHR', 'WIA', 'WILC', 'WIMI', 'WINA', 'WING', 'WINT',
    'WINV', 'WINVR', 'WINVW', 'WIRE', 'WISA', 'WISH', 'WIT', 'WIW', 'WIX', 'WK',
    'WKEY', 'WKHS', 'WKME', 'WKSP', 'WKSPW', 'WLDN', 'WLFC', 'WLK', 'WLKP', 'WLL',
    'WLMS', 'WLY', 'WLYB', 'WM', 'WMB', 'WMC', 'WMG', 'WMK', 'WMPN', 'WMS', 'WMT',
    'WNC', 'WNEB', 'WNNR', 'WNS', 'WNW', 'WOLF', 'WOOF', 'WOR', 'WORX', 'WOW',
    'WPC', 'WPCA', 'WPCB', 'WPM', 'WPP', 'WPRT', 'WQGA', 'WRAC', 'WRAP', 'WRB',
    'WRBY', 'WRE', 'WRK', 'WRLD', 'WRN', 'WSBC', 'WSBCP', 'WSBF', 'WSC', 'WSFS',
    'WSM', 'WSO', 'WSR', 'WST', 'WSTG', 'WTBA', 'WTER', 'WTFC', 'WTFCM', 'WTFCP',
    'WTI', 'WTM', 'WTMA', 'WTMAR', 'WTMAU', 'WTRG', 'WTRH', 'WTS', 'WTT', 'WTTR',
    'WTW', 'WU', 'WULF', 'WVE', 'WVFC', 'WVVI', 'WVVIP', 'WW', 'WWAC', 'WWACU',
    'WWACW', 'WWD', 'WWE', 'WWR', 'WWW', 'WY', 'WYNN', 'WYY', 'X', 'XAIR', 'XBIO',
    'XBIOW', 'XBIT', 'XCUR', 'XEL', 'XELA', 'XELAP', 'XELB', 'XENE', 'XERS', 'XFIN',
    'XFINU', 'XFINW', 'XFLT', 'XFOR', 'XGN', 'XHR', 'XIN', 'XL', 'XLO', 'XM',
    'XMTR', 'XNCR', 'XNET', 'XOM', 'XOMA', 'XOMAO', 'XOMAP', 'XOS', 'XOSWW', 'XP',
    'XPAX', 'XPAXW', 'XPDB', 'XPDBU', 'XPDBW', 'XPEL', 'XPER', 'XPEV', 'XPL', 'XPO',
    'XPOA', 'XPOF', 'XPON', 'XPRO', 'XRAY', 'XRTX', 'XRX', 'XSPA', 'XTLB', 'XTNT',
    'XXII', 'XYF', 'XYL', 'Y', 'YALA', 'YCBD', 'YELL', 'YELP', 'YETI', 'YEXT',
    'YGMZ', 'YI', 'YJ', 'YMAB', 'YMM', 'YMTX', 'YORW', 'YOTAU', 'YOU', 'YPF', 'YQ',
    'YRD', 'YSG', 'YTEN', 'YTPG', 'YTRA', 'YUM', 'YUMC', 'YVR', 'YY', 'Z', 'ZBH',
    'ZBRA', 'ZCMD', 'ZD', 'ZDGE', 'ZEAL', 'ZEN', 'ZENV', 'ZEPP', 'ZEST', 'ZETA',
    'ZEUS', 'ZEV', 'ZG', 'ZGN', 'ZH', 'ZI', 'ZIM', 'ZIMV', 'ZING', 'ZINGU', 'ZINGW',
    'ZION', 'ZIONL', 'ZIONO', 'ZIONP', 'ZIP', 'ZIVO', 'ZIVOW', 'ZKIN', 'ZLAB', 'ZM',
    'ZME', 'ZNH', 'ZNTL', 'ZOM', 'ZS', 'ZSAN', 'ZT', 'ZTAQU', 'ZTAQW', 'ZTEK',
    'ZTO', 'ZTR', 'ZTS', 'ZUMZ', 'ZUO', 'ZVIA', 'ZVO', 'ZWRK', 'ZWRKU', 'ZWRKW',
    'ZWS', 'ZY', 'ZYME', 'ZYNE', 'ZYXI',
]

