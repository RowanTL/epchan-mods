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
import polars as pl
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("file", help="path to xls file", type=str)
args = parser.parse_args()

file: Path = Path(args.file)

df: pl.DataFrame = pl.read_excel(args.file)
df = df.reverse()
df = df.with_columns(pl.col("Adj Close").pct_change().alias("Daily Ret"))
df = df.with_columns(pl.col("Daily Ret").shift(-1))
df = df.drop_nulls()
df[["Adj Close", "Daily Ret"]].write_csv(f"data/dailyret_{file.stem}.csv", include_header=False)


'''close_prices: list = df["Adj Close"].tolist()
today: list = []
tmo: list = []
# to for today, tm for tmo
for to, tm in zip(close_prices[:-1], close_prices[1:]):
    today.append(to)
    tmo.append(tm)
final_df: pd.DataFrame = pd.DataFrame({"today": today, "tmo": tmo})
final_df.to_csv(f"data/{args.file.replace('.xls','.csv')}", header=False, index=False)
print(final_df)'''