import itertools
from ast import literal_eval

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, ward
from scipy.spatial.distance import pdist

from utils.routing.distances import distance_picking_cluster


def cluster_locations(list_coord, distance_threshold, dist_method, clust_start):
    ''' Step 1: Create clusters of locations'''
    if dist_method == 'euclidian':
        Z = ward(pdist(np.stack(list_coord)))
    else:
        Z = ward(pdist(np.stack(list_coord), metric=distance_picking_cluster))
    fclust1 = fcluster(Z, t=distance_threshold, criterion='distance')
    return fclust1


def clustering_mapping(df, distance_threshold, dist_method, orders_number, wave_start, clust_start, df_type):
    '''Step 2: Clustering and mapping'''
    if df.empty:
        df['OrderID'] = pd.Series(dtype=int)
        df['WaveID'] = pd.Series(dtype=int)
        df['ClusterID'] = pd.Series(dtype=int)
        return {}, {}, df, wave_start, clust_start

    list_coord, list_OrderNumber, clust_id, df = cluster_wave(
        df, distance_threshold, 'custom', clust_start, df_type
    )
    if len(clust_id) == 0:
        df['OrderID'] = pd.Series(dtype=int)
        df['WaveID'] = pd.Series(dtype=int)
        df['ClusterID'] = pd.Series(dtype=int)
        return {}, {}, df, wave_start, clust_start

    clust_idmax = max(clust_id)
    dict_map, dict_omap, df, Wave_max = lines_mapping_clst(
        df, list_coord, list_OrderNumber, clust_id, orders_number, wave_start
    )
    return dict_map, dict_omap, df, Wave_max, clust_idmax


def cluster_wave(df, distance_threshold, dist_method, clust_start, df_type):
    '''Step 3: Create waves by clusters'''
    if df_type == 'df_mono':
        df['Coord_Cluster'] = df['Coord']
    if df.empty:
        return np.array([]), np.array([]), [], df

    df_map = pd.DataFrame(df.groupby(['OrderNumber', 'Coord_Cluster'])['SKU'].count()).reset_index()
    if df_map.empty:
        return np.array([]), np.array([]), [], df

    parsed_coords = [literal_eval(t) for t in df_map.Coord_Cluster.values]
    if not parsed_coords:
        return np.array([]), np.array([]), [], df

    list_coord, list_OrderNumber = np.stack(parsed_coords), df_map.OrderNumber.values
    clust_id = cluster_locations(list_coord, distance_threshold, dist_method, clust_start)
    clust_id = [(i + clust_start) for i in clust_id]
    list_coord = np.stack(list_coord)
    return list_coord, list_OrderNumber, clust_id, df


def lines_mapping(df, orders_number, wave_start):
    '''Step 4: Mapping Order lines mapping without clustering '''
    if df.empty:
        df['OrderID'] = pd.Series(dtype=int)
        df['WaveID'] = pd.Series(dtype=int)
        return df, wave_start

    list_orders = df.OrderNumber.unique()
    dict_map = dict(zip(list_orders, range(1, len(list_orders) + 1), strict=False))
    df['OrderID'] = df['OrderNumber'].map(dict_map)
    df['WaveID'] = (df.OrderID % orders_number == 0).shift(1).fillna(0).cumsum() + wave_start
    waves_number = int(df.WaveID.max() + 1) if pd.notna(df.WaveID.max()) else wave_start
    return df, waves_number


def lines_mapping_clst(df, list_coord, list_OrderNumber, clust_id, orders_number, wave_start):
    '''Step 4: Mapping Order lines mapping with clustering '''
    if df.empty or len(list_OrderNumber) == 0:
        df['OrderID'] = pd.Series(dtype=int)
        df['WaveID'] = pd.Series(dtype=int)
        df['ClusterID'] = pd.Series(dtype=int)
        return {}, {}, df, wave_start

    dict_map = dict(zip(list_OrderNumber, clust_id, strict=False))
    df['ClusterID'] = df['OrderNumber'].map(dict_map)
    df = df.sort_values(['ClusterID', 'OrderNumber'], ascending=True)
    list_orders = list(df.OrderNumber.unique())

    dict_omap = dict(zip(list_orders, range(1, len(list_orders) + 1), strict=False))
    df['OrderID'] = df['OrderNumber'].map(dict_omap)
    df['WaveID'] = wave_start + (
        (df.OrderID % orders_number == 0) | (df.ClusterID.diff() != 0)
    ).shift(1).fillna(0).cumsum()

    wave_max = int(df.WaveID.max()) if pd.notna(df.WaveID.max()) else wave_start
    return dict_map, dict_omap, df, wave_max


def locations_listing(df_orderlines, wave_id):
    ''' Step 5: Listing location per Wave of orders'''
    df = df_orderlines[df_orderlines.WaveID == wave_id]
    list_coord = list(df['Coord'].apply(literal_eval).values)
    list_coord.sort()
    list_coord = [k for k, _ in itertools.groupby(list_coord)]
    n_locs = len(list_coord)
    n_lines = len(df)
    n_pcs = df.PCS.sum()

    return list_coord, n_locs, n_lines, n_pcs
