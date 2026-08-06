'''Financial and Operations Cost Model layer for warehouse picking route optimization:
Translates physical walking distance (meters) into workforce time, financial costs (₹),
daily savings, and additional order capacity.
'''


def calculate_picking_costs(
    total_distance_m: float,
    walking_speed_mps: float = 1.2,
    hourly_wage_inr: float = 250.0,
    shift_hours: float = 8.0,
    num_pickers: int = 10,
    seconds_per_line: float = 15.0,
) -> dict:
    '''Calculate time, labor costs, and capacity metrics for a given walking distance.'''
    if walking_speed_mps <= 0:
        raise ValueError("Walking speed must be greater than zero.")

    walking_time_seconds = total_distance_m / walking_speed_mps
    walking_time_hours = walking_time_seconds / 3600.0
    walking_cost_inr = walking_time_hours * hourly_wage_inr

    return {
        'total_distance_m': round(total_distance_m, 2),
        'walking_time_seconds': round(walking_time_seconds, 2),
        'walking_time_hours': round(walking_time_hours, 2),
        'walking_cost_inr': round(walking_cost_inr, 2),
    }


def compare_financial_savings(
    baseline_distance_m: float,
    optimized_distance_m: float,
    walking_speed_mps: float = 1.2,
    hourly_wage_inr: float = 250.0,
    shift_hours: float = 8.0,
    num_pickers: int = 10,
    seconds_per_line: float = 15.0,
    operating_days_per_year: int = 300,
) -> dict:
    '''Compare baseline vs optimized metrics to calculate financial savings (₹) and shift capacity gains.'''
    base_metrics = calculate_picking_costs(
        baseline_distance_m, walking_speed_mps, hourly_wage_inr, shift_hours, num_pickers, seconds_per_line
    )
    opt_metrics = calculate_picking_costs(
        optimized_distance_m, walking_speed_mps, hourly_wage_inr, shift_hours, num_pickers, seconds_per_line
    )

    distance_saved_m = max(0.0, baseline_distance_m - optimized_distance_m)
    distance_saved_pct = (distance_saved_m / baseline_distance_m * 100.0) if baseline_distance_m > 0 else 0.0

    hours_saved_single = (base_metrics['walking_time_hours'] - opt_metrics['walking_time_hours'])
    hours_saved_total = hours_saved_single * num_pickers

    daily_cost_saved_inr = hours_saved_total * hourly_wage_inr
    annual_cost_saved_inr = daily_cost_saved_inr * operating_days_per_year

    seconds_saved_total = hours_saved_total * 3600.0
    extra_lines_per_shift = int(seconds_saved_total / seconds_per_line) if seconds_per_line > 0 else 0

    return {
        'baseline_distance_m': round(baseline_distance_m, 2),
        'optimized_distance_m': round(optimized_distance_m, 2),
        'distance_saved_m': round(distance_saved_m, 2),
        'distance_saved_pct': round(distance_saved_pct, 2),
        'baseline_cost_inr': round(base_metrics['walking_cost_inr'] * num_pickers, 2),
        'optimized_cost_inr': round(opt_metrics['walking_cost_inr'] * num_pickers, 2),
        'daily_cost_saved_inr': round(daily_cost_saved_inr, 2),
        'annual_cost_saved_inr': round(annual_cost_saved_inr, 2),
        'hours_saved_per_shift': round(hours_saved_total, 2),
        'extra_lines_per_shift': extra_lines_per_shift,
    }
