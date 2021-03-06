import Papa from 'papaparse';

var chatData = [];
var chatDelay = 0;
var chatIndex = 0;
var chatLastUpdate = 0;
var chatStart = 0;
var metadata = {};
var previousTime = 0;
var seeking = true;
var updatingChat = false;
var videoLeague = '';

const emoteRe = /(?:^|\s):([A-Za-z0-9]+?):(?!\S)/g;
const MAX_MESSAGES_NUM = 60;

export function ready() {
    global.videoElement = document.querySelector('video');
    global.videoElement.addEventListener('loadeddata', videoLoaded);
    global.chatContainer = document.getElementById('chatContainer');
    if (global.chatContainer != null) {
        chatStart = parseInt(global.chatContainer.dataset.start);
        videoLeague = global.chatContainer.dataset.league;
        window.addEventListener('resize', resizeChat);
    }

    document.addEventListener('keydown', keydownHandler, true);

    var bookmarkButtons = document.getElementsByClassName('bookmark-button');
    for (var i = 0; i < bookmarkButtons.length; i++) {
        bookmarkButtons[i].addEventListener('click', bookmarkSeek);
    }
    var chatDelayButtons = document.getElementsByClassName('chat-delay-button');
    for (var i = 0; i < chatDelayButtons.length; i++) {
        chatDelayButtons[i].addEventListener('click', adjustChatDelay);
    }

    window.addEventListener('popstate', setTimeFromHistory, false);
}


function adjustChatDelay(event) {
    let chatDelayIndicator = document.getElementById('chatDelay');
    chatDelay += parseInt(this.dataset.amount);
    chatDelayIndicator.innerHTML = chatDelay;
}


function bookmarkSeek(event) {
    if (global.videoElement == null) {
        return;
    }
    global.videoElement.currentTime = this.dataset.position;
    setURL(this.dataset.position);
}


function clearChat() {
    while (window.chatContainer.childElementCount > 0) {
        global.chatContainer.removeChild(global.chatContainer.firstChild);
    }
}


function createMessage(line) {
    if (line[2] == "Blinkyy") {
        return;
    }

    var container = document.createElement('div');
    container.classList.add('chat-message');

    var userInfoContainer = document.createElement('div');
    userInfoContainer.classList.add('user-info');

    var icon = document.createElement('img')
    icon.classList.add('team');
    let teamSrc = metadata.teams[line[1]];
    if (teamSrc === undefined) {
        teamSrc = metadata.teams['NULL'];
    }
    icon.src = teamSrc;
    userInfoContainer.appendChild(icon);

    var user = document.createElement('span');
    user.classList.add('user');
    var teamClass = ['team', videoLeague];
    if (line[1] != 'NULL') {
        teamClass.push(line[1]);
    }
    user.classList.add(teamClass.join('-'));
    user.textContent = line[2] + ':';
    userInfoContainer.appendChild(user);
    container.appendChild(userInfoContainer);

    var msg = document.createElement('span');
    msg.classList.add('msg');
    if (line[3].startsWith('&gt;')) {
        msg.classList.add('green');
    }
    var emoteMatch;
    while((emoteMatch = emoteRe.exec(line[3])) !== null) {
        let emoteSrc = metadata.emotes[emoteMatch[1]];
        if (emoteSrc !== undefined) {
            let emote = document.createElement('img');
            emote.classList.add('emote');
            emote.src = emoteSrc;
            line[3] = line[3].replace(emoteMatch[0], emote.outerHTML);
        }
    }
    msg.innerHTML = line[3];
    container.appendChild(msg);

    global.chatContainer.prepend(container);
}


function formatSeconds(secondString) {
    var components = [];
    var time = parseFloat(secondString);
    var hours = Math.floor(time / 3600);
    time -= hours * 3600;
    if (hours > 0) {
        components.push(hours.toString());
    }
    var minutes = Math.floor(time / 60);
    time -= minutes * 60;
    if (minutes > 0) {
        components.push(minutes.toString().padStart(2, '0'));
    }
    var seconds = Math.floor(time);
    time -= seconds;
    components.push(seconds.toString().padStart(2, '0'));
    var milliseconds = Math.round(time * 1000).toString();
    return [components.join(':'), milliseconds].join('.');
}



function loadChat(chatSrc, metadataSrc) {
    if (global.videoElement == null) {
        return;
    }
    var metadataLoaded = fetch(metadataSrc).then(function(response) {
        if (response.status !== 200) {
            console.error('Unable to fetch chat metadata.');
            return;
        }
        response.json().then(function(data) {
            metadata = data;
            console.info(`Loaded chat metadata.`)
        });
    });
    Papa.parse(chatSrc, {
        download: true,
        delimiter: "\t",
        complete: function(results, file) {
            chatData = results.data;
            var startIndex = 0;
            var endIndex = chatData.length + 1;
            var duration = Math.floor(window.videoElement.duration * 1000);
            for (var i = 0; i < chatData.length; i++) {
                chatData[i][0] = parseInt(chatData[i][0]) - chatStart;
                if (chatData[i][0] < 0) {
                    startIndex = i;
                } else if (chatData[i][0] > duration) {
                    endIndex = i;
                    break;
                }
            }
            chatData = chatData.slice(startIndex + 1, endIndex);
            console.info(`Loaded ${chatData.length} chat messages.`)
            metadataLoaded.then(function() {
                global.videoElement.addEventListener('playing', function() {
                    window.requestAnimationFrame(updateChat);
                });

                if (!global.videoElement.paused) {
                    window.requestAnimationFrame(updateChat);
                }
            });
        }
    });
}

function keydownHandler(event) {
    switch (event.code) {
        case "ArrowDown":
            event.preventDefault();
            global.videoElement.currentTime -= 60;
            break;
        case "ArrowLeft":
            event.preventDefault();
            global.videoElement.currentTime -= 5;
            break;
        case "ArrowRight":
            event.preventDefault();
            global.videoElement.currentTime += 5;
            break;
        case "ArrowUp":
            event.preventDefault();
            global.videoElement.currentTime += 60;
            break;
        case "Space":
            event.preventDefault();
            togglePlayback();
            break;
    }
}

function seekToInitial() {
    const urlParams = new URLSearchParams(window.location.search);
    var time = urlParams.get('t');
    if (time == null) {
        return;
    }
    time = time.split(':');

    var totalSeconds = 0;
    for (var i = 0; i < time.length; i++) {
        totalSeconds *= 60;
        totalSeconds += parseFloat(time[i]);
    }
    global.videoElement.currentTime = totalSeconds;
}


function setURL(time) {
    var url = new URL('', window.location.href);
    url.searchParams.set('t', formatSeconds(time));
    history.pushState({'time': time}, document.title, url.toString().replace(/%3A/g, ":"));
}


function setTimeFromHistory(event) {
    if (global.videoElement == null) {
        return;
    }
    global.videoElement.currentTime = history.state ? history.state.time : 0;
}

function togglePlayback() {
    if (global.videoElement.paused) {
        global.videoElement.play();
    } else {
        global.videoElement.pause();
    }
}


function refreshChatWindow() {
    while (global.chatContainer.childElementCount > MAX_MESSAGES_NUM) {
        global.chatContainer.removeChild(global.chatContainer.lastChild);
    }
}

function resizeChat() {
    let isPortraitMode = window.matchMedia('(max-width: 768px) and (orientation: portrait)').matches;
    if (isPortraitMode) {
        let documentHeight = document.documentElement.clientHeight;
        let videoHeight = global.videoElement.clientHeight;
        var chatHeight = documentHeight - videoHeight - 10;
    } else {
        var chatHeight = global.videoElement.offsetHeight;
    }
    global.chatContainer.style.height = chatHeight + 'px';
    global.chatContainer.style.maxHeight = chatHeight + 'px';
}

function updateChat() {
    if (updatingChat) {
        return;
    }
    if (Date.now() - chatLastUpdate < 40) {
        window.requestAnimationFrame(updateChat);
        return;
    }
    updatingChat = true;

    var time = Math.floor(global.videoElement.currentTime * 1000);
    time -= chatDelay;

    // If the video has gone back in time, find the current chat position again.
    if (previousTime > time) {
        clearChat();
        chatIndex = 0;
        while (chatIndex < chatData.length) {
            if (time < chatData[chatIndex][0]) {
                break;
            }
            chatIndex += 1;
        }
        chatIndex = Math.max(chatIndex - MAX_MESSAGES_NUM, 0);
    }

    var messages = [];
    while (chatIndex < chatData.length) {
        var line = chatData[chatIndex];
        if (line[0] <= time) {
            messages.push(line);
            chatIndex += 1;
        } else {
            break;
        }
    }

    // Draw last MAX_MESSAGES_NUM captured chat messages.
    if (messages.length > 0) {
        messages = messages.slice(-MAX_MESSAGES_NUM);
        for (var i = 0; i < messages.length; i++) {
            createMessage(messages[i]);
        }
        refreshChatWindow();
    }

    previousTime = time;

    updatingChat = false;
    chatLastUpdate = Date.now();
    if (!global.videoElement.paused) {
        window.requestAnimationFrame(updateChat);
    }
}

function videoLoaded() {
    seekToInitial();
    if (global.chatContainer != null) {
        resizeChat();
        var chatSrc = global.chatContainer.dataset.src;
        var metadataSrc = global.chatContainer.dataset.metadata;
        loadChat(chatSrc, metadataSrc);
    }
}
