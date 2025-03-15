#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 23:49:55 2025

@author: rowan

Chops the Adjusted closing price of an xls file into a pair per line.
Saves the result into the current directory with the same name but different
extension.
"""

import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("file", help="path to xls file", type=str)
args = parser.parse_args()

df: pd.DataFrame = pd.read_excel(args.file)
close_prices: list = df["Adj Close"].tolist()
today: list = []
tmo: list = []
# to for today, tm for tmo
for to, tm in zip(close_prices[:-1], close_prices[1:]):
    today.append(to)
    tmo.append(tm)
final_df: pd.DataFrame = pd.DataFrame({"today": today, "tmo": tmo})
final_df.to_csv(f"data/{args.file.replace('.xls','.csv')}", header=False, index=False)
print(final_df)