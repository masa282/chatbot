const roomName = JSON.parse(document.getElementById('room-name').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    //document.querySelector('#chat-log').value += (data.message + '\n');

    // add msg to chat log
    add_chat_log(data.message, "right");
    // speak
    synthVoice(data.message,'en-US');
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    messageInputDom.value = '';
    // add msg to chat log
    add_chat_log(message, "left");
};


function synthVoice(text, lang) {
    const synth = window.speechSynthesis;  
    const utterance = new SpeechSynthesisUtterance();
    utterance.lang = lang;
    utterance.text = text;
    synth.speak(utterance);
};

function add_chat_log (msg, rl){
    const chat_log_container = document.querySelector("#chat-log-container");
    const msg_container = document.createElement('div');
    msg_container.classList.add("container");
    
    const msg_p = document.createElement("p");
    msg_p.innerText = msg
    
    const time_span = document.createElement("span");
    time_span.classList.add("time-"+rl)
    const now = new Date();
    const formatedTime = now.toLocaleString('ja-JP', { hour12: false })
    time_span.innerText = formatedTime

    msg_container.appendChild(msg_p);
    msg_container.appendChild(time_span);
    chat_log_container.appendChild(msg_container);
};