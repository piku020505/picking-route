'''ABC Slotting and Layout Optimization module:
Performs ABC SKU demand velocity classification and simulates re-slotting fast-moving SKUs
closer to the depot, measuring the compounding effect with order batching strategies.
'''

import pandas as pd

from utils.batch.simulation_batch import simulate_batch
from utils.cluster.simulation_cluster import simulation_cluster


def perform_abc_analysis(df_orderlines: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    '''Perform Pareto ABC analysis on SKUs based on picking frequency.

    Class A: Top 70% of total pick lines (~20% SKUs)
    Class B: Next 20% of total pick lines (~30% SKUs)
    Class C: Remaining 10% of pick lines (~50% SKUs)
    '''
    df = df_orderlines.copy()
    sku_col = 'SKU' if 'SKU' in df.columns else ('Ref' if 'Ref' in df.columns else 'Coord')

    sku_counts = df[sku_col].value_counts().reset_index()
    sku_counts.columns = [sku_col, 'pick_count']
    sku_counts = sku_counts.sort_values(by='pick_count', ascending=False).reset_index(drop=True)

    total_picks = sku_counts['pick_count'].sum()
    sku_counts['cum_picks'] = sku_counts['pick_count'].cumsum()
    sku_counts['cum_pct'] = (sku_counts['cum_picks'] / total_picks) * 100.0

    def assign_class(pct):
        if pct <= 70.0:
            return 'A'
        elif pct <= 90.0:
            return 'B'
        else:
            return 'C'

    sku_counts['ABC_Class'] = sku_counts['cum_pct'].apply(assign_class)
    df_classified = df.merge(sku_counts[[sku_col, 'ABC_Class']], on=sku_col, how='left')

    summary_records = []
    for abc_cls in ['A', 'B', 'C']:
        subset = sku_counts[sku_counts['ABC_Class'] == abc_cls]
        summary_records.append({
            'ABC Class': abc_cls,
            'SKU Count': len(subset),
            'SKU Share (%)': round(len(subset) / len(sku_counts) * 100.0, 1),
            'Pick Count': subset['pick_count'].sum(),
            'Pick Share (%)': round(subset['pick_count'].sum() / total_picks * 100.0, 1),
        })

    df_abc_summary = pd.DataFrame(summary_records)
    return df_classified, df_abc_summary


def reslot_skus(
    df_orderlines: pd.DataFrame, y_low: float = 5.5, y_high: float = 50.0
) -> pd.DataFrame:
    '''Re-slot SKUs based on ABC class: Class A placed closest to origin depot [0, y_low].'''
    df_classified, _ = perform_abc_analysis(df_orderlines)
    sku_col = 'SKU' if 'SKU' in df_classified.columns else ('Ref' if 'Ref' in df_classified.columns else 'Coord')

    # Get unique physical storage locations sorted by distance to depot [0, y_low]
    unique_locations = df_classified[['x', 'y']].drop_duplicates().copy()
    unique_locations['depot_dist'] = unique_locations['x'] + (unique_locations['y'] - y_low).abs()
    sorted_locations = unique_locations.sort_values(by='depot_dist').reset_index(drop=True)

    # Sort SKUs by popularity class (A first, then B, then C)
    sku_order = df_classified.groupby(sku_col).agg(
        abc=('ABC_Class', 'first'),
        picks=(sku_col, 'count')
    ).reset_index()

    class_order = {'A': 0, 'B': 1, 'C': 2}
    sku_order['class_rank'] = sku_order['abc'].map(class_order)
    sku_order = sku_order.sort_values(by=['class_rank', 'picks'], ascending=[True, False]).reset_index(drop=True)

    # Assign locations
    num_locs = len(sorted_locations)
    sku_to_loc = {}
    for idx, row in sku_order.iterrows():
        loc_row = sorted_locations.iloc[idx % num_locs]
        sku_to_loc[row[sku_col]] = (loc_row['x'], loc_row['y'])

    # Apply new coordinates to dataset
    df_reslotted = df_classified.copy()
    df_reslotted['x'] = df_reslotted[sku_col].apply(lambda s: sku_to_loc[s][0])
    df_reslotted['y'] = df_reslotted[sku_col].apply(lambda s: sku_to_loc[s][1])
    df_reslotted['Coord'] = df_reslotted.apply(lambda r: f"[{r['x']}, {r['y']}]", axis=1)

    return df_reslotted


def evaluate_slotting_impact(
    df_orderlines: pd.DataFrame,
    wave_size: int = 5,
    distance_threshold: float = 35.0,
    y_low: float = 5.5,
    y_high: float = 50.0,
) -> pd.DataFrame:
    '''Evaluate picking distance for 4 scenarios to demonstrate compounding gains:
    1. Baseline (Original Layout, 1 order/wave)
    2. Batching Only (Original Layout, Wave Size N)
    3. Re-slotting Only (Re-slotted Layout, 1 order/wave)
    4. Compounding (Re-slotted Layout + Batching Wave Size N)
    '''
    df_reslotted = reslot_skus(df_orderlines, y_low, y_high)
    n_lines = len(df_orderlines)
    origin_loc = [0, y_low]

    # Scenario 1: Original + Baseline (1 order/wave)
    _, res1 = simulate_batch(1, 2, y_low, y_high, origin_loc, n_lines, df_orderlines.copy())
    dist_orig_base = res1.iloc[0]['distance']

    # Scenario 2: Original + Batching Wave N
    _, res2 = simulate_batch(wave_size, wave_size + 1, y_low, y_high, origin_loc, n_lines, df_orderlines.copy())
    dist_orig_batch = res2.iloc[0]['distance']

    # Scenario 3: Re-slotted + Baseline (1 order/wave)
    _, res3 = simulate_batch(1, 2, y_low, y_high, origin_loc, n_lines, df_reslotted.copy())
    dist_reslot_base = res3.iloc[0]['distance']

    # Scenario 4: Re-slotted + Batching Wave N
    list_res = [[], [], [], [], [], [], []]
    res4, _ = simulation_cluster(y_low, y_high, df_reslotted.copy(), list_res, wave_size, wave_size + 1, distance_threshold)
    dist_compounding = res4.loc[wave_size, 'distance_method_3']

    df_compounding = pd.DataFrame([
        {
            'Scenario': '1. Baseline (Original Layout, 1 Order/Wave)',
            'Walking Distance (m)': round(dist_orig_base, 2),
            'Reduction vs Baseline (%)': 0.0,
        },
        {
            'Scenario': '2. Batching Only (Original Layout, Wave Size N)',
            'Walking Distance (m)': round(dist_orig_batch, 2),
            'Reduction vs Baseline (%)': round((1 - dist_orig_batch / dist_orig_base) * 100.0, 1),
        },
        {
            'Scenario': '3. Re-slotting Only (ABC Reslot, 1 Order/Wave)',
            'Walking Distance (m)': round(dist_reslot_base, 2),
            'Reduction vs Baseline (%)': round((1 - dist_reslot_base / dist_orig_base) * 100.0, 1),
        },
        {
            'Scenario': '4. Compounding (ABC Reslot + Batching + Clustering)',
            'Walking Distance (m)': round(dist_compounding, 2),
            'Reduction vs Baseline (%)': round((1 - dist_compounding / dist_orig_base) * 100.0, 1),
        },
    ])

    return df_compounding
