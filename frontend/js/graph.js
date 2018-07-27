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

/**
 * Add up all the numbers in an array
 */
function sum(arr) {
  return arr.reduce((total, num) => total + num);
}

function drawChart(config) {

  const monthsCovered = Math.min(config.incomes.length, config.expenses.length);

  // Omit future events and convert to thousands
  const incomes = config.incomes.slice(0, monthsCovered).map((val) => {
    return Math.round(val / 1000);
  });
  const expenses = config.expenses.slice(0, monthsCovered).map((val) => {
    return Math.round(val / 1000);
  });

  const nets = range(1, monthsCovered).map((month, index) => {
    const incomeToDate = sum(incomes.slice(0, index + 1));
    const expensesToDate = sum(expenses.slice(0, index + 1));
    return incomeToDate - expensesToDate;
  });

  const myChart = new Chart(document.querySelector(config.element), {
    type: 'line',
    data: {
      labels: months,
      datasets: [{
        label: 'Income',
        data: incomes,
        backgroundColor: 'transparent',
        borderColor: 'darkgreen',
      }, {
        label: 'Expenses',
        data: expenses,
        backgroundColor: 'transparent',
        borderColor: 'maroon',
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
            stepSize: 1,
            callback: (value, index, values) => {
              if (value) {
                value = `${value}k`;
              }
              return value;
            }
          }
        }]
      },
      legend: {
        position: 'bottom',
        usePointStyle: true,
        labels: {
          boxWidth: 10,
        }
      }
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