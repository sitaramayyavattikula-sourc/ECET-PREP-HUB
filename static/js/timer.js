// ===============================
// ECET 3-Hour Exam Timer
// ===============================

let totalSeconds = 3 * 60 * 60; // 3 Hours

const timer = document.getElementById("timer");
const timerBox = document.querySelector(".timer-box");

let warningShown = false;

function updateTimer() {

    let hours = Math.floor(totalSeconds / 3600);

    let minutes = Math.floor((totalSeconds % 3600) / 60);

    let seconds = totalSeconds % 60;

    timer.innerHTML =
        String(hours).padStart(2, '0') + ":" +
        String(minutes).padStart(2, '0') + ":" +
        String(seconds).padStart(2, '0');

    // ===============================
    // Last 10 Minutes
    // ===============================
    if (totalSeconds <= 600 && totalSeconds > 300) {

        timerBox.classList.add("warning");

        if (!warningShown) {

            warningShown = true;

            alert("⚠ Warning!\n\nOnly 10 minutes remaining.\nPlease review your answers.");

        }

    }

    // ===============================
    // Last 5 Minutes
    // ===============================
    if (totalSeconds <= 300) {

        timerBox.classList.remove("warning");

        timerBox.classList.add("danger");

    }

    // ===============================
    // Time Over
    // ===============================
    if (totalSeconds <= 0) {

        clearInterval(countdown);

        alert("⏰ Time is over!\n\nYour test will now be submitted automatically.");

        document.querySelector("form").submit();

        return;

    }

    totalSeconds--;

}

updateTimer();

const countdown = setInterval(updateTimer, 1000);