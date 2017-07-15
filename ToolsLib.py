#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 11:06:10 2017

@author: TaoLuo
"""

import os
import pandas as pd
import numpy as np
import datetime as dt

#%%
def getpricets(sym, dti, dte,datapath):
    filelist = os.listdir(datapath)
    if (sym + ".csv") not in filelist:
        print("Cannot find symbol: ",  sym)
        return 0
    else:
        symdata = pd.read_csv(datapath+sym+".csv", encoding = 'iso-8859-1')
        symdata = symdata.set_index(symdata['Date'],drop = False)
        return symdata.loc[dti:dte]

#%%
# need to load stockuniverse data


#%%
def AddColumn(data, crossdata):
    for date in crossdata.keys():
        print(date)
        currdata = []
        tickers = crossdata[date].index
        for ticker in tickers:
            currdata.append(list(data[ticker].loc[date]))
        crossdata[date][data[ticker].columns] = pd.DataFrame(currdata, columns = data[ticker].columns, index = tickers)
        return crossdata

PASTRET5d = {}
period = 5
for ticker in stockuniverse.keys():
    cl = stockuniverse[ticker]['CLOSE_AFTY']
    series = cl.pct_change(periods = period)
    series = list(series)
    PASTRET5d[ticker] = pd.DataFrame(series, columns = ['PASTRET5d'], index = stockuniverse[ticker].index).fillna(0)
crossdata = AddColumn(PASTRET5d, crossdata)
