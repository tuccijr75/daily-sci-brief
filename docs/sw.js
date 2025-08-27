// Minimal offline cache: cache-busts on file change via version string below.
const VERSION = "v3";
const CORE = [
  "./",
  "./index.html",
  "./archive.html",
  "./manifest.json",
  "./sw.js",
  "./daily.json",
  "./daily.csv",
  "./feed.xml",
  "./records/index.json"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.origin === location.origin) {
    // network-first for JSON; cache-first for static
    if (url.pathname.endsWith(".json")) {
      e.respondWith(
        fetch(e.request).then(r => {
          const clone = r.clone();
          caches.open(VERSION).then(c => c.put(e.request, clone));
          return r;
        }).catch(() => caches.match(e.request))
      );
      return;
    }
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
  }
});
