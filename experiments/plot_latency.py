import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('experiments/results/latency_summary.csv')

df.plot(x='mode', y='avg_ms', kind='bar', legend=False)
plt.ylabel('avg latency (ms)')
plt.tight_layout()
plt.savefig('experiments/results/latency_summary.png')

print("Saved experiments/results/latency_summary.png")
