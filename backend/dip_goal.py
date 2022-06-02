from random import randrange
import diptest.diptest as dt
import numpy as np

def all_dip_calculations(data, is_data_sorted=True):
    """
    Almost same function as diptest.dip_test
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


def goal_function_for(sorted_numpy_column):
    margin = 4
    # Initial value only matters for b_score
    b_score = 999  # we want: min
    b_pval_left = 0
    b_pval_right = 0
    b_index = -1
    _, pval_all, _, _ = all_dip_calculations(sorted_numpy_column)
    length = len(sorted_numpy_column)
    
    if len(sorted_numpy_column) < 3 + margin * 2:
        print(
            f"CDF array too short {len(sorted_numpy_column)} < {2 + margin * 2}")
        # logger.error(f"CDF array too short {len(sorted_numpy_column)} < {2 + margin * 2}")
        return -1, -1, -1, -1, -1

    log = "Goal function: "

    for i in range(margin, len(sorted_numpy_column)-(margin)):
        left, right = split_at(i, sorted_numpy_column)
        _, pval_left, _, _ = all_dip_calculations(left)
        _, pval_right, _, _ = all_dip_calculations(right)
        score = - pval_all + pval_left + pval_right
        # print(f"Calcuated score at split {i} is {score}. Current best score is {b_score} at split {b_index} ")
        if score < b_score:
            b_score = score
            b_pval_left = pval_left
            b_pval_right = pval_right
            b_index = i
        assert length == len(sorted_numpy_column)
    log += f" Best results sc:{round(b_score,3)} in:{round(b_index,3)} dip_all:{round(pval_all,3)} pval_l:{round(b_pval_left,3)} pval_r:{round(b_pval_right,3)}"
    # logger.info(log)
    print(log)
    return b_score, b_index, pval_all, b_pval_left, b_pval_right
