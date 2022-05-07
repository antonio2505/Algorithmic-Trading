import config
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import numpy as np
# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd
import threading
import time

api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        #self.data = {}
        self.nextValidOrderId=0
        self.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType',
                                    'Currency', 'Position', 'Avg cost'])
        self.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                          'Account', 'Symbol', 'SecType',
                                          'Exchange', 'Action', 'OrderType',
                                          'TotalQty', 'CashQty', 'LmtPrice',
                                          'AuxPrice', 'Status'])
    '''        
    def historicalData(self, reqId, bar):
        #print(f'Time: {bar.date}, Open: {bar.open}, close: {bar.close}')
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"high":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"high":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
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


def hist_data(symbols, time="mintue", interval=5, start_date="2022-03-01"):
    bars = {}
    for symbol in symbols:
        if time =="minute":
            temp = pd.DataFrame()
            temp = api.get_bars(symbol, TimeFrame(interval, TimeFrameUnit.Minute), start_date, adjustment='all').df
            temp.index = temp.index.tz_convert("America/New_York")
            temp = temp.between_time('09:31', '16:00')
            bars[symbol] =temp
            
        elif time == "hour":
            temp = pd.DataFrame()
            temp = api.get_bars(symbol, TimeFrame.Hour, start_date, adjustment='raw').df
            temp.index = temp.index.tz_convert("America/New_York")
            temp = temp.between_time('09:31', '16:00')
            bars[symbol] =temp
            
        elif time =="day":
            temp = pd.DataFrame()
            temp = api.get_bars(symbol, TimeFrame.Day, start_date, adjustment='raw').df
            temp.index = temp.index.tz_convert("America/New_York")
            temp = temp.between_time('09:31', '16:00')
            bars[symbol] =temp
   
    return bars

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
def MACD(df_dict,a=12,b=26,c=9):
    """function to calculate MACD
       typical values a(fast moving average) = 12; 
                      b(slow moving average) =26; 
                      c(signal line ma window) =9"""
    for df in df_dict:
        df_dict[df]["MA_Fast"]=df_dict[df]["close"].ewm(span=a,min_periods=a).mean()
        df_dict[df]["MA_Slow"]=df_dict[df]["close"].ewm(span=b,min_periods=b).mean()
        df_dict[df]["MACD"]=df_dict[df]["MA_Fast"]-df_dict[df]["MA_Slow"]
        df_dict[df]["Signal"]=df_dict[df]["MACD"].ewm(span=c,min_periods=c).mean()
        df_dict[df].drop(["MA_Fast","MA_Slow"], axis=1, inplace=True)


def stochOscltr(df_dict, lookback=14, k=3, d=3):
    """function to calculate Stochastic Oscillator
       lookback = lookback period
       k and d = moving average window for %K and %D"""
    for df in df_dict:
        df_dict[df]["HH"] = df_dict[df]["high"].rolling(lookback).max()
        df_dict[df]["LL"] = df_dict[df]["low"].rolling(lookback).min()
        df_dict[df]["%K"] = (100 * (df_dict[df]["close"] - df_dict[df]["LL"])/(df_dict[df]["HH"]-df_dict[df]["LL"])).rolling(k).mean()
        df_dict[df]["%D"] = df_dict[df]["%K"].rolling(d).mean()
        df_dict[df].drop(["HH","LL"], axis=1, inplace=True)

def atr(df_dict,n):
    "function to calculate True Range and Average True Range"
    for df in df_dict:
        df_dict[df]['H-L']=abs( df_dict[df]['high']- df_dict[df]['low'])
        df_dict[df]['H-PC']=abs( df_dict[df]['high']- df_dict[df]['close'].shift(1))
        df_dict[df]['L-PC']=abs( df_dict[df]['low']- df_dict[df]['close'].shift(1))
        df_dict[df]['TR']= df_dict[df][['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
        #df['ATR'] = df['TR'].rolling(n).mean()
        df_dict[df]['ATR'] =  df_dict[df]['TR'].ewm(com=n,min_periods=n).mean()
        df_dict[df].drop(["H-L","H-PC","L-PC","TR"], axis=1, inplace=True)


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
    #print("starting passthrough for.....",tickers)
    #hist_data(ticker)
    time.sleep(5)
    df = hist_data(tickers, time='minute', interval=5)
    stochOscltr(df)
    MACD(df)
    MACD(df)
    atr(df,60)
    #df.dropna(inplace=True)
    for ticker in tickers:
        quantity = int(capital/df[ticker]["close"][-1])
        if quantity == 0:
            continue
        if len(pos_df.columns)==0:
            if df[ticker]["MACD"][-1]> df[ticker]["Signal"][-1] and \
               df[ticker]["%K"][-1]> 30 and \
               df[ticker]["%K"][-1] > df[ticker]["%K"][-2]:
                   app.reqIds(-1)
                   time.sleep(2)
                   
                   app.placeOrder(app.nextValidOrderId,usTechStk(ticker),marketOrder("BUY",quantity))
                   time.sleep(5)
                   try:
                       pos_df = app.pos_df
                       time.sleep(5)
                       sl_q = pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1]
                       app.placeOrder(app.nextValidOrderId+1,usTechStk(ticker),stopOrder("SELL",sl_q,round(df[ticker]["close"][-1]-df[ticker]["atr"][-1],1)))
                   except Exception as e:
                        print(e, "no fill for {}".format(ticker))
          
        elif len(pos_df.columns)!=0 and ticker not in pos_df["Symbol"].tolist():
            if df[ticker]["MACD"][-1]> df[ticker]["Signal"][-1] and \
               df[ticker]["%K"][-1]> 30 and \
               df[ticker]["%K"][-1] > df[ticker]["%K"][-2]:
                   app.reqIds(-1)
                   time.sleep(2)
                   
                   app.placeOrder(app.nextValidOrderId,usTechStk(ticker),marketOrder("BUY",quantity))
                   time.sleep(5)
                   try:
                       pos_df = app.pos_df
                       time.sleep(5)
                       sl_q = pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1]
                       app.placeOrder(app.nextValidOrderId+1,usTechStk(ticker),stopOrder("SELL",sl_q,round(df[ticker]["close"][-1]-df[ticker]["atr"][-1],1)))
                   except Exception as e:
                        print(e, "no fill for {}".format(ticker))
                   
        elif len(pos_df.columns)!=0 and ticker in pos_df["Symbol"].tolist():
            if pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1] == 0:
                if df[ticker]["MACD"][-1]> df[ticker]["Signal"][-1] and \
                   df[ticker]["%K"][-1]> 30 and \
                   df[ticker]["%K"][-1] > df[ticker]["%K"][-2]:
                   app.reqIds(-1)
                   time.sleep(2)
                   
                   app.placeOrder(app.nextValidOrderId,usTechStk(ticker),marketOrder("BUY",quantity))
                   time.sleep(5)
                   try:
                       pos_df = app.pos_df
                       time.sleep(5)
                       sl_q = pos_df[pos_df["Symbol"]==ticker]["Position"].sort_values(ascending=True).values[-1]
                       app.placeOrder(app.nextValidOrderId+1,usTechStk(ticker),stopOrder("SELL",sl_q,round(df[ticker]["close"][-1]-df[ticker]["atr"][-1],1)))
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
timeout = time.time() + 60*60*1
while time.time() <= timeout:
    main()
    time.sleep(300 - ((time.time() - starttime) % 300.0))
