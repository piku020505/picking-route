'''Synthetic Data Generator module:
Generates realistic order line datasets with configurable order counts, SKU counts,
aisle layouts, and Pareto (80/20) demand velocity skews.
'''

import numpy as np
import pandas as pd


def generate_synthetic_orderlines(
    n_lines: int = 1000,
    n_orders: int = 250,
    n_skus: int = 100,
    num_aisles: int = 10,
    y_low: float = 5.5,
    y_high: float = 50.0,
    pareto_alpha: float = 1.1,
    seed: int = 42,
) -> pd.DataFrame:
    '''Generate a synthetic order lines DataFrame matching the warehouse schema.

    Parameters:
    - n_lines: Total number of order lines to generate.
    - n_orders: Total number of unique orders.
    - n_skus: Total number of unique SKUs.
    - num_aisles: Number of picking aisles along the x-axis.
    - y_low, y_high: Aisle bounds on the y-axis (meters).
    - pareto_alpha: Shape parameter for Zipf/Pareto demand distribution.
    - seed: Random seed for reproducibility.
    '''
    np.random.seed(seed)

    order_ids = [3780000 + i for i in range(1, n_orders + 1)]
    sku_ids = [f"SKU_{i:04d}" for i in range(1, n_skus + 1)]

    # Generate SKU probabilities following Zipf/Pareto distribution
    zipf_weights = 1.0 / (np.arange(1, n_skus + 1) ** pareto_alpha)
    sku_probs = zipf_weights / zipf_weights.sum()

    # Assign SKUs to fixed warehouse 2D storage coordinates
    aisle_x_coords = np.linspace(5.0, 50.0, num_aisles)
    sku_coord_map = {}
    for sku in sku_ids:
        x = float(np.random.choice(aisle_x_coords))
        y = float(np.round(np.random.uniform(y_low, y_high), 1))
        sku_coord_map[sku] = (x, y)

    selected_orders = np.random.choice(order_ids, size=n_lines)
    selected_skus = np.random.choice(sku_ids, size=n_lines, p=sku_probs)
    selected_pcs = np.random.randint(1, 6, size=n_lines)

    records = []
    for idx in range(n_lines):
        order_num = selected_orders[idx]
        sku = selected_skus[idx]
        pcs = selected_pcs[idx]
        x, y = sku_coord_map[sku]

        records.append({
            'Unnamed: 0': idx,
            'DATE': '12/11/2018',
            'OrderNumber': order_num,
            'SKU': sku,
            'PCS': pcs,
            'ReferenceID': f"REF_{sku}",
            'Location': f"LOC_{sku}",
            'Alley_Number': int(round((x / 50.0) * num_aisles)),
            'Cellule': int(round((y - y_low) / (y_high - y_low) * 25)),
            'Coord': f"[{x}, {y}]",
            'AlleyCell': f"A{int(round(x)):02d}{int(round(y)):02d}",
            'x': x,
            'y': y,
        })

    df_synthetic = pd.DataFrame(records)
    return df_synthetic
