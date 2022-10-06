var active_graph="portforlio-1d";
document.getElementById("btn-radio-1d").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-1d");
})
document.getElementById("btn-radio-10d").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-10d");
})

function change_graph(old_graph, new_graph) {
    if (old_graph === new_graph) {
        return;
    }
    document.getElementById(old_graph).style.display = "none";
    document.getElementById(new_graph).style.removeProperty("display");
    active_graph = new_graph;
}

const data_1d = {
labels: ["09:30", "09:35", "09:40", "09:45", "09:50", "09:55", "10:00", "09:30", "09:35", "09:40", "09:45", "09:50", "09:55", "10:00", "09:30", "09:35", "09:40", "09:45", "09:50", "09:55", "10:00", "09:30", "09:35", "09:40", "09:45", "09:50", "09:55", "10:00"],
datasets: [
    {
        label: "value",
        backgroundColor: "green",
        borderColor: "green",
        radius: 1,
        data: [0, 10, 5, 2, 20, 30, 41, 15, 10, 5, 2, 20, 30, 33, 15, 10, 5, 2, 20, 30, 35, 37, 38, 39, 45],
    },
    {
        label: "previous close",
        backgroundColor: "green",
        borderColor: "green",
        borderDash: [10, 15],
        radius: 0,
        data: Array(25).fill(5),
    },
]
};

const data_10d = {
    labels: ["10-01", "10-02", "10-04", "10-05", "10-09", "10-11", "10-12", "10-13", "10-14", "10-15"],
    datasets: [
        {
            label: "value",
            backgroundColor: "green",
            borderColor: "green",
            radius: 4,
            data: [0, 10, 5, 2, 20, 30, 45, 15, 10, 5, 2, 20],
        },
    ]
    };

const config_fine = {
    type: "line",
    data: data_1d,
    options: {
        interaction: {
            intersect: false,
        },
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
            grid: {
                display: false,
            }
            }
        }
    }
};

const config_coarse = {
    type: "line",
    data: data_10d,
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
    }
};

new Chart(
    document.getElementById("portforlio-1d"),
    config_fine
);

new Chart(
    document.getElementById("portforlio-10d"),
    config_coarse
);