from utils.cluster.clustering import clustering_mapping, lines_mapping
from utils.process.processing import monomult_concat, process_lines
from utils.routing.distances import centroid_mapping


def df_mapping(df_orderlines, orders_number, distance_threshold, mono_method, multi_method):
    ''' Mapping Order lines Dataframe using clustering'''
    df_mono, df_multi = process_lines(df_orderlines)
    wave_start = 0
    clust_start = 0

    if mono_method == 'clustering':
        df_type = 'df_mono'
        dict_map, dict_omap, df_mono, waves_number, clust_idmax = clustering_mapping(
            df_mono, distance_threshold, 'custom', orders_number, wave_start, clust_start, df_type
        )
    else:
        df_mono, waves_number = lines_mapping(df_mono, orders_number, 0)
        clust_idmax = 0

    wave_start = waves_number
    clust_start = clust_idmax

    if multi_method == 'clustering':
        df_type = 'df_multi'
        df_multi = centroid_mapping(df_multi)
        dict_map, dict_omap, df_multi, waves_number, clust_idmax = clustering_mapping(
            df_multi, distance_threshold, 'custom', orders_number, wave_start, clust_start, df_type
        )
    else:
        df_multi, waves_number = lines_mapping(df_multi, orders_number, wave_start)

    df_orderlines, waves_number = monomult_concat(df_mono, df_multi)
    return df_orderlines, waves_number
