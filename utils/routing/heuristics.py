'''Routing heuristics module for warehouse order picking routes:
1. Next Closest Location (Greedy / Nearest Neighbor)
2. S-Shape (Serpentine) Routing
3. Return Routing
'''

from collections import defaultdict

from utils.routing.distances import distance_picking


def route_next_closest(origin_loc, list_locs, y_low, y_high):
    '''Next Closest Location (Greedy / Nearest Neighbor) heuristic.'''
    if not list_locs:
        return 0, [origin_loc, origin_loc]

    locs = list_locs.copy()
    current_loc = origin_loc
    route = [current_loc]
    total_distance = 0

    while locs:
        distances = [distance_picking(current_loc, loc, y_low, y_high) for loc in locs]
        min_dist = min(distances)
        min_idx = distances.index(min_dist)
        next_loc = locs.pop(min_idx)

        total_distance += min_dist
        current_loc = next_loc
        route.append(current_loc)

    total_distance += distance_picking(current_loc, origin_loc, y_low, y_high)
    route.append(origin_loc)
    return total_distance, route


def route_s_shape(origin_loc, list_locs, y_low, y_high):
    '''S-Shape (Serpentine) Routing heuristic.'''
    if not list_locs:
        return 0, [origin_loc, origin_loc]

    # Group locations by aisle (x-coordinate)
    aisle_map = defaultdict(list)
    for loc in list_locs:
        aisle_map[loc[0]].append(loc[1])

    sorted_aisles = sorted(aisle_map.keys())
    current_x, current_y = origin_loc[0], origin_loc[1]
    total_distance = 0
    route = [[current_x, current_y]]

    num_aisles = len(sorted_aisles)
    for idx, aisle_x in enumerate(sorted_aisles):
        y_coords = sorted(aisle_map[aisle_x])
        is_last_aisle = (idx == num_aisles - 1)

        # Move to aisle_x along cross-aisle
        dist_x = abs(aisle_x - current_x)
        total_distance += dist_x
        current_x = aisle_x
        route.append([current_x, current_y])

        # Current side: bottom (y_low) vs top (y_high)
        is_at_bottom = abs(current_y - y_low) <= abs(current_y - y_high)

        if is_at_bottom:
            if is_last_aisle:
                # Last aisle: option to return to bottom vs traverse to top
                max_y = max(y_coords)
                dist_up_and_back = (max_y - y_low) * 2
                dist_full_traverse = (y_high - y_low)

                if dist_up_and_back < dist_full_traverse:
                    for y in y_coords:
                        route.append([current_x, y])
                    route.append([current_x, y_low])
                    total_distance += dist_up_and_back
                    current_y = y_low
                else:
                    for y in y_coords:
                        route.append([current_x, y])
                    route.append([current_x, y_high])
                    total_distance += (y_high - y_low)
                    current_y = y_high
            else:
                # Traverse completely from bottom to top
                for y in y_coords:
                    route.append([current_x, y])
                route.append([current_x, y_high])
                total_distance += (y_high - y_low)
                current_y = y_high
        else:
            if is_last_aisle:
                min_y = min(y_coords)
                dist_down_and_back = (y_high - min_y) * 2
                dist_full_traverse = (y_high - y_low)

                if dist_down_and_back < dist_full_traverse:
                    for y in reversed(y_coords):
                        route.append([current_x, y])
                    route.append([current_x, y_high])
                    total_distance += dist_down_and_back
                    current_y = y_high
                else:
                    for y in reversed(y_coords):
                        route.append([current_x, y])
                    route.append([current_x, y_low])
                    total_distance += (y_high - y_low)
                    current_y = y_low
            else:
                # Traverse completely from top to bottom
                for y in reversed(y_coords):
                    route.append([current_x, y])
                route.append([current_x, y_low])
                total_distance += (y_high - y_low)
                current_y = y_low

    # Return to depot from final location
    final_dist = abs(current_x - origin_loc[0]) + abs(current_y - origin_loc[1])
    total_distance += final_dist
    route.append(origin_loc)

    return int(total_distance), route


def route_return(origin_loc, list_locs, y_low, y_high):
    '''Return Routing heuristic.'''
    if not list_locs:
        return 0, [origin_loc, origin_loc]

    aisle_map = defaultdict(list)
    for loc in list_locs:
        aisle_map[loc[0]].append(loc[1])

    sorted_aisles = sorted(aisle_map.keys())
    current_x, current_y = origin_loc[0], origin_loc[1]
    total_distance = 0
    route = [[current_x, current_y]]

    for aisle_x in sorted_aisles:
        y_coords = sorted(aisle_map[aisle_x])
        max_y = max(y_coords)

        # Move along bottom cross-aisle to aisle_x
        dist_x = abs(aisle_x - current_x)
        total_distance += dist_x
        current_x = aisle_x
        route.append([current_x, y_low])

        # Enter aisle up to max_y and return to y_low
        for y in y_coords:
            route.append([current_x, y])

        dist_up_and_back = (max_y - y_low) * 2
        total_distance += dist_up_and_back
        route.append([current_x, y_low])
        current_y = y_low

    # Return to depot along bottom cross-aisle
    dist_back_origin = abs(current_x - origin_loc[0]) + abs(current_y - origin_loc[1])
    total_distance += dist_back_origin
    route.append(origin_loc)

    return int(total_distance), route


def benchmark_routing_heuristics(origin_loc, list_locs, y_low, y_high):
    '''Benchmark all three heuristics on a set of picking locations.'''
    dist_greedy, route_greedy = route_next_closest(origin_loc, list_locs, y_low, y_high)
    dist_sshape, route_sshape = route_s_shape(origin_loc, list_locs, y_low, y_high)
    dist_return, route_return_path = route_return(origin_loc, list_locs, y_low, y_high)

    results = {
        'Next Closest': {'distance': dist_greedy, 'route': route_greedy},
        'S-Shape': {'distance': dist_sshape, 'route': route_sshape},
        'Return': {'distance': dist_return, 'route': route_return_path},
    }
    return results
