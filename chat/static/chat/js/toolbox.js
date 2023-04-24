const toolBoxes = document.querySelectorAll("[name='toolbox']");
toolBoxes.forEach( function(toolBox){
    register_clikcevents_toolbox(toolBox);
});

function register_clikcevents_toolbox(dtag){
    let speak = dtag.querySelector('[name="re-speak"]');
    speak.addEventListener("click", (e) => {
        register_clickevent_speak(e);
    });
    let analyzeText = dtag.querySelector("[name='analyze-text']");
    analyzeText.addEventListener("click", (e) => {
        register_clickevent_analyzeText(e);
    });
};

function register_clickevent_analyzeText(e){
    let text = get_msg_content(e.target.parentNode);
    // validate text input
    send_message("analyze", text);
};

function register_clickevent_speak(e){
    let text = get_msg_content(e.target.parentNode);
    synthVoice(text, lang);
};

function get_msg_content(e){
    let parentElement = e;
    while (parentElement) {
        if (parentElement.children[0].tagName == "P") {
            return parentElement.children[0].textContent;
        }
        else{ parentElement = parentElement.parentNode; }
    } 
};