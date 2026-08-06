'''Sensitivity and Robustness Analysis module:
Evaluates how clustering distance threshold variations and layout scale parameters
shift the optimal wave size (N*) and total picking distance.
'''

import pandas as pd

from utils.cluster.simulation_cluster import simulation_cluster


def run_sensitivity_analysis(
    df_orderlines: pd.DataFrame,
    threshold_list: list[float] | None = None,
    n_min: int = 1,
    n_max: int = 10,
    y_low: float = 5.5,
    y_high: float = 50.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    '''Run sensitivity matrix simulation across threshold values and wave sizes.'''
    if threshold_list is None:
        threshold_list = [15, 25, 35, 45, 55]
    records = []
    optima_records = []

    for dist_thresh in threshold_list:
        list_results = [[], [], [], [], [], [], []]
        df_reswave, _ = simulation_cluster(
            y_low, y_high, df_orderlines, list_results, n_min, n_max + 1, dist_thresh
        )

        df_reswave_reset = df_reswave.reset_index()
        for _, row in df_reswave_reset.iterrows():
            records.append({
                'threshold': dist_thresh,
                'orders_number': int(row['orders_number']),
                'Method 1 (No Clustering)': row['distance_method_1'],
                'Method 2 (Single-Line Cluster)': row['distance_method_2'],
                'Method 3 (Cluster + Centroids)': row['distance_method_3'],
            })

        best_row = df_reswave_reset.loc[df_reswave_reset['distance_method_3'].idxmin()]
        optima_records.append({
            'Threshold (m)': dist_thresh,
            'Optimal Wave Size (N*)': int(best_row['orders_number']),
            'Min Distance Method 3 (m)': round(best_row['distance_method_3'], 2),
            'Baseline Distance (m)': round(df_reswave_reset.loc[0, 'distance_method_1'], 2),
        })

    df_sensitivity = pd.DataFrame(records)
    df_optima = pd.DataFrame(optima_records)
    return df_sensitivity, df_optima
