import setupSentry from './sentry';
import {ready as videoReady} from './video'


function ready() {
    // DOM is ready.
    setupSentry();

    if (document.getElementById('videoPage') != null) {
        videoReady();
    }
}

if (document.readyState !== 'loading') {
    ready();
} else {
    document.addEventListener('DOMContentLoaded', ready);
}
