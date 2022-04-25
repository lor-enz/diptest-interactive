<script>
import { Chart, Bar } from "vue3-charts";

const startAreaSize = 7;
const zeroAreaSize = 10;
function randomIntFromInterval(min, max) { // min and max included 
  return Math.floor(Math.random() * (max - min + 1) + min)
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
      count: 0,
      canvas: null,
      points: [],
      copyPasteData: [],
      chartDataHistogram: [
        { x: "Draw", y: 400 },
        { x: "something", y: 200 },
        { x: "in", y: 100 },
        { x: "the ", y: 50 },
        { x: "canvas", y: 25 },
      ],
      chartDataCumulative: [
        { x: "Draw", y: 25 },
        { x: "something", y: 50 },
        { x: "in", y: 100 },
        { x: "the ", y: 200 },
        { x: "canvas", y: 400 },
      ],
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
        var newX = Math.round(e.offsetX / 20) * 20;
        var newY = (e.offsetY >= this.canv.height - zeroAreaSize) ? randomIntFromInterval(this.canv.height-5,this.canv.height) : e.offsetY
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
      this.canvas.fillRect(0, this.canv.height-zeroAreaSize, this.canv.width, zeroAreaSize);
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
    convert() {
      console.log("convert()");
      // Change from canvas pixel coordinates (that are top to bottom) to something coordinate data like
      const map = Array.prototype.map;
      var points = map.call(this.points, (element) => {
        let [x, y] = element;
        return [x / 20 + 1, y];
      });
      // Chart data
      var chartDataHistogram = [];
      points.forEach(function ([x1, y1], index) {
        chartDataHistogram.push({ x: x1, y: y1 });
      });
      this.chartDataHistogram = chartDataHistogram;
      // Actual CDF (cumulative distribution funciton)
      var chartDataCumulative = [];
      var totalsum = 0;
      points.forEach(function ([x1, y1], index) {
          totalsum = totalsum + y1
      });
      var sum = 0;
      points.forEach(function ([x1, y1], index) {
        sum = sum + y1
        chartDataCumulative.push({ x: x1, y: sum / totalsum });
      });
      this.chartDataCumulative = chartDataCumulative;
      // copyPasteData
      var copyPasteData = []
      chartDataCumulative.forEach(function (dict, index) {
        copyPasteData.push(dict['y']*100);
      });
      this.copyPasteData = copyPasteData
    },
    copy() {
      this.$refs.myinput.focus();
      document.execCommand("copy");
    },
  },

  // Lifecycle hooks are called at different stages
  // of a component's lifecycle.
  // This function will be called when the component is mounted.
  mounted() {
    this.canv = document.getElementById("myCanvas");
    this.canvas = this.canv.getContext("2d");
    this.clear();
  },
};
</script>

<template>
  <div>
    <h1>Line to Histogram</h1>
    
    <div>
    
    <p>
      
    </p>
  </div>
    <div class="row">
      <div class="column">
        <h2>How to</h2>
        <p>
          The large white box below is the canvas. <br> 
          Move your Mouse cursor from the yellow start area on the left to the right end of the canvas. <br>
          No need to click! <br> Your mouse will leave a trail, you don't need to click any mouse button while
          doing so! Once the mourse cursor leaves the canvas the line you drew will
          be converted into data for the charts on the right.
        </p>
        <h2>Canvas</h2>
        <canvas
          id="myCanvas"
          width="800"
          height="500"
          @mousemove="keepDrawing"
          @mousedown="keepDrawing"
          @mouseleave="convert"
        />
        <input
          v-on:focus="$event.target.select()"
          ref="myinput"
          readonly
          :value="copyPasteData"
        />
        <button @click="copy">Copy</button>
      </div>
      <div class="column">
        <Chart :data="chartDataHistogram" :margin="margin" :direction="direction">
          <template #layers>
            <Bar :dataKeys="['x', 'y']" :barStyle="{ fill: '#586d2a' }" />

            template> Chart> div>
          </template></Chart
        >
        <Chart :data="chartDataCumulative" :margin="margin" :direction="direction">
          <template #layers>
            <Bar :dataKeys="['x', 'y']" :barStyle="{ fill: '#586d2a' }" />

            template> Chart> div>
          </template></Chart
        >
      </div>
    </div>
    <br />
    
    <br />
    
  </div>
  
</template>

<style scoped>
#myCanvas {
  border: 1px solid grey;
}

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
</style>

