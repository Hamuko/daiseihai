import Papa from 'papaparse';

var chatData = [];
var chatIndex = 0;
var chatStart = 0;
var previousTime = 0;
var seeking = true;
var updatingChat = false;
var videoLeague = '';
var metadata = {};
const emoteRe = /(?:^|\s):([A-Za-z0-9]+?):(?!\S)/g;


export function ready() {
    global.videoElement = document.querySelector('video');
    global.videoElement.addEventListener('loadeddata', resizeChat);
    global.chatContainer = document.getElementById('chatContainer');
    chatStart = parseInt(global.chatContainer.dataset.start);
    var chatSrc = global.chatContainer.dataset.src;
    var metadataSrc = global.chatContainer.dataset.metadata;
    if (chatStart > 0) {
        videoLeague = global.chatContainer.dataset.league;
        loadChat(chatSrc, metadataSrc);
        window.addEventListener('resize', resizeChat);
    }

    document.addEventListener('keydown', keydownHandler, true);

    var bookmarkButtons = document.getElementsByClassName('bookmark-button');
    for (var i = 0; i < bookmarkButtons.length; i++) {
        bookmarkButtons[i].addEventListener('click', bookmarkSeek);
    }
}


function bookmarkSeek(event) {
    if (global.videoElement == null) {
        return;
    }
    global.videoElement.currentTime = this.dataset.position;
}


function clearChat() {
    while (window.chatContainer.childElementCount > 0) {
        global.chatContainer.removeChild(global.chatContainer.firstChild);
    }
}


function createMessage(line) {
    var container = document.createElement('div');
    container.classList.add('chat-message');

    var icon = document.createElement('img')
    icon.classList.add('team');
    let teamSrc = metadata.teams[line[1]];
    if (teamSrc === undefined) {
        teamSrc = metadata.teams['NULL'];
    }
    icon.src = teamSrc;
    container.appendChild(icon);

    var user = document.createElement('span');
    user.classList.add('user');
    var teamClass = ['team', videoLeague];
    if (line[1] != 'NULL') {
        teamClass.push(line[1]);
    }
    user.classList.add(teamClass.join('-'));
    user.textContent = line[2] + ':';
    container.appendChild(user);

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
            emote.src = emoteSrc;
            line[3] = line[3].replace(emoteMatch[0], emote.outerHTML);
        }
    }
    msg.innerHTML = line[3];
    container.appendChild(msg);

    global.chatContainer.prepend(container);
}


function loadChat(chatSrc, metadataSrc) {
    if (global.videoElement == null) {
        return;
    }
    fetch(metadataSrc).then(function(response) {
        if (response.status !== 200) {
            console.error('Unable to fetch chat metadata.');
            return;
        }
        response.json().then(function(data) {
            metadata = data;
        });
    });
    Papa.parse(chatSrc, {
        download: true,
        delimiter: "\t",
        complete: function(results, file) {
            chatData = results.data;
            var startIndex = 0;
            for (var i = 0; i < chatData.length; i++) {
                chatData[i][0] = parseInt(chatData[i][0]) - chatStart;
                if (chatData[i][0] < 0) {
                    startIndex = i;
                }
            }
            chatData = chatData.slice(startIndex + 1);
            global.videoElement.addEventListener('timeupdate', function() {
                window.requestAnimationFrame(updateChat);
            });
        }
    });
}

function keydownHandler(event) {
    switch (event.key) {
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
    }
}

function refreshChatWindow() {
    while (global.chatContainer.childElementCount > 50) {
        global.chatContainer.removeChild(global.chatContainer.lastChild);
    }
}

function resizeChat() {
    if (global.chatContainer != null) {
        global.chatContainer.style.maxHeight = global.videoElement.offsetHeight + 'px';
    }
}

function updateChat() {
    if (updatingChat) {
        return;
    }
    updatingChat = true;

    var time = Math.floor(global.videoElement.currentTime * 1000);

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

    // Draw last 50 captured chat messages.
    if (messages.length > 0) {
        messages = messages.slice(-50);
        for (var i = 0; i < messages.length; i++) {
            createMessage(messages[i]);
        }
        refreshChatWindow();
    }

    previousTime = time;

    updatingChat = false;
}