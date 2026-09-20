// ==========================================
// ECET Mock Examination 3-Hour Countdown Timer
// ==========================================

(function () {
    // 3 Hours in seconds (10,800 seconds / 180 minutes)
    const DEFAULT_DURATION_SECONDS = 3 * 60 * 60;

    const timerElem = document.getElementById("timer");
    const timerBox = document.querySelector(".timer-box");
    const branchInput = document.querySelector('input[name="branch"]');
    const branch = (branchInput ? branchInput.value : "cme").toLowerCase();

    // Storage Keys
    const TIMER_STORAGE_KEY = `ecet_exam_timer_${branch}`;
    const ANSWERS_STORAGE_KEY = `ecet_exam_answers_${branch}`;
    const WARNING_SHOWN_KEY = `ecet_exam_warning_${branch}`;

    // Prevent duplicate intervals across reloads/re-executions
    if (window._ecetTimerInterval) {
        clearInterval(window._ecetTimerInterval);
        window._ecetTimerInterval = null;
    }

    // Support configurable duration via URL parameter for testing (e.g., ?duration=10)
    const urlParams = new URLSearchParams(window.location.search);
    const testDurationParam = urlParams.get("duration");
    const examDurationSeconds = testDurationParam && !isNaN(parseInt(testDurationParam))
        ? parseInt(testDurationParam)
        : DEFAULT_DURATION_SECONDS;

    // Clear all exam-related storage for this branch
    function clearExamStorage() {
        try {
            localStorage.removeItem(TIMER_STORAGE_KEY);
            localStorage.removeItem(ANSWERS_STORAGE_KEY);
            sessionStorage.removeItem(WARNING_SHOWN_KEY);
        } catch (e) {
            console.error("Failed to clear exam storage:", e);
        }
    }

    // Check if an explicit new exam attempt is requested via query param (e.g. ?new=1 or ?restart=1)
    if (urlParams.get("new") === "1" || urlParams.get("restart") === "1") {
        clearExamStorage();
        // Clean URL parameters without reloading
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }

    // Format seconds to HH:MM:SS
    function formatTime(totalSeconds) {
        totalSeconds = Math.max(0, Math.floor(totalSeconds));
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        return (
            String(hours).padStart(2, "0") + ":" +
            String(minutes).padStart(2, "0") + ":" +
            String(seconds).padStart(2, "0")
        );
    }

    // Retrieve or initialize exam end time
    let endTime = null;
    const now = Date.now();

    try {
        const storedTimer = localStorage.getItem(TIMER_STORAGE_KEY);
        if (storedTimer) {
            const parsed = JSON.parse(storedTimer);
            if (parsed && typeof parsed.endTime === "number") {
                endTime = parsed.endTime;
            }
        }
    } catch (e) {
        console.error("Failed to parse stored timer:", e);
    }

    // If no existing end time found or invalid, create new exam countdown
    if (!endTime) {
        endTime = now + (examDurationSeconds * 1000);
        try {
            localStorage.setItem(TIMER_STORAGE_KEY, JSON.stringify({
                startTime: now,
                endTime: endTime,
                duration: examDurationSeconds,
                branch: branch
            }));
        } catch (e) {
            console.error("Failed to save exam timer to localStorage:", e);
        }
    }

    let isSubmitting = false;

    // Update UI and styling
    function updateDisplay(remainingSeconds) {
        if (!timerElem) return;

        timerElem.innerText = formatTime(remainingSeconds);

        if (timerBox) {
            // Last 5 minutes: Danger styling (< 300s)
            if (remainingSeconds <= 300 && remainingSeconds > 0) {
                timerBox.classList.remove("warning");
                timerBox.classList.add("danger");
            }
            // Last 10 minutes: Warning styling (< 600s)
            else if (remainingSeconds <= 600 && remainingSeconds > 300) {
                timerBox.classList.add("warning");
                timerBox.classList.remove("danger");

                // Show 10-minute warning alert once
                if (!sessionStorage.getItem(WARNING_SHOWN_KEY)) {
                    sessionStorage.setItem(WARNING_SHOWN_KEY, "true");
                    setTimeout(() => {
                        alert("⚠️ Warning!\n\nOnly 10 minutes remaining.\nPlease review your answers.");
                    }, 50);
                }
            } else {
                timerBox.classList.remove("warning");
                timerBox.classList.remove("danger");
            }
        }
    }

    // Automatic Submission when timer hits 00:00:00
    function autoSubmitExam() {
        if (isSubmitting) return;
        isSubmitting = true;

        if (window._ecetTimerInterval) {
            clearInterval(window._ecetTimerInterval);
            window._ecetTimerInterval = null;
        }

        // Freeze display at exactly 00:00:00
        if (timerElem) {
            timerElem.innerText = "00:00:00";
        }
        if (timerBox) {
            timerBox.classList.remove("warning");
            timerBox.classList.add("danger");
        }

        const form = document.getElementById("quizForm") || document.querySelector("form");

        // Prevent further answering / editing:
        // Lock user interaction without disabling inputs (so values are still sent in POST)
        if (form) {
            form.style.pointerEvents = "none";
            form.style.userSelect = "none";
            form.style.opacity = "0.75";

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting Exam...';
            }
        }

        // Clear stored exam session
        clearExamStorage();

        // Inform student and submit form
        alert("Time's Up! Your examination has been automatically submitted.");

        if (form) {
            form.submit();
        }
    }

    // Tick handler
    function tick() {
        const currentTime = Date.now();
        const diffMs = endTime - currentTime;
        const remainingSeconds = Math.max(0, Math.ceil(diffMs / 1000));

        updateDisplay(remainingSeconds);

        if (remainingSeconds <= 0) {
            if (window._ecetTimerInterval) {
                clearInterval(window._ecetTimerInterval);
                window._ecetTimerInterval = null;
            }
            autoSubmitExam();
        }
    }

    // Answer Persistence: save answers on select and restore on page load
    const quizForm = document.getElementById("quizForm") || document.querySelector("form");

    function restoreAnswers() {
        try {
            const savedAnswers = localStorage.getItem(ANSWERS_STORAGE_KEY);
            if (savedAnswers && quizForm) {
                const answersObj = JSON.parse(savedAnswers);
                Object.keys(answersObj).forEach(name => {
                    const value = answersObj[name];
                    const radio = quizForm.querySelector(`input[type="radio"][name="${name}"][value="${CSS.escape(value)}"]`);
                    if (radio) {
                        radio.checked = true;
                    }
                });
            }
        } catch (e) {
            console.error("Failed to restore answers:", e);
        }
    }

    function setupAnswerSaving() {
        if (!quizForm) return;

        quizForm.addEventListener("change", function (e) {
            if (e.target && e.target.type === "radio") {
                try {
                    const checkedRadios = quizForm.querySelectorAll('input[type="radio"]:checked');
                    const answersObj = {};
                    checkedRadios.forEach(radio => {
                        answersObj[radio.name] = radio.value;
                    });
                    localStorage.setItem(ANSWERS_STORAGE_KEY, JSON.stringify(answersObj));
                } catch (err) {
                    console.error("Failed to save answer state:", err);
                }
            }
        });

        // Manual submit handler
        quizForm.addEventListener("submit", function () {
            if (window._ecetTimerInterval) {
                clearInterval(window._ecetTimerInterval);
                window._ecetTimerInterval = null;
            }
            clearExamStorage();
        });
    }

    // Initialize answer preservation
    restoreAnswers();
    setupAnswerSaving();

    // Initial tick to immediately render correct time
    tick();

    // Start interval if exam is still active
    const initialDiffMs = endTime - Date.now();
    if (initialDiffMs > 0) {
        window._ecetTimerInterval = setInterval(tick, 1000);
    }
})();
