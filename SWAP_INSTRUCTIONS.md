# 🔄 SWAP_INSTRUCTIONS.md — Asset Replacement & File Cleanup Guide

This document provides step-by-step instructions for placing your custom synthetic dataset and generated result figures into the project repository, as well as cleaning up legacy illustrative graphics.

---

## 1. 📁 Dataset Swap (`static/in/`)

To replace the original sample dataset with your custom **6,000 order line synthetic dataset**:

### Commands:
```bash
# Copy synthetic dataset into static/in/
cp static/in/anand_synthetic_df_lines.csv static/in/df_lines.csv
```

---

## 2. 🖼️ Result Chart PNG Swap (`static/img/`)

All 7 quantitative result figures are dynamically computed by running your code against `anand_synthetic_df_lines.csv`:

| Generated Image | Description & Benchmark Result |
| :--- | :--- |
| **`warehouse_layout.png`** | 2D Warehouse layout grid mapping all SKU locations and depot origin `[0, 5.5]`. |
| **`batch_final.png`** | Experiment 1: Total walking distance reduction vs wave size (~636k m → ~147k m, -77% drop). |
| **`cluster_final_results.png`** | Experiment 2: Comparison of Method 1 (No cluster), Method 2 (Single-line), and Method 3 (Cluster + centroids). |
| **`heuristics_benchmark.png`** | Single Picker Routing Heuristics comparison: Next-Closest vs S-Shape (Serpentine) vs Return. |
| **`cost_savings.png`** | Financial workforce labor cost comparison (Baseline vs Optimized daily/annual ₹ savings). |
| **`sensitivity_heatmap.png`** | Sensitivity matrix heatmap across distance thresholds (15m–55m) and wave sizes (1–10). |
| **`abc_slotting.png`** | Pareto ABC SKU demand classification & 4-scenario compounding reduction (84.5%+ drop). |

### Command to Regenerate All 7 Charts:
```bash
uv run python -c "import sys; sys.path.insert(0, '.'); import scratch.generate_charts"
```

---

## 3. 🧹 Legacy Illustrative Graphic Cleanup

The following original files in `static/img/` were general illustrative explainer graphics (concepts, flow diagrams, or stock illustrations). You can either retain or clean them up depending on your preference:

| Legacy File | Purpose | Recommendation |
| :--- | :--- | :--- |
| `trolley.jpeg` | Generic stock image of a picking cart. | **Delete** (not required for technical analysis). |
| `wave_picking.gif` | Animated explainer of wave picking concepts. | **Retain** (helpful visual context for readers). |
| `intro_1.gif` | Baseline single-order picking route animation. | **Retain** (helpful visual context). |
| `wave_creation.png` | Conceptual flowchart of wave creation logic. | **Retain** (updated white font version). |
| `cluster_process.png` | Conceptual flowchart of spatial clustering. | **Retain** (updated white font version). |
| `cluster_analysis.png` | Conceptual flowchart of centroid mapping. | **Retain** (updated white font version). |

---

## 4. 🔀 Git Commit Command

```bash
git add static/in/ static/img/ SWAP_INSTRUCTIONS.md
git commit -m "feat: swap in 6,000 line synthetic dataset, 7 generated result charts, and swap instructions"
git push origin main
```
