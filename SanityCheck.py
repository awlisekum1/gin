#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 15:10:06 2017

@author: TaoLuo
"""

import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#%% interval table
def create_stats_table(axiscols, valcol, intervals = 5):
    row, col = axiscols.shape
    interval_tab = pd.DataFrame(None, axiscols.index, columns = axiscols.columns)
    for i in range(col):
        interval_tab[axiscols.columns[i]] = pd.DataFrame(pd.qcut(axiscols[axiscols.columns[i]], intervals, labels = False).values, index = axiscols.index)
    interval_tab[valcol.columns] = copy.deepcopy(valcol)
    result = interval_tab.groupby(list(axiscols.columns))
    return result

result = []
intervals = 5
start = "2017-04-20"
end = "2017-05-15"
Ndays = 10
dates = pd.DataFrame(sorted(list(crossdata.keys())), columns = ['date'])
dates = dates.set_index('date', drop = False)
dates = dates.loc[start:end]
dates = list(dates['date'])
for day,date in enumerate(dates):
    if day < len(dates) - Ndays:
        tempdata = crossdata[date]
        tempdata['FLOATMARKETCAP'] = tempdata['CLOSE'] * tempdata['FLOAT_A_SHARES']  
        mask1 = tempdata.VOLUME > 0 
        mask1 = mask1 & (tempdata.HIGH != tempdata.LOW)
        mask1 = mask1 & ((tempdata.VOLUME / tempdata.CLOSE / tempdata.FLOAT_A_SHARES) > 0.0002)
        tempdata = tempdata[mask1]
        axiscols = tempdata[['CLOSE', 'FLOATMARKETCAP']]
        valcol = (crossdata[dates[day+Ndays]].loc[tempdata.index,'CLOSE'] /  tempdata['CLOSE'] - 1).fillna(0)
        ind = valcol.index
        valcol = pd.DataFrame(valcol.values, columns = ['RET1m'], index = ind)
        valcol = valcol.loc[tempdata.index]
        temp = create_stats_table(axiscols, valcol, intervals)
        result.append(list(temp.mean()['RET1m'].values))
result = pd.DataFrame(result)
result.mean()
result.std()
heat = pd.DataFrame(result.mean().values.reshape(intervals, intervals))
print(heat)
plt.figure()
plt.plot(result.mean())
plt.figure()
plt.plot(result.std())



#%% correlation between return and factor
result = []
start = "2017-01-02"
end = "2017-05-16"
Ndays = 1
dates = pd.DataFrame(sorted(list(crossdata.keys())), columns = ['date'])
dates = dates.set_index('date', drop = False)
dates = dates.loc[start:end]
dates = list(dates['date'])
for day,date in enumerate(dates):
    if day < len(dates) - Ndays:
        tempdata = crossdata[date]
        tempdata['FLOATMARKETCAP'] = tempdata['CLOSE'] * tempdata['FLOAT_A_SHARES'] 
        mask1 = tempdata.VOLUME > 0 
        mask1 = mask1 & (tempdata.HIGH != tempdata.LOW)
        mask1 = mask1 & ((tempdata.VOLUME / tempdata.CLOSE / tempdata.FLOAT_A_SHARES) > 0.0002)
        tempdata = tempdata[mask1]
        axiscols = tempdata[['CLOSE', 'FLOATMARKETCAP']]
        factorvalue = axiscols['CLOSE'].values * axiscols['FLOATMARKETCAP'].values
        valcol = (crossdata[dates[day+Ndays]].loc[tempdata.index,'CLOSE'] /  tempdata['CLOSE'] - 1).fillna(0)
        res = np.corrcoef(factorvalue, valcol)[0][1]
        result.append(res)
plt.plot(result)

                