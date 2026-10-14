import numpy as np
import data_prep
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


def typical_sample_pvals(histo, n, repetitions=100, alpha=0.05):
    """
    The ideal sample has no sampling noise, so its p-value is not what a real sample of n
    points from the drawn shape would get. This draws `repetitions` random samples of n
    from the shape and returns the median of their p-values and the share of samples
    with p < alpha (the test's power at that level). Seeded, so the same drawing and n
    always give the same answer.
    """
    rng = np.random.default_rng(0)
    pvals = np.array([
        dt.dip_pval(dt.dip(data_prep.random_samples_from_histo(histo, n, rng), is_data_sorted=True), n)
        for _ in range(repetitions)])
    return float(np.median(pvals)), float(np.mean(pvals < alpha))
