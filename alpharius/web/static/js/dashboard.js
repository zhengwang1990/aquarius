
let current_time_period = localStorage.getItem("time_period");
if (!current_time_period) change_time_period = "1d";
const graph_time_periods = ["1d", "1w", "1m", "6m", "1y", "5y"];

var active_time_period = null;
function change_time_period(time_period) {
    if (active_time_period === time_period) {
        return;
    }
    if (active_time_period) {
        document.getElementById("graph-" + active_time_period).style.display = "none";
    }
    document.getElementById("graph-" + time_period).style.removeProperty("display");
    document.getElementById("currnet-change").style.color = HISTORIES["color_" + time_period];
    document.getElementById("currnet-change").innerHTML = HISTORIES["change_" + time_period];
    active_time_period = time_period;
    localStorage.setItem("time_period", time_period);
}

change_time_period(current_time_period);
document.getElementById("btn-radio-" + active_time_period).checked = true;
for (const time_period of graph_time_periods) {
    document.getElementById("btn-radio-" + time_period).addEventListener("click", () => {
        change_time_period(time_period);
    });
}

const graph_granularity = {
    "1d": "fine", "1w": "coarse", "1m": "coarse",
    "6m": "fine", "1y": "fine", "5y": "fine",
};

var graph_data = {}
for (const time_period of graph_time_periods) {
    graph_data[time_period] = {
        labels: HISTORIES["time_" + time_period],
        datasets: [
            {
                label: "value",
                backgroundColor: HISTORIES["color_" + time_period],
                borderColor: HISTORIES["color_" + time_period],
                radius: graph_granularity[time_period] === "fine" ? 1 : 4,
                data: HISTORIES["equity_" + time_period],
            },
        ],
    };
}
graph_data["1d"]["datasets"].push({
    label: "previous close",
    backgroundColor: HISTORIES["color_1d"],
    borderColor: HISTORIES["color_1d"],
    borderDash: [6, 6],
    radius: 0,
    data: Array(HISTORIES["time_1d"].length).fill(HISTORIES["prev_close"]),
});

const config_coarse = {
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
        }
    }
};
const config_fine = Object.assign({options: {scales: {x: {display: false}}}}, config_coarse);

for (const time_period of graph_time_periods) {
    var config = {data: graph_data[time_period]};
    var base_config = graph_granularity[time_period] === "fine" ? config_fine : config_coarse;
    Object.assign(config, base_config);
    new Chart(document.getElementById("graph-" + time_period), config);
}