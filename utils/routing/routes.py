from utils.routing.distances import distance_picking, next_location


def create_picking_route(origin_loc, list_locs, y_low, y_high):
    '''Calculate total distance to cover for a list of locations'''
    wave_distance = 0
    start_loc = origin_loc
    list_chemin = [start_loc]

    while len(list_locs) > 0:
        list_locs, start_loc, next_loc, distance_next = next_location(start_loc, list_locs, y_low, y_high)
        start_loc = next_loc
        list_chemin.append(start_loc)
        wave_distance += distance_next

    wave_distance += distance_picking(start_loc, origin_loc, y_low, y_high)
    list_chemin.append(origin_loc)
    return wave_distance, list_chemin


def create_picking_route_cluster(origin_loc, list_locs, y_low, y_high):
    '''Calculate total distance to cover for a list of locations (cluster version).'''
    wave_distance = 0
    distance_max = 0
    start_loc = origin_loc
    list_chemin = [start_loc]

    while len(list_locs) > 0:
        list_locs, start_loc, next_loc, distance_next = next_location(start_loc, list_locs, y_low, y_high)
        start_loc = next_loc
        list_chemin.append(start_loc)
        if distance_next > distance_max:
            distance_max = distance_next
        wave_distance += distance_next

    wave_distance += distance_picking(start_loc, origin_loc, y_low, y_high)
    list_chemin.append(origin_loc)
    return wave_distance, list_chemin, distance_max
