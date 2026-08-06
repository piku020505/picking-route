import itertools
from ast import literal_eval


def df_mapping_batch(df_orderlines, orders_number):
    '''Mapping of orderlines with wave numbers'''
    list_orders = df_orderlines.OrderNumber.unique()
    dict_map = dict(zip(list_orders, range(1, len(list_orders) + 1), strict=False))
    df_orderlines['OrderID'] = df_orderlines['OrderNumber'].map(dict_map)
    df_orderlines['WaveID'] = (df_orderlines.OrderID % orders_number == 0).shift(1).fillna(0).cumsum()
    waves_number = int(df_orderlines.WaveID.max() + 1)
    return df_orderlines, waves_number


def locations_listing(df_orderlines, wave_id):
    '''Getting storage locations to cover for a wave of orders'''
    df = df_orderlines[df_orderlines.WaveID == wave_id]
    list_locs = list(df['Coord'].apply(literal_eval).values)
    list_locs.sort()
    list_locs = [k for k, _ in itertools.groupby(list_locs)]
    n_locs = len(list_locs)
    return list_locs, n_locs
