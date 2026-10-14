// The race track analogy for the dip test.
//
// The track's walls run at ECDF ± halfWidth. A racing line is the shortest path through
// the track (a "taut string"). Turning left means the CDF bends upwards (density rising),
// turning right means it bends downwards (density falling), so every place where the
// line stops turning left and starts turning right is a mode.
//
// The taut string needs the fewest such switches of any path through the track
// (Davies & Kovac 2001). A track of half-width d therefore fits a one-mode line exactly
// when some unimodal CDF lies within d of the ECDF, so the dip is half the width of the
// narrowest track on which the racing line turns left and then right only once.

/**
 * Racing line through the track around the ECDF of the sorted samples `xs`.
 * Returns the line's corner points [[x, y], ...] from the first to the last sample,
 * plus the slopes of all its segments (including the flat lead-in and run-out).
 */
export function racingLine(xs, halfWidth) {
  const n = xs.length;
  const span = xs[n - 1] - xs[0] || 1;
  // Gates at every sample. Just before x_i the ECDF is i/n, at x_i it is (i+1)/n,
  // so the line must pass within halfWidth of both.
  const gates = [];
  // Lead-in and run-out: far outside the data the CDF is 0 and 1. Starting from there
  // leaves the line free to cross the first and last gate wherever it likes.
  gates.push({ x: xs[0] - 1000 * span, lo: 0, hi: 0 });
  for (let i = 0; i < n; i++) {
    gates.push({
      x: xs[i],
      lo: Math.max(0, (i + 1) / n - halfWidth),
      hi: Math.min(1, i / n + halfWidth),
    });
  }
  gates.push({ x: xs[n - 1] + 1000 * span, lo: 1, hi: 1 });

  const corners = [[gates[0].x, 0]];
  let anchor = 0;
  let [ax, ay] = corners[0];
  // Funnel algorithm: widen the fan of possible directions from the last corner until
  // a gate falls outside it, then add a corner where the fan was pinched.
  while (anchor < gates.length - 1) {
    let maxLow = -Infinity, maxLowAt = -1;
    let minHigh = Infinity, minHighAt = -1;
    let corner = null;
    for (let i = anchor + 1; i < gates.length; i++) {
      const dx = gates[i].x - ax;
      const low = (gates[i].lo - ay) / dx;
      const high = (gates[i].hi - ay) / dx;
      if (low > minHigh) {
        corner = [minHighAt, gates[minHighAt].hi];
        break;
      }
      if (high < maxLow) {
        corner = [maxLowAt, gates[maxLowAt].lo];
        break;
      }
      if (low >= maxLow) [maxLow, maxLowAt] = [low, i];
      if (high <= minHigh) [minHigh, minHighAt] = [high, i];
    }
    if (corner === null) {
      // the last gate is a single point, so the fan ends there
      corner = [gates.length - 1, gates[gates.length - 1].lo];
    }
    [anchor, ay] = corner;
    ax = gates[anchor].x;
    corners.push([ax, ay]);
  }

  const slopes = [];
  for (let k = 1; k < corners.length; k++) {
    slopes.push((corners[k][1] - corners[k - 1][1]) / (corners[k][0] - corners[k - 1][0]));
  }
  return { corners: corners.slice(1, -1), slopes, allCorners: corners };
}

/**
 * Modes of the racing line: the steepest stretches, where it stops turning left and
 * starts turning right. Returns the x positions of their midpoints.
 */
export function racingLineModes({ allCorners, slopes }) {
  // merge neighbouring segments whose slopes differ only by rounding errors
  const tolerance = 1e-7 * Math.max(...slopes.map(Math.abs));
  const runs = [];
  slopes.forEach((slope, k) => {
    const last = runs[runs.length - 1];
    if (last && Math.abs(slope - last.slope) <= tolerance) {
      last.end = k + 1;
    } else {
      runs.push({ slope, start: k, end: k + 1 });
    }
  });
  const modes = [];
  // the flat lead-in and run-out are never modes, so only inner runs can be peaks
  for (let r = 1; r < runs.length - 1; r++) {
    if (runs[r].slope > runs[r - 1].slope && runs[r].slope > runs[r + 1].slope) {
      const from = allCorners[runs[r].start][0];
      const to = allCorners[runs[r].end][0];
      modes.push((from + to) / 2);
    }
  }
  return modes;
}
