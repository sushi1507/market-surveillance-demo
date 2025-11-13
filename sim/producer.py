# sim/producer.py
import pandas as pd
import os

os.makedirs("data", exist_ok=True)
infile = "data/real_ticks.csv"
outfile = "data/stream_ticks.csv"

if not os.path.exists(infile):
    raise SystemExit(f"{infile} not found. Run data_fetch.py first.")

df = pd.read_csv(infile, parse_dates=[0], infer_datetime_format=True)
# Normalize columns - if names differ, try to detect price/volume
if 'ts' not in df.columns:
    df.rename(columns={df.columns[0]: 'ts'}, inplace=True)
if 'price' not in df.columns:
    # attempt to find a numeric column for price
    candidates = [c for c in df.columns if c.lower() in ('close','last','price','adj close','close/last','open')]
    if candidates:
        df.rename(columns={candidates[0]:'price'}, inplace=True)
if 'volume' not in df.columns:
    candidates = [c for c in df.columns if 'vol' in c.lower() or 'volume' in c.lower()]
    if candidates:
        df.rename(columns={candidates[0]:'volume'}, inplace=True)

# keep only ts, price, volume
keep = [c for c in ['ts','price','volume'] if c in df.columns]
df = df[keep].copy()
df.to_csv(outfile, index=False)
print("Wrote stream CSV:", outfile, "rows:", len(df))

