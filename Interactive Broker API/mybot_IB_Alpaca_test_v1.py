import requests
import json
import alpaca_trade_api as tradeapi
import numpy as np
# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd
import threading
import time

endpoint = "https://data.alpaca.markets/v1"
headers = json.loads(open("key.txt",'r').read())
api = tradeapi.REST(headers["APCA-API-KEY-ID"], headers["APCA-API-SECRET-KEY"], base_url='https://paper-api.alpaca.markets')

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        #self.data = {}
        #self.nextValidOrderId=0
        self.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType',
                                    'Currency', 'Position', 'Avg cost'])
        self.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                          'Account', 'Symbol', 'SecType',
                                          'Exchange', 'Action', 'OrderType',
                                          'TotalQty', 'CashQty', 'LmtPrice',
                                          'AuxPrice', 'Status'])
    '''        
    def historicalData(self, reqId, bar):
        #print(f'Time: {bar.date}, Open: {bar.open}, Close: {bar.close}')
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
    '''
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        
        #logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)
        
    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        dictionary = {"Account":account, "Symbol": contract.symbol, "SecType": contract.secType,
                      "Currency": contract.currency, "Position": position, "Avg cost": avgCost}
        self.pos_df = self.pos_df.append(dictionary, ignore_index=True)
        
    def positionEnd(self):
        print("Latest position data extracted")
        
    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        dictionary = {"PermId":order.permId, "ClientId": order.clientId, "OrderId": orderId, 
                      "Account": order.account, "Symbol": contract.symbol, "SecType": contract.secType,
                      "Exchange": contract.exchange, "Action": order.action, "OrderType": order.orderType,
                      "TotalQty": order.totalQuantity, "CashQty": order.cashQty, 
                      "LmtPrice": order.lmtPrice, "AuxPrice": order.auxPrice, "Status": orderState.status}
        self.order_df = self.order_df.append(dictionary, ignore_index=True)
        



def usTechStk(symbol,sec_type="STK",currency="USD",exchange="SMART"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def hist_data(symbols, timeframe="15Min", limit=200, start="", end="", after="", until=""):
    """
    returns historical bar data for a string of symbols separated by comma
    symbols should be in a string format separated by comma e.g. symbols = "MSFT,AMZN,GOOG"
    """
    df_data = {}
    bar_url = endpoint + "/bars/{}".format(timeframe)
    params = {"symbols" : symbols,
              "limit" : limit,
              "start" : start,
              "end" : end,
              "after" : after,
              "until" : until}
    r = requests.get(bar_url, headers = headers, params = params)
    json_dump = r.json()
    for symbol in json_dump:
        temp = pd.DataFrame(json_dump[symbol])
        temp.rename({"t":"Time","o":"Open","h":"High","l":"Low","c":"Close","v":"Volume"},axis=1, inplace=True)
        temp["Time"] = pd.to_datetime(temp["Time"], unit="s")
        temp.set_index("Time",inplace=True)
        temp.index = temp.index.tz_localize("UTC").tz_convert("America/Indiana/Petersburg")
        temp.between_time('09:31', '16:00')
        df_data[symbol] = temp
    return df_data
'''
def histData(req_num,contract,duration,candle_size):
    """extracts historical data"""
    app.reqHistoricalData(reqId=req_num, 
                          contract=contract,
                          endDateTime='',
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='ADJUSTED_LAST',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=0,
                          chartOptions=[])	 # EClient function to request contract details
'''

def websocket_con():
    app.run()

app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=1) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
'''
#tickers = "AAPL,FB,AMZN,INTC,MSFT,GOOG,CSCO,CMCSA,ADBE,NVDA,NFLX,PYPL,AMGN,AVGO,TXN,CHTR,QCOM,GILD,FISV,BKNG,INTU,ADP,CME,TMUS,MU"           
stoch_signal = {}
for ticker in tickers.split(","):
    stoch_signal[ticker] = ""
'''
tickers = ["FB","AMZN","INTC","MSFT","AAPL","GOOG","CSCO","CMCSA","ADBE","NVDA",
           "NFLX","PYPL","AMGN","AVGO","TXN","CHTR","QCOM","GILD","FISV","BKNG",
           "INTU","ADP","CME","TMUS","MU"]

capital = 1000

###################storing trade app object in dataframe#######################
'''
def dataDataframe(TradeApp_obj,symbols, symbol):
    "returns extracted historical data in dataframe format"
    df = pd.DataFrame(TradeApp_obj.data[symbols.index(symbol)])
    df.set_index("Date",inplace=True)
    return df
'''
def MACD(DF,a=12,b=26,c=9):
    """function to calculate MACD
       typical values a(fast moving average) = 12; 
                      b(slow moving average) =26; 
                      c(signal line ma window) =9"""
    df = DF.copy()
    df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    return df

def stochOscltr(DF,a=20,b=3):
    """function to calculate Stochastics
       a = lookback period
       b = moving average window for %D"""
    df = DF.copy()
    df['C-L'] = df['Close'] - df['Low'].rolling(a).min()
    df['H-L'] = df['High'].rolling(a).max() - df['Low'].rolling(a).min()
    df['%K'] = df['C-L']/df['H-L']*100
    #df['%D'] = df['%K'].ewm(span=b,min_periods=b).mean()
    return df['%K'].rolling(b).mean()

def atr(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    #df['ATR'] = df['TR'].rolling(n).mean()
    df['ATR'] = df['TR'].ewm(com=n,min_periods=n).mean()
    return df['ATR']

def marketOrder(direction,quantity):
    order = Order()
    order.action = direction
    order.orderType = "MKT"
    order.totalQuantity = quantity
    order.tif = "IOC"
    return order

def stopOrder(direction,quantity,st_price):
    order = Order()
    order.action = direction
    order.orderType = "STP"
    order.totalQuantity = quantity
    order.auxPrice = st_price
    return order


def main():
    #app.data = {}
    app.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType',
                            'Currency', 'Position', 'Avg cost'])
    app.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                      'Account', 'Symbol', 'SecType',
                                      'Exchange', 'Action', 'OrderType',
                                      'TotalQty', 'CashQty', 'LmtPrice',
                                      'AuxPrice', 'Status'])
    app.reqPositions()
    time.sleep(2)
    pos_df = app.pos_df
    pos_df.drop_duplicates(inplace=True,ignore_index=True) # position callback tends to give duplicate values
    app.reqOpenOrders()
    time.sleep(2)
    ord_df = app.order_df
    for ticker in tickers:
        print("starting passthrough for.....",ticker)
        #hist_data(ticker)
        time.sleep(5)
        df = hist_data(ticker)
        df[ticker]["stoch"] = stochOscltr(df[ticker])
        df[ticker]["macd"] = MACD(df[ticker])["MACD"]
        df[ticker]["signal"] = MACD(df[ticker])["Signal"]
        df[ticker]["atr"] = atr(df[ticker],60)
        df[ticker].dropna(inplace=True)
        quantity = int(capital/df[ticker]["Close"][-1])
        if quantity == 0:
            continue
        if len(pos_df.columns)==0:
            if df[ticker]["macd"][-1]> df[ticker]["signal"][-1] and \
               df[ticker]["stoch"][-1]> 30 and \
               df[ticker]["stoch"][-1] > df[ticker]["stoch"][-2]:
                   app.reqIds(-1)
                   time.sleep(2)
                   
                   app.placeOrder(app.nextValidOrderId,usTechStk(ticker),marketOrder("BUY",quantity))
                   time.sleep(5)
                   try:
                       pos_df = app.pos_df
                       time.sleep(5)
                       sl_q = pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1]
                       app.placeOrder(app.nextValidOrderId+1,usTechStk(ticker),stopOrder("SELL",sl_q,round(df[ticker]["Close"][-1]-df[ticker]["atr"][-1],1)))
                   except Exception as e:
                        print(e, "no fill for {}".format(ticker))
          
        elif len(pos_df.columns)!=0 and ticker not in pos_df["Symbol"].tolist():
            if df[ticker]["macd"][-1]> df[ticker]["signal"][-1] and \
               df[ticker]["stoch"][-1]> 30 and \
               df[ticker]["stoch"][-1] > df[ticker]["stoch"][-2]:
                   app.reqIds(-1)
                   time.sleep(2)
                   
                   app.placeOrder(app.nextValidOrderId,usTechStk(ticker),marketOrder("BUY",quantity))
                   time.sleep(5)
                   try:
                       pos_df = app.pos_df
                       time.sleep(5)
                       sl_q = pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1]
                       app.placeOrder(app.nextValidOrderId+1,usTechStk(ticker),stopOrder("SELL",sl_q,round(df[ticker]["Close"][-1]-df[ticker]["atr"][-1],1)))
                   except Exception as e:
                        print(e, "no fill for {}".format(ticker))
                   
        elif len(pos_df.columns)!=0 and ticker in pos_df["Symbol"].tolist():
            if pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1] == 0:
                if df[ticker]["macd"][-1]> df[ticker]["signal"][-1] and \
                   df[ticker]["stoch"][-1]> 30 and \
                   df[ticker]["stoch"][-1] > df[ticker]["stoch"][-2]:
                   app.reqIds(-1)
                   time.sleep(2)
                   
                   app.placeOrder(app.nextValidOrderId,usTechStk(ticker),marketOrder("BUY",quantity))
                   time.sleep(5)
                   try:
                       pos_df = app.pos_df
                       time.sleep(5)
                       sl_q = pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1]
                       app.placeOrder(app.nextValidOrderId+1,usTechStk(ticker),stopOrder("SELL",sl_q,round(df[ticker]["Close"][-1]-df[ticker]["atr"][-1],1)))
                   except Exception as e:
                        print(e, "no fill for {}".format(ticker))
            elif pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1] > 0:
                try:
                    ord_id = ord_df[ord_df["Symbol"]==ticker]["OrderId"].sort_values(ascending=True).values[-1]
                    old_quantity = pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1]
                    app.cancelOrder(ord_id)
                    app.reqIds(-1)
                    time.sleep(2)
                    
                    app.placeOrder(app.nextValidOrderId,usTechStk(ticker),stopOrder("SELL",old_quantity,round(df[ticker]["Close"][-1]-df[ticker]["atr"][-1],1)))
                except Exception as e:
                    print(ticker,e)


#extract and store historical data in dataframe repetitively
starttime = time.time()
timeout = time.time() + 60*1
while time.time() <= timeout:
    main()
    time.sleep(900 - ((time.time() - starttime) % 900.0))
