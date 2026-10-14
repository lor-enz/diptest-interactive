<script>
import BarChart from "./components/barChart.ts";
import EcdfChart from "./components/EcdfChart.vue";
const startAreaSize = 7;
const zeroAreaSize = 20;
const canvasLineInterval = 17;

const colorblind_friendly_palette = {
  orange: "230,159,0", // ???
};

function randomIntFromInterval(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

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
      pval: 0,
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
      // clear if starting on left
      if (e.offsetX < startAreaSize) {
        this.clear();
      }

      if (e.offsetX >= this.x) {
        var newX =
          Math.round(e.offsetX / canvasLineInterval) * canvasLineInterval;
        var newY =
          e.offsetY >= this.canv.height - zeroAreaSize
            ? randomIntFromInterval(this.canv.height - 4, this.canv.height)
            : e.offsetY;
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
      if (Array.isArray(this.low_high)) {
        for (let bar = this.low_high[0]; bar <= this.low_high[1]; bar++) {
          barColors[bar] = blue;
        }
      }
      if (Array.isArray(this.modal_triangle)) {
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
          this.result = {
            samples: data["samples"],
            xMax: this.cleanHistogramData.length,
            dip: data["dip"],
            lowHighIndex: data["low_high_index"],
            triangleIndex: data["modal_triangle_index"],
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
    <h1>Diptest Tool</h1>
    <div class="row">
      <div class="column">
        <h2 id="how-to-title">How to</h2>
        <p>
          📈 Move your mouse cursor from the left of the canvas to the right. <br />
          ℹ️ No need to click! <br />
          📊 Once the mourse cursor leaves the canvas area, the tool will convert the mouses trail into data for the charts on the right. <br>
          <br>
          The 🟨 yellow area is the start area. Touching it with your mouse will clear the canvas. <br>
          The 🟥 red area is the random low value area. Drawing here will set random low value points.
        </p>
        <h2 id="canvas-title" >Canvas</h2>
        <canvas
          id="myCanvas"
          width="800"
          height="500"
          @mousemove="keepDrawing"
          @mousedown="keepDrawing"
          @mouseleave="startCalculation"
        />
        <div class="row">
          <div class="column">
            <h3 class="centeredparagraph">
              Dip: {{ dipResponse }}  Pval: {{ pval }}
              <br />
              Modal Triangle 🟥 {{ modal_triangle }} - Low high 🟦 {{ low_high }}
            </h3>
            <p>
              Your drawing is read as the <b>shape</b> of a distribution, not as counts.
              The test runs on an ideal sample of
              <select v-model.number="n">
                <option v-for="size in sampleSizes" :key="size" :value="size">{{ size }}</option>
              </select>
              points placed exactly along that shape. The dip barely depends on this number,
              but the p-value does: the same shape is far more convincing with more points.
            </p>
          </div>
        </div>
        <p id="footnote">Backend: [{{ backurl }}]</p>
      </div>
      <div class="column">
        <div>
          <BarChart :chartData="upperChartData" />
        </div>
        <h3>⬆️        Histogram        ⬆️</h3>
        <h3>⬇️ Empirical Cumulative Distribution (ECDF) ⬇️</h3>
        <div v-if="result">
          <EcdfChart
            v-bind="result"
            :trackFactor="trackFactor"
            @modes="racingLineModes = $event"
          />
          <p class="legend">
            <span class="swatch ecdf"></span> ECDF of the sample
            <span class="swatch interval"></span> modal interval (low, high)
            <span class="swatch triangle"></span> modal triangle: the dashed gap is 2·dip
            <span class="swatch track"></span> race track: ECDF ± half-width
            <span class="swatch line"></span> racing line
          </p>
          <p>
            <b>The race track.</b> The track's walls run at the ECDF ± a half-width.
            A racing line takes the shortest way through. Turning left means the
            distribution is getting denser, turning right means it is thinning out, so each
            🏎️ marks a place where the line stops turning left and starts turning right: a mode.
            The <b>dip is half the width of the narrowest track whose racing line switches from
            left to right only once.</b> Make the track narrower than that and the line needs
            more switches.
          </p>
          <label class="track-slider">
            Track half-width: {{ trackFactor.toFixed(2) }} × dip
            <input v-model.number="trackFactor" type="range" min="0.25" max="2" step="0.01" />
          </label>
          <p v-if="racingLineModes" class="centeredparagraph">
            Half-width {{ racingLineModes.halfWidth.toFixed(4) }}:
            the racing line has <b>{{ racingLineModes.count }}</b>
            mode{{ racingLineModes.count === 1 ? "" : "s" }}.
          </p>
        </div>
        <p v-else class="centeredparagraph">Draw something in the canvas to see its ECDF.</p>
      </div>
    </div>
    <p></p>
  </div>
</template>

<style scoped>
h1 {
  font-family: verdana;
  color: #383838;
  text-align: center;
}

h2 {
  font-family: verdana;
  color: #383838;
  text-align: center;
  margin: 15px;
}

h3 {
  font-family: verdana;
  color: #383838;
  text-align: center;
}

div {
  text-align: center;
}

p {
  font-family: verdana;
  font-size: 15px;
  text-align: left;
}

.row {
  display: flex;
}

.column {
  flex: 50%;
}

#myCanvas {
  border: 1px solid grey;
}

#footnote {
  display: flex;
  font-size: 7px;
  color: #b5b5b5;
  text-indent: 0px;
  margin: 1px;
}

#how-to-title {
  margin: 1px;
}

#canvas-title {
  margin: 20px;
}

.centeredparagraph {
  text-align: center;
}

.legend {
  font-size: 12px;
  line-height: 1.8;
}

.swatch {
  display: inline-block;
  width: 14px;
  height: 10px;
  margin: 0 3px 0 10px;
  vertical-align: middle;
}
.swatch.ecdf { background: #383838; height: 2px; }
.swatch.interval { background: rgba(56, 182, 217, 0.5); border: 1px solid rgb(56, 182, 217); }
.swatch.triangle { background: rgba(227, 98, 128, 0.35); border: 1px solid rgb(200, 50, 90); }
.swatch.track { background: rgba(80, 80, 80, 0.3); border-top: 2px dashed #555; border-bottom: 2px dashed #555; }
.swatch.line { background: rgb(230, 159, 0); height: 3px; }

.track-slider {
  display: block;
  font-family: verdana;
  font-size: 14px;
}

.track-slider input {
  width: 60%;
  vertical-align: middle;
}
</style>
