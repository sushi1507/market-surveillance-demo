# tools/metrics.py
import pandas as pd
import numpy as np

alerts = pd.read_csv('alerts.csv', parse_dates=['alert_ts','event_ts'])
stream = pd.read_csv('data/stream_ticks_clean.csv', parse_dates=['ts'])

print("== Alerts summary ==")
if not alerts.empty:
    lat = alerts['proc_latency_ms'].astype(float)
    print("alerts_count:", len(alerts))
    print("avg_latency_ms:", round(lat.mean(),2))
    print("p95_latency_ms:", round(np.percentile(lat,95),2))
    print("p99_latency_ms:", round(np.percentile(lat,99),2))
else:
    print("No alerts found.")

print("\n== Stream summary ==")
rows = len(stream)
print("clean_rows:", rows)
if rows > 1:
    t0 = stream['ts'].iloc[0]
    t1 = stream['ts'].iloc[-1]
    total_seconds = (t1 - t0).total_seconds()
    total_seconds = total_seconds if total_seconds>0 else (rows * 0.02)
    print("start:", t0, "end:", t1, "duration_s:", round(total_seconds,2))
    print("events_per_sec:", round(rows/total_seconds,2))
else:
    print("Not enough rows to compute throughput.")

