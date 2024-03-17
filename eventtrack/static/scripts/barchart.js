var ctx = document.getElementById('myChart').getContext('2d');

var initialData = {
    labels: ['Tank 1', 'Tank 2'],
    datasets: [{
        label: 'liquid level',
        data: [0, 0],
        backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
        borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
        borderWidth: 1
    }]
};

Chart.defaults.font.size = 14;

var myChart = new Chart(ctx, {
    type: 'bar',
    data: initialData,
    options: {
        plugins: {
            font: {
                size: 20
            },
            title: {
                display: true,
                text: 'Liquid level meters'
            },
            legend: {
                display: false,
                labels: {
                    color: 'rgb(255, 99, 132)'
                }
            }
        },
        scales: {
            y: {
                suggestedMin: 50,
                suggestedMax: 100,
            }
        }
    }
});

function updateChart() {
    fetch('/get_tanks_data/')
    .then(response => response.json())
    .then(data => {
        myChart.data.datasets[0].data = [data.tank1, data.tank2];
        myChart.update();
    })
    .catch(error => console.error('Error:', error));
}

setInterval(updateChart, 1000);