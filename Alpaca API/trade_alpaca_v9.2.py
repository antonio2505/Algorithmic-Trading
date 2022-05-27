

import time
from datetime import datetime
#import datetime as dt
from alpaca_trade_api.rest import REST
import config
from tradingview_ta import *

api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)#tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA"
tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA,ADBE,NVDA,NFLX,PYPL,AMGN,AVGO,TXN,CHTR,QCOM,GILD,FISV,BKNG,INTU,ADP,CME,TMUS,MU,TSLA"
tickers = tickers.split(",")

#tickers = tickers.split(",")



max_pos = 3000 #max position size for each ticker
stop_loss = max_pos*0.05 
take_profit = max_pos*0.01 #1% for each trade

stoch_signal = {}
for ticker in tickers:
    stoch_signal[ticker] = ""



def techAnalysis(symbols, screener='america', exchange='NASDAQ'):
    '''
    go to tvdb.brianthe.dev to select screener and exchange 
    
    Interval.INTERVAL_15_MINUTES
    Interval.INTERVAL_1_DAY
    Interval.INTERVAL_30_MINUTES
    Interval.INTERVAL_5_MINUTES
    Interval.INTERVAL_1_MINUTES
    '''
    try:
        print(f"Analysis for {symbols}")
        tesla = TA_Handler(screener=screener,
                       symbol=symbols,
                       exchange=exchange,
                       interval=Interval.INTERVAL_5_MINUTES)
    
        result = tesla.get_analysis().indicators
        
        last_bbLower = result['BB.lower']
        last_bbUpper = result['BB.upper']
        last_RSI     = result['RSI']
        last_RSI_2 = result['RSI[1]']
        last_D = result['Stoch.D']
        last_D_2 = result['Stoch.D[1]']
        last_K = result['Stoch.K']
        last_K_2 = result['Stoch.K[1]']
        last_close = result["close"]
    except Exception as e:
        print(e)
        pass
    
    return last_close,last_bbLower,last_bbUpper,last_RSI,last_RSI_2,last_D,last_D_2,last_K,last_K_2
   

def main():
    global stoch_signal

    positions = api.list_positions()
    
    for ticker in tickers:

        existing_pos = False

        last_close,last_downbb,last_upbb,last_rsi,last_rsi_2,last_d,last_d_2,last_k,last_k_2 = techAnalysis(ticker)
       
        print("last Close :", last_close)
        print("last bblower :", last_downbb)
        print("last bbupper :", last_upbb)
        print("last RSI   :", last_rsi)
        print("last RSI2  :", last_rsi_2)
        print("last %D      :", last_d)
        print("last %D 2    :", last_d_2)
        print("last %K      :", last_k)
        print("last %K 2    :", last_k_2)
        print("\n")

        if last_close <= last_downbb:
            stoch_signal[ticker] = "oversold"
        elif last_close >= last_upbb:
            stoch_signal[ticker] = "overbought"
        
        for position in positions:
            if len(positions) > 0:
                if position.symbol == ticker and position.qty !=0:
                    print("existing position of {} stocks in {}...skipping".format(position.qty, ticker))
                    existing_pos = True
        
        if stoch_signal[ticker]=="oversold" and last_rsi < 30 and last_d < last_k and existing_pos == False:
            
            api.submit_order(ticker, max(1,int(max_pos/last_close)), "buy", "market", "ioc")
            print("bought {} stocks in {}".format(int(max_pos/last_close),ticker))
            time.sleep(2)
        
        elif stoch_signal[ticker]=="overbought" and last_rsi > 70 and last_d > last_k and existing_pos == False:

            api.submit_order(ticker, max(1,int(max_pos/last_close)), "sell", "market", "ioc")
            print("bought {} stocks in {}".format(int(max_pos/last_close),ticker))
            time.sleep(2)

profit = 0
loss = 0
def sl_tp():
    global profit
    global loss
    positions = api.list_positions()
    for position in positions:
        try:
            for ticker in tickers:
                if position.symbol == ticker and float(api.get_position(ticker).unrealized_intraday_pl) >= take_profit:
                    api.close_position(ticker)
                    print(f"{ticker} closed with profit")
                    time.sleep(3)
                    profit+=1
                                        
                elif position.symbol == ticker and float(api.get_position(ticker).unrealized_intraday_pl) <= -stop_loss:
                    api.close_position(ticker)
                    print(f"{ticker} closed with loss")
                    time.sleep(3)
                    loss+=1
        except Exception as e:
            print(e)
            continue




clock = api.get_clock()
#clock.is_open
starttime = time.time()
#timeout = starttime + 60*5
#end_time = "01:30:00"
while True:
    if clock.is_open:
        try:
            print("starting iteration at {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            main()
            sl_tp()
            print("Waiting........")
            time.sleep(300 - ((time.time() - starttime) % 300))
        except Exception as e:
            print(e)
            continue
    else:
        print("Market is Closed,")
    
    #if datetime.now().strftime("%H:%M:%S") == end_time:
       # break



#close out all positions and orders    
api.close_all_positions()
time.sleep(5)
api.cancel_all_orders()
time.sleep(5)
