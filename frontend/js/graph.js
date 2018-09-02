const lib = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.min.js';

const months = [
  'Jan.',
  'Feb.',
  'March',
  'April',
  'May',
  'June',
  'July',
  'Aug.',
  'Sept.',
  'Oct.',
  'Nov.',
  'Dec.',
]

function range(start, end, increment) {
  if (increment === undefined) {
    increment = 1;
  }

  const result = [];
  for (var i = start; i <= end; i++) {
    result.push(i);
  }
  return result
}

function roundDecimal(num, places) {
  num = num.toFixed(places);
  return parseFloat(num);
}

/**
 * Add up all the numbers in an array
 */
function sum(arr) {
  return arr.reduce((total, num) => total + num);
}

function drawChart(config) {

  const monthsCovered = Math.min(
                          config.data.incomes.filter((i) => i > 0).length,
                          config.data.expenses.filter((i) => i > 0).length
                        );

  // Omit future events
  const incomes = config.data.incomes.slice(0, monthsCovered);
  const expenses = config.data.expenses.slice(0, monthsCovered);

  const incomes_normal = config.data.incomes_normal.slice(0, monthsCovered);
  const incomes_one_off = config.data.incomes_one_off.slice(0, monthsCovered);
  const expenses_normal = config.data.expenses_normal.slice(0, monthsCovered);
  const expenses_one_off = config.data.expenses_one_off.slice(0, monthsCovered);

  const nets = range(1, monthsCovered).map((month, index) => {
    const incomeToDate = sum(incomes.slice(0, index + 1));
    const expensesToDate = sum(expenses.slice(0, index + 1));
    return incomeToDate - expensesToDate;
  });

  const chart = new Chart(document.querySelector(config.element), {
    type: 'line',
    data: {
      labels: months,
      datasets: [{
        label: 'All Income',
        data: incomes,
        backgroundColor: 'transparent',
        borderColor: 'darkgreen',
      }, {
        label: 'One off Income',
        data: incomes_one_off,
        backgroundColor: 'transparent',
        borderColor: 'rgba(0, 0, 128, .2)',  // Blue 20%
      }, {
        label: 'Normal Income',
        data: incomes_normal,
        backgroundColor: 'transparent',
        borderColor: 'rgba(0, 100, 0, .2)',  // Dark green 20%
      }, {
        label: 'All Expenses',
        data: expenses,
        backgroundColor: 'transparent',
        borderColor: 'maroon',
      }, {
        label: 'Normal Expenses',
        data: expenses_normal,
        backgroundColor: 'transparent',
        borderColor: 'rgba(128, 0, 0, .2)',  // Maroon 20%
      }, {
        label: 'One Off Expenses',
        data: expenses_one_off,
        backgroundColor: 'transparent',
        borderColor: 'rgba(255, 0, 0, .2)',  // Transparent
      }, {
        label: 'Net',
        data: nets,
        backgroundColor: 'transparent',
        borderColor: 'black',
      }]
    },
    options: {
      responsive: false,
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true,
            stepSize: 1000,
            callback: (value, index, values) => {
              if (value) {
                value = `${value / 1000}k`;
              }
              return value;
            }
          }
        }]
      },
      tooltips: {
        callbacks: {
          label: function(tooltipItem, data) {
            // @see: http://www.chartjs.org/docs/latest/configuration/tooltip.html#tooltip-callbacks
            return tooltipItem.yLabel.toLocaleString("en-US");
          },
          labelColor: function(tooltipItem, chart) {
            const color = chart.config.data.datasets[tooltipItem.datasetIndex].borderColor;
            return {
              borderColor: color,
              backgroundColor: color,
            }
          },
        }
      },
      legend: {
        position: 'bottom',
        usePointStyle: true,
        labels: {
          boxWidth: 10,
        }
      },
      animation: {
          duration: 0, // general animation time
      },
    }
  });
}

export function loadChart() {
  if (!window.chartConfig) {
    return;
  }

  const script = document.createElement('script');
  script.src = lib;
  script.defer = true;
  script.onload = () => drawChart(window.chartConfig);
  document.body.appendChild(script);
}