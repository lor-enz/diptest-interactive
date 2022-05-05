from random import randrange
import diptest.diptest as dt
import numpy as np

# # # # # # # # # # # # # # # # # # # # # # 
# rafodi = RAndom FOrest with DIp-test    #
# # # # # # # # # # # # # # # # # # # # # # 

def split_at(index, column):
    left = column[:index]  # From Beginning to (excluding) index
    right = column[index:]  # From (including) index to End
    return left, right


def goal_function_for(sorted_numpy_column):
    margin = 5
    if len(sorted_numpy_column) < 2 + margin * 2:
        print(
            f"CDF array too short {len(sorted_numpy_column)} < {2 + margin * 2}")
        # logger.error(f"CDF array too short {len(sorted_numpy_column)} < {2 + margin * 2}")
        return -1, -1, -1, -1, -1

    log = "Goal function..."

    b_score = -999  # we want: max
    b_dip_left = 999  # we want: min
    b_dip_right = 999  # we want: min
    b_index = -1
    dip_all = dt.dip(sorted_numpy_column)
    length = len(sorted_numpy_column)

    for i in range(2+margin, len(sorted_numpy_column)-(1+margin)):
        left, right = split_at(i, sorted_numpy_column)
        dip_left = dt.dip(left)
        dip_right = dt.dip(right)
        score = dip_all + dip_left + dip_right # we want to maximize this!
        # print(f"Calcuated score at split {i} is {score}. Current best score is {b_score} at split {b_index} ")
        if score > b_score:
            b_score = score
            b_dip_left = dip_left
            b_dip_right = dip_right
            b_index = i
        assert length == len(sorted_numpy_column)
    log += f" Best results sc:{round(b_score,3)} in:{round(b_index,3)} dip_app:{round(dip_all,3)} dip_l:{round(b_dip_left,3)} dip_r:{round(b_dip_right,3)}"
    # logger.info(log)
    return b_score, b_index, dip_all, b_dip_left, b_dip_right


# Create child splits for a node or make terminal
def split(node, max_depth, min_size, n_features, depth):
    left, right = node['groups']
    del (node['groups'])
    # check for a no split
    if not left or not right:
        node['left'] = node['right'] = to_terminal(left + right)
        return
    # check for max depth
    if depth >= max_depth:
        node['left'], node['right'] = to_terminal(left), to_terminal(right)
        return
    # process left child
    if len(left) <= min_size:
        node['left'] = to_terminal(left)
    else:
        node['left'] = get_split(left, n_features)
        split(node['left'], max_depth, min_size, n_features, depth + 1)
    # process right child
    if len(right) <= min_size:
        node['right'] = to_terminal(right)
    else:
        node['right'] = get_split(right, n_features)
        split(node['right'], max_depth, min_size, n_features, depth + 1)


# Create a terminal node value
def to_terminal(group):
    # print(f"to_terminal {group}")
    outcomes = [row[-1] for row in group]
    return max(set(outcomes), key=outcomes.count)


# Is this tested? Does it work?
def get_split(dataset, n_features, is_dataset_numpy=False):
    """ For the given dataset the best split point is chosen using the gini index.
    """
    if not is_dataset_numpy:
        dataset = np.array(dataset)
    class_values = list(set(row[-1] for row in dataset))  # last column of
    b_index = 999  # column
    b_value = 999  # value = row[index]
    b_score = 0  # dip value
    b_groups = None  # left and right group
    features = list()
    while len(features) < n_features:
        index = randrange(len(dataset[0]) - 1)
        if index not in features:
            features.append(index)
    for index in features:
        column = dataset.T[index]
        dip_value = dt.dip(np.array(column), is_data_sorted=False)
        if dip_value > b_score:
            # b_index = index
            # b_value = row[index]
            b_score = dip_value
            # b_groups = groups
    return {'index': b_index, 'value': b_value, 'groups': b_groups}


# Build a decision tree
def build_tree(train, max_depth, min_size, n_features):
    # print(f"build_tree {train} {max_depth} {min_size} {n_features}")
    root = get_split(train, n_features)
    split(root, max_depth, min_size, n_features, 1)
    return root
