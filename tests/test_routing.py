'''Unit tests for warehouse picking route heuristics.'''

import pytest

from utils.routing.heuristics import (
    benchmark_routing_heuristics,
    route_next_closest,
    route_return,
    route_s_shape,
)


@pytest.fixture
def sample_locations():
    # 2D coordinates [(x, y)] in warehouse layout
    return [[10.0, 15.0], [10.0, 40.0], [25.0, 20.0], [25.0, 45.0]]


def test_route_next_closest(sample_locations):
    origin = [0, 5.5]
    dist, route = route_next_closest(origin, sample_locations, 5.5, 50.0)
    assert dist > 0
    assert len(route) == len(sample_locations) + 2  # origin + locs + origin
    assert route[0] == origin
    assert route[-1] == origin


def test_route_s_shape(sample_locations):
    origin = [0, 5.5]
    dist, route = route_s_shape(origin, sample_locations, 5.5, 50.0)
    assert dist > 0
    assert route[0] == origin
    assert route[-1] == origin


def test_route_return(sample_locations):
    origin = [0, 5.5]
    dist, route = route_return(origin, sample_locations, 5.5, 50.0)
    assert dist > 0
    assert route[0] == origin
    assert route[-1] == origin


def test_benchmark_routing_heuristics(sample_locations):
    origin = [0, 5.5]
    results = benchmark_routing_heuristics(origin, sample_locations, 5.5, 50.0)
    assert 'Next Closest' in results
    assert 'S-Shape' in results
    assert 'Return' in results
    assert results['Next Closest']['distance'] > 0
    assert results['S-Shape']['distance'] > 0
    assert results['Return']['distance'] > 0
