function get_dataset(timeframe, processor) {
    const values = GL_BARS["values"][timeframe][processor];
    var colors = [];
    for (value of values) {
        colors.push(value >= 0 ? "rgb(5,170,40)": "rgb(237,73,55)");
    }
    return {label: 'G/L', data: values, backgroundColor: colors};
}

const config = {
    type: 'bar',
    data: {},
    options: {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
             x: {
                ticks: {
                    autoSkip: true,
                    autoSkipPadding: 15,
                    maxRotation: 0,
                }
            },
            y: {
                beginAtZero: true
            }
        }
    },
};
const chart = new Chart(document.getElementById("graph-gl-all"), config);
const processor_select = document.getElementById("processor-select");
const timeframe_select = document.getElementById("timeframe-select");

function update_chart() {
    chart.data = {
        labels: GL_BARS["labels"][timeframe_select.value],
        datasets: [get_dataset(timeframe_select.value, processor_select.value)]
    }
    chart.update();
}
update_chart();
for (select of [processor_select, timeframe_select]) {
    select.addEventListener("change", function(event){
        update_chart();
    });
}