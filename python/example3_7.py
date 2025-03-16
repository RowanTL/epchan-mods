# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# All of these strategies are money agnostic and I appreciate that

# # Simple Mean-Reverting Model with and without Transaction Costs

import numpy as np

import pandas as pd

startDate=20060101

endDate=20061231

df=pd.read_table('SPX_20071123.txt')

df['Date']=df['Date'].astype('int')

df.set_index('Date', inplace=True)

df.sort_index(inplace=True)

dailyret=df.pct_change()

marketDailyret=dailyret.mean(axis=1)

# np.array(dailyret)-np.array(marketDailyret.reshape(dailyret.shape)) takes the
# daily market returns and subtracts that value from all of the assets for
# that day. Note the - sign at the start of the line!
weights=-(np.array(dailyret)-np.array(marketDailyret).reshape((dailyret.shape[0], 1)))

wtsum=np.nansum(abs(weights), axis=1)

# fills indicies where wtsum==0 with 0.
weights[wtsum==0,]=0

# replaces 0s with 1s? Can't divide by zero as done below
wtsum[wtsum==0]=1

weights=weights/wtsum.reshape((dailyret.shape[0],1))

dailypnl=np.nansum(np.array(pd.DataFrame(weights).shift())*np.array(dailyret), axis=1)

dailypnl=dailypnl[np.logical_and(df.index >= startDate, df.index <= endDate)]

sharpeRatio=np.sqrt(252)*np.mean(dailypnl)/np.std(dailypnl)

sharpeRatio

# .6412322 without transaction costs

# # With transaction costs

onewaytcost=0.0005

weights=weights[np.logical_and(df.index >= startDate, df.index <= endDate)]

dailypnlminustcost=dailypnl - (np.nansum(abs(weights-np.array(pd.DataFrame(weights).shift())), axis=1)*onewaytcost)

# What is the risk free rate?
sharpeRatioMinusTcost=np.sqrt(252)*np.mean(dailypnlminustcost)/np.std(dailypnlminustcost)

sharpeRatioMinusTcost

# -2.1617433 with transactions costs