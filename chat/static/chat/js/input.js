'use strict';
const log = document.querySelector('.output_log');
const output = document.querySelector('.output_result');
const output2 = document.querySelector('#chat-message-input');
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.interimResults = true;
recognition.maxAlternatives = 1;

document.querySelector('button').addEventListener('click', () => {
    let recogLang = document.querySelector('[name=lang]:checked');
    recognition.lang = recogLang.value;
    recognition.start();
});

recognition.addEventListener('speechstart', () => {
    log.textContent = 'Speech has been detected.';
});

recognition.addEventListener('result', (e) => {
    log.textContent= 'Result has been detected.';
    let last = e.results.length - 1;
    let text = e.results[last][0].transcript;
    output.textContent = text;
    output2.value = text;
    log.textContent = 'Confidence: ' + e.results[0][0].confidence;
});

recognition.addEventListener('speechend', () => {
    recognition.stop();
});

recognition.addEventListener('error', (e) => {
    output.textContent = 'Error: ' + e.error;
});