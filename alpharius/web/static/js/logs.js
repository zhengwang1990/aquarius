const elem = document.getElementById("datepicker");
const datepicker = new Datepicker(elem, {
  autohide: true,
  daysOfWeekDisabled: [0, 6],
  format: "M dd yyyy",
  minDate: Date.parse('2022-10-01T00:00:00'),
  maxDate: Date.now(),
});
document.getElementById("calendar-icon").addEventListener("click", () => {datepicker.show()});

// Back-to-top button
let btt_button = document.getElementById("btn-back-to-top");
window.onscroll = function () {
  scrollFunction();
};
function scrollFunction() {
console.log(document.body.scrollTop)
  if (
    document.body.scrollTop > 20 ||
    document.documentElement.scrollTop > 20
  ) {
    btt_button.style.display = "block";
  } else {
    btt_button.style.display = "none";
  }
}
btt_button.addEventListener("click", backToTop);

function backToTop() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}