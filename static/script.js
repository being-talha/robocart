document.addEventListener("DOMContentLoaded", function () {

    const modeToggle = document.getElementById("modeToggle");
    const body = document.body;

    // Apply saved theme on load
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        body.classList.add("dark-mode");
        modeToggle.checked = true;
    }

    // Toggle dark mode on switch
    modeToggle.addEventListener("change", function () {
        body.classList.toggle("dark-mode");

        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });

});









