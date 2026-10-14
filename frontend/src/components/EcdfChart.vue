<script>
import { racingLine, racingLineModes } from "../racingLine.js";

const W = 640;
const H = 400;
const M = { left: 44, right: 14, top: 16, bottom: 34 };
const Y_MIN = -0.06;
const Y_MAX = 1.06;

export default {
  name: "EcdfChart",
  props: {
    samples: { type: Array, required: true }, // sorted sample positions
    xMax: { type: Number, required: true }, // number of bars; bar i covers [i, i+1)
    dip: { type: Number, required: true },
    lowHighIndex: { type: Array, default: null },
    triangleIndex: { type: Array, default: null },
    triangleSide: { type: String, default: null },
    trackFactor: { type: Number, default: 1 }, // track half-width in units of the dip
  },
  emits: ["modes"],
  data() {
    return { W, H, M };
  },
  computed: {
    n() {
      return this.samples.length;
    },
    // A track narrower than 1/(2n) cannot hold any line through the ECDF's steps.
    // The tiny extra keeps a track of exactly 1/(2n) from closing up through rounding.
    halfWidth() {
      return Math.max(this.trackFactor * this.dip, 1 / (2 * this.n)) * (1 + 1e-9);
    },
    ecdfPath() {
      const { n } = this;
      let d = `M${this.sx(0)},${this.sy(0)}`;
      this.samples.forEach((x, i) => {
        d += `H${this.sx(x)}V${this.sy((i + 1) / n)}`;
      });
      return d + `H${this.sx(this.xMax)}`;
    },
    // walls: ECDF + h (upper) and ECDF - h (lower), between the first and last sample
    upperWall() {
      const { n, halfWidth: h } = this;
      return this.samples
        .map((x, i) => `${this.sx(x)},${this.sy(i / n + h)} ${this.sx(x)},${this.sy((i + 1) / n + h)}`)
        .join(" ");
    },
    lowerWall() {
      const { n, halfWidth: h } = this;
      return this.samples
        .map((x, i) => `${this.sx(x)},${this.sy(i / n - h)} ${this.sx(x)},${this.sy((i + 1) / n - h)}`)
        .join(" ");
    },
    trackPolygon() {
      const lowerReversed = this.lowerWall.split(" ").reverse().join(" ");
      return `${this.upperWall} ${lowerReversed}`;
    },
    line() {
      return racingLine(this.samples, this.halfWidth);
    },
    racingLinePoints() {
      return this.line.corners.map(([x, y]) => `${this.sx(x)},${this.sy(y)}`).join(" ");
    },
    modes() {
      return racingLineModes(this.line);
    },
    modeMarkers() {
      return this.modes.map((x) => ({ x: this.sx(x), y: this.sy(this.lineAt(x)) }));
    },
    modalInterval() {
      if (!this.lowHighIndex) return null;
      const [lo, hi] = this.lowHighIndex.map((i) => this.sx(this.samples[i]));
      return { lo, hi };
    },
    // The modal triangle: a chord of the convex minorant (left of the modal interval) or
    // concave majorant (right of it), and the ECDF point furthest from it. That gap is 2·dip.
    triangle() {
      if (!this.triangleIndex) return null;
      const { n } = this;
      const [i1, i2, i3] = this.triangleIndex;
      const [x1, x2, x3] = [i1, i2, i3].map((i) => this.samples[i]);
      // the minorant runs through the bottoms of the ECDF's steps, the majorant through the tops
      const offset = this.triangleSide === "left" ? 0 : 1;
      const y1 = (i1 + offset) / n;
      const y3 = (i3 + offset) / n;
      const apex = (i2 + 1 - offset) / n;
      const chordAtApex = y1 + ((x2 - x1) * (y3 - y1)) / (x3 - x1);
      const p = (x, y) => `${this.sx(x)},${this.sy(y)}`;
      return {
        polygon: `${p(x1, y1)} ${p(x2, apex)} ${p(x3, y3)}`,
        chord: { x1: this.sx(x1), y1: this.sy(y1), x2: this.sx(x3), y2: this.sy(y3) },
        gap: { x: this.sx(x2), y1: this.sy(apex), y2: this.sy(chordAtApex) },
      };
    },
    xTicks() {
      const step = this.xMax > 30 ? 5 : this.xMax > 12 ? 2 : 1;
      const ticks = [];
      for (let x = 0; x <= this.xMax; x += step) ticks.push(x);
      return ticks;
    },
    start() {
      return this.sx(this.samples[0]);
    },
    finish() {
      return this.sx(this.samples[this.n - 1]);
    },
  },
  watch: {
    modes: {
      handler(modes) {
        this.$emit("modes", { count: modes.length, halfWidth: this.halfWidth });
      },
      immediate: true,
    },
  },
  methods: {
    sx(x) {
      return M.left + (x / this.xMax) * (W - M.left - M.right);
    },
    sy(y) {
      return M.top + ((Y_MAX - y) / (Y_MAX - Y_MIN)) * (H - M.top - M.bottom);
    },
    lineAt(x) {
      const c = this.line.allCorners;
      let k = 1;
      while (k < c.length - 1 && c[k][0] < x) k++;
      const [x0, y0] = c[k - 1];
      const [x1, y1] = c[k];
      return y0 + ((y1 - y0) * (x - x0)) / (x1 - x0);
    },
  },
};
</script>

<template>
  <svg
    class="ecdf-chart"
    :viewBox="`0 0 ${W} ${H}`"
    role="img"
    aria-label="Empirical CDF with the dip test's modal interval, modal triangle and race track"
  >
    <defs>
      <clipPath id="plot-area">
        <rect :x="M.left" :y="M.top" :width="W - M.left - M.right" :height="H - M.top - M.bottom" />
      </clipPath>
    </defs>

    <!-- axes -->
    <g class="axis">
      <line :x1="M.left" :x2="W - M.right" :y1="sy(0)" :y2="sy(0)" />
      <line :x1="M.left" :x2="M.left" :y1="sy(0)" :y2="sy(1)" />
      <g v-for="t in xTicks" :key="'x' + t">
        <line :x1="sx(t)" :x2="sx(t)" :y1="sy(0)" :y2="sy(0) + 4" />
        <text :x="sx(t)" :y="sy(0) + 16" text-anchor="middle">{{ t }}</text>
      </g>
      <g v-for="t in [0, 0.5, 1]" :key="'y' + t">
        <line :x1="M.left - 4" :x2="M.left" :y1="sy(t)" :y2="sy(t)" />
        <line class="grid" :x1="M.left" :x2="W - M.right" :y1="sy(t)" :y2="sy(t)" />
        <text :x="M.left - 8" :y="sy(t) + 4" text-anchor="end">{{ t }}</text>
      </g>
    </g>

    <g clip-path="url(#plot-area)">
      <!-- modal interval -->
      <g v-if="modalInterval" class="modal-interval">
        <rect :x="modalInterval.lo" :y="M.top" :width="Math.max(modalInterval.hi - modalInterval.lo, 1)" :height="sy(0) - M.top" />
        <line :x1="modalInterval.lo" :x2="modalInterval.lo" :y1="M.top" :y2="sy(0)" />
        <line :x1="modalInterval.hi" :x2="modalInterval.hi" :y1="M.top" :y2="sy(0)" />
      </g>

      <!-- race track: asphalt between the walls, kerbs on the walls -->
      <polygon class="track" :points="trackPolygon" />
      <polyline class="kerb" :points="upperWall" />
      <polyline class="kerb-stripes" :points="upperWall" />
      <polyline class="kerb" :points="lowerWall" />
      <polyline class="kerb-stripes" :points="lowerWall" />
      <line class="start-finish" :x1="start" :x2="start" :y1="sy(halfWidth)" :y2="sy(-halfWidth)" />
      <line class="start-finish" :x1="finish" :x2="finish" :y1="sy(1 + halfWidth)" :y2="sy(1 - halfWidth)" />

      <!-- the ECDF itself -->
      <path class="ecdf" :d="ecdfPath" />

      <!-- racing line -->
      <polyline class="racing-line" :points="racingLinePoints" />

      <!-- modal triangle -->
      <g v-if="triangle" class="triangle">
        <polygon :points="triangle.polygon" />
        <line class="chord" :x1="triangle.chord.x1" :y1="triangle.chord.y1" :x2="triangle.chord.x2" :y2="triangle.chord.y2" />
        <line class="gap" :x1="triangle.gap.x" :x2="triangle.gap.x" :y1="triangle.gap.y1" :y2="triangle.gap.y2" />
      </g>
    </g>

    <!-- labels on top, outside the clip so they stay readable -->
    <g v-if="modalInterval" class="modal-interval-label">
      <text :x="modalInterval.lo - 3" :y="M.top + 12" text-anchor="end">low</text>
      <text :x="modalInterval.hi + 3" :y="M.top + 12">high</text>
    </g>
    <text
      v-if="triangle"
      class="gap-label"
      :x="triangle.gap.x + 5"
      :y="(triangle.gap.y1 + triangle.gap.y2) / 2 + 4"
    >2·dip</text>
    <g v-for="(m, k) in modeMarkers" :key="'mode' + k">
      <circle class="mode-dot" :cx="m.x" :cy="m.y" r="3.5" />
      <text class="car" :x="m.x" :y="m.y - 8" text-anchor="middle">🏎️</text>
    </g>
  </svg>
</template>

<style scoped>
.ecdf-chart {
  width: 100%;
  height: auto;
  font-family: verdana, sans-serif;
  font-size: 11px;
}
.axis line {
  stroke: #888;
}
.axis .grid {
  stroke: #e6e6e6;
}
.axis text {
  fill: #555;
}
.modal-interval rect {
  fill: rgba(56, 182, 217, 0.12);
}
.modal-interval line {
  stroke: rgb(56, 182, 217);
  stroke-width: 1.5;
}
.modal-interval-label text {
  fill: rgb(30, 130, 170);
  font-weight: bold;
}
.track {
  fill: rgba(80, 80, 80, 0.22);
}
.kerb {
  fill: none;
  stroke: #555;
  stroke-width: 3;
}
.kerb-stripes {
  fill: none;
  stroke: white;
  stroke-width: 3;
  stroke-dasharray: 5 5;
}
.start-finish {
  stroke: #222;
  stroke-width: 3;
  stroke-dasharray: 3 3;
}
.ecdf {
  fill: none;
  stroke: #383838;
  stroke-width: 1.5;
}
.racing-line {
  fill: none;
  stroke: rgb(230, 159, 0);
  stroke-width: 2.5;
}
.triangle polygon {
  fill: rgba(227, 98, 128, 0.2);
  stroke: rgb(200, 50, 90);
  stroke-width: 1;
}
.triangle .chord {
  stroke: rgb(200, 50, 90);
  stroke-width: 2;
}
.triangle .gap {
  stroke: rgb(200, 50, 90);
  stroke-width: 2;
  stroke-dasharray: 4 3;
}
.gap-label {
  fill: rgb(170, 30, 70);
  font-weight: bold;
}
.mode-dot {
  fill: rgb(230, 159, 0);
  stroke: #222;
  stroke-width: 1.5;
}
.car {
  font-size: 16px;
}
</style>
