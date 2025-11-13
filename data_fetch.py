# data_fetch.py
import yfinance as yf
import pandas as pd
import os

os.makedirs('data', exist_ok=True)

# CHANGE SYMBOL if you want a different BSE-listed ticker
symbol = "TCS.BO"       # e.g., RELIANCE.BO, INFY.BO, HDFCBANK.BO
period = "5d"
interval = "1m"         # can fallback to '5m' if empty

print(f"Downloading {symbol} {period} @ {interval} ...")
df = yf.download(tickers=symbol, period=period, interval=interval, progress=True)

if df.empty:
    print("No 1m data returned. Trying 5m interval...")
    interval = "5m"
    df = yf.download(tickers=symbol, period=period, interval=interval, progress=True)

if df.empty:
    raise SystemExit("No intraday data returned. Try another symbol or longer period.")

df.reset_index(inplace=True)
# normalize names
rename_map = {}
if 'Datetime' in df.columns:
    rename_map['Datetime'] = 'ts'
elif 'Date' in df.columns:
    rename_map['Date'] = 'ts'
if 'Close' in df.columns:
    rename_map['Close'] = 'price'
if 'Volume' in df.columns:
    rename_map['Volume'] = 'volume'

df.rename(columns=rename_map, inplace=True)

# keep only ts, price, volume
cols = [c for c in ['ts','price','volume'] if c in df.columns]
df = df[cols]

out = "data/real_ticks.csv"
df.to_csv(out, index=False)
print("Saved", out, "rows:", len(df))
