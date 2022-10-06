var active_graph="portforlio-1d";
document.getElementById("btn-radio-1d").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-1d");
});
document.getElementById("btn-radio-10d").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-10d");
});
document.getElementById("btn-radio-1m").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-1m");
});
document.getElementById("btn-radio-6m").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-6m");
});
document.getElementById("btn-radio-1y").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-1y");
});
document.getElementById("btn-radio-5y").addEventListener("click", () => {
    change_graph(active_graph, "portforlio-5y");
});


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

const data_1m = {
    labels: ["10-01", "10-02", "10-04", "10-05", "10-09", "10-11", "10-12", "10-13", "10-14", "10-15", "10-17", "10-18"],
    datasets: [
        {
            label: "value",
            backgroundColor: "green",
            borderColor: "green",
            radius: 4,
            data: [7, 10,0, 10, 5, 2, 20, 30, 45, 15, 10, 5, 2, 20],
        },
    ]
};

const data_6m = {
    labels: ["01-01", "01-25", "02-11", "03-05", "04-09", "05-11", "06-12", "07-13", "08-12", "09-15", "09-17", "09-18", "10-11", "10-12", "10-13", "10-14", "10-15", "10-17", "10-18"],
    datasets: [
        {
            label: "value",
            backgroundColor: "green",
            borderColor: "green",
            radius: 1,
            data: [7, 10,0, 32, 5, 2, 20, 30, 45, 15, 10, 5, 2, 20, 7, 10,0, 10, 5, 2, 20, 30, 45, 15, 10, 5, 2, 20],
        },
    ]
};

const data_1y = {
    labels: ["2022-01-01", "", "", "2022-02-02", "", "", "2022-03-04", "", "", "2022-04-01", "", "", "2022-05-01", "", "", "2022-06-01", "", "", "2022-10-01"],
    datasets: [
        {
            label: "value",
            backgroundColor: "green",
            borderColor: "green",
            radius: 1,
            data: [7, 10,0, 32, 5, 2, 20, 30, 45, 15, 10, 5, 2, 15, 7, 23,0, 10, 5, 2, 1, 32, 44, 1, 10, 5, 24, 11],
        },
    ]
};

const data_5y = {
    labels: ["01-01", "01-25", "02-11", "03-05", "04-09", "05-11", "06-12", "07-13", "08-12", "09-15", "09-17", "09-18", "10-11", "10-12", "10-13", "10-14", "10-15", "10-17", "10-18"],
    datasets: [
        {
            label: "value",
            backgroundColor: "red",
            borderColor: "red",
            radius: 1,
            data: [7, 10,0, 32, 5, 2, 20, 30, 45, 15, 10, 5, 2, 20, 7, 10,0, 10, 5, 2, 20, 30, 45, 15, 10, 5, 2, 20],
        },
    ]
};

const config_fine = {
    type: "line",
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

const config_1d = {data: data_1d};
Object.assign(config_1d, config_fine);
new Chart(document.getElementById("portforlio-1d"), config_1d);

const config_10d = {data: data_10d};
Object.assign(config_10d, config_coarse);
new Chart(document.getElementById("portforlio-10d"), config_10d);

const config_1m = {data: data_1m};
Object.assign(config_1m, config_coarse);
new Chart(document.getElementById("portforlio-1m"), config_1m);

const config_6m = {data: data_6m};
Object.assign(config_6m, config_fine);
new Chart(document.getElementById("portforlio-6m"), config_6m);

const config_1y = {data: data_1y};
Object.assign(config_1y, config_fine);
new Chart(document.getElementById("portforlio-1y"), config_1y);

const config_5y = {data: data_5y};
Object.assign(config_5y, config_fine);
new Chart(document.getElementById("portforlio-5y"), config_5y);