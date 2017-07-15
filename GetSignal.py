#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 17:02:39 2017

@author: TaoLuo
"""

import pandas as pd
import numpy as np
import pickle
import copy
import datetime
import os
import matplotlib.pyplot as plt

import imp
import Strategy
imp.reload(Strategy)

def get_portfolio_diff(stocklist, currstocklist):
    buystocklist = [ticker for ticker in stocklist if ticker not in currstocklist]
    sellstocklist = [ticker for ticker in currstocklist if ticker not in stocklist]
    remainstocklist = [ticker for ticker in stocklist if ticker in currstocklist]
    totallist = []
    totallist.extend(buystocklist)
    totallist.extend(sellstocklist)
    totallist.extend(remainstocklist)
    return buystocklist, sellstocklist, remainstocklist, totallist
    
def generate_tradelist(day, dates, account, tradelist, holdings, crossdata, index, tradecost):
    
    stocklist, weight, iftrade = Strategy.strategy_marketcap(day, dates, account, tradelist, holdings, crossdata, index, tradecost)
    
    date = dates[day]
    currstocklist = holdings[date]['ticker']
    curdata = crossdata[date]
    nextdate = dates[day + 1]
    nextdata = crossdata[nextdate]

    buystocklist, sellstocklist, remainstocklist, totallist = get_portfolio_diff(stocklist, currstocklist)
    currtradelist = []
    for i, ticker in enumerate(totallist):
        if iftrade == True:
            tradeprice = curdata.loc[ticker,'CLOSE']
            executionprice = nextdata.loc[ticker, 'VWAP']
            if ticker in buystocklist:
                targetposition = np.floor(weight.loc[ticker, "weight"]/100/tradeprice)*100
                cost = abs(targetposition * tradeprice * tradecost['buy'])
                
            elif ticker in sellstocklist:
                targetposition = -holdings[date].loc[ticker, "stocknumber"]
                cost = abs(targetposition * tradeprice * tradecost['sell'])
                
            elif ticker in remainstocklist:
                targetposition = np.floor(weight.loc[ticker,"weight"]/100/tradeprice)*100 - holdings[date].loc[ticker, "stocknumber"] 
                cost = abs(targetposition * tradeprice * (tradecost['buy'] if targetposition > 0 else tradecost['sell']))  
                
            currtradelist.append([ticker, targetposition, executionprice, cost])
            
    currtradelist = pd.DataFrame(currtradelist, columns = ["ticker", "tradenumber","tradeprice", "cost"])
    currtradelist = currtradelist.set_index('ticker', drop = False)
    currtradelist = currtradelist.loc[currtradelist['tradenumber'] != 0]
    currtradelist = currtradelist.sort_values('tradenumber')
    
    return currtradelist
