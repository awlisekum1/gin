#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 17:41:52 2017

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

#%%
def strategy_marketcap(day, dates, account, tradelist, holdings, crossdata, index, tradecost):
    date = dates[day]
    curdata = crossdata[date]
    mask1 = curdata['VOLUME'] > 0
    mask2 = curdata.index != '000033.SZ'
    mask = mask1 & mask2
    if dates[day] > "2017-06-23":
        mask3 = curdata['PE_TTM'] > 0
        mask = mask & mask3
    curdata = curdata[mask]
    period = 2
    N = 30
    posratio = 1    
    iftrade = True

    temp = curdata['CLOSE'] * curdata['CLOSE'] * curdata['FREE_FLOAT_SHARES']

#    temp = temp.sort_values()[:N]
#    stocklist = temp.index
    stocklist = temp.sort_values().index[:N - 5] | temp.sort_values().index[-5:]
    totalvalue = account.loc[date, 'totalvalue'] * posratio
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
        
    return stocklist, weight, iftrade

#%%
def strategy_marketcap1(day, dates, account, tradelist, holdings, crossdata, index, tradecost):
    date = dates[day]
    curdata = crossdata[date].loc[crossdata[date]['VOLUME'] > 0]
#    Nday = 5
#    if day >= Nday:
#        tempdata = crossdata[dates[day - Nday]]
#        Past5DayRet = curdata.loc[tempdata.index, 'CLOSE_AFTY'] / tempdata['CLOSE_AFTY'] - 1
#        mask = (Past5DayRet > -0.2)
#        mask = mask.loc[mask == True]
#        curdata = curdata.loc[mask.index]

    period = 1
    N = 60
    posratio = 1
    
    iftrade = True
    if day % period == 0:
        iftrade = True
    else:
        iftrade = False
    # 1
#    temp = curdata['CLOSE'] * curdata['CLOSE'] * curdata['FREE_FLOAT_SHARES']
    temp = curdata['CLOSE'] * curdata['CLOSE'] * curdata['FREE_FLOAT_SHARES']
    
    # 2
#    coef = 0.
#    temp = coef*(curdata['CLOSE'] * curdata['FREE_FLOAT_SHARES'])/sum((curdata['CLOSE'].values * curdata['FREE_FLOAT_SHARES'].values)) + \
#            (1-coef) * np.sqrt(curdata['CLOSE'])/sum(np.sqrt(curdata['CLOSE']))
    temp = temp.sort_values()[:N]

#    correls = []
#    Ndayback = 5
#    backdays = 5
#    if day >= backdays:
#        for i in range(backdays):
#            tempdata = crossdata[dates[day - i - backdays]]
#            tempdata['FLOATMARKETCAP'] = tempdata['CLOSE'] * tempdata['FLOAT_A_SHARES'] 
#            mask1 = tempdata.VOLUME > 0 
#            mask1 = mask1 & (tempdata.HIGH != tempdata.LOW)
#            mask1 = mask1 & ((tempdata.VOLUME / tempdata.CLOSE / tempdata.FLOAT_A_SHARES) > 0.0002)
#            tempdata = tempdata[mask1]
#            axiscols = tempdata[['CLOSE', 'FLOATMARKETCAP']]
#            factorvalue = (axiscols['CLOSE'].values * axiscols['FLOATMARKETCAP']).fillna(0).values
#            valcol = (crossdata[dates[day - i]].loc[tempdata.index,'CLOSE'] /  tempdata['CLOSE'] - 1).fillna(0)
#            correls.append(np.corrcoef(factorvalue, valcol)[0][1])
#        
#        fact = correls[0] - correls[1]
#        if fact > 0.12:
#            posratio = 0.6
#            iftrade = True
#        elif 0.02 < fact <= 0.12:
#            posratio = 0.8
#            iftrade = True
#        elif fact < -0.02:
#            posratio = 1
#            iftrade = True
            
    stocklist = temp.index

    totalvalue = account.loc[date, 'totalvalue'] * posratio
    weight = pd.DataFrame([totalvalue*0.99/N]*N, columns = ["weight"],index = stocklist)
    
        
#    if day >= 1 and account.loc[dates[day],'totalvalue']/account.loc[dates[day-1],'totalvalue'] < 0.985:
#        weight = pd.DataFrame([totalvalue*0.7/N]*N, columns = ["weight"],index = stocklist)
#        iftrade = True
#    elif day >= 2 and account.loc[dates[day],'totalvalue']/account.loc[dates[day-2],'totalvalue'] < 0.975:
#        weight = pd.DataFrame([totalvalue*0.99/N]*N, columns = ["weight"],index = stocklist)
#        iftrade = True
#    elif day >= 3 and account.loc[dates[day],'totalvalue']/account.loc[dates[day-3],'totalvalue'] < 0.96:
#        weight = pd.DataFrame([totalvalue*0.8/N]*N, columns = ["weight"],index = stocklist)
#        iftrade = True
        
    return stocklist, weight, iftrade