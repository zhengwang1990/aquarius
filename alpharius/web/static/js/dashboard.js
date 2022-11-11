var active_timeframe = sessionStorage.getItem("timeframe");
if (!active_timeframe) active_timeframe = "1d";
var saved_compares = sessionStorage.getItem("compares");
var active_compares = new Set();
if (saved_compares !== null) {
    for (const symbol of JSON.parse(saved_compares)) {
        active_compares.add(symbol);
    }
}

const graph_timeframes = ["1d", "1w", "1m", "6m", "1y", "5y"];
const compare_symbols = ["qqq", "spy", "tqqq"];
document.getElementById("current-equity").innerHTML = HISTORIES["current_equity"];

const graph_point_radius = {
    "1d": 0, "1w": 3, "1m": 2,
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
    document.getElementById("btn-" + active_timeframe).classList.remove("active");
    document.getElementById("btn-" + timeframe).classList.add("active");
    document.getElementById("current-change").innerHTML = HISTORIES["change_" + timeframe];
    active_timeframe = timeframe;
    sessionStorage.setItem("timeframe", active_timeframe);
}
change_timeframe(active_timeframe);

function change_compare(symbol) {
    document.getElementById("btn-" + symbol).classList.toggle("active");
    if (active_compares.has(symbol)) {
        active_compares.delete(symbol);
    } else {
        active_compares.add(symbol);
    }
    sessionStorage.setItem("compares", JSON.stringify(Array.from(active_compares)));
}
for (const symbol of active_compares.values()) {
    document.getElementById("btn-" + symbol).classList.add("active");
}

var graph_data = {}
for (const timeframe of graph_timeframes) {
    graph_data[timeframe] = [{
        label: "value",
        backgroundColor: HISTORIES["color_" + timeframe],
        borderColor: HISTORIES["color_" + timeframe],
        borderWidth: 2,
        radius: graph_point_radius[timeframe],
        data: HISTORIES["equity_" + timeframe]
    }];
}
const light_color = HISTORIES["color_1d"] === "red" ? "rgba(252, 0, 0, 0.25)" : "rgba(0, 128, 0, 0.25)";
graph_data["1d"][0].segment = {
    borderColor: ctx => HISTORIES["time_1d"][ctx.p1DataIndex] > HISTORIES['market_close'] ? light_color : undefined
};
graph_data["1d"].push({
    label: "previous close",
    borderColor: 'grey',
    borderDash: [6, 6],
    borderWidth: 1,
    radius: 0,
    data: Array(HISTORIES["time_1d"].length).fill(HISTORIES["prev_close"])
});
var symbol_data = {}
for (const timeframe of graph_timeframes) {
    symbol_data[timeframe] = {};
    for (const symbol of compare_symbols) {
        dataset = {
            label: symbol.toUpperCase(),
            backgroundColor: symbol_colors[symbol],
            borderColor: symbol_colors[symbol],
            borderWidth: 2,
            radius: graph_point_radius[timeframe],
            data: HISTORIES[symbol + "_" + timeframe]
        };
        if (timeframe === "1d") {
            dataset.segment = {
                borderColor:
                 ctx => HISTORIES["time_1d"][ctx.p1DataIndex] > HISTORIES['market_close'] ? symbol_colors[symbol + "light"] : undefined
            };
        }
        symbol_data[timeframe][symbol] = dataset;
    }
}

const config = {
    type: "line",
    data: {},
    options: {
        maintainAspectRatio: false,
        interaction: {
            intersect: false
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
                    maxRotation: 0
                }
            }
        },
        spanGaps: true
    }
};
const chart = new Chart(document.getElementById("portfolio-graph"), config);
function update_chart() {
    chart.data = {
        labels: HISTORIES["time_" + active_timeframe],
        datasets: graph_data[active_timeframe].slice()
    }
    for (const symbol of active_compares.values()) {
        chart.data.datasets.push(symbol_data[active_timeframe][symbol]);
    }
    chart.update();
}
update_chart();

for (const timeframe of graph_timeframes) {
    document.getElementById("btn-" + timeframe).addEventListener("click", () => {
        if (active_timeframe === timeframe) {
            return;
        }
        change_timeframe(timeframe);
        update_chart();
    });
}
for (const symbol of compare_symbols) {
     document.getElementById("btn-" + symbol).addEventListener("click", () => {
        change_compare(symbol);
        update_chart();
    });
}

const buttons = document.getElementsByClassName("my-btn-outline");
for (var button of buttons) {
    button.classList.add(isMobile ? "my-btn-outline-no-hover" : "my-btn-outline-hover");
}
