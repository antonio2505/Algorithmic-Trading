
#include <Trade/Trade.mqh>


input int closeTimeHour =17;
input int closeTimeMin = 0;
input int closeTimeSec = 0;

input double TargetProfit = 10;



int OnInit()
  {

   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {

   
  }

void OnTick()
  {
   
   MqlDateTime structTime;
   TimeCurrent(structTime);
   
   structTime.hour = closeTimeHour;
   structTime.min = closeTimeMin;
   structTime.sec = closeTimeSec;
   
   datetime timeClose = StructToTime(structTime);
   
   double profit = AccountInfoDouble(ACCOUNT_EQUITY) - AccountInfoDouble(ACCOUNT_BALANCE);
   
   if(TimeCurrent() > timeClose || profit >= TargetProfit){
      
      //close all open position
      CTrade trade;
      for(int i=PositionsTotal()-1; i>=0; i--){
      
         ulong posTicket = PositionGetTicket(i); //get the ticket of the open position
         if(PositionSelectByTicket(posTicket)){
         
            //if true we found a open position
            if(trade.PositionClose(posTicket)){
               
               if(TimeCurrent() > timeClose) Print(__FUNCTION__," > Pos #", posTicket, "was close because of close time...");
               else if(profit >= TargetProfit) Print(__FUNCTION__," > Pos #", posTicket, "was close because of profit...");
            
            }
            
         }
      }
   
   }
   
   Comment("\nServer Time: ", TimeCurrent(),
            "\nClose Time: ", timeClose,
            "\nProfit    :  ",DoubleToString(profit, 2), "(Target: ", DoubleToString(TargetProfit,2),")");
   
  }
//+------------------------------------------------------------------+
