import diptest.diptest as dt

def all_dip_calculations(data, is_data_sorted):
    """
    Almost same function as diptest.dip_test (I want to leave the diptest files as is)
    Modified to get everything in one go: dip_value, pval, modal_triangle, low_high 
    """
    n_points = data.shape[0]
    dip_value, low_high, modal_triangle = dt.dip(
        data, just_dip=False, is_data_sorted=is_data_sorted, debug=False)
    pval = dt.dip_pval(dip_value, n_points, dt.PVAL_BY_TABLE, 2000)
    return dip_value, pval, modal_triangle, low_high
