# Market Surveillance — Real-time Trade/Order Anomaly Detector (Demo)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-demo-orange.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](/LICENSE)


**One-line:** Prototype that ingests minute-level BSE intraday bars → hybrid detector (rule + ML) → explainable alerts + triage dashboard.

## What this repo contains
- `data/real_ticks.csv` — intraday bars (downloaded from Yahoo Finance for a BSE-listed ticker)  
- `data/stream_ticks_clean.csv` — cleaned stream used for demo  
- `processing/processor.py` — streaming prototype (feature engineering + hybrid detector: z-score rules + IsolationForest)  
- `alerts.csv` — generated alerts (sample annotated alerts in `deliverables/alerts_annotated.csv`)  
- `dashboard/app.py` — Streamlit triage UI (5-minute resample + top explanations)  
- `experiments/orderflow_sim.py` — order-flow latency simulator  
- `experiments/results/latency_summary.png` — latency chart from experiments  
- `deliverables/alerts_annotated.csv` — top 10 annotated alerts (human-friendly explanations)

## Screenshots

**Streamlit triage dashboard**  
![Streamlit Dashboard](deliverables/screenshots/streamlit_dashboard.png)

**Latency comparison (order-flow simulator)**  
![Latency summary](deliverables/screenshots/latency_summary.png)

**Sample annotated alerts (deliverables/alerts_annotated.csv)**  
![Annotated alerts sample](deliverables/screenshots/annotated_alerts.png)


## Quickstart (local)
1. Create & activate a Python venv.  
2. `pip install -r requirements.txt` (or `pip install numpy pandas scikit-learn streamlit matplotlib yfinance python-dateutil`)  
3. `python data_fetch.py`  # fetch intraday bars (TCS.BO by default)  
4. `python sim/producer.py`  # normalize to stream CSV  
5. `python processing/processor.py`  # run detector, generates `alerts.csv`  
6. `python tools/annotate_alerts.py`  # creates sample annotated alerts  
7. `streamlit run dashboard/app.py`  # open dashboard at http://localhost:8501  
8. `python experiments/orderflow_sim.py` and run `experiments/plot_latency.py` to produce latency chart

### How to run (quick)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# mac / linux
# source venv/bin/activate
pip install -r requirements.txt
python data_fetch.py
python sim/producer.py
python processing/processor.py
python tools/annotate_alerts.py
streamlit run dashboard/app.py

## Results 
- Clean rows processed: **1861**  
- Alerts generated: **224**  
- Average per-alert processing latency: **30.06 ms**  
- p95 latency: **38.04 ms**  
- p99 latency: **43.58 ms**  
- (Note: events/sec is 0.0 because data used are minute-bars across multiple days. For real-time tick feeds you would measure events/sec with a live feed.)

## How this maps to BSE
- **Surveillance & anomaly detection:** The prototype shows ingestion → feature engineering → hybrid detection → explainable alerting, which maps directly to market surveillance (trade/order anomaly detection).  
- **Low-latency awareness:** Measured p95/p99 latencies and a separate order-flow simulator show tradeoffs between latency and batching — concepts important for high-throughput exchange systems.  
- **SOC / Triage fit:** Alerts are emitted with severity/explanation and a triage-ready CSV/dashboard that mimics SIEM/SOC workflows.

## Notes & next steps for production
- For production, ingest exchange tick feed (paid/participant feed), use Kafka/Redis for throughput, deploy models in a low-latency model serving stack, and integrate with a SIEM for alert escalation.
