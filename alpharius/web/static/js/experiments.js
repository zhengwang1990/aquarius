const datepicker_elem = document.getElementById("intraday-datepicker");
const datepicker = new Datepicker(datepicker_elem, {
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
var symbol_tree = {symbols: [], children: {}}
var symbol_input = document.getElementById("intraday-symbol-input");
const symbol_set = new Set(ALL_SYMBOLS)
const intraday_alert = document.getElementById("intraday-alert");
const intraday_chart_container = document.getElementById("intraday-chart-container");

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

function displayAlert(type, message) {
    intraday_chart_container.style.display = "none";
    for (c of intraday_alert.classList.values()) {
        if (c != "alert") {
            intraday_alert.classList.remove(c);
        }
    }
    intraday_alert.classList.add("alert-" + type);
    intraday_alert.innerHTML = message;
    intraday_alert.style.removeProperty("display");
}

function get_chart_data(date, symbol) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", `/charts?date=${date}&symbol=${symbol}`, false);
    xmlHttp.send(null);
    var res = xmlHttp.responseText;
    var obj = JSON.parse(res);
    chart_data = obj;
    trimmed_chart_data = {
        labels: [],
        prices: [],
        volumes: [],
        prev_close: chart_data["prev_close"]
    }
    for (var i = 0; i < chart_data["labels"].length; i++) {
        var label = chart_data["labels"][i];
        if (label >= "09:30" && label < "16:00") {
            trimmed_chart_data.labels.push(label);
            trimmed_chart_data.prices.push(chart_data["prices"][i]);
            trimmed_chart_data.volumes.push(chart_data["volumes"][i]);
        }
    }
}

function get_intraday_chart() {
    var date = datepicker.getDate("yyyy-mm-dd");
    if (date === undefined) {
        displayAlert("danger", "Date must be selected");
        return;
    }
    if (!validateDate(date)) {
        displayAlert("danger", `${date} is not a valid date`);
        return;
    }
    var symbol = symbol_input.value.toUpperCase();
    if (symbol.length === 0) {
        displayAlert("danger", "Symbol must be entered");
        return;
    }
    if (!validateSymbol(symbol)) {
        displayAlert("danger", `${symbol} is not a valid symbol`);
        return;
    }
    get_chart_data(date, symbol);
    update_intraday_chart();
}

function update_intraday_chart() {
    var current_data = chart_mode === "compact" ? trimmed_chart_data : chart_data;
    var prices = current_data["prices"];
    const data = {
        labels: current_data["labels"],
        datasets: [{
            data: prices,
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
            borderSkipped: false,
            barPercentage: 1.8,
            categoryPercentage: 0.8,
            yAxisID: "y"
        }, {
           data: current_data["volumes"],
                backgroundColor: (ctx) => {
                const { raw: {x, g} } = ctx;
                let color, alpha;
                if (x < "09:30" || x >= "16:00") {
                    alpha = 0.3;
                } else {
                    alpha = 0.9;
                }
                if (g == 1) {
                    color = `rgba(5, 170, 40, ${alpha})`;
                } else {
                    color = `rgba(237, 73, 55, ${alpha})`;
                }
                return color;
            },
            borderColor: "black",
            borderWidth: chart_mode === "compact" ? 0.5 : 1,
            yAxisID: "yLower",
            barPercentage: 1.8,
            categoryPercentage: 0.8,
        }]
    };
    var position = "end";
    var prev_close = current_data["prev_close"];
    if (prices.length > 5) {
        var startDistance = 0;
        var endDistance = 0;
        for (var i = 0; i < 5; i++) {
            startDistance += Math.abs(prices[i].c - prev_close);
            endDistance += Math.abs(prices[prices.length - 1 - i].c - prev_close);
        }
        if (startDistance > endDistance) {
            position = "start";
        }
    }
    const prev_close_annotation = {
        type: "line",
        borderWidth: chart_mode === "compact" ? 0.5 : 1,
        borderColor: "rgba(141, 141, 141, 0.3)",
        borderDash: [6, 6],
        scaleID: "y",
        value: current_data["prev_close"],
        label: {
            display: chart_mode === "full",
            backgroundColor: "rgba(100, 100, 100, 0.7)",
            content: `previous close ${prev_close.toFixed(2)}`,
            position: position
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
            parsing: {
                xAxisKey: "x",
                yAxisKey: "s"
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        beforeBody: (ctx) => {
                            if (ctx[0].raw.o !== undefined) {
                                return [
                                    `O: ${ctx[0].raw.o.toFixed(2)}`,
                                    `H: ${ctx[0].raw.h.toFixed(2)}`,
                                    `L: ${ctx[0].raw.l.toFixed(2)}`,
                                    `C: ${ctx[0].raw.c.toFixed(2)}`
                                ];
                            } else {
                                return `Volume: ${ctx[0].raw.s}`
                            }
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
            scales: {
                x: {
                    ticks: {
                        autoSkip: true,
                        autoSkipPadding: 15,
                        maxRotation: 0
                    }
                },
                yLower: {
                    beginAtZero: true,
                    stack: "yScale",
                    stackWeight: 1,
                    ticks: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: false,
                    stack: "yScale",
                    stackWeight: 4
                }
            }
        },
        plugins: [candlestick]
    };
    intraday_alert.style.display = "none";
    intraday_chart_container.style.removeProperty("display");
    if (chart === null) {
        chart = new Chart(document.getElementById("graph-intraday-chart"), chart_config);
    } else {
        chart.data = chart_config.data;
        chart.options = chart_config.options;
        chart.plugins = chart_config.plugins;
        chart.update();
    }
}

document.getElementById("intraday-chart-btn").addEventListener("click", get_intraday_chart);

window.addEventListener("resize", function(event) {
    const width = window.innerWidth;
    if (width <= 1600) {
        if (chart_mode !== "compact") {
            chart_mode = "compact";
            if (intraday_chart_container.style.display !== "none") {
                update_intraday_chart();
            }
        }
    } else {
        if (chart_mode !== "full") {
            chart_mode = "full";
            if (intraday_chart_container.style.display !== "none") {
                update_intraday_chart();
            }
        }
    }
}, true);

function validateDate(date) {
    return date.match(/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) !== null;
}

function validateSymbol(symbol) {
    return symbol_set.has(symbol);
}

if (typeof(INIT_SYMBOL) !== "undefined" && typeof(INIT_DATE) !== "undefined" && validateDate(INIT_DATE) && validateSymbol(INIT_SYMBOL)) {
    datepicker.setDate(Date.parse(INIT_DATE) + (new Date().getTimezoneOffset() * 60000));
    symbol_input.value = INIT_SYMBOL;
    get_chart_data(INIT_DATE, INIT_SYMBOL);
    update_intraday_chart();
} else {
    displayAlert("info", "Enter date and symbol, and click GO")
}


// Construct trie tree
for (var symbol of ALL_SYMBOLS) {
    var node = symbol_tree;
    for (var char of symbol) {
        if (node.children[char] === undefined) {
            node.children[char] = {symbols: [], children: {}}
        }
        node = node.children[char];
        if (node.symbols.length < 10) {
            node.symbols.push(symbol);
        }
    }
}

/*the autocomplete function takes two arguments,
the text field element and an array of possible autocompleted values:*/
var currentFocus;
/*execute a function when someone writes in the text field:*/
symbol_input.addEventListener("input", function(e) {
    var a, b, val = this.value;
    var s = val;
    displayAlert("info", s);
    /*close any already open lists of autocompleted values*/
    closeAllLists();
    s += ";closeList";
    displayAlert("info", s);
    if (!val) { return false;}
    currentFocus = -1;
    /*create a DIV element that will contain the items (values):*/
    a = document.createElement("DIV");
    a.setAttribute("id", this.id + "-autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
    s += ";createlist";
    displayAlert("info", s);
    /*append the DIV element as a child of the autocomplete container:*/
    this.parentNode.appendChild(a);
    var node = symbol_tree;
    for (var char of val) {
        if (node.children[char] !== undefined) {
            node = node.children[char]
        } else {
            node = null;
            break;
        }
    }
    var arr = [];
    if (node !== null) {
        arr = node.symbols;
    }
    s += ";" + arr;
    displayAlert("info", s);
    /*for each item in the array...*/
    for (var i = 0; i < arr.length; i++) {
        /*create a DIV element for each matching element:*/
        b = document.createElement("DIV");
        /*make the matching letters bold:*/
        b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
        b.innerHTML += arr[i].substr(val.length);
        /*insert a input field that will hold the current array item's value:*/
        b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
        /*execute a function when someone clicks on the item value (DIV element):*/
        b.addEventListener("click", function(e) {
            /*insert the value for the autocomplete text field:*/
            symbol_input.value = this.getElementsByTagName("input")[0].value;
            /*close the list of autocompleted values,
            (or any other open lists of autocompleted values:*/
            closeAllLists();
        });
        a.appendChild(b);
    }
    s += ";render";
    displayAlert("info", s);
});
/*execute a function presses a key on the keyboard:*/
symbol_input.addEventListener("keydown", function(e) {
    var x = document.getElementById(this.id + "-autocomplete-list");
    if (x) {
        x = x.getElementsByTagName("div");
    } else {
        return;
    }
    if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
    } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
    } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            x[currentFocus].click();
        }
    }
});
function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
 }
function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
    }
}
function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != symbol_input) {
            x[i].parentNode.removeChild(x[i]);
        }
    }
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {closeAllLists(e.target);});