# tools/annotate_alerts.py
import pandas as pd, os
os.makedirs('deliverables', exist_ok=True)

alerts = pd.read_csv('alerts.csv')
if alerts.empty:
    print("No alerts.csv found or empty")
    raise SystemExit

sample = alerts.sort_values('alert_ts', ascending=False).head(10).copy()

def explain_row(ex):
    if pd.isna(ex): return "Anomaly detected"
    ex_lower = ex.lower()
    if 'rule_vol_z' in ex_lower:
        return "Large sudden volume spike detected"
    if 'iso_score' in ex_lower:
        return "Model-based unusual price-volume pattern detected"
    if 'price' in ex_lower:
        return "Significant price deviation vs recent baseline"
    return "Anomaly (hybrid detector)"

sample['annotation'] = sample['explanation'].apply(explain_row)
out = 'deliverables/alerts_annotated.csv'
sample.to_csv(out, index=False)
print("Wrote", out)
