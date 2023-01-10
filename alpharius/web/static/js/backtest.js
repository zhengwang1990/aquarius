const processor_select = document.getElementById("processor-select");
const ndays_select = document.getElementById("ndays-select");

processor_select.addEventListener("change", function(event){
    redirect();
});

ndays_select.addEventListener("change", function(event){
    redirect();
});

function redirect() {
    var processor = processor_select.value;
    var ndays = ndays_select.value;
    var redirect = "?ndays=" + ndays;
    if (processor !== "ALL PROCESSORS") {
        redirect += "&processor=" + processor;
    }
    window.location.href = redirect;
}
