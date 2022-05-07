#import pandas as pd
import datetime as dt
#import yfinance as yf
#from yahoo_fin.stock_info import tickers_sp500, tickers_nasdaq
#import numpy as np
import time
#from datetime import datetime
#import datetime as dt
from alpaca_trade_api.rest import REST, TimeFrame
import config

api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)#tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA"


#stocks = pd.read_csv("sp500.csv")["Symbol"]
#sp500_stock = tickers_sp500()

#ALPACA ASSETS
import config
import alpaca_trade_api as tradeapi
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)
assets = api.list_assets()

tickers = []
for asset in assets:
    if asset.status == "active" and asset.tradable==True and asset.shortable==True:
        #print(asset)
        tickers.append(asset.symbol)
        


#days_back = 200
#start = dt.datetime.today()-dt.timedelta(days_back)
#end = dt.datetime.today()

market_cap = 200000000
gap = 5
vol_stock = []
df = {}

############################# STRATEGIES ###############################
count=0
for symbol in tickers:
    try:
        #df[symbol] = yf.download(symbol,start,end)
        #df[symbol] = api.get_barset(symbol, 'day', limit=100).df
        df[symbol] = api.get_bars(symbol, TimeFrame.Day, "2022-02-01", adjustment='raw').df
        print(symbol,"download,")
        df[symbol]["market_cap"] = round(df[symbol]["volume"].mul(df[symbol]["close"]))
        df[symbol]["Gap%"] = round(df[symbol]["close"].pct_change()*100,2)
        last_change = df[symbol]["Gap%"][-1]
        if abs(last_change) > gap and df[symbol]["market_cap"][-1] >market_cap:
            vol_stock.append(symbol)
            count+=1
    except:
        continue


print(f"########## Stocks with Gap% > {gap}% And Cap > {market_cap}: #########")
print("")
print(f"{count} Stocks has been selected:")

print("")
print(vol_stock)
print("")
for i in vol_stock:
    print(f"{i}: Gap= {df[i]['Gap%'][-1]}%  &&  Market Cap= {df[i]['market_cap'][-1]}")


