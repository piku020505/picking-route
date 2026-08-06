import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.cluster.simulation_cluster import simulation_cluster
from utils.cost.cost_model import compare_financial_savings
from utils.routing.heuristics import benchmark_routing_heuristics
from utils.sensitivity.sensitivity import run_sensitivity_analysis
from utils.slotting.slotting import evaluate_slotting_impact

os.makedirs('static/img', exist_ok=True)
plt.style.use('dark_background')
plt.rcParams['font.size'] = 11
plt.rcParams['figure.dpi'] = 300

df_lines = pd.read_csv('static/in/anand_synthetic_df_lines.csv')
y_low, y_high = 5.5, 50.0
origin_loc = [0, y_low]

print("Generating Chart 1: warehouse_layout.png...")
plt.figure(figsize=(10, 6))
coords = [eval(c) for c in df_lines['Coord']]
xs = [c[0] for c in coords]
ys = [c[1] for c in coords]

plt.scatter(xs, ys, c='#00d2ff', alpha=0.5, s=25, label='SKU Storage Locations', edgecolors='none')
plt.scatter([0], [y_low], c='#ff4757', s=200, marker='*', label='Depot [0, 5.5]', zorder=5)
plt.axhline(y_low, color='#70a1ff', linestyle='--', alpha=0.7, label=f'Bottom Cross-Aisle (y={y_low}m)')
plt.axhline(y_high, color='#70a1ff', linestyle='--', alpha=0.7, label=f'Top Cross-Aisle (y={y_high}m)')

plt.title('2D Warehouse Layout & SKU Storage Grid (Synthetic Dataset)', fontsize=14, pad=12, color='white')
plt.xlabel('X-Coordinate / Alley Index (m)', color='white')
plt.ylabel('Y-Coordinate / Rack Location (m)', color='white')
plt.grid(True, linestyle=':', alpha=0.3)
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig('static/img/warehouse_layout.png')
plt.close()

print("Generating Chart 2 & 3: batch_final.png & cluster_final_results.png...")
list_res = [[], [], [], [], [], [], []]
df_reswave, _ = simulation_cluster(y_low, y_high, df_lines.head(3000), list_res, 1, 10, 35.0)

plt.figure(figsize=(10, 6))
wave_sizes = df_reswave.index
plt.plot(
    wave_sizes, df_reswave['distance_method_1'], marker='o', linewidth=2.5,
    color='#ff4757', label='Method 1: Chronological Batching'
)
plt.plot(
    wave_sizes, df_reswave['distance_method_3'], marker='s', linewidth=2.5,
    color='#2ed573', label='Method 3: Spatial Clustering + Centroids'
)
plt.fill_between(
    wave_sizes, df_reswave['distance_method_1'], df_reswave['distance_method_3'],
    color='#2ed573', alpha=0.15
)

plt.title('Order Wave Size Impact on Total Walking Distance (6,000 Lines)', fontsize=14, pad=12, color='white')
plt.xlabel('Wave Size (Orders per Wave)', color='white')
plt.ylabel('Total Walking Distance (m)', color='white')
plt.grid(True, linestyle=':', alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('static/img/batch_final.png')
plt.close()

plt.figure(figsize=(11, 6))
x = np.arange(len(wave_sizes))
width = 0.25

plt.bar(x - width, df_reswave['distance_method_1'], width, label='Method 1: No Clustering', color='#ff6b81')
plt.bar(x, df_reswave['distance_method_2'], width, label='Method 2: Single-Line Clustering', color='#eccc68')
plt.bar(x + width, df_reswave['distance_method_3'], width, label='Method 3: Cluster + Centroids', color='#70a1ff')

plt.title('Wave Creation Method Comparison Across Wave Sizes', fontsize=14, pad=12, color='white')
plt.xlabel('Wave Size (Orders/Wave)', color='white')
plt.ylabel('Walking Distance (m)', color='white')
plt.xticks(x, wave_sizes)
plt.grid(axis='y', linestyle=':', alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('static/img/cluster_final_results.png')
plt.close()

print("Generating Chart 4: heuristics_benchmark.png...")
records = []
for w in range(1, 11):
    sub_locs = [eval(c) for c in df_lines['Coord'].head(w * 30)]
    b = benchmark_routing_heuristics(origin_loc, sub_locs, y_low, y_high)
    for k, v in b.items():
        records.append({'Wave Size': w, 'Heuristic': k, 'Distance (m)': v['distance']})
df_h = pd.DataFrame(records)

plt.figure(figsize=(10, 6))
for heur, color in zip(['Next Closest', 'S-Shape', 'Return'], ['#2ed573', '#ffa502', '#ff4757'], strict=False):
    sub = df_h[df_h['Heuristic'] == heur]
    plt.plot(
        sub['Wave Size'], sub['Distance (m)'], marker='o', linewidth=2.5,
        color=color, label=f'{heur} Heuristic'
    )

plt.title('Single Picker Routing Heuristics Comparison (SPRP Benchmark)', fontsize=14, pad=12, color='white')
plt.xlabel('Wave Size (Orders per Wave)', color='white')
plt.ylabel('Average Route Distance (m)', color='white')
plt.grid(True, linestyle=':', alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('static/img/heuristics_benchmark.png')
plt.close()

print("Generating Chart 5: cost_savings.png...")
m1_base = df_reswave.loc[1, 'distance_method_1']
m3_opt = df_reswave.loc[9, 'distance_method_3']
cost_res = compare_financial_savings(m1_base, m3_opt, 1.2, 250.0, 8.0, 10, 15.0)

plt.figure(figsize=(10, 5.5))
categories = ['Baseline Cost / Day', 'Optimized Cost / Day', 'Daily Savings (₹)']
values = [cost_res['baseline_cost_inr'], cost_res['optimized_cost_inr'], cost_res['daily_cost_saved_inr']]
colors = ['#ff4757', '#70a1ff', '#2ed573']

bars = plt.bar(categories, values, color=colors, width=0.5)
title_txt = f"Financial Labor Cost Impact (Daily ₹ Savings: ₹{cost_res['daily_cost_saved_inr']:,.0f})"
plt.title(title_txt, fontsize=14, pad=12, color='white')
plt.ylabel('Cost in INR (₹)', color='white')
plt.grid(axis='y', linestyle=':', alpha=0.3)

for bar in bars:
    yval = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2.0, yval + (max(values) * 0.02),
        f"₹{yval:,.0f}", ha='center', va='bottom', color='white', fontweight='bold'
    )

plt.tight_layout()
plt.savefig('static/img/cost_savings.png')
plt.close()

print("Generating Chart 6: sensitivity_heatmap.png...")
df_sens, _ = run_sensitivity_analysis(df_lines.head(1500), [15, 25, 35, 45, 55], 1, 10, y_low, y_high)
pivot = df_sens.pivot(index='threshold', columns='orders_number', values='Method 3 (Cluster + Centroids)')

plt.figure(figsize=(10, 6))
plt.imshow(pivot.values, aspect='auto', cmap='viridis')
plt.colorbar(label='Distance (m)')
plt.yticks(range(len(pivot.index)), pivot.index)
plt.xticks(range(len(pivot.columns)), pivot.columns)

for r in range(len(pivot.index)):
    for c in range(len(pivot.columns)):
        val = pivot.values[r, c]
        plt.text(c, r, f"{val:,.0f}", ha='center', va='center', color='white', fontsize=9)

title_sens = 'Sensitivity Analysis: Walking Distance Across Thresholds (m) & Wave Sizes'
plt.title(title_sens, fontsize=13, pad=12, color='white')
plt.xlabel('Orders per Wave (N)', color='white')
plt.ylabel('Distance Threshold (m)', color='white')
plt.tight_layout()
plt.savefig('static/img/sensitivity_heatmap.png')
plt.close()

print("Generating Chart 7: abc_slotting.png...")
df_comp = evaluate_slotting_impact(df_lines.head(1000), wave_size=5, distance_threshold=35.0)

plt.figure(figsize=(11, 6))
scenarios = [
    'Baseline\n(Original, 1/wave)', 'Batching Only\n(Original, 5/wave)',
    'ABC Reslot Only\n(Reslotted, 1/wave)', 'Compounding\n(Reslot + Batch + Cluster)'
]
dists = df_comp['Walking Distance (m)']
colors = ['#ff4757', '#ffa502', '#1e90ff', '#2ed573']

bars = plt.bar(scenarios, dists, color=colors, width=0.5)
plt.title('Compounding Impact of ABC Slotting, Batching & Spatial Clustering', fontsize=14, pad=12, color='white')
plt.ylabel('Total Walking Distance (m)', color='white')
plt.grid(axis='y', linestyle=':', alpha=0.3)

for bar in bars:
    yval = bar.get_height()
    red_pct = (1 - yval / dists.iloc[0]) * 100.0
    label = f"{yval:,.0f} m\n(-{red_pct:.1f}%)" if red_pct > 0 else f"{yval:,.0f} m"
    plt.text(
        bar.get_x() + bar.get_width() / 2.0, yval + (max(dists) * 0.02),
        label, ha='center', va='bottom', color='white', fontweight='bold'
    )

plt.tight_layout()
plt.savefig('static/img/abc_slotting.png')
plt.close()

print("All 7 chart PNG images successfully generated in static/img/")
