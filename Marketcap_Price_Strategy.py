#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 20:28:46 2017

@author: TaoLuo
"""

import pandas as pd
import numpy as np
import pickle
import copy
import datetime
import os
import matplotlib.pyplot as plt
import PerformanceAnalysis
#%% Data Update
startdate = "2017-04-06"
entrydate = "2017-07-13"
today = "2017-07-13"

filepath = "/Users/TaoLuo/Desktop/backtest/Python/DataCleaning/"
crossdata = pickle.load(open(filepath+'crossdata.p','rb'))
if today in crossdata.keys():
    del crossdata[today]
#stockuniverse = pickle.load(open(filepath+'stockuniverse.p','rb'))
dailydatapath = "/Users/TaoLuo/Desktop/ownClound/aciestech/wss/"
dailydata = pd.read_csv(dailydatapath + "marketdata_"+today+".csv",encoding = 'iso-8859-1')
dailydata = dailydata.set_index(['CODE'], drop = True)
if today not in crossdata.keys():
    crossdata[today] = copy.deepcopy(dailydata)
pickle.dump(crossdata, open(filepath+"crossdata.p","wb"))

index = pickle.load(open(filepath+'index.p','rb'))
index = pd.DataFrame(index.values.astype(float), columns = index.columns, index = index.index)
dailyindexpath = '/Users/TaoLuo/Desktop/ownClound/aciestech/index/'
dailyindex = pd.read_csv(dailyindexpath + 'index_' + today + '.csv',encoding = 'iso-8859-1')
indextoday = pd.DataFrame(np.array([dailyindex['CLOSE'][5],dailyindex['CLOSE'][4],dailyindex['CLOSE'][3]]).reshape(1,3), columns = index.columns, index = [today])
if today in index.index:
    index.loc[today] = indextoday.values
else:
    index = index.append(indextoday)
index = index.sort_index()
if dailyindex.CLOSE.dtype == float:
    pickle.dump(index, open(filepath+"index.p","wb"))
else:
    print('Index Data Not Valid!!!')

#%% Calendar

Calendarpath = '/Users/TaoLuo/Desktop/backtest/R/Lib/Lib/Funcs/'
calendar = pd.read_csv(Calendarpath + 'Calendar.csv', encoding = 'iso-8859-1', header = None)
calendar.columns = ['Date', 'Weekday']
calendar = calendar.set_index(calendar['Date'])

#%% Account infomation: current stocklist, account, totolvalue, cash, stock value, etc, read from outside files   
######################
### Initialization ###
######################
productionPath = '/Users/TaoLuo/Desktop/backtest/Python/Stock Strategy/Product1/'
InitialValue = 43000000
#account = pd.DataFrame(None, columns = ['totalvalue','stockvalue','cash'], index = calendar.loc[entrydate:].index)
#account.loc[today] = [InitialValue,InitialValue,0]
#holdings = {}
#holdings[today] = pd.DataFrame(None, columns = ['ticker','stockvalue','stocknumber','stockprice','entryprice'])
#pickle.dump(holdings, open(productionPath+"holdings.p","wb"))
#pickle.dump(account, open(productionPath+"account.p","wb"))

######################
### Working Status ###
######################

####
holdings = pickle.load(open(productionPath+'holdings.p','rb'))
account = pickle.load(open(productionPath+'account.p','rb'))
NAV = pickle.load(open(productionPath+'NAV.p','rb'))

####
temp_holding = pd.read_csv(productionPath + 'account and holdings files/' + today + '_holdings' + '.csv' ,encoding = 'iso-8859-1')
temp_holding = temp_holding[temp_holding.columns[[1,12,4,10,9]]]
temp_holding.columns = ['ticker','stockvalue','stocknumber','stockprice','entryprice']
for i, ticker in enumerate(temp_holding.ticker):
    ticker = str(ticker)
    if len(ticker) < 6:
        ticker = str(0) * (6-len(ticker)) + ticker + '.SZ'
    elif ticker[0] == '3':
        ticker = ticker + '.SZ'
    elif ticker[0] == '6':
        ticker = ticker + '.SH'
    temp_holding.loc[i,'ticker'] = ticker
temp_holding = temp_holding.set_index('ticker', drop = False)
holdings[today] = copy.deepcopy(temp_holding)
####
temp_account = pd.read_csv(productionPath + 'account and holdings files/' + today + '_account' + '.csv' ,encoding = 'iso-8859-1')
account.loc[today, "totalvalue"] = temp_account.loc[1, temp_account.columns[6]]
account.loc[today, "stockvalue"] = temp_account.loc[1, temp_account.columns[7]]
account.loc[today, "cash"] = temp_account.loc[1, temp_account.columns[2]]
####
temp_NAV = pd.read_csv(productionPath + 'account and holdings files/' + today + '_NAV' + '.csv' ,encoding = 'iso-8859-1')
NAVtoday = pd.DataFrame([temp_NAV.iloc[0][0]/49000000], columns = NAV.columns, index = [today])
if today in NAV.index:
    NAV.loc[today] = NAVtoday.values
else:
    NAV = NAV.append(NAVtoday)
####
pickle.dump(holdings, open(productionPath + "holdings.p","wb"))
pickle.dump(account, open(productionPath + "account.p","wb"))
pickle.dump(NAV, open(productionPath + "NAV.p","wb"))

#%% Stock List & weight
dates = calendar.loc[entrydate:today]['Date'].values
day = len(calendar.loc[entrydate:today]) - 1
period = 5
N = 50
posratio = 0.8
totalvalue = account.loc[today, 'totalvalue'] * posratio
iftrade = True
mask1 = crossdata[today]['VOLUME']>0
mask2 = crossdata[today]['VOLUME']/crossdata[today]['TOTAL_SHARES'] > 0.0008
mask3 = crossdata[today]['PE_TTM']>0
#mask4 = crossdata[today]['ANNUALSTDEVR_24M']>0.25
mask = mask1 & mask2 & mask3 
curdata = crossdata[today].loc[mask]
tradetable = crossdata[today]

#Nday = 5
#if day >= Nday:
#    tempdata = crossdata[dates[day - Nday]]
#    Past5DayRet = curdata.loc[tempdata.index, 'CLOSE_AFTY'] / tempdata['CLOSE_AFTY'] - 1
#    mask = (Past5DayRet > -0.2)
#    mask = mask.loc[mask == True]
#    curdata = curdata.loc[mask.index]

temp = curdata['CLOSE'] * curdata['CLOSE'] * curdata['FREE_FLOAT_SHARES']
mask1 = temp.index != '000595.SZ'
mask2 = temp.index != '000780.SZ'
mask3 = temp.index != '002248.SZ'
mask4 = temp.index != '000033.SZ'
mask5 = temp.index != '600370.SH'
mask = mask1 & mask2 & mask3 & mask4 & mask5
temp = temp[mask]
stocklist = temp.sort_values().index[:N - 5] | temp.sort_values().index[-5:]
weight = pd.DataFrame([totalvalue*0.99/N]*N, columns = ["weight"],index = stocklist)

if day % period == 0:
    iftrade = True
else:
    iftrade = False
    
if day >= 1 and account.loc[dates[day],'totalvalue']/account.loc[dates[day-1],'totalvalue'] < 0.985:
    weight = pd.DataFrame([totalvalue*0.7/N]*N, columns = ["weight"],index = stocklist)
    iftrade = True
elif day >= 2 and account.loc[dates[day],'totalvalue']/account.loc[dates[day-2],'totalvalue'] < 0.975:
    weight = pd.DataFrame([totalvalue*0.99/N]*N, columns = ["weight"],index = stocklist)
    iftrade = True
elif day >= 3 and account.loc[dates[day],'totalvalue']/account.loc[dates[day-3],'totalvalue'] < 0.96:
    weight = pd.DataFrame([totalvalue*0.8/N]*N, columns = ["weight"],index = stocklist)
    iftrade = True


#%% Trade List for tomorrow
currstocklist = holdings[today].index
def get_portfolio_diff(stocklist, currstocklist):
    buystocklist = [ticker for ticker in stocklist if ticker not in currstocklist]
    sellstocklist = [ticker for ticker in currstocklist if ticker not in stocklist]
    remainstocklist = [ticker for ticker in stocklist if ticker in currstocklist]
    totallist = []
    totallist.extend(buystocklist)
    totallist.extend(sellstocklist)
    totallist.extend(remainstocklist)
    return buystocklist, sellstocklist, remainstocklist, totallist

buystocklist, sellstocklist, remainstocklist, totallist = get_portfolio_diff(stocklist, currstocklist)
tradelist = []
for i, ticker in enumerate(totallist):
    if iftrade == True and (ticker[0] == '0' or ticker[0] == '3' or ticker[0] == '6'):
        tradeprice = tradetable.loc[ticker,'CLOSE']
        if ticker in buystocklist:
            targetposition = np.floor(weight.loc[ticker, "weight"]/100/tradeprice)*100
        elif ticker in sellstocklist:
            targetposition = -holdings[today].loc[ticker, "stocknumber"]
        elif ticker in remainstocklist:
            targetposition = np.floor((np.floor(weight.loc[ticker,"weight"]/100/tradeprice)*100 - holdings[today].loc[ticker, "stocknumber"])/100)*100
        tradelist.append([ticker, targetposition, tradeprice])
tradelist = pd.DataFrame(tradelist, columns = ["ticker", "tradenumber","tradeprice"])
tradelist = tradelist.loc[tradelist['tradenumber'] != 0]

order = pd.DataFrame(None,columns=['AccountTpye','Account','Ticker','TradeNum','Direction', 'AlgoID','AlgoParams'])
order['AccountTpye'] = ["0"] * len(tradelist['ticker'])
order['Account'] = [101800000076] * len(tradelist['ticker'])
order['Ticker'] = tradelist['ticker'].values
order['TradeNum'] = np.abs([int(i) for i in tradelist['tradenumber'].values])
order['Direction'] = (np.sign(tradelist['tradenumber'].values)*(-0.5)+1.5).astype(int)
order['AlgoID'] = "VWAP"
order['AlgoParams'] = "beginTime=091500;endTime=145000;limitPrice=0;participateRate=0.0;tradingStyle=0"
order.to_csv(productionPath + "order"+today+".csv", columns = None, header = False, index = False)
