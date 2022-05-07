#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 23:55:07 2022

@author: kassi
"""

from ibapi.client import EClient #===> allow us for making the connection with your ib account
from ibapi.wrapper import EWrapper #==> help us translate the info tws send 
from ibapi.contract import Contract
import threading
import time
import pandas as pd

class TradingApp(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self,self)
        self.data = {}
    
    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        if reqId in self.data:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
        
        print("reqId:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))

def websocket_con():
    app.run()
          
app = TradingApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()

def usTeckcurr(symbol,sec_type="CASH",currency="USD",exchange="IDEALPRO"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange= exchange
    return contract

#usTeckcurr()

def histdata(req_num, contract, duration='1 M', candle_size='5 mins'):
    app.reqHistoricalData(reqId=req_num,
                        contract=contract,
                        endDateTime='',
                        durationStr=duration,
                        barSizeSetting=candle_size,
                        whatToShow='MIDPOINT',
                        useRTH=1,
                        formatDate=1,
                        keepUpToDate=0,
                        chartOptions=[])


#data_dict = app.data

###############################storing data into dataframe ##################################
def dataframe(tradeapp_ojt, tickers):
    df_dict = {}
    for ticker in tickers:
        df_dict[ticker]=pd.DataFrame(tradeapp_ojt.data[tickers.index(ticker)])
        df_dict[ticker].set_index("Date", inplace=True)
    tradeapp_ojt.data = {}
    return df_dict

#historicaldata = dataframe(app,tickers)

tickers = ['EUR','AUD']  #,'GBP','NZD','JPY','CHF','CAD'
starttime = time.time()
timeout = time.time() + 60*5
while time.time() <= timeout:
    for ticker in tickers:
        histdata(tickers.index(ticker),usTeckcurr(ticker),'3600 S', '30 secs')
        time.sleep(3)
    historicalData = dataframe(app,tickers)
    time.sleep(30 - ((time.time() - starttime) % 30))
   











