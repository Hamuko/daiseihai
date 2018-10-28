import * as Sentry from '@sentry/browser';

export default function setupSentry() {
    let release = document.querySelector('meta[name=release]').content;
    Sentry.init({
        dsn: 'https://abca44c8d2a64a9b999a6fdc238b680e@sentry.io/1264504',
        release: release,
        ignoreErrors: [
            "ResizeObserver loop limit exceeded",
            "Synchronous XMLHttpRequest on the main thread is deprecated",
            "Element.createShadowRoot is deprecated",
        ],
    });
}
