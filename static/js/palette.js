// =========================================================
// ECET Mock Examination Question Palette & Navigation
// =========================================================

(function () {
    let currentQuestion = 1;
    let totalQuestions = 200;
    let isProgrammaticScroll = false;
    let scrollTimeout = null;

    function init() {
        // Prevent browser auto-restoration of scroll position on reload
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual';
        }

        // Always ensure examination begins cleanly at the very top (Header, Title, Timer, Question 1)
        window.scrollTo(0, 0);

        const totalCards = document.querySelectorAll(".question-card").length;
        if (totalCards > 0) {
            totalQuestions = totalCards;
        }

        // Setup question card click delegation to update current question without scrolling
        const quizForm = document.getElementById("quizForm");
        if (quizForm) {
            quizForm.addEventListener("click", function (e) {
                const card = e.target.closest(".question-card");
                if (card) {
                    const qNum = parseInt(card.getAttribute("data-question"), 10);
                    if (qNum && qNum !== currentQuestion) {
                        setCurrentQuestion(qNum, false);
                    }
                }
            });

            // Listen to radio answer selections - update state and palette without any scrolling/jumping
            quizForm.addEventListener("change", function (e) {
                if (e.target && e.target.type === "radio") {
                    const card = e.target.closest(".question-card");
                    if (card) {
                        const qNum = parseInt(card.getAttribute("data-question"), 10);
                        if (qNum && qNum !== currentQuestion) {
                            setCurrentQuestion(qNum, false);
                        }
                    }
                    updatePaletteUI();
                }
            });
        }

        // Setup scroll observer to update current question when user scrolls naturally through exam
        setupScrollObserver();

        // Initial UI sync at Question 1 (without scrolling anywhere)
        setCurrentQuestion(1, false);
        updatePaletteUI();
    }

    // Check if question has a selected radio option
    function isQuestionAnswered(qNum) {
        const checked = document.querySelector(`input[name="question_${qNum}"]:checked`);
        return checked !== null;
    }

    // Update entire palette: colors, labels, stats counters, and navigation button states
    function updatePaletteUI() {
        let answeredCount = 0;

        for (let i = 1; i <= totalQuestions; i++) {
            const btn = document.getElementById(`paletteBtn_${i}`);
            const answered = isQuestionAnswered(i);

            if (answered) {
                answeredCount++;
            }

            if (btn) {
                // EXACT PRIORITY RULE:
                // Current question MUST ALWAYS be yellow (.current), regardless of answered state!
                if (i === currentQuestion) {
                    btn.className = "palette-btn current";
                    btn.setAttribute("aria-label", `Question ${i} — Current Question`);
                } else if (answered) {
                    btn.className = "palette-btn answered";
                    btn.setAttribute("aria-label", `Question ${i} — Answered`);
                } else {
                    btn.className = "palette-btn unanswered";
                    btn.setAttribute("aria-label", `Question ${i} — Not Answered`);
                }
            }
        }

        const unansweredCount = totalQuestions - answeredCount;

        // Update Counter Display Badges
        const answeredElem = document.getElementById("paletteAnsweredCount");
        const unansweredElem = document.getElementById("paletteUnansweredCount");
        const totalElem = document.getElementById("paletteTotalCount");

        if (answeredElem) answeredElem.innerText = answeredCount;
        if (unansweredElem) unansweredElem.innerText = unansweredCount;
        if (totalElem) totalElem.innerText = totalQuestions;

        // Update Top Navigation buttons state
        const btnPrevTop = document.getElementById("btnPrevTop");
        const btnNextTop = document.getElementById("btnNextTop");
        const currDisplayTop = document.getElementById("currentQuestionNumTop");

        if (btnPrevTop) btnPrevTop.disabled = (currentQuestion <= 1);
        if (btnNextTop) btnNextTop.disabled = (currentQuestion >= totalQuestions);
        if (currDisplayTop) currDisplayTop.innerText = currentQuestion;

        // Update Bottom Navigation buttons state
        const btnPrevBottom = document.getElementById("btnPrevBottom");
        const btnNextBottom = document.getElementById("btnNextBottom");
        const currDisplayBottom = document.getElementById("currentQuestionNumBottom");

        if (btnPrevBottom) btnPrevBottom.disabled = (currentQuestion <= 1);
        if (btnNextBottom) btnNextBottom.disabled = (currentQuestion >= totalQuestions);
        if (currDisplayBottom) currDisplayBottom.innerText = currentQuestion;
    }

    // Set current question and optionally scroll target question card into view
    // Note: NEVER scrolls to the palette!
    function setCurrentQuestion(qNum, shouldScroll) {
        if (qNum < 1 || qNum > totalQuestions) return;
        currentQuestion = qNum;

        // Highlight active question card
        document.querySelectorAll(".question-card").forEach(c => c.classList.remove("active-question"));
        const card = document.getElementById(`questionCard_${qNum}`);
        if (card) {
            card.classList.add("active-question");
            if (shouldScroll) {
                isProgrammaticScroll = true;
                if (scrollTimeout) clearTimeout(scrollTimeout);
                card.scrollIntoView({ behavior: "smooth", block: "start" });
                scrollTimeout = setTimeout(() => {
                    isProgrammaticScroll = false;
                }, 800);
            }
        }

        // Question palette MUST NEVER be scrolled into view during question selection/navigation.
        // The palette remains undisturbed at the bottom of the page before Submit.
        updatePaletteUI();
    }

    // Navigation function from intentional palette button click
    window.goToQuestion = function (qNum) {
        setCurrentQuestion(qNum, true);
    };

    // Previous / Next button navigation
    window.navigateQuestion = function (direction) {
        const target = currentQuestion + direction;
        if (target >= 1 && target <= totalQuestions) {
            setCurrentQuestion(target, true);
        }
    };

    // Observe scroll position to track current question naturally as user scrolls
    function setupScrollObserver() {
        if (!("IntersectionObserver" in window)) return;

        const observer = new IntersectionObserver((entries) => {
            if (isProgrammaticScroll) return;

            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const qNum = parseInt(entry.target.getAttribute("data-question"), 10);
                    if (qNum && qNum !== currentQuestion) {
                        currentQuestion = qNum;
                        document.querySelectorAll(".question-card").forEach(c => c.classList.remove("active-question"));
                        entry.target.classList.add("active-question");
                        updatePaletteUI();
                    }
                }
            });
        }, {
            root: null,
            rootMargin: "-20% 0px -50% 0px",
            threshold: 0.1
        });

        document.querySelectorAll(".question-card").forEach(card => {
            observer.observe(card);
        });
    }

    // Confirmation Modal Handlers
    window.openSubmitModal = function () {
        let answered = 0;
        for (let i = 1; i <= totalQuestions; i++) {
            if (isQuestionAnswered(i)) answered++;
        }
        const unanswered = totalQuestions - answered;

        const modalAnswered = document.getElementById("modalAnsweredCount");
        const modalTotal = document.getElementById("modalTotalCount");
        const pillAnswered = document.getElementById("modalPillAnswered");
        const pillUnanswered = document.getElementById("modalPillUnanswered");

        if (modalAnswered) modalAnswered.innerText = answered;
        if (modalTotal) modalTotal.innerText = totalQuestions;
        if (pillAnswered) pillAnswered.innerText = `${answered} Answered`;
        if (pillUnanswered) pillUnanswered.innerText = `${unanswered} Not Answered`;

        const modal = document.getElementById("submitConfirmModal");
        if (modal) {
            modal.style.display = "flex";
            document.body.style.overflow = "hidden";
        }
    };

    window.closeSubmitModal = function () {
        const modal = document.getElementById("submitConfirmModal");
        if (modal) {
            modal.style.display = "none";
            document.body.style.overflow = "";
        }
    };

    window.confirmExamSubmit = function () {
        const modal = document.getElementById("submitConfirmModal");
        if (modal) modal.style.display = "none";
        document.body.style.overflow = "";

        const form = document.getElementById("quizForm");
        if (form) {
            form.submit();
        }
    };

    // Close modal on Escape key
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            window.closeSubmitModal();
        }
    });

    // Run when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
