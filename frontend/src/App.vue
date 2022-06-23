<script>
import BarChart from "./components/barChart.ts";
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
      lowerChartData: {
        labels: ["Draw", "something", "in", "the", "Canvas"],
        datasets: [
          {
            data: [400, 600, 700, 750, 775],
            backgroundColor: ["rgba(136, 149, 66, 1.0)"],
          },
        ],
      },
      backurl:
        "the api url. Filled with VUE_APP_API_URL environment variable during BUILD, not RUNTIME",
      canvas: null,
      cleanHistogramData: [],
      cleanCumulativeData: [],
      points: [1,2,3], // pixelcoordinates of drawn line start/endpoints
      dipResponse: 0, // dip value between 0 and 0.25
      howUnimodalInPercent: 0,
      split_index: 0,
      pval_left: 0,
      pval_right: 0,
      score: 0,
      low_high: "[]",
      modal_triangle: "[]",
      pval: 0,
      ecdf: [],
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
        wasPointAdded = true;
      }
      var [lastX, lastY] = this.points[this.points.length - 1];
      if (lastX !== newX) {
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
      // Histogramdata
      var cleanHistogramData = [];
      this.points.forEach(function (element, index) {
        let [x1, y1] = element;
        cleanHistogramData.push(y1);
      });

      // Actual CDF (cumulative distribution funciton)
      var cleanCumulativeData = [];
      var totalsum = 0;
      cleanHistogramData.forEach(function (value, index) {
        totalsum = totalsum + value;
      });
      var sum = 0;
      cleanHistogramData.forEach(function (value, index) {
        sum = sum + value;
        cleanCumulativeData.push(sum / totalsum);
      });
      this.cleanHistogramData = cleanHistogramData;
      this.cleanCumulativeData = cleanCumulativeData;
    },
    createChartData() {
      // Data
      this.upperChartData.datasets[0].data = this.cleanHistogramData;
      this.lowerChartData.datasets[0].data = this.cleanCumulativeData;
      // Labels
      var labels = [...Array(this.cleanHistogramData.length).keys()];
      labels[this.split_index] = "]";
      labels[this.split_index + 1] = "[";
      this.lowerChartData.labels = labels;
      this.upperChartData.labels = labels;
      // Bar Colors
      var barColors = [];
      var lightgreen = "rgb(136, 149, 66)";
      var kiwigreen = "rgb(201, 219, 96)";
      var red = "rgb(227, 98, 128)";
      var blue = "rgb(56, 182, 217)";
      var purple = "rgb(142,140,173)";

      var split_index = this.split_index;
      this.cleanHistogramData.forEach(function (value, index) {
        if (index <= split_index) barColors.push(kiwigreen);
        else barColors.push(lightgreen);
      });
      barColors[this.low_high[0]] = blue;
      barColors[this.low_high[1]] = blue;
      barColors[this.modal_triangle[0]] = red;
      barColors[this.modal_triangle[1]] = red;
      barColors[this.modal_triangle[2]] = red;
      this.low_high.forEach((element) => {
        if (this.modal_triangle.includes(element)) {
          barColors[element] = purple;
        }
      });

      this.lowerChartData.datasets[0].backgroundColor = barColors;
      this.upperChartData.datasets[0].backgroundColor = barColors;
    },
    copy() {
      this.$refs.myinput.focus();
      document.execCommand("copy");
    },
    async requestDipValue() {
      if (this.cleanCumulativeData.length < 6) {
        this.wrong();
        return;
      }
      const requestOptions = {
        method: "CALC",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(this.cleanHistogramData),
      };
      var req_url = `${this.backurl}/dip-from-histo`;
      console.log(
        `fetching from: ${req_url} with method: ${requestOptions["method"]} `
      );
      fetch(req_url, requestOptions)
        .then((response) => {
          console.log("Response:", response);
          return response.json();
        })
        .then((data) => {
          // console.log("...with data:", data);
          this.dipResponse = Number(data["dip"]).toFixed(3);
          this.howUnimodalInPercent = this.howUnimodalInPercent = Math.round(
            (1 - this.dipResponse * 4) * 100
          );
          this.modal_triangle = data["modal_triangle"];
          this.low_high = data["low_high"];
          this.split_index = data["split_index"];
          this.pval_left = Number(data["dip_left"]).toFixed(4);
          this.pval_right = Number(data["dip_right"]).toFixed(4);
          this.pval = Number(data["pval"]).toFixed(4);
          this.ecdf = data["ecdf"];

          this.score = Number(data["score"]).toFixed(2);
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
      this.howUnimodalInPercent = "err";
      this.modal_triangle = "err";
      this.low_high = "err";
      this.split_index = "err";
      this.pval_left = "err";
      this.pval_right = "err";
      this.score = "err";
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
    this.backurl = process.env.VUE_APP_API_URL.trim();
    if (!this.backurl.startsWith("http")) {
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
              Dip: {{ dipResponse }} (or {{howUnimodalInPercent}}%)  Pval: {{ pval }}
              <br />
              Modal Triangle 🟥 {{ modal_triangle }} - Low high 🟦 {{ low_high }}
            </h3>
          </div>
        </div>
        <p id="footnote">Backend: [{{ backurl }}]</p>
      </div>
      <div class="column">
        <div>
          <BarChart :chartData="upperChartData" />
        </div>
        <!-- <h3>
          Split at: {{ split_index }}, pval_left: {{ pval_left }}, pval_right:
          {{ pval_right }}
        </h3>
        <h3>Score (lower is better): {{ this.score }}</h3> -->
        <h3>⬆️        Histogram        ⬆️</h3>
        <h3>⬇️ Cumulative Distribution ⬇️</h3>
        <div>
          <BarChart :chartData="lowerChartData" />
        </div>
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
</style>
