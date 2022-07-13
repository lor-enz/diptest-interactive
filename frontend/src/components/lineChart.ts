import { defineComponent, h, PropType } from 'vue'
import { Line } from 'vue-chartjs'

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement, // can we remove LineElement?
  CategoryScale,
  LinearScale,
  Plugin,
  LineController,
  PointElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, LineController, PointElement)

export default defineComponent({
  name: 'LineChart',
  components: {
    Line
  },
  props: {
    chartId: {
      type: String,
      default: 'line-chart'
    },
    width: {
      type: Number,
      default: 400
    },
    height: {
      type: Number,
      default: 365
    },
    cssClasses: {
      default: '',
      type: String
    },
    styles: {
    //   type: Object as PropType<Partial<CSSStyleDeclaration>>,
    //   default: () => {}
    },
    plugins: {
    //   type: Array as PropType<Plugin<'line'>[]>,
    //   default: () => []
    }
  },
  setup(props) {
    const chartData = { }

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      events: [], // disable everything on hover
      animation: {
        duration: 400,
      },
      plugins: {
        legend: {
          display: false,
        },
      },
      scaleShowValues: true,
      scales: {
        x: {
          ticks: {
            autoSkip: false
          },
          grid: {
            display: false,
          },
        },
        y: {
          grid: {
            display: false,
          },
        },
      },
    }

    return () =>
      h(Line, {
        chartData,
        chartOptions,
        chartId: props.chartId,
        width: props.width,
        height: props.height,
        cssClasses: props.cssClasses,
        styles: props.styles,
        plugins: props.plugins
      })
  }
})
