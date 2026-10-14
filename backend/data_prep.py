import numpy as np


def quantile_samples_from_histo(histo, n):
    """
    Treats the histogram as a density and returns n points placed at its quantiles.

    Bar i covers the interval [i, i+1) and its height is the (relative) density there,
    spread evenly over the bar. Point k (k = 1..n) sits where the cumulative distribution
    reaches (k - 0.5) / n. The result is a deterministic, sorted "ideal sample" whose ECDF
    is within 1/(2n) of the histogram's CDF everywhere, so its dip is within 1/(2n) of the
    drawn shape's dip.
    """
    heights = np.asarray(histo, dtype=np.float64)
    cumulative = np.cumsum(heights)
    total = cumulative[-1]
    targets = (np.arange(1, n + 1) - 0.5) / n * total
    # first bar whose cumulative mass exceeds the target; never an empty bar
    bars = np.searchsorted(cumulative, targets, side='right')
    mass_before = cumulative[bars] - heights[bars]
    return bars + (targets - mass_before) / heights[bars]


def random_samples_from_histo(histo, n, rng):
    """
    Draws n points at random from the histogram read as a density, the way a real sample
    of size n from that shape would come out. Returned sorted.
    """
    heights = np.asarray(histo, dtype=np.float64)
    bars = rng.choice(len(heights), size=n, p=heights / heights.sum())
    return np.sort(bars + rng.random(n))
