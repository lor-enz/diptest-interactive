import { defineComponent, h, PropType } from 'vue'

import { Bar } from 'vue-chartjs'

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  Plugin
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default defineComponent({
  name: 'BarChart',
  components: {
    Bar
  },
  props: {
    chartId: {
      type: String,
      default: 'bar-chart'
    },
    width: {
      type: Number,
      default: 400
    },
    height: {
      type: Number,
      default: 350
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
    //   type: Array as PropType<Plugin<'bar'>[]>,
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
      h(Bar, {
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
