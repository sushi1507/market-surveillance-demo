# dashboard/app.py
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Market Surveillance Demo", layout="wide")
st.title("📈 BSE Market Surveillance — Demo Dashboard")
st.markdown("Prototype: minute-level bars → hybrid detector → explainable alerts (demo)")

# TICKS
ticks_path = "data/stream_ticks_clean.csv"
if os.path.exists(ticks_path):
    try:
        ticks = pd.read_csv(ticks_path, parse_dates=["ts"])
        st.subheader("Latest Market Bars")
        st.dataframe(ticks.tail(30))
    except Exception as e:
        st.error(f"Failed to load ticks from {ticks_path}: {e}")
else:
    st.warning(f"Ticks file not found: {ticks_path}. Run data_fetch + producer + processor first.")

st.markdown("---")

# ALERTS
alerts_path = "alerts.csv"
if not os.path.exists(alerts_path):
    st.error(f"alerts.csv not found at project root ({alerts_path}). Run processing/processor.py to generate alerts.")
else:
    try:
        alerts = pd.read_csv(alerts_path)
        # parse timestamps
        if 'alert_ts' in alerts.columns:
            alerts['alert_ts'] = pd.to_datetime(alerts['alert_ts'], errors='coerce')
        else:
            # try to locate a datetime-like column and rename to alert_ts
            for c in alerts.columns:
                if 'time' in c.lower() or 'date' in c.lower():
                    alerts = alerts.rename(columns={c:'alert_ts'})
                    alerts['alert_ts'] = pd.to_datetime(alerts['alert_ts'], errors='coerce')
                    break

        st.subheader("Recent Alerts")
        st.dataframe(alerts.sort_values("alert_ts", ascending=False).head(30))

        # Summary metrics
        st.markdown("### Summary")
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            st.metric("Total alerts", int(len(alerts)))
        with col2:
            try:
                tmin = alerts['alert_ts'].min()
                tmax = alerts['alert_ts'].max()
                if pd.isna(tmin) or pd.isna(tmax):
                    st.metric("Time span", "unknown")
                else:
                    st.metric("Time span", f"{pd.to_datetime(tmin).strftime('%Y-%m-%d %H:%M')} → {pd.to_datetime(tmax).strftime('%Y-%m-%d %H:%M')}")
            except Exception:
                st.metric("Time span", "unknown")

        # Time-series (5-minute resample)
        try:
            if 'alert_ts' in alerts.columns and alerts['alert_ts'].notna().sum() > 0:
                # resample to 5 minutes for better granularity
                alerts_ts = alerts.set_index('alert_ts').resample('5T').size().rename('count')
                if alerts_ts.sum() == 0:
                    alerts_ts = alerts.set_index('alert_ts').resample('15T').size().rename('count')

                st.subheader("Alerts over time (5-minute intervals)")
                st.line_chart(alerts_ts)

                st.subheader("Alerts per period (bar)")
                st.bar_chart(alerts_ts)
            else:
                st.info("Alert timestamps not parseable — cannot show time-series.")
        except Exception as e:
            st.error(f"Error preparing time-series: {e}")

        # Top explanations
        st.subheader("Top explanations (sample)")
        if 'explanation' in alerts.columns:
            top = alerts['explanation'].value_counts().reset_index().head(12)
            top.columns = ['explanation','count']
            st.table(top)
        else:
            st.info("No 'explanation' column found in alerts.csv")

        # Show annotated alerts if available
        ann_path = "deliverables/alerts_annotated.csv"
        if os.path.exists(ann_path):
            try:
                ann = pd.read_csv(ann_path)
                st.subheader("Sample annotated alerts (deliverables/alerts_annotated.csv)")
                cols = [c for c in ['alert_ts','event_ts','price','volume','explanation','annotation'] if c in ann.columns]
                st.dataframe(ann[cols].head(10))
            except Exception as e:
                st.info(f"Could not load annotated alerts: {e}")
        else:
            st.info("Annotated alerts file not found (deliverables/alerts_annotated.csv)")

    except Exception as e:
        st.error(f"Failed loading alerts.csv: {e}")

st.markdown("---")
st.caption("Prototype/demo only — not production. For production use exchange tick feeds, Kafka/Redis, and hardened model serving.")
