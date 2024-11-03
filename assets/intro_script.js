// intro_script.js

function startIntro() {
    var intro = introJs();
    intro.setOptions({
        steps: [
            {
                intro: "Welcome to the Collapsible Tree Dashboard! Let's take a quick tour."
            },
            {
                element: document.querySelector("#collapsible-tree"),
                intro: "This is the main visualization area. You can explore the collectives and tags here."
            },
            {
                element: document.querySelector("#tree-info"),
                intro: "When you click on a tag, detailed statistics will appear here."
            },
            {
                element: document.querySelector("#help-button"),
                intro: "Click this Help button anytime to start the tour again."
            }
        ]
    });
    intro.start();
}

document.addEventListener('DOMContentLoaded', function () {
    // Start intro on page load
    startIntro();
});
