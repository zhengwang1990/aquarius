function get_dataset(timeframe, processor) {
    const values = GL_BARS["values"][timeframe][processor];
    var colors = [];
    for (value of values) {
        colors.push(value >= 0 ? "rgb(5,170,40)": "rgb(237,73,55)");
    }
    return {label: 'G/L', data: values, backgroundColor: colors};
}

const gl_config = {
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
const gl_chart = new Chart(document.getElementById("graph-gl-all"), gl_config);
const processor_select = document.getElementById("processor-select");
const timeframe_select = document.getElementById("timeframe-select");

function update_gl_chart() {
    gl_chart.data = {
        labels: GL_BARS["labels"][timeframe_select.value],
        datasets: [get_dataset(timeframe_select.value, processor_select.value)]
    }
    gl_chart.update();
}
update_gl_chart();
for (select of [processor_select, timeframe_select]) {
    select.addEventListener("change", function(event){
        update_gl_chart();
    });
}

var trans_label = [];
var trans_value = [];
for (entry of TRANSACTION_CNT) {
    trans_label.push(entry["processor"]);
    trans_value.push(entry["cnt"]);
}
const trans_cnt_config = {
    type: "pie",
    data:  {
        labels: trans_label,
        datasets: [
            {
              label: '',
              data: trans_value,
              backgroundColor: ["#4890e8", "#4fdba8", "#915bde", "#fabe57", "#1bd1cf", "#eb624d", "#8f8f7f"]
            }
        ]
    },
    options: {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
            legend: {position: "top"}
        }
    }
};

const trans_chart = new Chart(document.getElementById("graph-trans-cnt"), trans_cnt_config);

var annual_return_datasets = [];
const symbol_colors = {
    "my portfolio": "rgb(62, 110, 186)",
    "qqq": "rgb(11, 166, 188)",
    "spy": "rgb(215, 150, 40)",
};
for (var i = 0; i < ANNUAL_RETURN["symbols"].length; i++) {
    const symbol = ANNUAL_RETURN["symbols"][i];
    annual_return_datasets.push({
        label: symbol,
        data: ANNUAL_RETURN["returns"][i],
        backgroundColor: symbol_colors[symbol.toLowerCase()]
    });
}
const annual_return_config = {
    type: "bar",
    data: {
        labels: ANNUAL_RETURN["years"],
        datasets: annual_return_datasets
    },
    options: {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
            legend: {position: "top"},
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y.toFixed(2) + '%';
                        }
                        return label;
                    }
                }
            }
        }
    },
};
const annual_return_chart = new Chart(document.getElementById("graph-annual-return"), annual_return_config);