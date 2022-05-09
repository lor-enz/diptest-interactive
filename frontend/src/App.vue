<script>
import { Chart, Bar } from "vue3-charts";

const startAreaSize = 7;
const zeroAreaSize = 20;

function randomIntFromInterval(min, max) {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}

export default {
  name: "DipTestApp",
  components: {
    Chart,
    Bar,
  },

  // Properties returned from data() becomes reactive state
  // and will be exposed on `this`.
  data() {
    return {
      backurl: "the api url. Filled after mounting with VUE_APP_API_URL environment variable", 
      canvas: null,
      canvasLineInterval: 17,
      axis: {
        primary: {
          type: "band",
          format: (val) => {
            // console.log("val is %s, split_index is %s", val, this.split_index);
            if (val === this.split_index) {
              return ">S<<<";
            }
            return val % 5 == 0 || val == 1 ? val : "";
          },
        },
        secondary: {
          domain: ["dataMin", "dataMax+0.05"],
          type: "linear",
          ticks: 8,
        },
      },
      chartSize: {
        width: 530,
        height: 380
      },

      points: [], // pixelcoordinates of drawn line start/endpoints
      chartDataHistogram: [
        // data feed for top chart
        { x: "Draw", y: 400 },
        { x: "something", y: 200 },
        { x: "in", y: 100 },
        { x: "the ", y: 50 },
        { x: "canvas", y: 25 },
      ],
      chartDataCumulative: [
        // data feed for bottom chart
        { x: "Draw", y: 25 },
        { x: "something", y: 50 },
        { x: "in", y: 100 },
        { x: "the ", y: 200 },
        { x: "canvas", y: 400 },
      ],
      copyPasteData: [], // same as chartDataCumulative but only the y values in a list.
      dipResponse: 0, // dip value between 0 and 0.25
      howUnimodalInPercent: 0,
      split_index: 0,
      dip_left: 0,
      dip_right: 0,
      score: 0,
    };
  },

  // Methods are functions that mutate state and trigger updates.
  // They can be bound as event listeners in templates.
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
          Math.round(e.offsetX / this.canvasLineInterval) *
          this.canvasLineInterval;
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
      var canv = document.getElementById("myCanvas");
      this.canvas.clearRect(0, 0, canv.width, canv.height);
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
      var c = document.getElementById("myCanvas");
      newY = c.height - newY;

      if (this.points.length === 0) {
        this.points.push([newX, newY]);
      }
      var [lastX, lastY] = this.points[this.points.length - 1];
      if (lastX !== newX) {
        this.points.push([newX, newY]);
      }
    },
    createChartData() {
      // Change from canvas pixel coordinates (that are top to bottom) to something coordinate data like
      const map = Array.prototype.map;
      var points = map.call(this.points, (element) => {
        let [x, y] = element;
        return [x / this.canvasLineInterval + 1, y];
      });
      // Chart data
      var chartDataHistogram = [];
      points.forEach(function ([x1, y1], index) {
        chartDataHistogram.push({ x: index + 1, y: y1 });
      });
      // Actual CDF (cumulative distribution funciton)
      var chartDataCumulative = [];
      var totalsum = 0;
      chartDataHistogram.forEach(function (dict, index) {
        totalsum = totalsum + dict["y"];
      });
      var sum = 0;
      chartDataHistogram.forEach(function (dict, index) {
        sum = sum + dict["y"];
        chartDataCumulative.push({ x: index + 1, y: sum / totalsum });
      });
      this.chartDataHistogram = chartDataHistogram;
      this.chartDataCumulative = chartDataCumulative;
    },
    convertCanvasData() {
      console.log("convert()");
      this.createChartData();
      // copyPasteData
      var copyPasteData = [];
      this.chartDataCumulative.forEach(function (dict, index) {
        copyPasteData.push(dict["y"] * 100);
      });
      this.copyPasteData = copyPasteData;
      this.requestDipValue();
    },
    copy() {
      this.$refs.myinput.focus();
      document.execCommand("copy");
    },

    async requestDipValue() {
      const requestOptions = {
        method: "CALC",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(this.copyPasteData),
      };
      var req_url = `${this.backurl}/findsplit`
      console.log(`fetching from: ${req_url} with method: ${requestOptions["method"]} `)
      fetch(req_url, requestOptions)
        .then((response) => {
          console.log("resolved", response);
          return response.json();
        })
        .then((data) => {
          console.log(data);
          this.dipResponse = Number(data["dip_everything"]).toFixed(3);
          this.howUnimodalInPercent = this.howUnimodalInPercent = Math.round(
            (1 - this.dipResponse * 4) * 100
          );
          this.split_index = data["split_index"];
          this.dip_left = Number(data["dip_left"]).toFixed(2);
          this.dip_right = Number(data["dip_right"]).toFixed(2);
          this.score = Number(data["score"]).toFixed(2);
          this.createChartData(); // Yes calling it a second time after drawing. On purpose.
        })
        .catch((err) => {
          console.error("error retrieving data", err);
        });
    },
  },

  // Lifecycle hooks are called at different stages
  // of a component's lifecycle.
  // This function will be called when the component is mounted.
  mounted() {
    this.canv = document.getElementById("myCanvas");
    this.canvas = this.canv.getContext("2d");
    this.clear();
    console.log("----------------------------------MOUNTED-------------------------------------------")
    this.backurl = (process.env.VUE_APP_API_URL).trim()
    if (!this.backurl.startsWith('http')) {
        this.backurl = `http://${this.backurl}`
    }
    console.log(this.backurl)
  },
};
</script>

<template>
  <div id="app">
    <h1>Diptest Tool</h1>
    <div class="row">
      <div class="column">
        
    
        <h2>How to</h2>
        <p>
          Move your mouse cursor from the yellow start area on the leftof the canvas to the
          right end of the canvas. <br />
          No need to click! <br />
          Once the mourse cursor leaves the canvas the trail the mousecursor left, will be converted into data for the charts on the right.
        </p>
        <h2>Canvas</h2>
        <canvas
          id="myCanvas"
          width="800"
          height="500"
          @mousemove="keepDrawing"
          @mousedown="keepDrawing"
          @mouseleave="convertCanvasData"
        />
        <div class="row">
          <div class="column">
            <h2>
              Dip Value: {{ dipResponse }} Unimodal: {{ howUnimodalInPercent }}%
            </h2>
            <p id="centeredparagraph"> Copy CDF values for your own use</p>
            <input
              v-on:focus="$event.target.select()"
              ref="myinput"
              readonly
              :value="copyPasteData"
            />
            <button @click="copy">Copy</button>
          </div>
        </div>
        <p id="footnote"> Backend: [{{ backurl }}] </p>
      </div>
      <div class="column">
        <Chart
          :data="chartDataHistogram"
          :margin="margin"
          :direction="direction"
          :axis="axis"
          :size="chartSize"
        >
          <template #layers>
            <Bar
              :dataKeys="['x', 'y']"
              :barStyle="{ fill: '#889542' }"
            /> </template
        ></Chart>
        <h3>
          Split at: {{ split_index }}, dip_left: {{ dip_left }}, dip_right:
          {{ dip_right }}
        </h3>
        <h3>
          Score: {{this.score}}
        </h3>
        <Chart
          :data="chartDataCumulative"
          :margin="margin"
          :direction="direction"
          :axis="axis"
          :size="chartSize"
        >
          <template #layers>
            <Bar
              :dataKeys="['x', 'y']"
              :barStyle="{ fill: '#889542' }"
            /> </template
        ></Chart>
      </div>
    </div>
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
}

#centeredparagraph {
  text-align: center;
}

</style>
