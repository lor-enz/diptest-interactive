<script>
import BarChart from "./components/barChart.ts";
import EcdfChart from "./components/EcdfChart.vue";
const startAreaSize = 7;
const zeroAreaSize = 20;
const canvasLineInterval = 17;

const colorblind_friendly_palette = {
  orange: "230,159,0", // ???
};

export default {
  name: "DipTestApp",
  components: {
    BarChart,
    EcdfChart,
  },
  data() {
    return {
      upperChartData: {
        labels: ["Draw", "something", "in", "the", "Canvas"],
        datasets: [
          {
            data: [400, 200, 100, 50, 25],
            backgroundColor: ["rgba(136, 149, 66, 1.0)"],
          },
        ],
      },
      backurl:
        "the api url. Filled with VUE_APP_API_URL environment variable during BUILD, not RUNTIME",
      canvas: null,
      cleanHistogramData: [],
      points: [1,2,3], // pixelcoordinates of drawn line start/endpoints
      sampleSizes: [20, 50, 100, 200, 500, 1000, 5000],
      n: 200, // size of the ideal sample the dip test runs on
      trackFactor: 1, // race track half-width in units of the dip
      racingLineModes: null, // { count, halfWidth } reported by the ECDF chart
      dipResponse: 0, // dip value between 0 and 0.25
      low_high: "[]",
      modal_triangle: "[]",
      pval: 0, // p-value of the ideal sample
      typicalPval: 0, // median p-value of random samples of n from the drawing
      power: 0, // share of those random samples with p < 0.05
      dipAtFloor: false, // dip is 1/(2n): modal interval and triangle are arbitrary, so hidden
      result: null, // last successful response, drives the ECDF chart
    };
  },

  methods: {
    drawLine(x1, y1, x2, y2) {
      let ctx = this.canvas;
      ctx.beginPath();
      ctx.strokeStyle = "black";
      ctx.lineWidth = 2;
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
      ctx.closePath();
    },
    keepDrawing(e) {
      // the canvas is scaled to fit the window; work in its own 800x500 pixels
      const offsetX = (e.offsetX * this.canv.width) / this.canv.clientWidth;
      const offsetY = (e.offsetY * this.canv.height) / this.canv.clientHeight;
      // clear if starting on left
      if (offsetX < startAreaSize) {
        this.clear();
      }

      if (offsetX >= this.x) {
        var newX =
          Math.round(offsetX / canvasLineInterval) * canvasLineInterval;
        var newY =
          offsetY >= this.canv.height - zeroAreaSize
            ? this.canv.height // the bottom strip draws bars of height 0
            : Math.round(offsetY);
        this.drawLine(this.x, this.y, newX, newY);
        this.x = newX;
        this.y = newY;
        this.maybeAddPoint(newX, newY);
      }
    },
    clear() {    
      if (this.points.length < 3) {
        return
      }
      this.canvas.fillStyle = "#ffffffEE";
      this.canvas.fillRect(0,0,this.canv.width,this.canv.height);

      this.x = 0;
      this.points = [];
      // yellow marked area
      this.canvas.fillStyle = "#d1c30050";
      this.canvas.fillRect(0, 0, startAreaSize, this.canv.height);
      // red marked area
      this.canvas.fillStyle = "#d1000050";
      this.canvas.fillRect(
        0,
        this.canv.height - zeroAreaSize,
        this.canv.width,
        zeroAreaSize
      );
    },
    maybeAddPoint(newX, newY) {
      var wasPointAdded = false;
      var c = document.getElementById("myCanvas"); // TODO use data variable?
      newY = c.height - newY;

      if (this.points.length === 0) {
        this.points.push([newX, newY]);
        return true;
      }
      var [lastX, lastY] = this.points[this.points.length - 1];
      if (lastX === newX) {
        // still in the same column: the bar follows the cursor
        this.points[this.points.length - 1] = [newX, newY];
      } else {
        // a fast mouse can jump over columns; fill them in along the drawn line
        // instead of dropping them, which would squeeze the x-axis together
        for (let x = lastX + canvasLineInterval; x < newX; x += canvasLineInterval) {
          const fraction = (x - lastX) / (newX - lastX);
          this.points.push([x, Math.round(lastY + fraction * (newY - lastY))]);
        }
        this.points.push([newX, newY]);
        wasPointAdded = true;
      }
      return wasPointAdded;
    },
    startCalculation() {
      this.createDataLists();
      this.requestDipValue();
    },
    createDataLists() {
      // one bar per drawn column, its height in pixels; only the shape matters
      this.cleanHistogramData = this.points.map(([x, y]) => y);
    },
    createChartData() {
      this.upperChartData.datasets[0].data = this.cleanHistogramData;
      this.upperChartData.labels = [...Array(this.cleanHistogramData.length).keys()];
      // Bar Colors: modal interval blue, bars holding the modal triangle's corners red
      var lightgreen = "rgb(136, 149, 66)";
      var red = "rgb(227, 98, 128)";
      var blue = "rgb(56, 182, 217)";
      var barColors = this.cleanHistogramData.map(() => lightgreen);
      if (Array.isArray(this.low_high) && !this.dipAtFloor) {
        for (let bar = this.low_high[0]; bar <= this.low_high[1]; bar++) {
          barColors[bar] = blue;
        }
      }
      if (Array.isArray(this.modal_triangle) && !this.dipAtFloor) {
        this.modal_triangle.forEach((bar) => (barColors[bar] = red));
      }
      this.upperChartData.datasets[0].backgroundColor = barColors;
    },
    copy() {
      this.$refs.myinput.focus();
      document.execCommand("copy");
    },
    async requestDipValue() {
      if (this.cleanHistogramData.length < 6) {
        this.wrong();
        return;
      }
      const requestOptions = {
        method: "CALC",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(this.cleanHistogramData),
      };
      var req_url = `${this.backurl}/dip-from-histo?n=${this.n}`;
      console.log(
        `fetching from: ${req_url} with method: ${requestOptions["method"]} `
      );
      fetch(req_url, requestOptions)
        .then((response) => {
          console.log("Response:", response);
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return response.json();
        })
        .then((data) => {
          this.dipResponse = Number(data["dip"]).toFixed(4);
          this.modal_triangle = data["modal_triangle"];
          this.low_high = data["low_high"];
          this.pval = Number(data["pval"]).toFixed(4);
          this.typicalPval = Number(data["typical_pval"]).toFixed(4);
          this.power = `${Math.round(100 * data["power"])} %`;
          this.dipAtFloor = data["dip_at_floor"];
          this.result = {
            samples: data["samples"],
            xMax: this.cleanHistogramData.length,
            dip: data["dip"],
            lowHighIndex: this.dipAtFloor ? null : data["low_high_index"],
            triangleIndex: this.dipAtFloor ? null : data["modal_triangle_index"],
            triangleSide: data["modal_triangle_side"],
          };
          this.createChartData();
        })
        .catch((err) => {
          console.error("error retrieving data", err);
          this.wrong();
          this.createChartData();
        });
    },
    wrong() {
      this.dipResponse = "err";
      this.pval = "err";
      this.typicalPval = "err";
      this.power = "err";
      this.dipAtFloor = false;
      this.modal_triangle = "err";
      this.low_high = "err";
      this.result = null;
    },
  },

  watch: {
    n() {
      // the dip and p-value depend on the sample size; the drawing stays the same
      if (this.cleanHistogramData.length) this.requestDipValue();
    },
  },

  // Lifecycle hooks are called at different stages
  // of a component's lifecycle.
  // This function will be called when the component is mounted.
  mounted() {
    this.canv = document.getElementById("myCanvas");
    this.canvas = this.canv.getContext("2d");
    this.clear();
    console.log("--------------MOUNTED--------------");
    this.backurl = import.meta.env.VUE_APP_API_URL.trim();
    // relative URLs (e.g. "/api") point at the same origin and stay as they are
    if (!this.backurl.startsWith("http") && !this.backurl.startsWith("/")) {
      this.backurl = `http://${this.backurl}`;
    }
  },
};
</script>

<template>
  <div id="app">
    <header>
      <h1>Diptest Tool</h1>
      <p class="howto">
        📈 Move the mouse across the canvas from left to right, no click needed.
        The test runs when the cursor leaves the canvas.
        🟨 The start strip clears the canvas, 🟥 the bottom strip draws zeros.
      </p>
    </header>

    <main class="layout">
      <section class="panel">
        <h2>Draw a density</h2>
        <canvas
          id="myCanvas"
          width="800"
          height="500"
          @mousemove="keepDrawing"
          @mousedown="keepDrawing"
          @mouseleave="startCalculation"
        />

        <div class="stats">
          <div class="stat"><span class="label">Dip</span><span class="value">{{ dipResponse }}</span></div>
          <div class="stat"><span class="label">p (ideal sample)</span><span class="value">{{ pval }}</span></div>
          <div class="stat"><span class="label">p (typical sample)</span><span class="value">{{ typicalPval }}</span></div>
          <div class="stat"><span class="label">significant in</span><span class="value">{{ power }}</span></div>
          <label class="stat">
            <span class="label">sample size n</span>
            <select v-model.number="n">
              <option v-for="size in sampleSizes" :key="size" :value="size">{{ size }}</option>
            </select>
          </label>
        </div>
        <p v-if="dipAtFloor" class="note">
          The dip is 1/(2·{{ n }}), the smallest dip any {{ n }} points can have: half of
          one step of the ECDF. As far as {{ n }} points can tell, your shape is unimodal.
          Every step ties for the modal triangle, so neither it nor a modal interval is shown.
        </p>

        <details>
          <summary>How is the drawing tested?</summary>
          <p>
            Your drawing is read as the <b>shape</b> of a distribution, not as counts.
            The test runs on an ideal sample of n points placed exactly along that shape.
            The dip barely depends on n (it is within 1/(2n) of your shape's own dip, so
            only small n move it), but the p-value does: the same shape is far more
            convincing with more points.
          </p>
        </details>
        <details>
          <summary>Why two p-values?</summary>
          <p>
            The ideal sample is perfectly smooth, so its p-value is not what a real sample
            would get: real samples are noisy, which adds to their dip. For a faint dip the
            difference is large. The <b>typical sample</b> p-value repeats the test on 100
            random samples of the same size drawn from your shape. It is their median, and
            "significant in" is how often they reach p &lt; 0.05 (the test's power).
          </p>
        </details>
        <details>
          <summary>The race track</summary>
          <p>
            The track's walls run at the ECDF ± a half-width. A racing line takes the
            shortest way through. Turning left means the distribution is getting denser,
            turning right means it is thinning out, so each 🏎️ marks a place where the line
            stops turning left and starts turning right: a mode. The <b>dip is half the
            width of the narrowest track whose racing line switches from left to right only
            once.</b> Make the track narrower than that and the line needs more switches.
          </p>
        </details>
      </section>

      <section class="panel">
        <h2>Histogram</h2>
        <div class="histogram">
          <BarChart :chartData="upperChartData" :styles="{ height: '100%', position: 'relative' }" />
        </div>

        <h2>Empirical cumulative distribution (ECDF)</h2>
        <template v-if="result">
          <EcdfChart
            v-bind="result"
            :trackFactor="trackFactor"
            @modes="racingLineModes = $event"
          />
          <p class="legend">
            <span><span class="swatch ecdf"></span>ECDF of the sample</span>
            <span><span class="swatch interval"></span>modal interval</span>
            <span><span class="swatch triangle"></span>modal triangle (gap = 2·dip)</span>
            <span><span class="swatch track"></span>race track: ECDF ± half-width</span>
            <span><span class="swatch line"></span>racing line</span>
          </p>
          <label class="track-slider">
            <span>Track half-width {{ trackFactor.toFixed(2) }} × dip</span>
            <input v-model.number="trackFactor" type="range" min="0.25" max="2" step="0.01" />
            <span v-if="racingLineModes">
              = {{ racingLineModes.halfWidth.toFixed(4) }}:
              <b>{{ racingLineModes.count }}</b>
              mode{{ racingLineModes.count === 1 ? "" : "s" }}
            </span>
          </label>
        </template>
        <p v-else class="placeholder">Draw something in the canvas to see its ECDF.</p>
      </section>
    </main>

    <p id="footnote">Backend: [{{ backurl }}]</p>
  </div>
</template>

<style scoped>
/* Fit the drawing and the results into one screen. The canvas and the ECDF chart scale
   with the window height, since both have a fixed aspect ratio (8:5). */
#app {
  --ink: #383838;
  --muted: #666;
  --line: #ddd;
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 16px;
  font-family: verdana, sans-serif;
  color: var(--ink);
  font-size: 14px;
}

header {
  display: flex;
  align-items: baseline;
  gap: 24px;
  padding: 10px 0 6px;
}

h1 {
  margin: 0;
  font-size: 24px;
  white-space: nowrap;
}

.howto {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}

h2 {
  margin: 4px 0 6px;
  font-size: 15px;
}

.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.panel {
  min-width: 0;
}

#myCanvas {
  display: block;
  width: 100%;
  max-width: calc((100vh - 200px) * 1.6);
  height: auto;
  border: 1px solid grey;
  box-sizing: border-box;
  touch-action: none;
}

.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0 6px;
}

.stat {
  display: flex;
  flex-direction: column;
  padding: 4px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  min-width: 90px;
}

.stat .label {
  font-size: 11px;
  color: var(--muted);
}

.stat .value,
.stat select {
  font-size: 17px;
  font-weight: bold;
  font-variant-numeric: tabular-nums;
}

.note {
  margin: 4px 0 8px;
  font-size: 13px;
  color: var(--muted);
}

details {
  font-size: 13px;
  border-top: 1px solid var(--line);
  padding: 4px 0;
}

details p {
  margin: 4px 0 6px;
  line-height: 1.45;
}

summary {
  cursor: pointer;
  font-weight: bold;
}

.histogram {
  height: clamp(110px, 18vh, 200px);
}

.panel :deep(.ecdf-chart) {
  display: block;
  margin: 0 auto;
  max-width: calc((100vh - 400px) * 1.6);
}

.placeholder {
  color: var(--muted);
  text-align: center;
  padding: 60px 0;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2px 14px;
  margin: 4px 0;
  font-size: 11px;
}

.swatch {
  display: inline-block;
  width: 14px;
  height: 10px;
  margin-right: 4px;
  vertical-align: middle;
}
.swatch.ecdf { background: #383838; height: 2px; }
.swatch.interval { background: rgba(56, 182, 217, 0.5); border: 1px solid rgb(56, 182, 217); }
.swatch.triangle { background: rgba(227, 98, 128, 0.35); border: 1px solid rgb(200, 50, 90); }
.swatch.track { background: rgba(80, 80, 80, 0.3); border-top: 2px dashed #555; border-bottom: 2px dashed #555; }
.swatch.line { background: rgb(230, 159, 0); height: 3px; }

.track-slider {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 4px 10px;
  font-size: 13px;
}

.track-slider input {
  flex: 1 1 200px;
  max-width: 320px;
}

#footnote {
  font-size: 7px;
  color: #b5b5b5;
  margin: 8px 0 4px;
}

@media (max-width: 900px) {
  header {
    flex-direction: column;
    gap: 4px;
  }
  .layout {
    grid-template-columns: 1fr;
  }
  #myCanvas,
  .panel :deep(.ecdf-chart) {
    max-width: 100%;
  }
}
</style>
