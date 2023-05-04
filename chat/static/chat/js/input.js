'use strict';
const log = document.querySelector('.output_log');
const output = document.querySelector('#chat-message-input');
// const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// const recognition = new SpeechRecognition();

var recognition;

if ('webkitSpeechRecognition' in window) {
    // Safari
    recognition = new webkitSpeechRecognition();
} else if ('mozSpeechRecognition' in window) {
    // Firefox
    recognition = new mozSpeechRecognition();
} else if ('SpeechRecognition' in window) {
    // Chrome
    recognition = new SpeechRecognition();
} else {
    // Not supported
    console.log('Web Speech API is not supported.');
}

recognition.interimResults = true;
recognition.maxAlternatives = 1;
const speechIcon = document.querySelector("#speech-icon");
const micColor = {on:"red", off:"#4EA1D5"};

function completeLanguageTag(langCode) {
    const langCodes = {
        "en": "en-US",
        "es": "es-ES",
    };    
    if (langCodes.hasOwnProperty(langCode)) {
      return langCodes[langCode];
    } else {
      return "en-US";
    };
};


document.querySelector('#speech-input-btn').addEventListener('click', () => {
    let lang= completeLanguageTag(JSON.parse(document.getElementById('lang').textContent));
    speechIcon.style.fill = micColor.on;
    //let recogLang = document.querySelector('[name=lang]:checked');
    recognition.lang = lang; //recogLang.value;
    recognition.start();
});

recognition.addEventListener('speechstart', () => {
    log.textContent = 'Speech has been detected.';
});

recognition.addEventListener('result', (e) => {
    log.textContent= 'Result has been detected.';
    let last = e.results.length - 1;
    let text = e.results[last][0].transcript;
    //output.textContent = text;
    output.value = text;
    log.textContent = 'Confidence: ' + e.results[0][0].confidence;
});

recognition.addEventListener('speechend', () => {
    speechIcon.style.fill = micColor.off;
    recognition.stop();
});

recognition.addEventListener('error', (e) => {
    output.textContent = 'Error: ' + e.error;
});