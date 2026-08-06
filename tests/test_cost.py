'''Unit tests for financial and operations cost model.'''

import pytest

from utils.cost.cost_model import calculate_picking_costs, compare_financial_savings


def test_calculate_picking_costs():
    res = calculate_picking_costs(1200.0, walking_speed_mps=1.2, hourly_wage_inr=250.0)
    assert res['total_distance_m'] == 1200.0
    assert res['walking_time_seconds'] == 1000.0
    assert res['walking_time_hours'] == round(1000.0 / 3600, 2)
    assert res['walking_cost_inr'] > 0


def test_calculate_picking_costs_invalid():
    with pytest.raises(ValueError):
        calculate_picking_costs(1000.0, walking_speed_mps=0.0)


def test_compare_financial_savings():
    res = compare_financial_savings(
        baseline_distance_m=10000.0,
        optimized_distance_m=4000.0,
        walking_speed_mps=1.2,
        hourly_wage_inr=250.0,
        shift_hours=8.0,
        num_pickers=10,
        seconds_per_line=15.0,
    )
    assert res['distance_saved_m'] == 6000.0
    assert res['distance_saved_pct'] == 60.0
    assert res['daily_cost_saved_inr'] > 0
    assert res['annual_cost_saved_inr'] > res['daily_cost_saved_inr']
    assert res['extra_lines_per_shift'] > 0
