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
