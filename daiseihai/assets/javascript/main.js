import setupSentry from './sentry';

var bookmarkContainer;
var overlayElement;
var videoContainer;
var videoElement;

function bookmarkSeek(event) {
    videoElement.currentTime = this.dataset.position;
}

function closeVideo(event) {
    if (event.target != overlayElement) { return; }
    overlayElement.classList.remove('active');
    while (videoContainer.firstChild) {
        videoContainer.removeChild(videoContainer.firstChild);
    }
    while (bookmarkContainer.firstChild) {
        bookmarkContainer.removeChild(bookmarkContainer.firstChild);
    }
}

function getBookmarks(videoId) {
    fetch('/video/' + videoId + '/bookmarks/').then(function(response) {
        return response.json();
    }).then(function(bookmarks) {
        for (index in bookmarks) {
            var bookmark = bookmarks[index];
            var link = document.createElement('button');
            link.dataset.position = bookmark.position;
            link.innerText = bookmark.name;
            link.addEventListener('click', bookmarkSeek);
            bookmarkContainer.appendChild(link);
        }
    })
}

function keydownHandler(event) {
    if (overlayElement.classList.contains('active')) {
        event.preventDefault();
        switch (event.key) {
            case "ArrowDown":
                videoElement.currentTime -= 60;
                break;
            case "ArrowLeft":
                videoElement.currentTime -= 5;
                break;
            case "ArrowRight":
                videoElement.currentTime += 5;
                break;
            case "ArrowUp":
                videoElement.currentTime += 60;
                break;
        }
    }
}

function loadVideo(event) {
    event.preventDefault();
    videoElement = document.createElement('video')
    videoElement.autoplay = true;
    videoElement.controls = true;
    videoElement.src = this.href;
    videoContainer.appendChild(videoElement);
    getBookmarks(this.dataset.id);
    overlayElement.classList.add('active');
}

function ready() {
    // DOM is ready.
    setupSentry();

    document.addEventListener('keydown', keydownHandler, true);
    bookmarkContainer = document.getElementById('bookmarkContainer');
    overlayElement = document.getElementById('videoOverlay');
    overlayElement.addEventListener('click', closeVideo);
    videoContainer = document.getElementById('videoContainer');
    var streamLinks = document.getElementsByClassName('stream-link');
    for (var i = 0; i < streamLinks.length; i++) {
        streamLinks[i].addEventListener('click', loadVideo);
    }
}

if (document.readyState !== 'loading') {
    ready();
} else {
    document.addEventListener('DOMContentLoaded', ready);
}
