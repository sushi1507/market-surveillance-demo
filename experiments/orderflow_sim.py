# experiments/orderflow_sim.py
import time, csv, os
import numpy as np

os.makedirs('experiments/results', exist_ok=True)

def run_mode(mode, events=2000):
    lat=[]
    for i in range(events):
        t0=time.time()
        if mode=='sync':
            time.sleep(0.002)
        elif mode=='async':
            time.sleep(0.0008)
        elif mode=='batch':
            if i%50==0:
                time.sleep(0.01)
            else:
                time.sleep(0.0005)
        t1=time.time()
        lat.append((t1-t0)*1000)
    return lat

modes=['sync','async','batch']
with open('experiments/results/latency_summary.csv','w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['mode','events','avg_ms','p95_ms','p99_ms','max_ms'])
    for m in modes:
        L = np.array(run_mode(m))
        w.writerow([m, len(L), round(L.mean(),3), round(np.percentile(L,95),3), round(np.percentile(L,99),3), round(L.max(),3)])
print("Saved experiments/results/latency_summary.csv")
