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

# # Pair Trading of GLD and GDX

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
from sklearn import linear_model

df1=pd.read_excel('GLD.xls')

df2=pd.read_excel('GDX.xls')

df=pd.merge(df1, df2, on='Date', suffixes=('_GLD', '_GDX'))

df.set_index('Date', inplace=True)

df.sort_index(inplace=True)

df.shape

trainset=np.arange(0, 252)

testset=np.arange(trainset.shape[0], df.shape[0])

# Long GLD, short GDX
# ## Determine hedge ratio on trainset

# This code is nice, but I need a specific fit.
sns.regplot(data=df.loc[:, ["Adj Close_GLD", "Adj Close_GDX"]], x="Adj Close_GDX", y="Adj Close_GLD")
plt.title("Adj Close_GLD vs. Adj Close_GDX (y vs. x)")
plt.show()

dat = df.loc[:, 'Adj Close_GLD'].iloc[trainset], df.loc[:, 'Adj Close_GDX'].iloc[trainset]
#model=sm.OLS(sm.add_constant(dat[0]), dat[1])  # dat[0] is y, dat[1] is X
model=sm.OLS(dat[0], dat[1])
reg = linear_model.LinearRegression()

# df.loc[:, 'Adj Close_GLD']

results=model.fit()
print(results.summary())
#print(results.params)
skresults = reg.fit(dat[1].to_numpy().reshape(-1, 1), dat[0].to_numpy())

# This bit of code doesn't work
#plt.title("Adj Close_GLD vs. Adj Close_GDX (y vs. x)")
#ax = df.loc[:, ["Adj Close_GLD", "Adj Close_GDX"]].plot(x="Adj Close_GDX", y="Adj Close_GLD", kind="scatter")
#abline_plot(model_results=results, ax=ax)
#plt.show()

hedgeRatio=results.params
skhedgeRatio=skresults.coef_

# see what happens when use sklearn's fit.
# Can try this with many different ways of fitting
# to see what happens.
# hedgeRatio[0] = skhedgeRatio[0]

print(f"sm hedge ratio: {hedgeRatio}")
print(f"sk hedge ratio: {skhedgeRatio}")

# ##  spread = GLD - hedgeRatio*GDX

spread=df.loc[:, 'Adj Close_GLD']-hedgeRatio[0]*df.loc[:, 'Adj Close_GDX']
plt.title("trainset spread")
plt.plot(spread.iloc[trainset])
plt.show()

plt.title("testset spread")
plt.plot(spread.iloc[testset])
plt.show()

spreadMean=np.mean(spread.iloc[trainset])

spreadMean

spreadStd=np.std(spread.iloc[trainset])

spreadStd

df['zscore']=(spread-spreadMean)/spreadStd

df['positions_GLD_Long']=0

df['positions_GDX_Long']=0

df['positions_GLD_Short']=0

df['positions_GDX_Short']=0

df.loc[df.zscore>=1, ('positions_GLD_Short', 'positions_GDX_Short')]=[-1, 1] # Short spread

df.loc[df.zscore<=-1, ('positions_GLD_Long', 'positions_GDX_Long')]=[1, -1] # Buy spread

df.loc[df.zscore<=0.5, ('positions_GLD_Short', 'positions_GDX_Short')]=0 # Exit short spread

df.loc[df.zscore>=0.5, ('positions_GLD_Long', 'positions_GDX_Long')]=0 # Exit long spread

df.fillna(method='ffill', inplace=True) # ensure existing positions are carried forward unless there is an exit signal

positions_Long=df.loc[:, ('positions_GLD_Long', 'positions_GDX_Long')]

positions_Short=df.loc[:, ('positions_GLD_Short', 'positions_GDX_Short')]

positions=np.array(positions_Long)+np.array(positions_Short)

positions=pd.DataFrame(positions)

# Assuming selling at the day's close
dailyret=df.loc[:, ('Adj Close_GLD', 'Adj Close_GDX')].pct_change()

# Combines the dailyret and positions based on the 0s, 1s, and -1s.
# pnl for profit and loss
pnl=(np.array(positions.shift())*np.array(dailyret)).sum(axis=1)

# Pairs trading is a type of market neutral strategy
# risk free rate 0 because of pair trading strategy? I still don't understand sorta.
sharpeTrainset=np.sqrt(252)*np.mean(pnl[trainset[1:]])/np.std(pnl[trainset[1:]])

print(f"Train sharpe: {sharpeTrainset}")

sharpeTestset=np.sqrt(252)*np.mean(pnl[testset])/np.std(pnl[testset])

print(f"Test sharpe: {sharpeTestset}")

plt.plot(np.cumsum(pnl[testset]))
plt.show()

#positions.to_pickle('example3_6_positions')
