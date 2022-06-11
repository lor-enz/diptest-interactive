

def visualize(tree):
    index = tree['index']
    value = tree['value']
    left = tree['left']
    right = tree['right']


def how_deep(tree):
    if isinstance(tree, dict):
        return 1 + how_deep(tree['left'])
    else:
        return 1


def print_tree(node, depth=0):
    if isinstance(node, dict):
        print('%s[X%d < %.3f]' % ((depth*' ', (node['index']+1), node['value'])))
        print_tree(node['left'], depth+1)
        print_tree(node['right'], depth+1)
    else:
        print('%s[%s]' % ((depth*' ', node)))

def save_to_pickle(some_object, filename):
    import pickle
    file_to_store = open(f"{filename}.pickle", "wb")
    pickle.dump(some_object, file_to_store)
    file_to_store.close()

def load_from_pickle(filename):
    import pickle
    file_to_read = open(f"{filename}.pickle", "rb")
    loaded_object = pickle.load(file_to_read)
    file_to_read.close()
    return loaded_object



tree = load_from_pickle("some_tree")
# print_tree(tree)

