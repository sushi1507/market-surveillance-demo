# processing/processor.py  (robust version)
import pandas as pd
import numpy as np
import time, datetime, csv, os
from sklearn.ensemble import IsolationForest
from collections import deque

os.makedirs("data", exist_ok=True)

STREAM_FILE = "data/stream_ticks.csv"
ALERT_FILE = "alerts.csv"

print("Loading stream file:", STREAM_FILE)
if not os.path.exists(STREAM_FILE):
    raise SystemExit(f"{STREAM_FILE} not found. Run sim/producer.py first.")

df_raw = pd.read_csv(STREAM_FILE, low_memory=False)
print("Columns found:", list(df_raw.columns))

# Heuristics to pick columns
possible_ts = [c for c in df_raw.columns if c.lower() in ("ts","datetime","date","time","timestamp")]
possible_price = [c for c in df_raw.columns if c.lower() in ("price","close","last","adj close","close/last","open")]
possible_volume = [c for c in df_raw.columns if 'vol' in c.lower()]

ts_col = possible_ts[0] if possible_ts else df_raw.columns[0]
price_col = possible_price[0] if possible_price else (df_raw.columns[1] if len(df_raw.columns)>1 else df_raw.columns[0])
vol_col = possible_volume[0] if possible_volume else (df_raw.columns[-1] if len(df_raw.columns)>2 else df_raw.columns[-1])

print(f"Using ts='{ts_col}', price='{price_col}', volume='{vol_col}'")

df = df_raw[[ts_col, price_col, vol_col]].copy()
df.columns = ["ts","price","volume"]

# Parse ts
try:
    df['ts'] = pd.to_datetime(df['ts'])
except Exception as e:
    print("Warning: could not parse ts column to datetime:", e)

# Coerce numeric
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

before_rows = len(df)
df = df.dropna(subset=['price','volume'])
after_rows = len(df)
dropped = before_rows - after_rows
print(f"Rows before cleaning: {before_rows}; after numeric coercion: {after_rows}; dropped: {dropped}")

if after_rows < 50:
    raise SystemExit("Not enough numeric rows after cleaning. Check your input CSV and column choices.")

df.to_csv("data/stream_ticks_clean.csv", index=False)
print("Wrote cleaned stream -> data/stream_ticks_clean.csv")

# Initialize alert file
with open(ALERT_FILE, "w", newline='') as f:
    w = csv.writer(f)
    w.writerow([
        "alert_ts", "event_ts", "price", "volume",
        "alert_type", "score", "explanation", "proc_latency_ms"
    ])

# Parameters
train_initial = 200 if after_rows > 300 else max(50, int(after_rows * 0.2))
rolling_window = 60
sleep_gap = 0.02  # controls event speed (50 events/sec simulated)

print("train_initial =", train_initial, "rolling_window =", rolling_window, "sleep_gap =", sleep_gap)

# Train model
train_df = df.iloc[:train_initial]
X_train = train_df[['price','volume']].values
iso = IsolationForest(contamination=0.01, random_state=42)
iso.fit(X_train)

vol_mean = train_df['volume'].mean()
vol_std = train_df['volume'].std() if train_df['volume'].std() > 0 else 1.0

rolling = deque(maxlen=rolling_window)
alerts = 0

for idx, row in df.iloc[train_initial:].iterrows():
    start_t = time.time()

    price = float(row["price"])
    volume = float(row["volume"])

    rolling.append((price, volume))
    prices = np.array([p for p,v in rolling]) if len(rolling)>0 else np.array([price])
    volumes = np.array([v for p,v in rolling]) if len(rolling)>0 else np.array([volume])

    price_mean = prices.mean()
    price_diff = price - price_mean
    vol_z = (volume - vol_mean) / (vol_std if vol_std>0 else 1.0)

    x = np.array([[price, volume]])
    iso_score = float(iso.decision_function(x)[0])
    iso_flag  = int(iso.predict(x)[0]) == -1

    rule_flag = abs(vol_z) > 3 or abs(price_diff) > 0.02 * price

    alert = rule_flag or iso_flag
    explanation = []
    score = 0.0

    if rule_flag:
        explanation.append(f"rule_vol_z={vol_z:.2f}")
        score += 0.6
    if iso_flag:
        explanation.append(f"iso_score={iso_score:.3f}")
        score += 0.4

    latency = (time.time() - start_t) * 1000

    if alert:
        alerts += 1
        with open(ALERT_FILE, "a", newline='') as f:
            w = csv.writer(f)
            w.writerow([
                datetime.datetime.utcnow().isoformat(),
                row["ts"], price, volume, "ANOMALY",
                round(score,3), ";".join(explanation),
                round(latency,2)
            ])

    time.sleep(sleep_gap)

print("Processing complete. Alerts generated:", alerts)
print("Cleaned rows used:", after_rows)

