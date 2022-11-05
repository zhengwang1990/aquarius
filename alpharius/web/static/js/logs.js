const elem = document.getElementById("datepicker");
const datepicker = new Datepicker(elem, {
  autohide: true,
  daysOfWeekDisabled: [0, 6],
  format: "M dd yyyy",
  minDate: Date.parse('2022-10-01T00:00:00'),
  maxDate: Date.now(),
});
document.getElementById("calendar-icon").addEventListener("click", () => {datepicker.show()});