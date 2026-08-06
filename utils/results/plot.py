import plotly.express as px
import streamlit as st

# Validated categorical palette (first three slots, light/dark variants).
# Series colors follow the entity: Method 1 = blue, Method 2 = orange, Method 3 = aqua.
LIGHT_SLOTS = ["#2a78d6", "#eb6834", "#1baf7a"]
DARK_SLOTS = ["#3987e5", "#d95926", "#199e70"]

METHOD_LABELS = {
    "distance_method_1": "Method 1 — No clustering",
    "distance_method_2": "Method 2 — Clustering on single-line orders",
    "distance_method_3": "Method 3 — Clustering + centroids for multi-line",
}

AXIS_LABELS = {
    "order_per_wave": "Wave size (orders/wave)",
    "orders_number": "Wave size (orders/wave)",
    "distance": "Total picking walking distance (m)",
    "method": "Batching method",
}


def _series_colors():
    '''Palette steps for the active Streamlit theme (light or dark).'''
    try:
        dark = st.context.theme.type == "dark"
    except Exception:
        dark = False
    return DARK_SLOTS if dark else LIGHT_SLOTS


def plot_simulation1(df_results, lines_number):
    '''Simulation 1 — total walking distance per wave size (single series).'''
    colors = _series_colors()
    fig = px.bar(
        data_frame=df_results,
        x='order_per_wave',
        y='distance',
        labels=AXIS_LABELS,
        color_discrete_sequence=[colors[0]],
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate='Wave size: %{x} orders/wave<br>Walking distance: %{y:,.0f} m<extra></extra>',
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(
        height=480,
        barcornerradius=4,
        bargap=0.3,
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, width='stretch')


def plot_simulation2(df_reswave, lines_number, distance_threshold):
    '''Simulation 2 — three batching methods compared (grouped bars).'''
    colors = _series_colors()
    color_map = dict(zip(METHOD_LABELS.values(), colors, strict=True))
    # Long format with readable method names for the legend
    df_plot = df_reswave.reset_index().melt(
        id_vars='orders_number', var_name='method', value_name='distance')
    df_plot['method'] = df_plot['method'].map(METHOD_LABELS)
    fig = px.bar(
        data_frame=df_plot,
        x='orders_number',
        y='distance',
        color='method',
        barmode='group',
        category_orders={'method': list(METHOD_LABELS.values())},
        color_discrete_map=color_map,
        labels=AXIS_LABELS,
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate='%{fullData.name}<br>Wave size: %{x} orders/wave<br>Walking distance: %{y:,.0f} m<extra></extra>',
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(
        height=480,
        barcornerradius=2,
        bargap=0.25,
        legend=dict(title=None, orientation='h', yanchor='bottom', y=1.02, x=0),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, width='stretch')


def plot_heuristics_benchmark(df_bench):
    '''Plot comparative routing heuristics (Next Closest vs S-Shape vs Return).'''
    colors = ["#2a78d6", "#1baf7a", "#eb6834"]
    fig = px.bar(
        df_bench,
        x='Wave Size',
        y='Distance (m)',
        color='Heuristic',
        barmode='group',
        color_discrete_sequence=colors,
        labels={'Wave Size': 'Wave size (orders/wave)', 'Distance (m)': 'Total Walking Distance (m)'},
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate='Heuristic: %{fullData.name}<br>Wave size: %{x}<br>Distance: %{y:,.0f} m<extra></extra>',
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(
        height=480,
        barcornerradius=3,
        bargap=0.2,
        legend=dict(title=None, orientation='h', yanchor='bottom', y=1.02, x=0),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, width='stretch')


def plot_sensitivity_heatmap(df_sensitivity):
    '''Plot sensitivity heatmap of walking distance across distance thresholds & wave sizes.'''
    pivot_df = df_sensitivity.pivot(
        index='threshold', columns='orders_number', values='Method 3 (Cluster + Centroids)'
    )
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Wave Size (orders/wave)", y="Distance Threshold (m)", color="Walking Distance (m)"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale="Viridis",
        aspect="auto",
    )
    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, width='stretch')


def plot_slotting_compounding(df_compounding):
    '''Plot compounding efficiency gains of ABC slotting re-allocation + order batching.'''
    colors = ["#d95926", "#3987e5", "#199e70", "#9b51e0"]
    fig = px.bar(
        df_compounding,
        x='Scenario',
        y='Walking Distance (m)',
        color='Scenario',
        color_discrete_sequence=colors,
        text='Reduction vs Baseline (%)',
    )
    fig.update_traces(
        texttemplate='-%{text:.1f}%',
        textposition='outside',
        marker_line_width=0,
    )
    fig.update_layout(
        height=480,
        showlegend=False,
        barcornerradius=4,
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis_title="Total Walking Distance (m)",
        xaxis_title=None,
    )
    st.plotly_chart(fig, width='stretch')
