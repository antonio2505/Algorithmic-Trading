import ccxt
from binance.client import Client
import config
import time
import ta
from datetime import datetime
import pandas as pd
pd.set_option('display.max_rows',None)
import numpy as np
import schedule
from ta.volatility import BollingerBands, AverageTrueRange
import warnings
warnings.filterwarnings('ignore')
#from ta.momentum import RSIIndicator, StochasticOscillator

#tickers = ['BTC/USDT','ETH/USDT']
def get_tickers(endswith = 'USDT'):
    client = Client()
    info = client.get_exchange_info()
    symbols = [x['symbol'] for x in info['symbols']]
    exclude = ['UP','DOWN','BEAR','BULL'] #exclude laverage tokens
    non_lav = [symbol for symbol in symbols if all(excludes not in symbol for excludes in exclude)]
    relevant = [symbol for symbol in non_lav if symbol.endswith(endswith)]
    return relevant

tickers = get_tickers()

exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_SECRET
        })

exchange_ftx = ccxt.ftxf({
            'apiKey': config.FTX_API_KEY,
            'secret': config.FTX_SECRET
        })

#balance = exchange.fetch_balance()
#print(balance)

#markets = exchange.load_markets()
#print(markets)
def hist_data_binance(symbol, time='15m',limit=365):
    bars = exchange.fetch_ohlcv(symbol, timeframe = time, limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp","open","high","low","close","volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def super_trend(df, period=7, multiplier=3):
    atr_indicator = AverageTrueRange(df['high'],df['low'],df['close'],window=period)
    df['atr'] = atr_indicator.average_true_range()
    df['upperband'] = ((df['high']+df['low']) /2) + (multiplier*df['atr'])
    df['lowerband'] = ((df['high']+df['low']) /2) - (multiplier*df['atr'])
    df['in_uptrend'] = True 
    
    for current in range(1,len(df.index)):
        previous = current - 1
        
        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True  
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]
            
            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] < df['lowerband'][previous]
        
            if not df['in_uptrend'][current] and df['upperband'][current] > df['lowerband'][previous]:
                df['upperband'][current] < df['upperband'][previous]
    return df
        

def stochastic(df_dict, lookback=14, k=3, d=3):
    """function to calculate Stochastic Oscillator
    lookback = lookback period
    k and d = moving average window for %K and %D"""
    df_dict["HH"] = df_dict["high"].rolling(lookback).max()
    df_dict["LL"] = df_dict["low"].rolling(lookback).min()
    df_dict["%K"] = (100 * (df_dict["close"] - df_dict["LL"])/(df_dict["HH"]-df_dict["LL"])).rolling(k).mean()
    df_dict["%D"] = df_dict["%K"].rolling(d).mean()
    df_dict.drop(["HH","LL"], axis=1, inplace=True)

def RSI(df_dict, n=14):
    df_dict['chance'] = df_dict['close'] - df_dict['close'].shift(1) 
    df_dict['gain'] = np.where(df_dict['chance']>=0, df_dict['chance'], 0)
    df_dict['loss'] = np.where(df_dict['chance']<0, -1*df_dict['chance'], 0)
    df_dict['avgGain'] = df_dict['gain'].ewm(alpha=1/n, min_periods=n).mean()
    df_dict['avgLoss'] = df_dict['loss'].ewm(alpha=1/n, min_periods=n).mean()
    df_dict['rs'] = df_dict['avgGain'] / df_dict['avgLoss']
    df_dict['rsi'] = 100 - (100/(1 + df_dict['rs']))
    df_dict['rsiDiff'] = df_dict['rsi'].diff()
    df_dict.drop(['chance','gain','loss','avgGain','avgLoss','rs','rsiDiff'], axis=1, inplace=True)


def BB(df_dict, n=14):
    for df in df_dict:
        df_dict['MB'] = df_dict['close'].rolling(n).mean()
        df_dict['UB'] = df_dict['MB'] + 2*df_dict['close'].rolling(n).std(ddof=0)
        df_dict['LB'] = df_dict['MB'] - 2*df_dict['close'].rolling(n).std(ddof=0)
        df_dict['BB_width'] = df_dict['MB'] - df_dict['LB']

dollar_amount = 5
in_position_quantity=0
in_position = False
def buy_sell_signal(df):
    global in_position
    global in_position_quantity
    
    print('checking for buys and sell...')
    print(df.tail(2))
    last_row_index = len(df.index) -1
    previous_row_index = last_row_index - 1
    
    print(last_row_index)
    print(previous_row_index)
    
    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print("changed to uptrend, buy\n")
        if not in_position:
            order = exchange.create_market_buy_order('ETH/USDT',float(dollar_amount/df['close'].iloc[-1]))
            in_position_quantity=float(order.qty)
            print(order)
            in_position = True
        else:
            print("Already in position, Nothing to buy")
        
    if not df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        if in_position:
            print("changed to downtrend, sell\n")
            order = exchange.create_market_sell_order('ETH/USDT',in_position_quantity)
            in_position = False
        else:
            print("you aren't in position, nothing to sell")

def buy_sell_signal_(df):
    global in_position_quantity
    sold = 0
    try:           
        #Stoch
        last_k = df["%K"].iloc[-1]
        last_d = df["%D"].iloc[-1]
        last_rsi = df['rsi'].iloc[-1]
        last_upbb = df['UB'].iloc[-1]
        last_downbb = df['LB'].iloc[-1]
        last_close = df['close'].iloc[-1]
        
        print("%K: ",last_k)
        print("%D: ",last_d)
        print("rsi: ",last_rsi)
        print("UB: ",last_upbb)
        print("LB: ",last_downbb)
        print("last Close",last_close)
        print("\n")
        
        if last_close <= last_downbb and last_rsi <= 30 and last_d < 20 and last_k >last_d:
            if in_position_quantity == 0:
                #buy 
                #symbol[:-1] remove the last character (T)
                order = exchange.create_market_buy_order('ETH/USDT',float(dollar_amount/last_close))
                in_position_quantity = float(order.qty)
                print(order)
            else:
                print("== Alread in position, nothing to do ==\n")
                
        elif last_close >= last_upbb and last_rsi >= 70 and last_d > 80 and last_k < last_d:
            if in_position_quantity > 0:
                #sell: in_position_quantity because we want to sell all the quantity of asset
                order = exchange.create_market_sell_order('ETH/USDT',in_position_quantity)
                print(order)
            else:
                print("== You have Nothing to sell ==\n")
                sold+=1
    except Exception as e:
        print(e)
        pass
    print(f"{sold} Symbols have been sold,")


  

def analysis():
    print(f"Fetching new bars and analysis for {datetime.now().isoformat()}")
    dff={}
    for ticker in tickers:
       dff[ticker]= hist_data_binance(ticker, time='15m', limit=100)
       #bb
       BB(dff[ticker])
       #super_trend
       #super_trend(dff[ticker])
       #rsi
       RSI(dff[ticker])
       #stochastic
       stochastic(dff[ticker])
       #buy or sell
       buy_sell_signal_(dff[ticker])
       #buy_sell_signal(dff[ticker])



schedule.every(15).minutes.do(analysis)

while True:
    schedule.run_pending()
    time.sleep(1)






