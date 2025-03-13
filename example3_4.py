# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Calculating Sharpe Ratio for Long-Only Vs Market Neutral Strategies

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

# This is long only
# First part of example

df=pd.read_excel('IGE.xls')

df.sort_values(by='Date', inplace=True)

dailyret=df.loc[:, 'Adj Close'].pct_change() # daily returns

excessRet=dailyret-0.04/252 #  excess daily returns = strategy returns - financing cost, assuming risk-free rate of 

# The sqrt(252) is annualizing the returns. 252 trading days in a year
# This strategy trades everyday.
sharpeRatio=np.sqrt(252)*np.mean(excessRet)/np.std(excessRet)

sharpeRatio

# This is market neutral
# Second part of example

df2=pd.read_excel('SPY.xls')

df=pd.merge(df, df2, on='Date', suffixes=('_IGE', '_SPY'))

df['Date']=pd.to_datetime(df['Date'])

df.set_index('Date', inplace=True)

df.sort_index(inplace=True)

dailyret=df[['Adj Close_IGE', 'Adj Close_SPY']].pct_change() # daily returns

dailyret.rename(columns={"Adj Close_IGE": "IGE", "Adj Close_SPY": "SPY"}, inplace=True)

netRet=(dailyret['IGE']-dailyret['SPY'])/2

sharpeRatio=np.sqrt(252)*np.mean(netRet)/np.std(netRet)

sharpeRatio

cumret=np.cumprod(1+netRet)-1

plt.plot(cumret)

# Drawdown calculations
from calculateMaxDD import calculateMaxDD

maxDrawdown, maxDrawdownDuration, startDrawdownDay=calculateMaxDD(cumret.values)

maxDrawdown

maxDrawdownDuration

startDrawdownDay
