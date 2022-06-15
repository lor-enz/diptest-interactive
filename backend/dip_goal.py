from random import randrange
import diptest.diptest as dt
import numpy as np

def all_dip_calculations(data, is_data_sorted):
    """
    Almost same function as diptest.dip_test (I want to leave the diptest files as is)
    Modified to get everything in one go: dip_value, pval, modal_triangle, low_high 
    """
    n_points = data.shape[0]
    dip_value, low_high, modal_triangle = dt.dip(
        data, just_dip=False, is_data_sorted=is_data_sorted, use_c=True, debug=False)
    pval = dt.dip_pval(dip_value, n_points, dt.PVAL_BY_TABLE, 2000)
    return dip_value, pval, modal_triangle, low_high


def split_at(index, column):
    left = column[:index]  # From Beginning to (excluding) index
    right = column[index:]  # From (including) index to End
    return left, right


def histogram_and_cdf(unsorted_column, bins=15):
    # np.histogram([1, 2, 1, 3, 3, 5, 1, 2, 4, 1, 5], bins=5) = [4, 2, 2, 1, 2]
    # TODO choose smart values for bins or range and so on
    # https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    histo, bins = np.histogram(unsorted_column, bins=bins)
    cdf = create_cdf(histo)
    return cdf, histo, bins

def create_cdf(histo):
    sum = 0
    cdf = []
    for el in histo:
        sum += el
        cdf.append(sum)
    return cdf

def goal_function_for(sorted_cdf):
    margin = 4 # >= 4 because that's what the diptest accepts
    # Initial value only matters for b_score
    b_score = 999  # we want: min
    b_pval_left = 0
    b_pval_right = 0
    b_index = -1
    _, pval_all, _, _ = all_dip_calculations(sorted_cdf, True)
    length = len(sorted_cdf)
    
    if len(sorted_cdf) < 3 + margin * 2:
        print(
            f"CDF array too short {len(sorted_cdf)} < {2 + margin * 2}")
        # logger.error(f"CDF array too short {len(sorted_cdf)} < {2 + margin * 2}")
        return -1, -1, -1, -1, -1

    log = "Goal function: "

    for i in range(margin, len(sorted_cdf)-(margin)):
        left, right = split_at(i, sorted_cdf)
        _, pval_left, _, _ = all_dip_calculations(left, True)
        _, pval_right, _, _ = all_dip_calculations(right, True)
        score = - pval_all + pval_left + pval_right
        # print(f"Calcuated score at split {i} is {score}. Current best score is {b_score} at split {b_index} ")
        if score < b_score:
            b_score = score
            b_pval_left = pval_left
            b_pval_right = pval_right
            b_index = i
        assert length == len(sorted_cdf)
    log += f" Best results sc:{round(b_score,3)} in:{round(b_index,3)} dip_all:{round(pval_all,3)} pval_l:{round(b_pval_left,3)} pval_r:{round(b_pval_right,3)}"
    # logger.info(log)
    # print(log)
    return b_score, b_index, pval_all, b_pval_left, b_pval_right


histogram_and_cdf([1, 2, 1, 3, 3, 5, 1, 2, 4, 1, 5], 5)