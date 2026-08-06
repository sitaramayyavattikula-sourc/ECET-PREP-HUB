// ===============================
// Question Palette
// ===============================

function markAnswered(questionNo){

    const btn = document.getElementById(

        "palette"+questionNo

    );

    btn.classList.remove(

        "not-visited"

    );

    btn.classList.remove(

        "current"

    );

    btn.classList.add(

        "answered"

    );

}

function gotoQuestion(questionNo){

    document

    .getElementById(

        "question"+questionNo

    )

    .scrollIntoView({

        behavior:"smooth",

        block:"start"

    });

    document

    .querySelectorAll(".palette-btn")

    .forEach(btn=>{

        btn.classList.remove(

            "current"

        );

    });

    const btn=document.getElementById(

        "palette"+questionNo

    );

    if(

        !btn.classList.contains(

            "answered"

        )

    ){

        btn.classList.remove(

            "not-visited"

        );

        btn.classList.add(

            "current"

        );

    }

}