import sys
sys.path.insert(0, '/tmp/picking-route-check')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
import numpy as np
import pandas as pd

from utils.routing.distances import distance_picking, next_location, centroid
from utils.cluster.clustering import cluster_locations

OUT = '/home/claude/swapkit2/static_img_new'
Y_LOW, Y_HIGH = 5.5, 50.0
BLUE = '#1f6feb'; ORANGE = '#d97706'; GREEN = '#059669'; GRAY = '#94a3b8'; RED = '#dc2626'
plt.rcParams.update({'figure.facecolor': 'white', 'axes.facecolor': 'white', 'font.size': 11})

def aisle_bg(ax, n_aisles=6, x_max=30):
    for x in np.linspace(0, x_max, n_aisles):
        ax.plot([x, x], [Y_LOW, Y_HIGH], color='#e2e8f0', linewidth=8, zorder=0)
    ax.set_xlim(-3, x_max+3); ax.set_ylim(0, Y_HIGH+5)
    ax.axis('off')

# ---------------------------------------------------------------
# 1. route_two_locations.png  (replaces trolley.jpeg AND batch_function_1.png)
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
aisle_bg(ax)
i_pt, j_pt = (6, 15), (18, 42)
ax.scatter(*i_pt, s=140, color=BLUE, zorder=5); ax.annotate('i (x1, y1)', i_pt, textcoords="offset points", xytext=(8,-14))
ax.scatter(*j_pt, s=140, color=ORANGE, zorder=5); ax.annotate('j (x2, y2)', j_pt, textcoords="offset points", xytext=(8,6))
# route A: via top cross-aisle
ax.plot([i_pt[0], i_pt[0]], [i_pt[1], Y_HIGH], color=GREEN, lw=2)
ax.plot([i_pt[0], j_pt[0]], [Y_HIGH, Y_HIGH], color=GREEN, lw=2)
ax.plot([j_pt[0], j_pt[0]], [Y_HIGH, j_pt[1]], color=GREEN, lw=2, label='Route via top cross-aisle')
# route B: via bottom cross-aisle
ax.plot([i_pt[0], i_pt[0]], [i_pt[1], Y_LOW], color=RED, lw=2, linestyle='--')
ax.plot([i_pt[0], j_pt[0]], [Y_LOW, Y_LOW], color=RED, lw=2, linestyle='--')
ax.plot([j_pt[0], j_pt[0]], [Y_LOW, j_pt[1]], color=RED, lw=2, linestyle='--', label='Route via bottom cross-aisle')
d = distance_picking(list(i_pt), list(j_pt), Y_LOW, Y_HIGH)
ax.set_title(f'distance_picking(i, j) — shorter route selected = {d} m')
ax.legend(loc='lower right', frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(f'{OUT}/route_two_locations.png', dpi=150); plt.close(fig)
print('1/10 route_two_locations.png')

# ---------------------------------------------------------------
# 2. next_closest_location.png (replaces batch_function_2.png)
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
aisle_bg(ax)
start = [6, 15]
candidates = [[6, 40], [18, 12], [12, 20], [24, 30]]
_, _, chosen, dmin = next_location(start, candidates.copy(), Y_LOW, Y_HIGH)
ax.scatter(*start, s=160, color=BLUE, zorder=5, marker='s'); ax.annotate('Current location', start, textcoords="offset points", xytext=(8,-14))
for c in candidates:
    color = GREEN if c == chosen else GRAY
    ax.scatter(*c, s=100, color=color, zorder=4)
    if c == chosen:
        ax.annotate(f'Chosen (d={dmin}m)', c, textcoords="offset points", xytext=(8,6), color=GREEN, fontweight='bold')
        ax.plot([start[0], c[0]], [start[1], c[1]], color=GREEN, lw=2, zorder=3)
    else:
        ax.annotate('candidate', c, textcoords="offset points", xytext=(8,6), color=GRAY, fontsize=8)
ax.set_title('next_location() — closest candidate selected from wave')
fig.tight_layout(); fig.savefig(f'{OUT}/next_closest_location.png', dpi=150); plt.close(fig)
print('2/10 next_closest_location.png')

# ---------------------------------------------------------------
# 3 & 4. Scenario 1 (single-order routes) vs Scenario 2 (wave picking)
# ---------------------------------------------------------------
orders = {
    'Order #1': [[4, 12], [4, 30]],
    'Order #2': [[10, 20], [10, 38]],
    'Order #3': [[16, 14], [16, 44]],
}
colors = {'Order #1': BLUE, 'Order #2': ORANGE, 'Order #3': GREEN}
depot = [0, Y_LOW]

fig, ax = plt.subplots(figsize=(8, 5))
aisle_bg(ax, x_max=20)
ax.scatter(*depot, s=140, color='black', marker='*', zorder=6, label='Depot')
total_d1 = 0
for name, pts in orders.items():
    route = [depot] + pts + [depot]
    xs, ys = zip(*route)
    ax.plot(xs, ys, color=colors[name], lw=2, marker='o', label=name)
    for a, b in zip(route[:-1], route[1:]):
        total_d1 += distance_picking(list(a), list(b), Y_LOW, Y_HIGH)
ax.set_title(f'Scenario 1 — 1 order per wave (3 separate trips, {total_d1} m total)')
ax.legend(loc='upper right', fontsize=8, frameon=False)
fig.tight_layout(); fig.savefig(f'{OUT}/scenario1_single_order_routes.png', dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
aisle_bg(ax, x_max=20)
ax.scatter(*depot, s=140, color='black', marker='*', zorder=6, label='Depot')
all_pts = [p for pts in orders.values() for p in pts]
route_pts = [depot]
remaining = all_pts.copy()
cur = depot
while remaining:
    remaining, cur, nxt, _ = next_location(cur, remaining, Y_LOW, Y_HIGH)
    route_pts.append(nxt); cur = nxt
route_pts.append(depot)
xs, ys = zip(*route_pts)
ax.plot(xs, ys, color=BLUE, lw=2.5, marker='o', zorder=4)
for name, pts in orders.items():
    for p in pts:
        ax.scatter(*p, s=90, color=colors[name], zorder=5)
total_d2 = sum(distance_picking(list(a), list(b), Y_LOW, Y_HIGH) for a, b in zip(route_pts[:-1], route_pts[1:]))
ax.set_title(f'Scenario 2 — Wave Picking, 3 orders combined ({total_d2} m, {(1-total_d2/total_d1)*100:.0f}% less)')
fig.tight_layout(); fig.savefig(f'{OUT}/scenario2_wave_picking_route.png', dpi=150); plt.close(fig)
print('3-4/10 scenario1/2 routes')

# ---------------------------------------------------------------
# 5. database_schema.png
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5)); ax.axis('off')
def box(ax, xy, w, h, title, rows, color):
    bx = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02", linewidth=1.4,
                         edgecolor=color, facecolor=color+'22')
    ax.add_patch(bx)
    ax.text(xy[0]+w/2, xy[1]+h-0.35, title, ha='center', fontweight='bold', fontsize=11)
    for i, r in enumerate(rows):
        ax.text(xy[0]+0.3, xy[1]+h-0.75-i*0.4, r, fontsize=9, family='monospace')
box(ax, (0, 0), 4, 3, 'Order Lines (WMS)', ['OrderNumber', 'SKU', 'PCS', 'ReferenceID', 'DATE'], BLUE)
box(ax, (6, 0), 4, 3, 'Master Data', ['ReferenceID', 'Location', 'Alley_Number', 'Cellule', 'Coord (x, y)'], ORANGE)
box(ax, (3, -2.2), 4, 2, 'df_lines (joined)', ['OrderNumber, SKU, Coord (x,y)', 'used by simulate_batch()'], GREEN)
ax.annotate('', xy=(3.1, -1.0), xytext=(2, -0.3), arrowprops=dict(arrowstyle='->', lw=1.5))
ax.annotate('', xy=(5.5, -1.0), xytext=(7, -0.3), arrowprops=dict(arrowstyle='->', lw=1.5))
ax.text(4.5, 1.5, 'JOIN\non\nReferenceID', ha='center', fontsize=9, style='italic', color='#444')
ax.set_xlim(-1, 11); ax.set_ylim(-3, 3.3)
fig.tight_layout(); fig.savefig(f'{OUT}/database_schema.png', dpi=150); plt.close(fig)
print('5/10 database_schema.png')

print("Batch 1 complete")
import sys
sys.path.insert(0, '/tmp/picking-route-check')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
from ast import literal_eval

from utils.routing.distances import centroid
from utils.cluster.clustering import cluster_locations

OUT = '/home/claude/swapkit2/static_img_new'
BLUE = '#1f6feb'; ORANGE = '#d97706'; GREEN = '#059669'; GRAY = '#94a3b8'; RED = '#dc2626'
plt.rcParams.update({'figure.facecolor': 'white', 'axes.facecolor': 'white', 'font.size': 11})

df = pd.read_csv('/tmp/picking-route-check/static/in/df_lines.csv')

def box(ax, xy, w, h, text, color, fontsize=9.5):
    bx = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.03", linewidth=1.4,
                         edgecolor=color, facecolor=color+'22')
    ax.add_patch(bx)
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha='center', va='center', fontsize=fontsize, wrap=True)

def arrow(ax, p1, p2):
    ax.annotate('', xy=p2, xytext=p1, arrowprops=dict(arrowstyle='->', lw=1.6, color='#333'))

# ---------------------------------------------------------------
# 6. order_lines_processing_flow.png
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5)); ax.axis('off')
box(ax, (0, 3.2), 3.2, 1, 'Raw Order Lines\n(df_lines.csv)', BLUE)
box(ax, (-1.8, 1.2), 3.2, 1, 'Mono-line Orders\n(1 SKU per order)', ORANGE)
box(ax, (2.2, 1.2), 3.2, 1, 'Multi-line Orders\n(2+ SKUs per order)', ORANGE)
box(ax, (-1.8, -0.8), 3.2, 1, 'Cluster on\nown coordinate', GREEN)
box(ax, (2.2, -0.8), 3.2, 1, 'Compute centroid,\nthen cluster', GREEN)
box(ax, (0, -2.8), 3.2, 1, 'WaveID assigned\n-> route simulation', BLUE)
arrow(ax, (1.6, 3.2), (-0.2, 2.2)); arrow(ax, (1.6, 3.2), (3.8, 2.2))
arrow(ax, (-0.2, 1.2), (-0.2, 0.2)); arrow(ax, (3.8, 1.2), (3.8, 0.2))
arrow(ax, (-0.2, -0.8), (1.4, -1.8)); arrow(ax, (3.8, -0.8), (2.0, -1.8))
ax.set_xlim(-3, 6.5); ax.set_ylim(-3.5, 4.5)
ax.set_title('Order Lines Processing for Wave Picking by Clustering')
fig.tight_layout(); fig.savefig(f'{OUT}/order_lines_processing_flow.png', dpi=150); plt.close(fig)
print('6/10 order_lines_processing_flow.png')

# ---------------------------------------------------------------
# 7. clustering_distance_methods.png — GENUINE, computed from own data
# ---------------------------------------------------------------
df_mono = df.groupby('OrderNumber').filter(lambda g: len(g) == 1).copy()
sample = df_mono.drop_duplicates('OrderNumber').head(120)
coords = [literal_eval(c) for c in sample['Coord']]
clust_walk = cluster_locations(coords, 15, 'custom', 1)
clust_eucl = cluster_locations(coords, 15, 'euclidian', 1)

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
xs = [c[0] for c in coords]; ys = [c[1] for c in coords]
sc1 = axes[0].scatter(xs, ys, c=clust_walk, cmap='tab20', s=40)
axes[0].set_title(f'Walking-Distance Clustering\n({len(set(clust_walk))} clusters, threshold=15m)')
sc2 = axes[1].scatter(xs, ys, c=clust_eucl, cmap='tab20', s=40)
axes[1].set_title(f'Euclidian-Distance Clustering\n({len(set(clust_eucl))} clusters, threshold=15m)')
for ax in axes:
    ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)')
fig.suptitle('Mono-line Order Clustering — cluster_locations() on synthetic data')
fig.tight_layout(); fig.savefig(f'{OUT}/clustering_distance_methods.png', dpi=150); plt.close(fig)
print(f'7/10 clustering_distance_methods.png  (walk clusters={len(set(clust_walk))}, eucl clusters={len(set(clust_eucl))})')

# ---------------------------------------------------------------
# 8. centroid_example.png — GENUINE, real order + its centroid
# ---------------------------------------------------------------
df_multi = df.groupby('OrderNumber').filter(lambda g: len(g) >= 3)
example_order = df_multi['OrderNumber'].iloc[0]
pts = [literal_eval(c) for c in df_multi[df_multi.OrderNumber == example_order]['Coord']]
cen = centroid(pts)
fig, ax = plt.subplots(figsize=(6.5, 5))
xs, ys = zip(*pts)
ax.scatter(xs, ys, s=130, color=BLUE, label='Picking locations', zorder=4)
for i, p in enumerate(pts):
    ax.annotate(f'SKU location {i+1}', p, textcoords='offset points', xytext=(8, 4), fontsize=9)
ax.scatter(*cen, s=180, color=ORANGE, marker='X', label=f'Centroid {tuple(cen)}', zorder=5)
for p in pts:
    ax.plot([p[0], cen[0]], [p[1], cen[1]], color=GRAY, linestyle='--', lw=1, zorder=1)
ax.set_title(f'Centroid of Multi-line Order #{example_order}')
ax.legend(frameon=False, fontsize=9)
ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)')
fig.tight_layout(); fig.savefig(f'{OUT}/centroid_example.png', dpi=150); plt.close(fig)
print(f'8/10 centroid_example.png  order={example_order}, centroid={cen}')

# ---------------------------------------------------------------
# 9. model_methodology.png
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 3.2)); ax.axis('off')
steps = ['Load\ndf_lines', 'Split\nmono/multi', 'Cluster\n(threshold)', 'Assign\nWaveID', 'Route\n(heuristic)', 'Distance\n+ Cost']
xs = np.linspace(0, 10, len(steps))
for x, s in zip(xs, steps):
    box(ax, (x-0.7, -0.5), 1.4, 1, s, BLUE, fontsize=9)
for i in range(len(xs)-1):
    arrow(ax, (xs[i]+0.7, 0), (xs[i+1]-0.7, 0))
ax.text(xs[2], 1.0, 'param: distance_threshold', ha='center', fontsize=8, style='italic', color='#555')
ax.text(xs[4], 1.0, 'param: heuristic choice', ha='center', fontsize=8, style='italic', color='#555')
ax.set_xlim(-1.5, 11); ax.set_ylim(-1.2, 1.8)
ax.set_title('Model Construction — Tunable Parameters at Each Step')
fig.tight_layout(); fig.savefig(f'{OUT}/model_methodology.png', dpi=150); plt.close(fig)
print('9/10 model_methodology.png')

# ---------------------------------------------------------------
# 10. three_wave_methods.png
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
rng = np.random.default_rng(3)
base_pts = rng.uniform(2, 28, size=(9, 2))
titles = ['Method 1\nNo clustering (baseline)', 'Method 2\nMono-line clustering', 'Method 3\nMono + centroid clustering']
colors_list = [GRAY, ORANGE, GREEN]
for ax, title, col in zip(axes, titles, colors_list):
    ax.scatter(base_pts[:,0], base_pts[:,1], s=70, color=col)
    if title.startswith('Method 2') or title.startswith('Method 3'):
        # draw grouping circles
        from scipy.spatial.distance import pdist, squareform
        d = squareform(pdist(base_pts))
        used = set()
        for i in range(len(base_pts)):
            if i in used: continue
            group = [i] + [j for j in range(len(base_pts)) if j != i and d[i,j] < 9 and j not in used]
            used.update(group)
            if len(group) > 1:
                gx, gy = base_pts[group,0], base_pts[group,1]
                ax.scatter(gx.mean(), gy.mean(), marker='X', s=100, color='black', zorder=5)
                circle = plt.Circle((gx.mean(), gy.mean()), max(gx.max()-gx.min(), gy.max()-gy.min())/2+2,
                                     fill=False, linestyle='--', color=col, lw=1)
                ax.add_patch(circle)
    ax.set_title(title, fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle('Three Wave-Creation Methods — Conceptual Comparison')
fig.tight_layout(); fig.savefig(f'{OUT}/three_wave_methods.png', dpi=150); plt.close(fig)
print('10/10 three_wave_methods.png')

print("Batch 2 complete")
