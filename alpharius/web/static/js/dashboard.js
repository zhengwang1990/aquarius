let current_time_period = localStorage.getItem("time_period");
if (!current_time_period) current_time_period = "1d";
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
    document.getElementById("current-change").innerHTML = HISTORIES["change_" + time_period];
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

const graph_point_radius = {
    "1d": 0, "1w": 3, "1m": 3,
    "6m": 0, "1y": 0, "5y": 0,
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
                borderWidth: 2,
                radius: graph_point_radius[time_period],
                data: HISTORIES["equity_" + time_period],
            },
        ],
    };
}

const light_color = HISTORIES['color_1d'] === "red" ? 'rgba(252, 0, 0, 0.25)' : 'rgba(0, 128, 0, 0.25)'
graph_data["1d"]["datasets"][0]["segment"] = {
    borderColor: ctx => HISTORIES["time_1d"][ctx.p1DataIndex] > HISTORIES['market_close'] ? light_color : undefined,
};
graph_data["1d"]["datasets"].push({
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
        }
    }
};

for (const time_period of graph_time_periods) {
    var config = {data: graph_data[time_period]};
    Object.assign(config, config_base);
    new Chart(document.getElementById("graph-" + time_period), config);
}