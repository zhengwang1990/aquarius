function get_dataset(processor) {
    const values = GL_BARS["values"][processor];
    var colors = [];
    for (value of values) {
        colors.push(value >= 0 ? "rgb(5,170,40)": "rgb(237,73,55)");
    }
    return {label: 'G/L', data: values, backgroundColor: colors};
}

const gl_data = {
    labels: GL_BARS["dates"],
    datasets: [get_dataset("ALL PROCESSORS")]
};
const config = {
    type: 'bar',
    data: gl_data,
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
processor_select.addEventListener("change", function(event){
    chart.data.datasets = [get_dataset(event.target.value)];
    chart.update()
});