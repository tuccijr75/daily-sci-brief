const CACHE = "brief-v1";
const ASSETS = ["./","./index.html","./daily.json","./daily.csv","./feed.xml","./manifest.json"];
self.addEventListener("install", e=>{ e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener("activate", e=>{ e.waitUntil(self.clients.claim()); });
self.addEventListener("fetch", e=>{
  const url = new URL(e.request.url);
  if (url.pathname.endsWith("/daily.json")) {
    // network-first for fresh data
    e.respondWith(fetch(e.request).then(r=>{
      const clone=r.clone(); caches.open(CACHE).then(c=>c.put(e.request, clone));
      return r;
    }).catch(()=>caches.match(e.request)));
  } else {
    e.respondWith(caches.match(e.request).then(res=>res||fetch(e.request)));
  }
});