import numpy as np


def infer_samples_from_histo(histo, standard_deviation=0.25, randomize=True):
    samples = []
    for histo_index in range(0, len(histo)):
        histo_value = histo[histo_index]

        for i in range(0, histo_value):
            # newvalue = np.random.normal(
            #     loc=histo_index+1, scale=standard_deviation, size=None) if randomize else histo_index+1

            newvalue = constrained_normal_distribution(histo_index+1, standard_deviation, 0.5) if randomize else histo_index+1
            samples.append(newvalue)

    return np.sort(np.array(samples))


def constrained_normal_distribution(location, standard_deviation, max_deviation):
    """Normal Distribution but with a (exclusive) maximal distribution"""
    random_value = np.random.normal(loc=location, scale=standard_deviation, size=None)
    if abs(random_value - location) > max_deviation:
        return constrained_normal_distribution(location, standard_deviation, max_deviation)
    else:
        return random_value


def test_constrained_normal_distribution():
    print("started")
    for _ in range(100000):
        result = constrained_normal_distribution(5, 1, 2)
        assert(result>=3 and result <=7)
    print("Done")

def test_infer_samples_from_histo():
    test_array = [1,3,5]
    print(infer_samples_from_histo(test_array, randomize=False))
    print(infer_samples_from_histo(
        test_array, randomize=True, standard_deviation=0.5))
    print(infer_samples_from_histo(
        test_array, randomize=True, standard_deviation=0.000001))

# some_testing()

test_constrained_normal_distribution()