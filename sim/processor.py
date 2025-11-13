import pandas as pd
import numpy as np
import time, datetime, csv, os
from sklearn.ensemble import IsolationForest
from collections import deque

os.makedirs("data", exist_ok=True)

STREAM_FILE = "data/stream_ticks.csv"
ALERT_FILE = "alerts.csv"

# Load stream
df = pd.read_csv(STREAM_FILE, parse_dates=["ts"])

# Initialize alert file
with open(ALERT_FILE, "w", newline='') as f:
    w = csv.writer(f)
    w.writerow([
        "alert_ts", "event_ts", "price", "volume",
        "alert_type", "score", "explanation", "proc_latency_ms"
    ])

# Parameters
train_initial = 200
rolling_window = 60
sleep_gap = 0.02  # controls event speed (50 events/sec)

# Train model on initial batch
train_df = df.iloc[:train_initial]
X_train = train_df[['price','volume']].values

iso = IsolationForest(contamination=0.01, random_state=42)
iso.fit(X_train)

# Compute baseline volume stats
vol_mean = train_df['volume'].mean()
vol_std = train_df['volume'].std() or 1

rolling = deque(maxlen=rolling_window)

alerts = 0

for idx, row in df.iloc[train_initial:].iterrows():
    start_t = time.time()

    price = row["price"]
    volume = row["volume"]

    rolling.append((price, volume))
    prices = np.array([p for p,v in rolling])
    volumes = np.array([v for p,v in rolling])

    price_mean = prices.mean()
    price_diff = price - price_mean
    vol_z = (volume - vol_mean) / vol_std

    x = np.array([[price, volume]])
    iso_score = iso.decision_function(x)[0]
    iso_flag  = iso.predict(x)[0] == -1

    rule_flag = abs(vol_z) > 3 or abs(price_diff) > 0.02 * price

    alert = rule_flag or iso_flag
    explanation = []
    score = 0

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
