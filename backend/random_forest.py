from random import randrange
from random import seed
import numpy as np
from csv import reader
from math import sqrt
import dip_goal as dg

# # # # # # # # # # # # # # # # # 
#          random forest        #
# # # # # # # # # # # # # # # # # 

# Load a CSV file
def load_csv(filename):
    dataset = list()
    with open(filename, 'r') as file:
        csv_reader = reader(file)
        for row in csv_reader:
            if not row:
                continue
            dataset.append(row)
    return dataset
    
# Convert string column to float
def str_column_to_float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())

# Convert string column to integer
def str_column_to_int(dataset, column):
    class_values = [row[column] for row in dataset]
    unique = set(class_values)
    lookup = dict()
    for i, value in enumerate(unique):
        lookup[value] = i
    for row in dataset:
        row[column] = lookup[row[column]]
    return lookup

def split_at(index, column):
    left = column[:index]  # From Beginning to (excluding) index
    right = column[index:]  # From (including) index to End
    return left, right

# Create child splits for a node or make terminal
def split(node, max_depth, min_size, n_features, depth, use_dip):
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
        node['left'] = get_split_wrapper(left, n_features, use_dip)
        split(node['left'], max_depth, min_size, n_features, depth + 1, use_dip)
    # process right child
    if len(right) <= min_size:
        node['right'] = to_terminal(right)
    else:
        node['right'] = get_split_wrapper(right, n_features, use_dip)
        split(node['right'], max_depth, min_size, n_features, depth + 1, use_dip)


# Create a terminal node value
def to_terminal(group):
    # print(f"to_terminal {group}")
    outcomes = [row[-1] for row in group]
    return max(set(outcomes), key=outcomes.count)


def get_split_wrapper(dataset, n_features, use_dip):
    if use_dip:
        return get_split_dip(dataset, n_features)
    else:
        return get_split_gini(dataset, n_features)

# Select the best split point for a dataset
def get_split_gini(dataset, n_features):
    class_values = list(set(row[-1] for row in dataset))
    b_index, b_value, b_score, b_groups = 999, 999, 999, None
    features = list()
    while len(features) < n_features:
        index = randrange(len(dataset[0])-1)
        if index not in features:
            features.append(index)
    for index in features:
        for row in dataset:
            ''' test_split splits left and right based on the value: row[index] '''
            groups = test_split(index, row[index], dataset) 
            gini = gini_index(groups, class_values)
            if gini < b_score:
                b_index, b_value, b_score, b_groups = index, row[index], gini, groups
    # index: where in the dataset did we just decide to split?
    # value: what's the value at position index in dataset?
    # groups: left and right based on the value: row[index] 
    return {'index':b_index, 'value':b_value, 'groups':b_groups}


# 
def get_split_dip(dataset, n_features, is_dataset_numpy=False):
    if not is_dataset_numpy:
        dataset = np.array(dataset)
    b_score = 999 # lower is better, so we start with something big to be overwritten
    b_split = 999
    b_features_index = 999
    features = list()
    while len(features) < n_features:
        index = randrange(len(dataset[0]) - 1)
        if index not in features:
            features.append(index)
    for features_index in features:
        current_feature = dataset[:,features_index]
        cdf, histo, bins = dg.histogram_and_cdf(current_feature)
        new_score, goal_split, _, _, _ = dg.goal_function_for(np.array(cdf))
        if new_score < b_score:
            b_score = new_score
            b_split = goal_split
            b_features_index = features_index
    splitbin = bins[goal_split]
    groups = test_split(b_features_index, splitbin, dataset) 
    left, right = groups
    return {'index': features_index, 'value': splitbin, 'groups': groups}

# Split a dataset based on an attribute and an attribute value
def test_split(index, value, dataset):
    left, right = list(), list()
    for row in dataset:
        if row[index] < value:
            left.append(row)
        else:
            right.append(row)
    return left, right


# Calculate the Gini index for a split dataset
def gini_index(groups, classes):
    # count all samples at split point
    n_instances = float(sum([len(group) for group in groups]))
    # sum weighted Gini index for each group
    gini = 0.0
    for group in groups:
        size = float(len(group))
        # avoid divide by zero
        if size == 0:
            continue
        score = 0.0
        # score the group based on the score for each class
        for class_val in classes:
            p = [row[-1] for row in group].count(class_val) / size
            score += p * p
        # weight the group score by its relative size
        gini += (1.0 - score) * (size / n_instances)
    return gini


# Build a decision tree
def build_tree(train, max_depth, min_size, n_features, use_dip):
    # print(f"build_tree {train} {max_depth} {min_size} {n_features}")
    root = get_split_wrapper(train, n_features, use_dip)
    split(root, max_depth, min_size, n_features, 1, use_dip)
    return root

# Random Forest Algorithm
def random_forest_gini(train, test, max_depth, min_size, sample_size, n_trees, n_features):
    trees = list()
    for _ in range(n_trees):
        sample = subsample(train, sample_size)
        tree = build_tree(sample, max_depth, min_size, n_features, use_dip=False)
        trees.append(tree)
    predictions = [bagging_predict(trees, row) for row in test]
    return(predictions)

# Random Forest Algorithm with my own dip based goal function
def random_forest_dip(train, test, max_depth, min_size, sample_size, n_trees, n_features):
    trees = list()
    for _ in range(n_trees):
        sample = subsample(train, sample_size)
        tree = build_tree(sample, max_depth, min_size, n_features, use_dip=True)
        trees.append(tree)
    print ("trees created")
    predictions = [bagging_predict(trees, row) for row in test]
    return(predictions)

# Create a random subsample from the dataset with replacement
def subsample(dataset, ratio):
    sample = list()
    n_sample = round(len(dataset) * ratio)
    while len(sample) < n_sample:
        index = randrange(len(dataset))
        sample.append(dataset[index])
    return sample

def predict(node, row):
    if row[node['index']] < node['value']:
        if isinstance(node['left'], dict):
            return predict(node['left'], row)
        else:
            return node['left']
    else:
        if isinstance(node['right'], dict):
            return predict(node['right'], row)
        else:
            return node['right']

# Calculate accuracy percentage
def accuracy_metric(actual, predicted):
    correct = 0
    for i in range(len(actual)):
        if actual[i] == predicted[i]:
            correct += 1
    return correct / float(len(actual)) * 100.0

# Split a dataset into k folds
def cross_validation_split(dataset, n_folds):
    dataset_split = list()
    dataset_copy = list(dataset)
    fold_size = int(len(dataset) / n_folds)
    for _ in range(n_folds):
        fold = list()
        while len(fold) < fold_size:
            index = randrange(len(dataset_copy))
            fold.append(dataset_copy.pop(index))
        dataset_split.append(fold)
    return dataset_split


# Evaluate an algorithm using a cross validation split
def evaluate_algorithm(dataset, algorithm, n_folds, *args):
    folds = cross_validation_split(dataset, n_folds)
    scores = list()
    for fold in folds:
        train_set = list(folds)
        train_set.remove(fold)
        train_set = sum(train_set, [])
        test_set = list()
        for row in fold:
            row_copy = list(row)
            test_set.append(row_copy)
            row_copy[-1] = None
        predicted = algorithm(train_set, test_set, *args)
        actual = [row[-1] for row in fold]
        accuracy = accuracy_metric(actual, predicted)
        scores.append(accuracy)
    return scores

# Make a prediction with a list of bagged trees
def bagging_predict(trees, row):
    predictions = [predict(tree, row) for tree in trees]
    return max(set(predictions), key=predictions.count)


def run_and_test(algorithm = random_forest_dip):
    
    # Test the random forest algorithm on sonar dataset
    seed(2)
    # load and prepare data
    filename = 'sonar.csv'
    dataset = load_csv(filename)
    # convert string attributes to integers
    for i in range(0, len(dataset[0])-1):
        str_column_to_float(dataset, i)
    # convert class column to integers
    str_column_to_int(dataset, len(dataset[0])-1)
    # evaluate algorithm
    n_folds = 5
    max_depth = 10
    min_size = 2
    sample_size = 1.0
    n_features = int(sqrt(len(dataset[0])-1))
    
    for n_trees in [30]:
        scores = evaluate_algorithm(dataset, algorithm, n_folds, max_depth, min_size,
            sample_size, n_trees, n_features)
        print('Trees: %d' % n_trees)
        print('Scores: %s' % scores)
        print('Mean Accuracy: %.3f%%' % (sum(scores) / float(len(scores))))

run_and_test(random_forest_dip)