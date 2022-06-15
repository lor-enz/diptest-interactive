import numpy as np

def infer_samples_from_histo(histo, standard_offset=0.1, randomize = True):
    samples = []
    for histo_index in range(0, len(histo)):
        histo_value = histo[histo_index]

        for i in range(0, histo_value):
            newvalue = np.random.normal(loc=histo_index+1, scale=standard_offset, size=None) if randomize else histo_index
            samples.append(newvalue)

    return np.sort(np.array(samples))


def some_testing():
    print(infer_samples_from_histo([5,3,1], randomize=False))
    print(infer_samples_from_histo([5,3,1], randomize=True, standard_offset=0.3))
    print(infer_samples_from_histo([5,3,1], randomize=True, standard_offset=0.000001))

