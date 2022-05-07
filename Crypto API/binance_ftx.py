import ccxt
import config
import vectorbt as vbt
import time
import pandas as pd
pd.set_option('display.max_rows',None)
import warnings
warnings.filterwarnings('ignore')
#from ta.momentum import RSIIndicator, StochasticOscillator

tickers = ['BTC/USDT']


exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_SECRET
        })

exchange_ftx = ccxt.ftx({
            'apiKey': config.FTX_API_KEY,
            'secret': config.FTX_SECRET
        })


in_position = False
def trade():
    binan = exchange.fetch_ohlcv('BTC/USDT', timeframe = '1m', limit=50)
    ftx = exchange_ftx.fetch_ohlcv('BTC/USDT', timeframe = '1m', limit=50)
    
    df = pd.DataFrame(binan, columns=["timestamp","open","high","low","close","volume"])
    df2 = pd.DataFrame(ftx, columns=["timestamp","open","high","low","close","volume"])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df2['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
      
    last_close_ftx = df2['close'].iloc[-1]
    last_close_binace = df['close'].iloc[-1]
    print('last close on Binance:',last_close_binace)
    print('last close on FTX:',last_close_ftx)
    
    if last_close_binace > last_close_ftx:
        if not in_position:
            print("binance > ftx: ", last_close_binace-last_close_ftx)
            print('buy btc on FTX and sell btc on BINANCE\n')
            #in_position = True
        
    elif last_close_binace < last_close_ftx:
        if not in_position:
            print("binance < ftx: ",last_close_ftx-last_close_binace)
            print('buy btc on BINANCE and sell btc on FTX\n')
           # in_position = True
        
    elif last_close_binace == last_close_ftx:
        if in_position:
            print("binance == ftx")
            print('EXIT THE ORDER\n')
            #in_position = False
            #break
        
    
    
    
    #return last_close_ftx, last_close_binace





starttime = time.time()
while True:
    try:
        print("starting iteration at {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        trade()
        print("Waiting........")
    except Exception as e:
        print(e)
        continue
    #time.sleep(60- ((time.time() - starttime) % 60))







'''
#balance = exchange.fetch_balance()
#print(balance)

#markets = exchange.load_markets()
#print(markets)

def hist_data_binance(symbol, time='15m',limit=365):
    bars = exchange.fetch_ohlcv(symbol, timeframe = time, limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp","open","high","low","close","volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def hist_data_fxt(symbol, time='15m',limit=365):
    bars = exchange_ftx.fetch_ohlcv(symbol, timeframe = time, limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp","open","high","low","close","volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


binance_btc = hist_data_binance('BTC/USDT')

ftx_btc = hist_data_fxt('BTC/USDT')
'''