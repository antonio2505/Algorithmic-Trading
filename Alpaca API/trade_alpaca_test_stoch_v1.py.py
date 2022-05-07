
#import yfinance as yf
#from yahoo_fin.stock_info import tickers_sp500, tickers_nasdaq
import numpy as np
import time
from datetime import datetime
#import datetime as dt
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import config
import pandas as pd

api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)#tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA"
#tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA,ADBE,NVDA,NFLX,PYPL,AMGN,AVGO,TXN,CHTR,QCOM,GILD,FISV,BKNG,INTU,ADP,CME,TMUS,MU"
#tickers = tickers_sp500()
#if tickers is not a list
tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA,ADBE,NVDA,NFLX,PYPL,AMGN,AVGO,TXN,CHTR,QCOM,GILD,FISV,BKNG,INTU,ADP,CME,TMUS,MU"
tickers = tickers.split(",")

#tickers = tickers.split(",")



max_pos = 3000 #max position size for each ticker
stoch_signal = {}
for ticker in tickers:
    stoch_signal[ticker] = ""


def hist_data(symbols, time="mintue", interval=15, start_date="2022-04-01"):
    bars = {}
    for symbol in symbols:
        if time =="minute":
            temp = pd.DataFrame()
            temp = api.get_bars(symbol, TimeFrame(interval, TimeFrameUnit.Minute), start_date, adjustment='all').df
            temp.index = temp.index.tz_convert("America/New_York")
            temp = temp.between_time('09:31', '16:00')
            print(f'{symbol}, download')
            bars[symbol] =temp
            
        elif time == "hour":
            temp = pd.DataFrame()
            temp = api.get_bars(symbol, TimeFrame.Hour, start_date, adjustment='raw').df
            temp.index = temp.index.tz_convert("America/New_York")
            temp = temp.between_time('09:31', '16:00')
            print(f'{symbol}, download')
            bars[symbol] =temp
            
        elif time =="day":
            temp = pd.DataFrame()
            temp = api.get_bars(symbol, TimeFrame.Day, start_date, adjustment='raw').df
            temp.index = temp.index.tz_convert("America/New_York")
            temp = temp.between_time('09:31', '16:00')
            print(f'{symbol}, download')
            bars[symbol] =temp
   
    return bars


bb_up = []
bb_down = []
rsi_up = []
rsi_down = []
def RSI(df_dict, n=14):
    for df in df_dict:
        df_dict[df]['chance'] = df_dict[df]['close'] - df_dict[df]['close'].shift(1) 
        df_dict[df]['gain'] = np.where(df_dict[df]['chance']>=0, df_dict[df]['chance'], 0)
        df_dict[df]['loss'] = np.where(df_dict[df]['chance']<0, -1*df_dict[df]['chance'], 0)
        df_dict[df]['avgGain'] = df_dict[df]['gain'].ewm(alpha=1/n, min_periods=n).mean()
        df_dict[df]['avgLoss'] = df_dict[df]['loss'].ewm(alpha=1/n, min_periods=n).mean()
        df_dict[df]['rs'] = df_dict[df]['avgGain'] / df_dict[df]['avgLoss']
        df_dict[df]['rsi'] = 100 - (100/(1 + df_dict[df]['rs']))
        df_dict[df]['rsiDiff'] = df_dict[df]['rsi'].diff()
        df_dict[df].drop(['chance','gain','loss','avgGain','avgLoss','rs','rsiDiff'], axis=1, inplace=True)


def BB(df_dict, n=20):
    for df in df_dict:
        df_dict[df]['MB'] = df_dict[df]['close'].rolling(n).mean()
        df_dict[df]['UB'] = df_dict[df]['MB'] + 2*df_dict[df]['close'].rolling(n).std(ddof=0)
        df_dict[df]['LB'] = df_dict[df]['MB'] - 2*df_dict[df]['close'].rolling(n).std(ddof=0)
        df_dict[df]['BB_width'] = df_dict[df]['MB'] - df_dict[df]['LB']



def stochastic(df_dict, lookback=14, k=3, d=3):
    """function to calculate Stochastic Oscillator
       lookback = lookback period
       k and d = moving average window for %K and %D"""
    for df in df_dict:
        df_dict[df]["HH"] = df_dict[df]["high"].rolling(lookback).max()
        df_dict[df]["LL"] = df_dict[df]["low"].rolling(lookback).min()
        df_dict[df]["%K"] = (100 * (df_dict[df]["close"] - df_dict[df]["LL"])/(df_dict[df]["HH"]-df_dict[df]["LL"])).rolling(k).mean()
        df_dict[df]["%D"] = df_dict[df]["%K"].rolling(d).mean()
        df_dict[df].drop(["HH","LL"], axis=1, inplace=True)


#days_back = 7
#start = dt.datetime.today()-dt.timedelta(days_back)
#end = dt.datetime.today()
def main():
    global stoch_signal
    historicalData = hist_data(tickers,time="minute", interval=5)
    RSI(historicalData)
    BB(historicalData)
    stochastic(historicalData)
    positions = api.list_positions()
    
    for ticker in tickers:
        historicalData[ticker].dropna(inplace=True)
        existing_pos = False

        last_k = historicalData[ticker]["%K"].iloc[-1]
        last_d = historicalData[ticker]["%D"].iloc[-1]
        #last_d_2 = historicalData[ticker]["%D"].iloc[-2]
        last_rsi = historicalData[ticker]["rsi"].iloc[-1]
        last_close = historicalData[ticker]["close"].iloc[-1]
        
        print(f"{ticker}:")
        print("%K: ",last_k)
        print("%D: ",last_d)
        print("rsi: ",last_rsi)
        print("last Close",last_close)
        print("\n")        

    
        for position in positions:
            if len(positions) > 0:
                if position.symbol == ticker and position.qty !=0:
                    print("existing position of {} stocks in {}...skipping".format(position.qty, ticker))
                    existing_pos = True
        
        if last_rsi <= 30 and last_d <=20 and last_d <= last_k and existing_pos == False:
            #if last_d >= 20:
            api.submit_order(ticker, max(1,int(max_pos/last_close)), "buy", "market", "ioc")
            print("bought {} stocks in {}".format(int(max_pos/last_close),ticker))
            stoch_signal[ticker]=='buy'
            time.sleep(2)
        
        elif last_rsi >= 80 and last_d >=80 and last_d >= last_k and existing_pos == False:
            #if last_d <= 80:
            api.submit_order(ticker, max(1,int(max_pos/last_close)), "sell", "market", "ioc")
            print("bought {} stocks in {}".format(int(max_pos/last_close),ticker))
            stoch_signal[ticker]=='sell'
            time.sleep(2)
                
        elif existing_pos == True:
            if stoch_signal[ticker]=='buy' and last_d >= 80:
                api.close_position(ticker)
                print(f"{ticker} closed")
                
            elif stoch_signal[ticker]=='sell' and last_d <= 20:
                api.close_position(ticker)
                print(f"{ticker} closed")



clock = api.get_clock()
#clock.is_open
starttime = time.time()
#timeout = starttime + 60*5
#end_time = "01:30:00"
while True:
    print("starting iteration at {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    main()
    print("Waiting........")
    
    time.sleep(300 - ((time.time() - starttime) % 300))
    
    #if datetime.now().strftime("%H:%M:%S") == end_time:
       # break



#close out all positions and orders    
api.close_all_positions()
time.sleep(5)
api.cancel_all_orders()
time.sleep(5)
