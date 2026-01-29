// Service Worker for UrgenceGabon.com PWA
const CACHE_NAME = 'urgencegabon-v1';
const OFFLINE_URL = '/';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Cache the offline page (homepage)
      return cache.add(OFFLINE_URL);
    })
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Tell the active service worker to take control of the page immediately
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // We only want to handle navigation requests (HTML pages)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => {
        // If network fails, return the cached offline page
        return caches.match(OFFLINE_URL);
      })
    );
  }
});
