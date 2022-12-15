const processor_select = document.getElementById("processor-select");

processor_select.addEventListener("change", function(event){
    var processor = processor_select.value;
    var redirect = "transactions";
    if (processor !== "ALL PROCESSORS") {
        redirect = "?processor=" + processor;
    }
    window.location.href = redirect;
});