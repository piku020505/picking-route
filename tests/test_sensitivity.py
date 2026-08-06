'''Unit tests for sensitivity and robustness analysis module.'''

import pandas as pd

from utils.data.generator import generate_synthetic_orderlines
from utils.sensitivity.sensitivity import run_sensitivity_analysis


def test_run_sensitivity_analysis():
    df_synth = generate_synthetic_orderlines(n_lines=100, n_orders=20, n_skus=15, seed=42)
    df_sensitivity, df_optima = run_sensitivity_analysis(
        df_synth, threshold_list=[25, 35], n_min=1, n_max=3, y_low=5.5, y_high=50.0
    )

    assert isinstance(df_sensitivity, pd.DataFrame)
    assert isinstance(df_optima, pd.DataFrame)
    assert len(df_optima) == 2
    assert 'Optimal Wave Size (N*)' in df_optima.columns
