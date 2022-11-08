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
let gtb_button = document.getElementById("btn-go-to-bottom");
window.onscroll = function () {
  scrollFunction();
};
function scrollFunction() {
  if (document.documentElement.scrollTop > 20) {
    btt_button.style.display = "block";
  } else {
    btt_button.style.display = "none";
  }
  if (document.documentElement.scrollTop < document.documentElement.scrollHeight - window.innerHeight - 20) {
    gtb_button.style.display = "block";
  } else {
    gtb_button.style.display = "none";
  }
}
btt_button.addEventListener("click", backToTop);
gtb_button.addEventListener("click", goToBottom);
function backToTop() {
  document.documentElement.scrollTop = 0;
}
function goToBottom() {
  document.documentElement.scrollTop = document.documentElement.scrollHeight - window.innerHeight;
}