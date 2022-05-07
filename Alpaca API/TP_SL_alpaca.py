
import config
from alpaca_trade_api.rest import REST
from datetime import datetime
import time



api = REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)

#tickers = "FB,AMZN,INTC,MSFT,AAPL,GOOG,CSCO,CMCSA,ADBE,NVDA,NFLX,PYPL,AMGN,AVGO,TXN,CHTR,QCOM,GILD,FISV,BKNG,INTU,ADP,CME,TMUS,MU"
#tickers = tickers.split(",")

tickers = [ 'MNDY', 'MULN', 'ONON', 'PAGS', 'AFRM', 'BEKE', 'BILI', 'COUP', 'DASH', 'DOCU', 'GTLB', 'KC', 
            'LI', 'NIO', 'SHOP', 'SOFI', 'STNE', 'TME', 'XPEV', 'YANG', 'YMM', 'FUTU', 'OKTA', 'PIK', 
           'SQ', 'PTON', 'ASAN','CWEB']


clock = api.get_clock()
#clock.is_open
profit = 0
loss = 0
starttime = time.time()
#timeout = starttime + 60*60*5
end_time = "01:30:00"
while clock.is_open:
    positions = api.list_positions()
    for position in positions:
        try:
            for ticker in tickers:
                if position.symbol == ticker and float(api.get_position(ticker).unrealized_intraday_pl) >= 50:
                    api.close_position(ticker)
                    print(f"{ticker} closed with profit")
                    time.sleep(3)
                    profit+=1
                                        
                elif position.symbol == ticker and float(api.get_position(ticker).unrealized_intraday_pl) <= -150:
                    api.close_position(ticker)
                    print(f"{ticker} closed with loss")
                    time.sleep(3)
                    loss+=1
        except Exception as e:
            print(e)
            continue
        
    #if datetime.now().strftime("%H:%M:%S") == end_time:
       # break
    
print("############# ================= PROFIT AND LOSS COUNT ======================################\n")
print(f"{profit} profits,")
print(f"{loss} losses,")
