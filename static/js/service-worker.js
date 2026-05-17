const SHELL_CACHE = "fabrix-shell-v1";
const STATIC_CACHE = "fabrix-static-v1";
const OFFLINE_URL = "/static/pwa/offline.html";

const SHELL_ASSETS = [
    "/",
    "/inventory/manage",
    "/billing",
    "/reports",
    "/static/css/style.css",
    "/static/js/app.js",
    "/static/js/dashboard.js",
    "/static/js/inventory.js",
    "/static/js/billing.js",
    "/static/pwa/icons/icon-192.png",
    "/static/pwa/icons/icon-512.png",
    "/manifest.webmanifest",
    OFFLINE_URL,
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((key) => ![SHELL_CACHE, STATIC_CACHE].includes(key))
                    .map((key) => caches.delete(key))
            )
        )
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    const request = event.request;
    const url = new URL(request.url);

    if (request.method !== "GET") {
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    const copy = response.clone();
                    caches.open(SHELL_CACHE).then((cache) => cache.put(request, copy));
                    return response;
                })
                .catch(async () => {
                    const cached = await caches.match(request);
                    return cached || caches.match(OFFLINE_URL);
                })
        );
        return;
    }

    if (url.pathname.startsWith("/static/")) {
        event.respondWith(
            caches.match(request).then((cached) => {
                if (cached) {
                    return cached;
                }
                return fetch(request).then((response) => {
                    const copy = response.clone();
                    caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy));
                    return response;
                });
            })
        );
    }
});
