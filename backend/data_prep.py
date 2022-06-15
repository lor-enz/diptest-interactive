import numpy as np


def infer_samples_from_histo(histo, standard_deviation=0.4, randomize=True):
    samples = []
    for histo_index in range(0, len(histo)):
        histo_value = histo[histo_index]

        for i in range(0, histo_value):
            newvalue = np.random.normal(
                loc=histo_index+1, scale=standard_deviation, size=None) if randomize else histo_index+1
            samples.append(newvalue)

    return np.sort(np.array(samples))


def some_testing():
    test_array = [1,3,5]
    print(infer_samples_from_histo(test_array, randomize=False))
    print(infer_samples_from_histo(
        test_array, randomize=True, standard_deviation=0.5))
    print(infer_samples_from_histo(
        test_array, randomize=True, standard_deviation=0.000001))

# some_testing()