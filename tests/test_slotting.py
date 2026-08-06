'''Unit tests for ABC SKU slotting and layout optimization.'''

import pandas as pd

from utils.data.generator import generate_synthetic_orderlines
from utils.slotting.slotting import (
    evaluate_slotting_heuristics_interplay,
    evaluate_slotting_impact,
    perform_abc_analysis,
    reslot_skus,
)


def test_perform_abc_analysis():
    df_synth = generate_synthetic_orderlines(n_lines=150, n_orders=30, n_skus=20, seed=42)
    df_classified, df_summary = perform_abc_analysis(df_synth)

    assert 'ABC_Class' in df_classified.columns
    assert set(df_classified['ABC_Class'].unique()).issubset({'A', 'B', 'C'})
    assert len(df_summary) == 3


def test_reslot_skus():
    df_synth = generate_synthetic_orderlines(n_lines=100, n_orders=20, n_skus=15, seed=42)
    df_reslotted = reslot_skus(df_synth, y_low=5.5, y_high=50.0)

    assert len(df_reslotted) == len(df_synth)
    assert 'x' in df_reslotted.columns
    assert 'y' in df_reslotted.columns


def test_evaluate_slotting_impact():
    df_synth = generate_synthetic_orderlines(n_lines=80, n_orders=15, n_skus=10, seed=42)
    df_compounding = evaluate_slotting_impact(df_synth, wave_size=2, distance_threshold=35.0)

    assert isinstance(df_compounding, pd.DataFrame)
    assert len(df_compounding) == 4
    assert 'Walking Distance (m)' in df_compounding.columns


def test_evaluate_slotting_heuristics_interplay():
    df_synth = generate_synthetic_orderlines(n_lines=60, n_orders=10, n_skus=8, seed=42)
    df_interplay = evaluate_slotting_heuristics_interplay(df_synth)

    assert isinstance(df_interplay, pd.DataFrame)
    assert len(df_interplay) == 3
    assert 'Re-slotting Gain (%)' in df_interplay.columns
