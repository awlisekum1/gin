import pandas as pd
import numpy as np
import pickle
import copy
import datetime
import os
import matplotlib.pyplot as plt

import imp
import AccountUpdate
import GetSignal
import PerformanceAnalysis
imp.reload(PerformanceAnalysis)
imp.reload(GetSignal)
imp.reload(AccountUpdate)

filepath = "/Users/TaoLuo/Desktop/backtest/Python/DataCleaning/"
crossdata = pickle.load(open(filepath+'crossdata.p','rb'))

Calendarpath = '/Users/TaoLuo/Desktop/backtest/R/Lib/Lib/Funcs/'
calendar = pd.read_csv(Calendarpath + 'Calendar.csv', encoding = 'iso-8859-1', header = None)
calendar.columns = ['Date', 'Weekday']
calendar = calendar.set_index(calendar['Date'])

index = pickle.load(open(filepath+'index.p','rb'))
#indexpath = "/Users/TaoLuo/Desktop/backtest/R/StrategyWorkFolder/"
#index = pd.read_csv(indexpath + 'Index300.csv', encoding = 'iso-8859-1')
#index.columns = ['Date', 'SZ50', 'HS300', 'ZZ500']
#index['Date'] = [pd.to_datetime(i, format = "%Y/%m/%d").strftime("%Y-%m-%d") for i in index['Date']]
#index = index.set_index('Date',drop = True)

ZZ500 = pd.read_csv('/Users/TaoLuo/Desktop/ownClound/aciestech/index/20060104-20170331/' + '000905.SH.csv', encoding = 'iso-8859-1')
ZZ500 = ZZ500.set_index('Date')


InitialValue = 43000000
start = "2017-05-12"
end = "2017-07-13"
dates = pd.DataFrame(sorted(list(crossdata.keys())), columns = ['date'])
dates = dates.set_index('date', drop = False)
dates = dates.loc[start:end]
dates = list(dates['date'])
account = pd.DataFrame(0, columns = ['totalvalue', 'stockvalue','cash'], index = dates)
account['totalvalue'].iloc[0], account['cash'].iloc[0] = InitialValue, InitialValue
holdings = {}
holdings[dates[0]] = pd.DataFrame(None, columns = ['ticker', 'stocknumber', 'stockprice', 'entryprice'])
tradelist = {}
tradelist[dates[0]] = pd.DataFrame(None, columns = ['ticker', 'tradernumber', 'tradeprice', 'cost'])
untraded = {}
tradecost = {'buy': 0.0003, 'sell': 0.0013}

for day, date in enumerate(dates):
    if day % 245 == 0:
        print(date)
    if day > 0:
        accountstatus = AccountUpdate.account_update(day, dates, tradelist, holdings, account, crossdata)
        account.loc[date], holdings[date], untraded[date] = copy.deepcopy(accountstatus['account']),\
                                                            copy.deepcopy(accountstatus['holdings']),\
                                                            copy.deepcopy(accountstatus['untraded'])
    if day < len(dates) - 1:
        tradelist[date] = GetSignal.generate_tradelist(day, dates, account, tradelist, holdings, crossdata, index, tradecost)     

account['zz500'] = index.loc[account.index, 'ZZ500']
#account['zz500'] = ZZ500.loc[account.index]
account['hs300'] = index.loc[account.index, 'HS300']
account['sz50'] = index.loc[account.index, 'SZ50']

res = PerformanceAnalysis.performance_analysis(account, tradelist, holdings, 'zz500', 0.5)




