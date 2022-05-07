#!pip3 install tqdm
import pandas as pd
import numpy as np
import vectorbt as vbt
from tqdm import tqdm
from binance.client import Client
'''
KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'
KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'
KLINE_INTERVAL_1WEEK = '1w'
KLINE_INTERVAL_1MONTH = '1M'
'''


def best_crypto(top_best, endswith = 'USDT'):
    
    client = Client()
    info = client.get_exchange_info()
    symbols = [x['symbol'] for x in info['symbols']]
    exclude = ['UP','DOWN','BEAR','BULL'] #exclude laverage tokens
    non_lav = [symbol for symbol in symbols if all(excludes not in symbol for excludes in exclude)]
    relevant = [symbol for symbol in non_lav if symbol.endswith(endswith)]
    
    kline = {}
    for symbol in relevant:
        kline[symbol] = vbt.CCXTData.download('SOLUSDT', start="30 minute ago", timeframe="5m")
        kline[symbol] = kline[symbol].get()
        print(f"{symbol} download,")
    
    returns, symbols = [],[]
    for symbol in relevant:
        if len(kline[symbol]) > 0:
            if kline[symbol]['Close']>=5:
                cumret = (kline[symbol]['Close'].pct_change() + 1).prod() -1
                returns.append(cumret)
                symbols.append(symbol)
            
    retdf = pd.DataFrame(returns, index=symbols, columns=['ret'])
    return retdf.ret.nlargest(top_best)

best_crypto = best_crypto(150)
crypto_list = list(best_crypto.index)

'''
crypto = []
for symbol in crypto_list:
    kline[symbol] = vbt.CCXTData.download('SOLUSDT', start="30 minute ago", timeframe="5m")
    kline[symbol] = kline[symbol].get()
    
    if kline[symbol]["Close"] >=5:
        crypto.append(symbol)
    

'''










