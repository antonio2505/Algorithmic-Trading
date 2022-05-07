#import pandas as pd
import datetime as dt
import numpy as np
from alpaca_trade_api.rest import REST, TimeFrame
import config


api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)
#tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA"

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


yesterday = dt.date(2022,4,10)
today = dt.date(2022,4,22)

market_cap = 200000000
gap = 5
vol_stock = []
df = {}
filtered={}
############################# STRATEGIES ###############################
count=0
for symbol in tickers:
    try:
        #df[symbol] = yf.download(symbol,start,end)
        #df[symbol] = api.get_barset(symbol, 'day', limit=100).df
        df[symbol] = api.get_bars(symbol, TimeFrame.Day, yesterday.isoformat(), today.isoformat(),adjustment='raw').df
        print(symbol,"download,")
        
        df[symbol]["previous_close"] = df[symbol]["close"].shift(1)
        filtered[symbol] = df[symbol][df[symbol].index.strftime("%Y-%m-%d")==today.isoformat()].copy()
        filtered[symbol]['percent']= filtered[symbol]["open"]/filtered[symbol]["previous_close"]
        filtered[symbol]['Gap (%)'] = round((filtered[symbol]['percent'] - 1)*100,2)
        filtered[symbol]['Up/Down'] = np.where(filtered[symbol]['Gap (%)']>0,"Goes Up","Goes Down")
        
        filtered[symbol]["market_cap"] = round(df[symbol]["volume"].mul(df[symbol]["close"]))
        
        last_gap = filtered[symbol]['Gap (%)'][-1]
        last_cap = filtered[symbol]["market_cap"][-1]

        if  abs(last_gap)> gap and last_cap > market_cap:
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
    print(f"{i}: Gap= {filtered[i]['Gap (%)'][-1]}%  &&  Market Cap= {filtered[i]['market_cap'][-1]}")













