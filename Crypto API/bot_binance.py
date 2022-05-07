#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 21:18:25 2022

@author: kassi
"""

from binance.client import Client
import vectorbt as vbt
import ccxt
import config
import time
from datetime import datetime
import pandas as pd
pd.set_option('display.max_rows',None)
import numpy as np
#import schedule
#from ta.volatility import BollingerBands, AverageTrueRange
import warnings
warnings.filterwarnings('ignore')
#from ta.momentum import RSIIndicator, StochasticOscillator

client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET)

candles = client.get_klines(symbol='BNBBTC', interval=Client.KLINE_INTERVAL_30MINUTE)


def hist_data(symbol, time='15m'):
    kline = vbt.CCXTData.download(symbol, start='1 day ago UTC', end='now UTC', timeframe=time)
    kline = kline.get()
    kline = kline.rename(columns={'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'})
    print(f"{symbol} download,")

    return kline





def get_binance_tickers(endswith = 'USDT'):
    exchange_info = client.get_exchange_info()
    symbols = [s['symbol'] for s in exchange_info['symbols']]
    #symbols = [x['symbol'] for x in info['symbols']]
    exclude = ['UP','DOWN','BEAR','BULL'] #exclude laverage tokens
    non_lav = [symbol for symbol in symbols if all(excludes not in symbol for excludes in exclude)]
    relevant = [symbol for symbol in non_lav if symbol.endswith(endswith)]
    return relevant


exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_SECRET
        })

#balance = exchange.fetch_balance()
#print(balance)
#markets = exchange.load_markets()
'''
def hist_data(symbol, time='15m',limit=365):
    bars = exchange.fetch_ohlcv(symbol, timeframe = time, limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp","open","high","low","close","volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df
'''        

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



dollar_amount = 3
in_position_quantity=0
sold = 0
def buy_sell_signal_(df,tickers):
    global in_position_quantity
    global sold
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
        
        if last_close <=10 and last_close <= last_downbb and last_rsi <= 30 and last_d < 20 and last_k >last_d:
            if in_position_quantity == 0:
                #buy 
                #symbol[:-1] remove the last character (T)
                order = exchange.create_market_buy_order(tickers,float(dollar_amount/last_close))
                print(f"bought {tickers}")
                in_position_quantity = float(order.qty)
                print(order)
            else:
                print("== Alread in position, nothing to do ==\n")
                
        elif last_close >= last_upbb and last_rsi >= 70 and last_d > 80 and last_k < last_d:
            if in_position_quantity > 0:
                #sell: in_position_quantity because we want to sell all the quantity of asset
                order = exchange.create_market_sell_order(tickers,in_position_quantity)
                print(order)
                sold+=1
            else:
                print("== You have Nothing to sell ==\n")
                
    except Exception as e:
        print(e)
        pass
    print(f"{sold} Symbols have been sold,\n")

tickers = get_binance_tickers()   


def analysis():
    print(f"Fetching new bars and analysis for {datetime.now().isoformat()}")
    dff={}
    for ticker in tickers:
       dff[ticker]= hist_data(ticker, time='15m')
       print(f"{ticker}: data download for analysis,")
       #bb
       BB(dff[ticker])
       #rsi
       RSI(dff[ticker])
       #stochastic
       stochastic(dff[ticker])
       #buy or sell
       buy_sell_signal_(dff[ticker], ticker)
       time.sleep(1)


#exchange.create_market_buy_order("SAND/USDT",1)
manager = vbt.ScheduleManager()
manager.every(15).minutes.do(analysis)
manager.start()

#while True:
#    schedule.run_pending()
#    time.sleep(1)





