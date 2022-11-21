const elem = document.getElementById("datepicker");
const datepicker = new Datepicker(elem, {
    autohide: true,
    format: "M dd yyyy",
    maxDate: new Date(),
    daysOfWeekDisabled: [0, 6]
});

// Global variables
var chart_mode = null;
var chart_data = null;
var trimmed_chart_data = null;
var chart = null;

if (window.innerWidth <= 800) {
    chart_mode = "compact";
} else {
    chart_mode = "full";
}

const candlestick = {
    id: "candlestick",
    beforeDatasetsDraw(chart, args, pluginOptions) {
        const { ctx, data, scales: { y } } = chart;
        ctx.save();
        ctx.lineWidth = chart_mode === "compact" ? 0.5 : 1;
        ctx.strokeStyle = "black";

        data.datasets[0].data.forEach((dataPoint, index) => {
            const bar_top = Math.max(dataPoint.c, dataPoint.o);
            const bar_bottom = Math.min(dataPoint.c, dataPoint.o);
            const x = chart.getDatasetMeta(0).data[index].x;

            ctx.beginPath();
            ctx.moveTo(x, y.getPixelForValue(bar_top));
            ctx.lineTo(x, y.getPixelForValue(dataPoint.h));
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(x, y.getPixelForValue(bar_bottom));
            ctx.lineTo(x, y.getPixelForValue(dataPoint.l));
            ctx.stroke();
        });
    }
};

function get_chart_data() {
    var date = "2022-11-18";
    var symbol = "QQQ";
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", `/charts?date=${date}&symbol=${symbol}`, false);
    xmlHttp.send(null);
    var res = xmlHttp.responseText;
    var obj = JSON.parse(res);
    chart_data = obj;
    trimmed_chart_data = {
        labels: [],
        values: [],
        prev_close: chart_data["prev_close"]
    }
    for (var i = 0; i < chart_data["labels"].length; i++) {
        var label = chart_data["labels"][i];
        if (label >= "09:30" && label < "16:00") {
            trimmed_chart_data.labels.push(label);
            trimmed_chart_data.values.push(chart_data["values"][i]);
        }
    }
}

function get_chart() {
    get_chart_data();
    update_chart();
}

function update_chart() {
    var current_data = chart_mode === "compact" ? trimmed_chart_data : chart_data;
    const data = {
        labels: current_data["labels"],
        datasets: [{
            data: current_data["values"],
            backgroundColor: (ctx) => {
                const { raw: {x, o, c} } = ctx;
                let color, alpha;
                if (x < "09:30" || x >= "16:00") {
                    alpha = 0.3;
                } else {
                    alpha = 0.9;
                }
                if (c >= o) {
                    color = `rgba(5, 170, 40, ${alpha})`;
                } else {
                    color = `rgba(237, 73, 55, ${alpha})`;
                }
                return color;
            },
            borderColor: "black",
            borderWidth: chart_mode === "compact" ? 0.5 : 1,
            borderSkipped: false
        }]
    };
    const prev_close_annotation = {
        type: "line",
        borderWidth: chart_mode === "compact" ? 0.5 : 1,
        borderColor: "rgba(141, 141, 141, 0.3)",
        borderDash: [6, 6],
        scaleID: "y",
        value: current_data["prev_close"],
        label: {
            display: chart_mode === "full",
            backgroundColor: "rgba(100, 100, 100, 0.5)",
            content: `previous close ${current_data["prev_close"].toFixed(2)}`,
            position: "end"
        }
    };
    const chart_config = {
        type: "bar",
        data: data,
        options: {
            maintainAspectRatio: false,
            interaction: {
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        beforeBody: (ctx) => {
                            return [
                                `O: ${ctx[0].raw.o.toFixed(2)}`,
                                `H: ${ctx[0].raw.h.toFixed(2)}`,
                                `L: ${ctx[0].raw.l.toFixed(2)}`,
                                `C: ${ctx[0].raw.c.toFixed(2)}`
                            ];
                        },
                        label: (ctx) => {
                            return '';
                        }
                    }
                },
                annotation: {
                    annotations: [prev_close_annotation]
                }
            },
            parsing: {
                xAxisKey: "x",
                yAxisKey: "s"
            },
            scales: {
                x: {
                    ticks: {
                        autoSkip: true,
                        autoSkipPadding: 15,
                        maxRotation: 0
                    }
                },
                y: {
                    beginAtZero: false
                }
            }
        },
        plugins: [candlestick]
    };
    if (chart === null) {
        chart = new Chart(document.getElementById("graph-charts"), chart_config);
    } else {
        chart.data = chart_config.data;
        chart.options = chart_config.options;
        chart.plugins = chart_config.plugins;
        chart.update();
    }
}

document.getElementById("chart-btn").addEventListener("click", get_chart);

window.addEventListener("resize", function(event) {
    const width = window.innerWidth;
    if (width <= 1300) {
        if (chart_mode !== "compact") {
            chart_mode = "compact";
            update_chart();
        }
    } else {
        if (chart_mode !== "full") {
            chart_mode = "full";
            update_chart();
        }
    }
}, true);