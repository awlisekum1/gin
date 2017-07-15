#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 17:12:53 2017

@author: TaoLuo
"""

import pandas as pd
import numpy as np
import pickle
import copy
import datetime
import os
import matplotlib.pyplot as plt

def account_update(day, dates, tradelist, holdings, account, crossdata):
    tickers = list(tradelist[dates[day-1]]['ticker'])
    holdtickers = list(holdings[dates[day-1]]['ticker'])
    currholdings = copy.deepcopy(holdings[dates[day-1]])
    cash = copy.deepcopy(account.loc[dates[day-1], 'cash'])
    currcrossdata =crossdata[dates[day]]
    untraded = []

    cols = ['CLOSE', 'TOTAL_SHARES', 'FLOAT_A_SHARES', 'CLOSE_AFTY']
    yestdata =crossdata[dates[day-1]][cols]
    tickerset = list(set().union(holdtickers, tickers))
    close_div = currcrossdata.loc[tickerset,'CLOSE'].values/yestdata.loc[tickerset,'CLOSE'].values
    close_afty_div = currcrossdata.loc[tickerset,'CLOSE_AFTY'].values/yestdata.loc[tickerset,'CLOSE_AFTY'].values
    shares_div = currcrossdata.loc[tickerset,'FLOAT_A_SHARES'].values/yestdata.loc[tickerset,'FLOAT_A_SHARES'].values
    for i, ticker in enumerate(tickerset):
        if close_afty_div[i] == 1 and close_div[i] != 1:
            if ticker in holdtickers:
                currholdings.loc[ticker, 'stocknumber'] /= close_div[i]
            if ticker in tickers:
                tradelist[dates[day-1]].loc[ticker, 'tradenumber'] /= close_div[i]
        elif abs(close_div[i] - close_afty_div[i]) > 0.01 and shares_div[i] != 1:
            if ticker in holdtickers:
                currholdings.loc[ticker, 'stocknumber'] *= close_div[i]/close_afty_div[i]
            if ticker in tickers:
                tradelist[dates[day-1]].loc[ticker, 'tradenumber'] *= close_div[i]/close_afty_div[i]

    for i, ticker in enumerate(tickers):
        if currcrossdata.loc[ticker, 'VOLUME'] > 0 and \
            currcrossdata.loc[ticker, 'VOLUME'] / (currcrossdata.loc[ticker, 'FLOAT_A_SHARES']) > 0.001 and \
            currcrossdata.loc[ticker, 'HIGH'] != currcrossdata.loc[ticker, 'LOW']:
            if tradelist[dates[day-1]].loc[ticker, 'tradenumber'] > currcrossdata.loc[ticker, 'VOLUME'] * 0.1:
                tradelist[dates[day-1]].loc[ticker,'tradenumber'] = np.floor(currcrossdata.loc[ticker,'VOLUME'] * 0.1/100)*100  
            if cash > (tradelist[dates[day-1]].loc[ticker, 'tradenumber'] * tradelist[dates[day-1]].loc[ticker, 'tradeprice'] + tradelist[dates[day-1]].loc[ticker, 'cost']):
                cash -= (tradelist[dates[day-1]].loc[ticker, 'tradenumber'] * tradelist[dates[day-1]].loc[ticker, 'tradeprice'] + tradelist[dates[day-1]].loc[ticker, 'cost'])
                if ticker in holdtickers:
                    tempstockvalue = currholdings.loc[ticker, 'stocknumber'] * currholdings.loc[ticker, 'entryprice']
                    currholdings.loc[ticker, 'stocknumber'] += tradelist[dates[day-1]].loc[ticker, 'tradenumber']
                    tempstockvalue += tradelist[dates[day-1]].loc[ticker,'tradenumber'] * tradelist[dates[day-1]].loc[ticker,'tradeprice']
                    if currholdings.loc[ticker,'stocknumber']:
                        currholdings.loc[ticker,'entryprice'] = tempstockvalue/currholdings.loc[ticker, 'stocknumber']
                    else:
                        currholdings.loc[ticker,'entryprice'] = 0
                else:
                    currholdings.loc[ticker] = None
                    currholdings.loc[ticker, 'ticker'] = ticker
                    currholdings.loc[ticker, 'stocknumber'] = tradelist[dates[day-1]].loc[ticker,'tradenumber']
                    currholdings.loc[ticker, 'entryprice'] = tradelist[dates[day-1]].loc[ticker,'tradeprice']
            else:
                untraded.append([ticker, 'nocash'])
        else:
            untraded.append([ticker, 'novolume'])
    currholdings = currholdings.loc[currholdings['stocknumber'] > 0]
    
    currtickers = list(currholdings.index)
    currholdings['stockprice'] = pd.DataFrame(currcrossdata.loc[currtickers, 'CLOSE'].values, columns = ['stockprice'], index = currtickers)
    stockvalue = np.dot(currholdings['stockprice'].values, currholdings['stocknumber'].values) if len(currholdings['stockprice'].values > 0) else 0
    newaccount = [cash+stockvalue, stockvalue, cash]
    return {'account': newaccount, 'holdings': currholdings, 'untraded': untraded}




