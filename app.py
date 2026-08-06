import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.batch.simulation_batch import simulation_batch
from utils.cluster.simulation_cluster import simulation_cluster
from utils.cost.cost_model import compare_financial_savings
from utils.data.generator import generate_synthetic_orderlines
from utils.results.plot import (
    plot_heuristics_benchmark,
    plot_sensitivity_heatmap,
    plot_simulation1,
    plot_simulation2,
    plot_slotting_compounding,
)
from utils.routing.heuristics import benchmark_routing_heuristics
from utils.sensitivity.sensitivity import run_sensitivity_analysis
from utils.slotting.slotting import (
    evaluate_slotting_heuristics_interplay,
    evaluate_slotting_impact,
    perform_abc_analysis,
)

# --- Page configuration -------------------------------------------------------
st.set_page_config(
    page_title="Improve Warehouse Productivity using Order Batching & Routing",
    initial_sidebar_state="expanded",
    layout="wide",
    page_icon="🛒",
)

# --- Warehouse layout constants -----------------------------------------------
Y_LOW, Y_HIGH = 5.5, 50.0        # alley low/high coordinates on the y-axis (m)
ORIGIN_LOC = [0, Y_LOW]        # picking route start/end point (depot)
DATA_FILE = Path("static/in/df_lines.csv")


# --- Cached data & simulations ------------------------------------------------
@st.cache_data(show_spinner=False)
def dataset_size():
    return len(pd.read_csv(DATA_FILE))


@st.cache_data(show_spinner=False)
def load(n):
    '''Load the first n order lines of the dataset'''
    return pd.read_csv(DATA_FILE).head(n)


@st.cache_data(show_spinner=False)
def run_simulation_1(lines_number, n1, n2):
    '''Simulation 1: total walking distance for each wave size in [n1, n2]'''
    df_orderlines = load(lines_number)
    _, df_results = simulation_batch(n1, n2, Y_LOW, Y_HIGH, ORIGIN_LOC, lines_number, df_orderlines)
    return df_results


@st.cache_data(show_spinner=False)
def run_simulation_2(lines_number, n1, n2, distance_threshold):
    '''Simulation 2: three wave-creation methods (no clustering / mono-line clustering / + centroids)'''
    df_orderlines = load(lines_number)
    list_results = [[], [], [], [], [], [], []]
    df_reswave, _ = simulation_cluster(Y_LOW, Y_HIGH, df_orderlines, list_results, n1, n2, distance_threshold)
    return df_reswave


@st.cache_data(show_spinner=False)
def run_heuristics_benchmark(lines_number, n1, n2):
    '''Benchmark Next Closest, S-Shape, and Return routing across wave sizes.'''
    df_orderlines = load(lines_number)
    records = []
    for wave_size in range(n1, n2 + 1):
        df_wave = df_orderlines.head(wave_size * 10)
        locations = []
        for coord_str in df_wave['Coord']:
            try:
                c = eval(coord_str)
                locations.append(c)
            except Exception:
                pass
        bench = benchmark_routing_heuristics(ORIGIN_LOC, locations, Y_LOW, Y_HIGH)
        for heur_name, h_data in bench.items():
            records.append({
                'Wave Size': wave_size,
                'Heuristic': heur_name,
                'Distance (m)': h_data['distance'],
            })
    return pd.DataFrame(records)


# --- Sidebar: simulation parameters -------------------------------------------
max_scope = max(1, dataset_size() // 1000)
with st.sidebar:
    st.title("🛒 Picking Route Optimisation")
    st.caption("Simulate order batching, spatial clustering, routing heuristics, and cost savings.")

    st.header("⚙️ Simulation Parameters")
    scope = st.slider(
        "Scope (thousand order lines)", 1, max_scope, min(5, max_scope),
        help=f"Number of order lines included — loaded dataset has {dataset_size():,} lines."
    )
    n1 = st.slider("N_MIN (orders/wave)", 1, 20, 1, help="Smallest wave size to simulate.")
    n2 = st.slider("N_MAX (orders/wave)", n1 + 1, 20, max(n1 + 1, 10), help="Largest wave size to simulate.")
    distance_threshold = st.slider(
        "Distance Threshold (m)", 10, 60, 35, help="Clustering threshold distance (m) between picking locations."
    )

    st.header("💰 Financial Cost Layer")
    walking_speed = st.number_input("Walking Speed (m/s)", 0.5, 3.0, 1.2, step=0.1)
    hourly_wage = st.number_input("Picker Hourly Wage (₹/hr)", 50.0, 2000.0, 250.0, step=10.0)
    shift_hours = st.number_input("Shift Duration (hours)", 4.0, 12.0, 8.0, step=0.5)
    num_pickers = st.number_input("Active Pickers Count", 1, 100, 10, step=1)
    seconds_per_line = st.number_input("Pick Time per Line (s)", 5.0, 60.0, 15.0, step=1.0)

    st.divider()
    st.markdown(
        "Warehouse Order Batching & Picking Route Optimization App 📦 · "
        "Made by [piku020505](https://github.com/piku020505)"
    )

lines_number = scope * 1000

# --- Main page -----------------------------------------------------------------
st.title("📦 Improve Warehouse Productivity using Order Batching & Routing")
st.markdown(
    f"Simulating **{lines_number:,} order lines** with wave sizes from **{n1}** to **{n2} orders/wave** — "
    "tune parameters in the sidebar to observe real-time operational impacts."
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🥇 Wave Size Impact",
    "🥈 Batching Methods",
    "🥉 Routing Heuristics",
    "💰 Financial & Ops Cost",
    "🎛️ Sensitivity Analysis",
    "🎯 ABC Slotting",
    "🎲 Synthetic Data & Tests",
])

# Tab 1: Wave size impact
with tab1:
    st.subheader("How does the number of orders per wave impact the total walking distance?")
    with st.spinner(f"Simulating {lines_number:,} order lines for wave sizes {n1} to {n2}…"):
        df_results = run_simulation_1(lines_number, n1, n2)

    base = df_results.iloc[0]
    best = df_results.loc[df_results["distance"].idxmin()]
    saving = 1 - best["distance"] / base["distance"]

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Baseline — {int(base['order_per_wave'])} order(s)/wave", f"{base['distance']:,.0f} m")
    col2.metric(
        f"Best — {int(best['order_per_wave'])} orders/wave", f"{best['distance']:,.0f} m",
        delta=f"-{saving:.0%} walking distance", delta_color="inverse"
    )
    col3.metric("Order lines simulated", f"{lines_number:,}")

    plot_simulation1(df_results, lines_number)

    with st.expander("📄 Results table"):
        st.dataframe(
            df_results.rename(columns={"order_per_wave": "Wave size (orders/wave)",
                              "distance": "Walking distance (m)"}),
            hide_index=True, width="stretch"
        )

# Tab 2: Batching & Clustering
with tab2:
    st.subheader("Does spatial clustering of picking locations reduce walking distance further?")
    st.markdown(
        f"Three wave-creation methods compared — **Method 1**: chronological batching · "
        f"**Method 2**: single-line clustering · **Method 3**: clustering + centroids "
        f"_(distance threshold: {distance_threshold} m)_."
    )

    with st.spinner(f"Running the three methods on {lines_number:,} order lines…"):
        df_reswave = run_simulation_2(lines_number, n1, n2, distance_threshold)

    best_n = df_reswave["distance_method_3"].idxmin()
    m1_val = df_reswave.loc[best_n, "distance_method_1"]
    m3_val = df_reswave.loc[best_n, "distance_method_3"]
    saving_2 = 1 - m3_val / m1_val

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Method 1 — {int(best_n)} orders/wave", f"{m1_val:,.0f} m")
    col2.metric(
        f"Method 3 — {int(best_n)} orders/wave", f"{m3_val:,.0f} m",
        delta=f"-{saving_2:.0%} vs Method 1", delta_color="inverse"
    )
    col3.metric("Distance threshold", f"{distance_threshold} m")

    plot_simulation2(df_reswave, lines_number, distance_threshold)

    with st.expander("📄 Results table"):
        st.dataframe(
            df_reswave.reset_index().rename(
                columns={
                    "orders_number": "Wave size (orders/wave)",
                    "distance_method_1": "Method 1 — No clustering (m)",
                    "distance_method_2": "Method 2 — Clustering single-line (m)",
                    "distance_method_3": "Method 3 — Clustering + centroids (m)",
                }
            ),
            hide_index=True, width="stretch"
        )

# Tab 3: Routing Heuristics Comparison
with tab3:
    st.subheader("Comparative Study: Next Closest vs S-Shape (Serpentine) vs Return Routing")
    st.markdown(
        "Benchmarking three classic single picker routing problem (SPRP) heuristics on the exact same dataset."
    )

    with st.spinner("Benchmarking routing heuristics across wave sizes…"):
        df_bench = run_heuristics_benchmark(lines_number, n1, n2)

    plot_heuristics_benchmark(df_bench)

    avg_dists = df_bench.groupby('Heuristic')['Distance (m)'].mean().reset_index()
    winner = avg_dists.loc[avg_dists['Distance (m)'].idxmin()]

    st.success(
        f"🏆 **Winning Routing Strategy**: **{winner['Heuristic']}** "
        f"with an average route distance of **{winner['Distance (m)']:,.0f} m**."
    )

    with st.expander("📄 Detailed Heuristics Data"):
        st.dataframe(df_bench, hide_index=True, width="stretch")

# Tab 4: Financial Cost Layer
with tab4:
    st.subheader("💰 Financial & Operational Labor Translation")
    st.markdown(
        "Translating physical picker walking distance reduction into workforce hours, "
        "daily labor cost savings (₹), and extra order throughput capacity."
    )

    df_orderlines = load(lines_number)
    df_reswave = run_simulation_2(lines_number, n1, n2, distance_threshold)

    base_dist = df_reswave.iloc[0]["distance_method_1"]
    opt_dist = df_reswave["distance_method_3"].min()

    cost_res = compare_financial_savings(
        base_dist, opt_dist, walking_speed, hourly_wage, shift_hours, num_pickers, seconds_per_line
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Daily Distance Saved", f"{cost_res['distance_saved_m']:,.0f} m",
        delta=f"-{cost_res['distance_saved_pct']:.1f}%"
    )
    c2.metric("Hours Saved per Shift", f"{cost_res['hours_saved_per_shift']:.1f} hrs", delta="Workforce Efficiency")
    c3.metric(
        "Daily Cost Saved (₹)", f"₹{cost_res['daily_cost_saved_inr']:,.0f}",
        delta="Labor Savings", delta_color="inverse"
    )
    c4.metric("Additional Lines / Shift", f"+{cost_res['extra_lines_per_shift']:,} lines", delta="Capacity Expansion")

    st.markdown("### 📊 Annualized Financial Impact")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.info(
            f"**Annual Labor Cost Savings**: **₹{cost_res['annual_cost_saved_inr']:,.0f} / year** "
            "*(assuming 300 operational days/year)*"
        )
    with col_a2:
        st.success(
            f"**Equivalent Productivity Boost**: **+{cost_res['extra_lines_per_shift'] * 300:,.0f} "
            "additional pick lines/year** without extra headcount."
        )

# Tab 5: Sensitivity Analysis
with tab5:
    st.subheader("🎛️ Sensitivity & Model Robustness Analysis")
    st.markdown(
        "Evaluating how distance threshold variations shift the optimal wave size $N^*$ and total walking distance."
    )

    thresh_input = st.multiselect(
        "Distance Thresholds to Compare (m)", [15, 25, 35, 45, 55], default=[15, 25, 35, 45, 55]
    )

    if thresh_input:
        with st.spinner("Running sensitivity matrix simulation…"):
            df_orderlines = load(min(lines_number, 2000))
            df_sensitivity, df_optima = run_sensitivity_analysis(df_orderlines, thresh_input, n1, n2, Y_LOW, Y_HIGH)

        plot_sensitivity_heatmap(df_sensitivity)

        st.markdown("### 🎯 Optimal Wave Size (N*) Shift Summary")
        st.dataframe(df_optima, hide_index=True, width="stretch")

# Tab 6: ABC Slotting Optimization
with tab6:
    st.subheader("🎯 ABC SKU Slotting & Layout Re-allocation")
    st.markdown(
        "Simulating SKU demand velocity classification (Pareto 80/20) and "
        "re-slotting fast-moving Class A items closer to the depot `[0, y_low]`."
    )

    df_orderlines = load(lines_number)
    _, df_abc_summary = perform_abc_analysis(df_orderlines)

    st.markdown("### 📊 SKU Pareto Demand Distribution")
    st.dataframe(df_abc_summary, hide_index=True, width="stretch")

    st.markdown("### 🚀 Compounding Efficiency Impact (Slotting + Order Batching)")
    with st.spinner("Evaluating compounding slotting & batching scenarios…"):
        df_compounding = evaluate_slotting_impact(
            df_orderlines, wave_size=max(n1, 5), distance_threshold=distance_threshold
        )

    plot_slotting_compounding(df_compounding)
    st.dataframe(df_compounding, hide_index=True, width="stretch")

    st.markdown("### 💡 Interplay of ABC Slotting with Routing Heuristics")
    st.markdown("Comparing how SKU re-slotting impacts Next Closest, S-Shape, and Return routing heuristics:")
    with st.spinner("Evaluating slotting & heuristics interplay…"):
        df_interplay = evaluate_slotting_heuristics_interplay(df_orderlines)
    st.dataframe(df_interplay, hide_index=True, width="stretch")

# Tab 7: Synthetic Data & Unit Tests
with tab7:
    st.subheader("🎲 Synthetic Order Line Generator & Automated Test Suite")
    st.markdown("Generate synthetic warehouse order line datasets or run the automated `pytest` test suite.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 🛠️ Generate Synthetic Dataset")
        n_synth_lines = st.number_input("Synthetic Lines", 100, 10000, 1000, step=100)
        n_synth_orders = st.number_input("Unique Orders", 20, 2000, 250, step=10)
        n_synth_skus = st.number_input("Unique SKUs", 10, 1000, 100, step=10)

        if st.button("Generate & Download CSV"):
            df_synth = generate_synthetic_orderlines(n_synth_lines, n_synth_orders, n_synth_skus)
            st.success(f"Generated {len(df_synth):,} synthetic order lines!")
            st.dataframe(df_synth.head(10), hide_index=True, width="stretch")

            csv_data = df_synth.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Synthetic df_lines.csv",
                data=csv_data,
                file_name="synthetic_df_lines.csv",
                mime="text/csv",
            )

    with col_s2:
        st.markdown("#### 🧪 Automated Unit Test Suite (Pytest)")
        st.markdown("Run all 13 unit tests for routing heuristics, cost models, sensitivity analysis, and slotting.")

        if st.button("▶️ Run Pytest Suite"):
            with st.spinner("Executing test suite…"):
                res = subprocess.run(["uv", "run", "pytest"], capture_output=True, text=True)
                if res.returncode == 0:
                    st.success("✅ All unit tests PASSED cleanly!")
                    st.code(res.stdout, language="bash")
                else:
                    st.error("❌ Test suite encountered failures:")
                    st.code(res.stderr or res.stdout, language="bash")
