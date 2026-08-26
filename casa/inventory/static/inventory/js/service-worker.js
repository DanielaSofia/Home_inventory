// Service Worker da PWA Home Inventory — cache do "app shell" e modo offline.
const CACHE_VERSION = "v7";
const CACHE_NAME = `home-inventory-${CACHE_VERSION}`;

const APP_SHELL = [
  "/lista-compras/",
  "/despensa/",
  "/definicoes/",
  "/pwa-diagnostico/",
  "/static/inventory/css/ui-revamp.css",
  "https://unpkg.com/dexie@4.0.8/dist/dexie.min.js",
  "/static/inventory/js/barcode_scanner.js",
  "/static/inventory/js/sync.js",
  "/static/inventory/manifest.json",
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    // Cada recurso é adicionado individualmente: se um falhar (ex.: CDN externo em baixo),
    // não impede os restantes de ficar em cache (cache.addAll falha tudo-ou-nada).
    caches.open(CACHE_NAME).then((cache) =>
      Promise.allSettled(APP_SHELL.map((url) => cache.add(url)))
    )
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  // Forms (POST) não são interceptados: offline, falham e a app trata o caso via sync.js.
  if (request.method !== "GET") return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request).then((cached) => cached || caches.match("/lista-compras/")))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(
      (cached) =>
        cached ||
        fetch(request)
          .then((response) => {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
            return response;
          })
          .catch(() => cached)
    )
  );
});
