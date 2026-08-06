document.addEventListener("DOMContentLoaded", function () {

    const loader = document.getElementById("page-loader");

    document.querySelectorAll("a").forEach(link => {

        link.addEventListener("click", function () {

            loader.style.width = "60%";

        });

    });

});

window.addEventListener("load", function () {

    const loader = document.getElementById("page-loader");

    loader.style.width = "100%";

    setTimeout(function () {

        loader.style.width = "0%";

    }, 200);

});