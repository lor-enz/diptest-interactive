<script>
import { Chart, Bar } from "vue3-charts";

const startAreaSize = 7;
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
      myData: [],
      chartData: [
        { x: "Draw", y: 100 },
        { x: "something", y: 50 },
        { x: "above", y: 25 },
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
        this.drawLine(this.x, this.y, newX, e.offsetY);
        this.x = newX;
        this.y = e.offsetY;
        this.maybeAddPoint(newX, e.offsetY);
      }
    },
    clear() {
      var canv = document.getElementById("myCanvas");
      this.canvas.clearRect(0, 0, canv.width, canv.height);
      this.x = 0;
      this.points = [];
      // grey marked area
      this.canvas.fillStyle = "#ffe291";
      this.canvas.fillRect(0, 0, startAreaSize, this.canv.height);
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
      const map = Array.prototype.map;
      var points = map.call(this.points, (element) => {
        let [x, y] = element;
        return [x / 20 + 1, y];
      });
      var myData = [];
      points.forEach(function ([x, y], index) {
        for (var i = 0; i < y; i++) {
          myData.push(x);
        }
      });
      this.myData = myData;
      // Do more stuff
      var chartData = [];
      points.forEach(function ([x1, y1], index) {
        chartData.push({ x: x1, y: y1 });
      });
      this.chartData = chartData;
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
    <h2>Canvas</h2>
    <div class="row">
      <div class="column">
        <canvas
          id="myCanvas"
          width="800"
          height="500"
          @mousemove="keepDrawing"
          @mousedown="keepDrawing"
          @mouseleave="convert"
        />
      </div>
      <div class="column">
        <Chart :data="chartData" :margin="margin" :direction="direction">
          <template #layers>
            <Bar :dataKeys="['x', 'y']" :barStyle="{ fill: '#586d2a' }" />

            template> Chart> div>
          </template></Chart
        >
      </div>
    </div>
    <br />
    <input
      v-on:focus="$event.target.select()"
      ref="myinput"
      readonly
      :value="myData"
    />
    <button @click="copy">Copy</button>
  </div>
  <div>
    <h2>How to</h2>
    <p>
      The large white box on the left is the canvas. Move your Mouse cursor from
      the yellow start area on the left to the right end of the canvas. Your
      mouse will leave a trail, you don't need to click any mouse button while
      doing so! Once the mourse cursor leaves the canvas the line you drew will
      be converted into a bar chart, visible below.
    </p>
    <p>
      {{ chartData }}
    </p>
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
  font-size: 20px;
}

.row {
  display: flex;
}

.column {
  flex: 50%;
}
</style>

