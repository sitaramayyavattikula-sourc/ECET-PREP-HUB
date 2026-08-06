function openModal(){

    const totalQuestions =
        document.querySelectorAll(".question-box").length;

    const answered =
        document.querySelectorAll("input[type=radio]:checked").length;

    document.getElementById("answeredCount").innerHTML =
        answered;

    document.getElementById("unansweredCount").innerHTML =
        totalQuestions - answered;

    document.getElementById("submitModal").style.display =
        "block";

}

function closeModal(){

    document.getElementById("submitModal").style.display =
        "none";

}

function submitQuiz(){

    document.querySelector("form").submit();

}