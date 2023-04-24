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
        Cookies.set(lang, data.chat_id, {expires: 60});
        // const cookieName = "chat_id";
        // const cookieValue = data.chat_id;
        // const expires = "; expires=" + new Date(Date.now() + 3600 * 1000).toUTCString();
        // document.cookie = cookieName + "=" + cookieValue + expires + "; path=/";
    }

    if (data.response_type == "chat"){
        add_chat_log(data.message, "AI", "chat");
        synthVoice(data.message, lang);
    } else if(data.response_type == "analyze"){
        add_chat_log(data.message, "AI", "analyze");
        synthVoice(data.message, lang);
    }
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
        send_message("chat", message);
        messageInputDom.value = '';
        add_chat_log(message, "human", "chat");
    }
};

function send_message(type, msg){
    chatSocket.send(JSON.stringify({
        'response_type': type,
        'message': msg,
    }));
};

function synthVoice(text, lang) {
    const synth = window.speechSynthesis;  
    const utterance = new SpeechSynthesisUtterance();
    utterance.lang = lang;
    utterance.text = text;
    synth.speak(utterance);
};

function add_chat_log (msg, speaker, type){
    const chat_log_container = document.querySelector("#chat-log-container");
    const msg_container = document.createElement("div");
    msg_container.classList.add("d-flex");
    msg_container.classList.add("flex-row");
    const icon_img = document.createElement("img");
    icon_img.alt = "avatar1";
    icon_img.style.width = '45px';
    icon_img.style.height = '100%';
    const div2 = document.createElement("div");
    div2.classList.add("single-msg-container");
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
    
    if (speaker == "AI"){
        icon_img.src = "https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava6-bg.webp" 
        msg_container.classList.add("justify-content-start");
        p_msg.classList.add("ms-3");
        p_msg.style.backgroundColor = "#EAEAEA";
        p_time.classList.add("ms-3");
        p_time.classList.add("float-end");
    } else if (speaker == "human"){
        icon_img.src = "https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp";
        msg_container.classList.add("justify-content-end");
        p_msg.classList.add("me-3");
        //p_msg.classList.add("bg-primary");
        p_time.classList.add("me-3");
        p_msg.style.backgroundColor = "#4EA1D5";
    }
    if ( type == "analyze"){
        p_msg.style.backgroundColor = "#E85A70";
    };

    div2.appendChild(p_msg);
    div2.appendChild(p_time);
    div2.appendChild(get_toolbox2chatlog());
    msg_container.appendChild(icon_img);
    msg_container.appendChild(div2);
    chat_log_container.appendChild(msg_container);
};

function get_toolbox2chatlog(){
    const container = document.createElement("div");
    container.classList.add("func-container");
    container.classList.add("float-end");

    // not bookmarked
    const svgBookmarked = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgBookmarked.setAttribute("class", "svg-func");
    svgBookmarked.setAttribute("name", "bookmarked");
    svgBookmarked.setAttribute("viewBox", "0 0 384 512");
    const pathBookmarked = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathBookmarked.setAttribute("d", "M0 48V487.7C0 501.1 10.9 512 24.3 512c5 0 9.9-1.5 14-4.4L192 400 345.7 507.6c4.1 2.9 9 4.4 14 4.4c13.4 0 24.3-10.9 24.3-24.3V48c0-26.5-21.5-48-48-48H48C21.5 0 0 21.5 0 48z");
    svgBookmarked.appendChild(pathBookmarked);

    // bookmarked
    const svgNotBookmarked = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgNotBookmarked.setAttribute("class", "svg-func");
    svgNotBookmarked.setAttribute("name", "unbookmarked");
    svgNotBookmarked.setAttribute("viewBox", "0 0 384 512");
    const pathNotBookmarked = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathNotBookmarked.setAttribute("d", "M0 48C0 21.5 21.5 0 48 0l0 48V441.4l130.1-92.9c8.3-6 19.6-6 27.9 0L336 441.4V48H48V0H336c26.5 0 48 21.5 48 48V488c0 9-5 17.2-13 21.3s-17.6 3.4-24.9-1.8L192 397.5 37.9 507.5c-7.3 5.2-16.9 5.9-24.9 1.8S0 497 0 488V48z");
    svgNotBookmarked.appendChild(pathNotBookmarked);

    // Analyze Text
    const svgAnalyzeText = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgAnalyzeText.setAttribute("class", "svg-func");
    svgAnalyzeText.setAttribute("name", "analyze-text");
    svgAnalyzeText.setAttribute("viewBox", "0 0 512 512");
    const pathAnalyzeText = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathAnalyzeText.setAttribute("d", "M441 58.9L453.1 71c9.4 9.4 9.4 24.6 0 33.9L424 134.1 377.9 88 407 58.9c9.4-9.4 24.6-9.4 33.9 0zM209.8 256.2L344 121.9 390.1 168 255.8 302.2c-2.9 2.9-6.5 5-10.4 6.1l-58.5 16.7 16.7-58.5c1.1-3.9 3.2-7.5 6.1-10.4zM373.1 25L175.8 222.2c-8.7 8.7-15 19.4-18.3 31.1l-28.6 100c-2.4 8.4-.1 17.4 6.1 23.6s15.2 8.5 23.6 6.1l100-28.6c11.8-3.4 22.5-9.7 31.1-18.3L487 138.9c28.1-28.1 28.1-73.7 0-101.8L474.9 25C446.8-3.1 401.2-3.1 373.1 25zM88 64C39.4 64 0 103.4 0 152V424c0 48.6 39.4 88 88 88H360c48.6 0 88-39.4 88-88V312c0-13.3-10.7-24-24-24s-24 10.7-24 24V424c0 22.1-17.9 40-40 40H88c-22.1 0-40-17.9-40-40V152c0-22.1 17.9-40 40-40H200c13.3 0 24-10.7 24-24s-10.7-24-24-24H88z");
    svgAnalyzeText.appendChild(pathAnalyzeText);

    // Re-Speak
    const svgSpeak = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgSpeak.setAttribute("class", "svg-func");
    svgSpeak.setAttribute("name", "re-speak");
    svgSpeak.setAttribute("viewBox", "0 0 640 512");
    const pathSpeak = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathSpeak.setAttribute("d", "M533.6 32.5C598.5 85.3 640 165.8 640 256s-41.5 170.8-106.4 223.5c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C557.5 398.2 592 331.2 592 256s-34.5-142.2-88.7-186.3c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zM473.1 107c43.2 35.2 70.9 88.9 70.9 149s-27.7 113.8-70.9 149c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C475.3 341.3 496 301.1 496 256s-20.7-85.3-53.2-111.8c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zm-60.5 74.5C434.1 199.1 448 225.9 448 256s-13.9 56.9-35.4 74.5c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C393.1 284.4 400 271 400 256s-6.9-28.4-17.7-37.3c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zM301.1 34.8C312.6 40 320 51.4 320 64V448c0 12.6-7.4 24-18.9 29.2s-25 3.1-34.4-5.3L131.8 352H64c-35.3 0-64-28.7-64-64V224c0-35.3 28.7-64 64-64h67.8L266.7 40.1c9.4-8.4 22.9-10.4 34.4-5.3z");
    svgSpeak.appendChild(pathSpeak);
    
    container.appendChild(svgBookmarked);
    container.appendChild(svgNotBookmarked);
    container.appendChild(svgAnalyzeText);
    container.appendChild(svgSpeak);
    register_clikcevents_toolbox(container);
    return container;
};