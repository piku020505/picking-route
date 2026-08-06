import itertools

import pandas as pd

from utils.batch.mapping_batch import df_mapping_batch
from utils.routing.routes import create_picking_route


def simulation_batch(n1, n2, y_low, y_high, origin_loc, lines_number, df_orderlines):
    '''Simulate picking distance for each wave size between n1 and n2.'''
    list_wid, list_dst, list_route, list_ord = [], [], [], []

    for orders_number in range(n1, n2):
        df_orderlines, waves_number = df_mapping_batch(df_orderlines, orders_number)
        distance_route = 0

        for wave_id in range(waves_number):
            df_wave = df_orderlines[df_orderlines.WaveID == wave_id]
            list_locs = list(df_wave['Coord'].apply(eval).values)
            list_locs.sort()
            list_locs = [k for k, _ in itertools.groupby(list_locs)]

            wave_distance, list_chemin = create_picking_route(origin_loc, list_locs, y_low, y_high)
            distance_route += wave_distance

            list_wid.append(wave_id)
            list_dst.append(wave_distance)
            list_route.append(list_chemin)
            list_ord.append(orders_number)

    df_waves = pd.DataFrame({
        'wave': list_wid,
        'distance': list_dst,
        'routes': list_route,
        'order_per_wave': list_ord,
    })

    df_results = pd.DataFrame(df_waves.groupby(['order_per_wave'])['distance'].sum())
    df_results.columns = ['distance']
    return df_waves, df_results.reset_index()
