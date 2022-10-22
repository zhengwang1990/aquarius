let current_timeframe = sessionStorage.getItem("timeframe");
let current_compares = sessionStorage.getItem("compares");
if (!current_timeframe) current_timeframe = "1d";
const graph_timeframes = ["1d", "1w", "1m", "6m", "1y", "5y"];
const compare_symbols = ["qqq", "spy", "tqqq"];
document.getElementById("current-equity").innerHTML = HISTORIES["current_equity"];

var active_timeframe = null;
var active_compares = new Set();
var charts = {};
const graph_point_radius = {
    "1d": 0, "1w": 3, "1m": 3,
    "6m": 0, "1y": 0, "5y": 0,
};
const symbol_colors = {
    "qqq": "rgb(11, 166, 188)",
    "qqqlight": "rgba(11, 166, 188, 0.25)",
    "spy": "rgb(215, 150, 40)",
    "spylight": "rgba(215, 150, 40, 0.25)",
    "tqqq": "rgb(170, 70, 190)",
    "tqqqlight": "rgba(170, 70, 190, 0.25)",
};

function change_timeframe(timeframe) {
    if (active_timeframe === timeframe) {
        return;
    }
    if (active_timeframe) {
        document.getElementById("graph-" + active_timeframe).style.display = "none";
        document.getElementById("btn-" + active_timeframe).classList.remove("active");
    }
    document.getElementById("graph-" + timeframe).style.removeProperty("display");
    document.getElementById("current-change").innerHTML = HISTORIES["change_" + timeframe];
    document.getElementById("btn-" + timeframe).classList.add("active");
    active_timeframe = timeframe;
    sessionStorage.setItem("timeframe", active_timeframe);
}

function change_compare(symbol) {
    document.getElementById("btn-" + symbol).classList.toggle("active");
    if (active_compares.has(symbol)) {
        active_compares.delete(symbol);
        for (const timeframe of graph_timeframes) {
            for (var i = 0; i < charts[timeframe].data.datasets.length; i++) {
                if (charts[timeframe].data.datasets[i].label === symbol.toUpperCase()) {
                    charts[timeframe].data.datasets.splice(i, 1);
                    break;
                }
            }
            charts[timeframe].update();
        }
    } else {
        active_compares.add(symbol);
        for (const timeframe of graph_timeframes) {
            dataset = {
                label: symbol.toUpperCase(),
                backgroundColor: symbol_colors[symbol],
                borderColor: symbol_colors[symbol],
                borderWidth: 2,
                radius: graph_point_radius[timeframe],
                data: HISTORIES[symbol + "_" + timeframe],
            };
            if (timeframe === "1d") {
                dataset.segment = {
                    borderColor:
                     ctx => HISTORIES["time_1d"][ctx.p1DataIndex] > HISTORIES['market_close'] ? symbol_colors[symbol + "light"] : undefined,
                };
            }
            charts[timeframe].data.datasets.push(dataset);
            charts[timeframe].update();
        }
    }
    sessionStorage.setItem("compares", JSON.stringify(Array.from(active_compares)));
}

change_timeframe(current_timeframe);
for (const timeframe of graph_timeframes) {
    document.getElementById("btn-" + timeframe).addEventListener("click", () => {
        change_timeframe(timeframe);
    });
}
for (const symbol of compare_symbols) {
     document.getElementById("btn-" + symbol).addEventListener("click", () => {
        change_compare(symbol);
    });
}

var graph_data = {}
for (const timeframe of graph_timeframes) {
    graph_data[timeframe] = {
        labels: HISTORIES["time_" + timeframe],
        datasets: [
            {
                label: "value",
                backgroundColor: HISTORIES["color_" + timeframe],
                borderColor: HISTORIES["color_" + timeframe],
                borderWidth: 2,
                radius: graph_point_radius[timeframe],
                data: HISTORIES["equity_" + timeframe],
            },
        ],
    };
}

const light_color = HISTORIES["color_1d"] === "red" ? "rgba(252, 0, 0, 0.25)" : "rgba(0, 128, 0, 0.25)";
graph_data["1d"].datasets[0].segment = {
    borderColor: ctx => HISTORIES["time_1d"][ctx.p1DataIndex] > HISTORIES['market_close'] ? light_color : undefined,
};
graph_data["1d"].datasets.push({
    label: "previous close",
    borderColor: 'grey',
    borderDash: [6, 6],
    borderWidth: 1,
    radius: 0,
    data: Array(HISTORIES["time_1d"].length).fill(HISTORIES["prev_close"]),
});

const config_base = {
    type: "line",
    options: {
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
        },
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
            }
        },
        spanGaps: true,
    }
};

for (const timeframe of graph_timeframes) {
    var config = {data: graph_data[timeframe]};
    Object.assign(config, config_base);
    charts[timeframe] = new Chart(document.getElementById("graph-" + timeframe), config);
}

if (current_compares !== null) {
    for (const symbol of JSON.parse(current_compares)) {
        change_compare(symbol);
    }
}