#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 17:44:30 2017

@author: TaoLuo
"""
import pandas as pd
import numpy as np
import pickle
import copy
import datetime
import os
import matplotlib.pyplot as plt

def performance_analysis(account, tradelist, holdings, hedge, hedgeratio):
    accountpnl = account['totalvalue'].pct_change(1)[1:]
    indexpnl = account[hedge].pct_change(1)[1:]
    pnl = accountpnl - indexpnl * hedgeratio
    correl = np.corrcoef(accountpnl, indexpnl)[0][1]
    vol = np.std(pnl) * np.sqrt(250)
    annulret = np.mean(pnl) * 250
    ret = sum(pnl)
    compret = np.cumprod(pnl + 1)[-1] - 1
    sharpe = annulret / vol
    winratio = sum(np.array(pnl) > 0)/len(pnl)
    maxdrawdown, cum, curmax = 1000000000, 0, 0
    for i in pnl:
        curmax = max(curmax, cum)
        cum += i
        maxdrawdown = min(maxdrawdown, cum - curmax)
    calmaratio = annulret/abs(maxdrawdown)
    
    lens1 = []
    for date in account.index:
        if date != account.index[-1] and len(holdings[date]) > 0 and len(tradelist[date]) > 0:
            temp = sum(np.abs(tradelist[date]['tradenumber'].values) * tradelist[date]['tradeprice'].values) / account.loc[date, 'totalvalue']
            lens1.append(temp)
    turnover = sum(lens1)*250/len(account.index)
    status = {'Volatility': vol, 'AnnulizedReturn': annulret, 'SimpleReturn': ret, 'CompoundReturn': compret, 'SharpeRatio':sharpe,\
              'WinRatio': winratio, 'MaxDrawdown': maxdrawdown, 'CalmarRatio': calmaratio, 'CorrelwIndex': correl, 'AnnulizedTurnover': turnover}
    plt.figure()
    plt.plot(np.cumsum(pnl.values))
    plt.tight_layout()
    plt.figure()
    plt.plot(account['totalvalue'].values/account['totalvalue'].values[0]-1)
    plt.tight_layout()
    print(pd.DataFrame(status, index = ['stats']))
    return {'stats':pd.DataFrame(status, index = ['stats']), 'pnl':pnl}

            
def pnlstats(pnl):
    vol = np.std(pnl) * np.sqrt(250)
    annulret = np.mean(pnl) * 250
    ret = sum(pnl)
    sharpe = annulret / vol
    winratio = sum(np.array(pnl)>0)/len(pnl)
    maxdrawdown, cum, curmax  = 100000000, 0, 0
    for i in pnl:
        curmax = max(curmax, cum)
        cum += i
        maxdrawdown = min(maxdrawdown, cum - curmax)
    calmaratio = sum(pnl)/abs(maxdrawdown)
    status = {'vol':vol, 'return':ret, 'sharpe':sharpe, 'winratio':winratio, 'maxdrawdown':maxdrawdown,'calmaratio':calmaratio}
    return pd.DataFrame(status,index = ['stats'])  