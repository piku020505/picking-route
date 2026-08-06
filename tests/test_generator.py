'''Unit tests for synthetic order line data generator.'''

import pandas as pd

from utils.data.generator import generate_synthetic_orderlines


def test_generate_synthetic_orderlines():
    df_synth = generate_synthetic_orderlines(n_lines=200, n_orders=40, n_skus=25, seed=42)

    assert isinstance(df_synth, pd.DataFrame)
    assert len(df_synth) == 200
    assert df_synth['OrderNumber'].nunique() <= 40
    assert df_synth['SKU'].nunique() <= 25

    expected_cols = {'OrderNumber', 'SKU', 'PCS', 'Coord', 'x', 'y'}
    assert expected_cols.issubset(set(df_synth.columns))
    assert (df_synth['x'] >= 0).all()
    assert (df_synth['y'] >= 5.5).all()
