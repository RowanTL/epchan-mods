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

# https://algotrading101.com/learn/pairs-trading-guide/

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

trainset=np.arange(0, 252)

testset=np.arange(trainset.shape[0], df.shape[0])

# Shorts/Longs each of the stocks depending on differences in spread
# ## Determine hedge ratio on trainset

# This code is nice, but I need a specific fit.
sns.regplot(data=df.loc[:, ["Adj Close_GLD", "Adj Close_GDX"]], x="Adj Close_GDX", y="Adj Close_GLD")
plt.title("Adj Close_GLD vs. Adj Close_GDX (y vs. x)")
plt.show()

dat = df.loc[:, 'Adj Close_GLD'].iloc[trainset], df.loc[:, 'Adj Close_GDX'].iloc[trainset]
#model=sm.OLS(sm.add_constant(dat[0]), dat[1])  # dat[0] is y, dat[1] is X
model=sm.OLS(dat[0], dat[1])
reg = linear_model.HuberRegressor()

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

# Why is this a good measure of spread?
# ##  spread = GLD - hedgeRatio*GDX

spread=df.loc[:, 'Adj Close_GLD']-hedgeRatio.iloc[0]*df.loc[:, 'Adj Close_GDX']
plt.title("trainset spread")
plt.plot(spread.iloc[trainset])
plt.show()

plt.title("testset spread")
plt.plot(spread.iloc[testset])
plt.show()

plt.title("Adj Close Price Charts")
plt.plot(df["Adj Close_GLD"], label="GLD")
plt.plot(df["Adj Close_GDX"], label="GDX")
plt.plot(spread, label="Spread")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
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

# This is where buy/sell decisions are made. Positions held overnight? Maybe.
# Literally shorts the entire spread, not each stock individually. Shorts both in this case.
#  The - doesn't necessarily mean it's losing money however. If the GLD_Short is -1 and
#  the pct_change for that day is also negative, it's a gain for the trader.
#  Remember that these stocks are correlated. When price of one moves, it's likely
#  the other one will follow. Sounds like statisical arbitrage Dr. Chan.
#  Leeching strategy isn't it. It's gonna take time to understand this crazy
#  complex system that takes years to fully grasp. This is why I'm going back to
#  school. I can steal Taylor's directional code for this.
#
# For pair trading: Short the outperforming stock and long the underperforming one.
# In this case, 1 is longing, -1 is shorting regardless of the _Strategy name.
df.loc[df.zscore > 1, ('positions_GLD_Short', 'positions_GDX_Short')]=[-1, 1] # Short spread

df.loc[df.zscore < -1, ('positions_GLD_Long', 'positions_GDX_Long')]=[1, -1] # Buy spread

df.loc[df.zscore <= 0.5, ('positions_GLD_Short', 'positions_GDX_Short')]=0 # Exit short spread

df.loc[df.zscore >= -0.5, ('positions_GLD_Long', 'positions_GDX_Long')]=0 # Exit long spread

#df.fillna(method='ffill', inplace=True) # ensure existing positions are carried forward unless there is an exit signal
df.ffill(inplace=True)

positions_Long=df.loc[:, ('positions_GLD_Long', 'positions_GDX_Long')]

positions_Short=df.loc[:, ('positions_GLD_Short', 'positions_GDX_Short')]

positions=np.array(positions_Long)+np.array(positions_Short)

positions=pd.DataFrame(positions)

# Assuming trading at the day's close
dailyret=df.loc[:, ('Adj Close_GLD', 'Adj Close_GDX')].pct_change()

# Combines the dailyret and positions based on the 0s, 1s, and -1s.
# pnl for profit and loss
pnl_per = np.array(positions.shift())*np.array(dailyret)
pnl=pnl_per.sum(axis=1)

# Transaction cost calculation. Not implemented yet.
one_way_transaction_cost = 0.0005
t_costs_per = (abs(pnl_per) * one_way_transaction_cost)
pnl_t_costs = (pnl_per - t_costs_per).sum(axis=1)

# Pairs trading is a type of market neutral strategy
# risk free rate 0 because of pair trading strategy? I still don't understand sorta.
sharpeTrainset=np.sqrt(252)*np.mean(pnl[trainset[1:]])/np.std(pnl[trainset[1:]])
#sharpeTrainset=np.sqrt(252)*np.mean(pnl_t_costs[trainset[1:]])/np.std(pnl_t_costs[trainset[1:]])

print(f"Train sharpe: {sharpeTrainset}")

sharpeTestset=np.sqrt(252)*np.mean(pnl[testset])/np.std(pnl[testset])
#sharpeTestset=np.sqrt(252)*np.mean(pnl_t_costs[testset])/np.std(pnl_t_costs[testset])

print(f"Test sharpe: {sharpeTestset}")

plt.title("cummulative sum of profit and loss on the testset")
plt.plot(np.cumsum(pnl[testset]))
plt.show()

#positions.to_pickle('example3_6_positions')
