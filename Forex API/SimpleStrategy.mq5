
#property version   "1.00"
#include <Trade\Trade.mqh>


//inputs
sinput string MAPERIODS;
input double ealots = 0.05;
input int mafastPeriod = 8;
input int maslowPeriod = 21;
input int mamiddlePeriod= 13;

// for H1 period
int trendMaFast;
int trendMaSlow;

//use for the 5 min period 
int handleMaFast;
int handleMaMiddle;
int handleMaSlow;

CTrade trade;

//magic number
int eamagic = 001;



int OnInit()
  {
  trade.SetExpertMagicNumber(eamagic);
  
  trendMaFast = iMA(_Symbol, PERIOD_H1, mafastPeriod, 0, MODE_EMA, PRICE_CLOSE);
  trendMaSlow = iMA(_Symbol, PERIOD_H1, maslowPeriod, 0, MODE_EMA, PRICE_CLOSE);
  
  handleMaFast = iMA(_Symbol, PERIOD_M5, mafastPeriod, 0, MODE_EMA, PRICE_CLOSE);
  handleMaMiddle = iMA(_Symbol, PERIOD_M5, mamiddlePeriod, 0, MODE_EMA, PRICE_CLOSE);
  handleMaSlow = iMA(_Symbol, PERIOD_M5, maslowPeriod, 0, MODE_EMA, PRICE_CLOSE);

   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {

   
  }

void OnTick()
  {
  double maTrendFast[], maTrendSlow[];
  CopyBuffer(trendMaFast,0,0,1,maTrendFast);
  CopyBuffer(trendMaSlow,0,0,1,maTrendSlow);
  
  // for the 5Min period
  double maFast[], maMiddle[], maSlow[];
  CopyBuffer(handleMaFast,0,0,1,maFast);
  CopyBuffer(handleMaMiddle,0,0,1,maMiddle);
  CopyBuffer(handleMaSlow,0,0,1,maSlow);
  
  
  double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
  static double lastbid = bid;
  
  int trendDirection = 0;
  if(maTrendFast[0] > maTrendSlow[0] && bid > maTrendFast[0]) trendDirection = 1;
  else if(maTrendFast[0] < maTrendSlow[0] && bid < maTrendFast[0]) trendDirection = -1;
  
  // check if position exist
  int positions = 0;
  for(int i=PositionsTotal()-1; i>=0; i--){//
      ulong posTicket = PositionGetTicket(i);
      if(PositionSelectByTicket(posTicket)){
         if(PositionGetString(POSITION_SYMBOL) == _Symbol  && PositionGetInteger(POSITION_MAGIC)==eamagic){
            positions++;
            
            if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY){//
               if(PositionGetDouble(POSITION_VOLUME) >= ealots){
                  double tp = PositionGetDouble(POSITION_PRICE_OPEN) + (PositionGetDouble(POSITION_PRICE_OPEN) - PositionGetDouble(POSITION_SL));
                  
                  if(bid >= tp){//
                     if(trade.PositionClosePartial(posTicket,NormalizeDouble(PositionGetDouble(POSITION_VOLUME)/2 ,2))) {//
                        double sl = PositionGetDouble(POSITION_PRICE_OPEN);
                        sl = NormalizeDouble(sl,_Digits);
                        if(trade.PositionModify(posTicket,sl,0)){//
                           
                        }
                     }//
                  }//  
               }
               else {
               
                  int lowest = iLowest(_Symbol, PERIOD_M5, MODE_LOW, 3, 1);
                  double sl = iLow(_Symbol, PERIOD_M5, lowest);
                  sl = NormalizeDouble(sl, _Digits);
                  if(sl > PositionGetDouble(POSITION_SL)){
                     if(trade.PositionModify(posTicket,sl,0)){
                     
                     }
                  }
               }
               
           }else if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_SELL){//
               if(PositionGetDouble(POSITION_VOLUME) >= ealots){
                  double tp = PositionGetDouble(POSITION_PRICE_OPEN) - (PositionGetDouble(POSITION_SL) - PositionGetDouble(POSITION_PRICE_OPEN));
                  
                  if(bid <= tp){//
                     if(trade.PositionClosePartial(posTicket,NormalizeDouble(PositionGetDouble(POSITION_VOLUME)/2 ,2))){
                        double sl = PositionGetDouble(POSITION_PRICE_OPEN);
                        sl = NormalizeDouble(sl,_Digits);
                        if(trade.PositionModify(posTicket,sl,0)){//
                        
                           }
                        }//
                     }//
                  }//            
               }//
               else {
               
                  int highest = iHighest(_Symbol, PERIOD_M5, MODE_HIGH, 3, 1);
                  double sl = iHigh(_Symbol, PERIOD_M5, highest);
                  sl = NormalizeDouble(sl, _Digits);
                  if(sl < PositionGetDouble(POSITION_SL)){
                     if(trade.PositionModify(posTicket,sl,0)){
                     
                     }
                  }
               }
           }//
      }//
  }//
  
    // check if open order exist
  int orders = 0;
  for(int i=OrdersTotal()-1; i>=0; i--){
      ulong orderTicket = OrderGetTicket(i);
      if(OrderSelect(orderTicket)){
         if(OrderGetString(ORDER_SYMBOL) == _Symbol  && OrderGetInteger(ORDER_MAGIC)==eamagic){
            if(OrderGetInteger(ORDER_TIME_SETUP) < TimeCurrent()-30*PeriodSeconds(PERIOD_M1)){
               trade.OrderDelete(orderTicket);//cancel order after 30Min
            }
            orders++;
         }
      }
  }
  
  if(trendDirection==1){
      if(maFast[0] > maMiddle[0] && maMiddle[0] > maSlow[0]){
         if(bid <= maFast[0]){
            if(positions + orders <= 0){
                 int indexHighest = iHighest(_Symbol, PERIOD_M5,MODE_HIGH,5,1);
                 double highPrice = iHigh(_Symbol, PERIOD_M5, indexHighest);
                 highPrice = NormalizeDouble(highPrice, _Digits);
 
                 double sl = iLow(_Symbol, PERIOD_M5, 0) - 30 * _Point;
                 sl = NormalizeDouble(sl, _Digits);
                                
                 trade.BuyStop(ealots,highPrice,_Symbol,sl);
            }
            
         }
   
      }
  }else if(trendDirection == -1){
      if(maFast[0] < maMiddle[0] && maMiddle[0] < maSlow[0]){
         if(bid >= maFast[0]){
            if(positions + orders <= 0){
                 int indexLowest = iLowest(_Symbol, PERIOD_M5,MODE_HIGH,5,1);
                 double lowPrice = iLow(_Symbol, PERIOD_M5, indexLowest);
                 lowPrice = NormalizeDouble(lowPrice, _Digits);
                 
                 double sl = iHigh(_Symbol, PERIOD_M5, 0) + 30 * _Point; //30: nbr of points
                 sl = NormalizeDouble(sl, _Digits);
                 
                 trade.SellStop(ealots,indexLowest, _Symbol,sl);
            }
         }        
   
      }
  }
  //lastbid = bid;//  update lastbid with the current bid price
  Comment("\n Fast Trend MA: ",DoubleToString(maTrendFast[0],_Digits),
          "\n Slow Trend MA: ",DoubleToString(maTrendSlow[0],_Digits),
          "\n Direction    : ", trendDirection,
          "\n",
          "\n Fast MA      : ", DoubleToString(maFast[0],_Digits),
          "\n Middle MA    : ", DoubleToString(maMiddle[0],_Digits),
          "\n Slow MA      : ", DoubleToString(maSlow[0],_Digits),
          "\n Posiyion     :  ",positions,
          "\n Order     :  ",orders);
          
  
}
//+------------------------------------------------------------------+
