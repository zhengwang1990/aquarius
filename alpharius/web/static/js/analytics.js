const values = GL_BARS["values"]["ALL"];
var colors = [];
for (value of values) {
    colors.push(value >= 0 ? "rgb(5,170,40)": "rgb(237,73,55)");
}
console.log(values);
const gl_data = {
    labels: GL_BARS["dates"],
    datasets: [{
        label: 'G/L',
        data: values,
        backgroundColor: colors
    }]
};
console.log(gl_data);
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
new Chart(document.getElementById("graph-gl-all"), config);