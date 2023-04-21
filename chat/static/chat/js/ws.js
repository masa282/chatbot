const roomName = JSON.parse(document.getElementById('chat-id').textContent);
const lang = completeLanguageTag(JSON.parse(document.getElementById('lang').textContent));

// const roomNames = ["en-US", "es-ES"];
// if(roomName not in roomNames){}

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + lang
    + '/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    let lang = completeLanguageTag(JSON.parse(document.getElementById('lang').textContent));
    const data = JSON.parse(e.data);

    if (data.chat_id.length !== 0){
        console.log(document.cookie);
        Cookies.set(lang, data.chat_id, {expires: 60});
        // const cookieName = "chat_id";
        // const cookieValue = data.chat_id;
        // const expires = "; expires=" + new Date(Date.now() + 3600 * 1000).toUTCString();
        // document.cookie = cookieName + "=" + cookieValue + expires + "; path=/";
        console.log(document.cookie);
    }

    // add msg to chat log
    add_chat_log(data.message, "AI");
    // speak
    synthVoice(data.message, lang);
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
    if (message.length > 0){
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        messageInputDom.value = '';
        // add msg to chat log
        add_chat_log(message, "human");
    }
};


function synthVoice(text, lang) {
    const synth = window.speechSynthesis;  
    const utterance = new SpeechSynthesisUtterance();
    utterance.lang = lang;
    utterance.text = text;
    synth.speak(utterance);
};

function add_chat_log (msg, speaker){
    const chat_log_container = document.querySelector("#chat-log-container");
    const msg_container = document.createElement("div");
    msg_container.classList.add("d-flex");
    msg_container.classList.add("flex-row");
    const icon_img = document.createElement("img");
    icon_img.alt = "avatar1";
    icon_img.style.width = '45px';
    icon_img.style.height = '100%';
    const div2 = document.createElement("div");
    const p_msg = document.createElement("p");
    p_msg.classList.add("small");
    p_msg.classList.add("p-2");
    p_msg.classList.add("mb-1");
    p_msg.classList.add("rounded-3");
    p_msg.innerHTML = msg;
    const p_time = document.createElement("p");
    p_time.classList.add("small");
    p_time.classList.add("rounded-3");
    p_time.classList.add("text-muted");
    p_time.innerHTML = "12:00 PM | Aug 13";
    
    if (speaker == "human"){
        icon_img.src = "https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava6-bg.webp" 
        msg_container.classList.add("justify-content-start");
        p_msg.classList.add("ms-3");
        p_msg.style.backgroundColor = "#EAEAEA";
        p_time.classList.add("ms-3");
        p_time.classList.add("float-end");
    } else if (speaker == "AI"){
        icon_img.src = "https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp";
        msg_container.classList.add("justify-content-end");
        p_msg.classList.add("me-3");
        //p_msg.classList.add("bg-primary");
        p_time.classList.add("me-3");
        p_msg.style.backgroundColor = "#4EA1D5";
    }

    div2.appendChild(p_msg);
    div2.appendChild(p_time);
    msg_container.appendChild(icon_img);
    msg_container.appendChild(div2);
    chat_log_container.appendChild(msg_container);
};