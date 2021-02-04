#Simple Breakout Strategy : buy signal as soon as its out of previous high and vice versus

import numpy as np
import matplotlib.pyplot as plt


class NadionModulatedPrism(QCAlgorithm):

    def Initialize(self):
        self.SetCash(100000)
        
        self.SetStartDate(2017,9,1)
        self.SetEndDate(2021,1,18) #uses american dating system
        
        self.symbol = self.AddEquity ("ETH", Resolution.Daily).Symbol
        
        #Dynamic change via changes in volatility
        self.lookback = 20 #changes the loopback link
        #dont want the loop back link to be too long or too small so adding constraints 
        self.ceiling, self.floor = 30, 10 #30 days etc change can be
        
        self.initialStopRisk = 0.98 # how close first stock to the securities line, this would allow for two percent loss before it gets hit
        self.trailingStopRisk = 0.9 # how close the stock risk would follow the assets price, trade at the price by 10 percent, gives it enough room to move in otherwise it would get stopped out at every short term reversal
        
        
        
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), \
                        self.TimeRules.AfterMarketOpen(self.symbol, 20), \
                        Action(self.EveryMarketOpen))
    

    def OnData(self, data):# called method everytime the method recieves new data, this method would decide what to do with the data 
        # create plot of the price of the securities that we are trading 
        
        self.Plot("Data Chart", self.symbol, self.Securities[self.symbol].Close)
        
    def EveryMarketOpen(self):
        close = self.History(self.symbol, 31, Resolution.Daily)["close"]#close price
        todayvol = np.std(close[1:31])
        yesterdayvol = np.std(close[0:30])
        deltavol = (todayvol - yesterdayvol) / todayvol
        self.lookback = round(self.lookback * (1 + deltavol))
        
        if self.lookback > self.ceiling:
            self.lookback = self.ceiling
        elif self.lookback < self.floor:
            self.lookback = self.floor
            
            
        self.high = self.History(self.symbol, self.lookback, Resolution.Daily)["high"]
        
        #check if we are already investors, checking if securies is in the highest high 
        if not self.Securities[self.symbol].Invested and \
                self.Securities[self.symbol].Close >= max(self.high[:-1]):
            self.SetHoldings(self.symbol, 1) #setting to one hundred percent holdings
            self.breakoutlvl = max(self.high[:-1])
            self.highestPrice = self.breakoutlvl
            
            
        if self.Securities[self.symbol].Invested: #thye minus symbolises the cell order
            if not self.Transactions.GetOpenOrders(self.symbol):
                self.stopMarketTicket = self.StopMarketOrder(self.symbol, \
                                        -self.Portfolio[self.symbol].Quantity, \
                                        self.initialStopRisk * self.breakoutlvl)
                                        
            
            if self.Securities[self.symbol].Close > self.highestPrice and \
                    self.initialStopRisk * self.breakoutlvl < self.Securities[self.symbol].Close * self.trailingStopRisk: 
                self.highestPrice = self.Securities[self.symbol].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.Securities[self.symbol].Close * self.trailingStopRisk
                self.stopMarketTicket.Update(updateFields)
                
                
                self.Debug(updateFields.StopPrice)
                
            self.Plot("Data Chart", "Stop Price", self.stopMarketTicket.Get(OrderField.StopPrice))
