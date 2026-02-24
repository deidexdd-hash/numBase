/**
 * Service Worker — Нумерология и Ансестология v4.0
 * Phase 9: PWA offline support
 *
 * Стратегии:
 *   /api/*            → Network-first (cache fallback при offline)
 *   data/*.json       → Cache-first (стабильные данные)
 *   fonts.googleapis  → Stale-while-revalidate
 *   всё остальное     → Cache-first (HTML, CSS, JS, SVG)
 */

const CACHE_NAME = 'numerology-v4';
const CACHE_DATA = 'numerology-data-v4';
const CACHE_API  = 'numerology-api-v4';

// Файлы, которые кэшируем при установке (app shell)
const PRECACHE_STATIC = [
  '/',
  '/index.html',
];

// Data-файлы (JSON) — кэшируем отдельно, cache-first
const PRECACHE_DATA = [
  '../data/formulas.json',
  '../data/practices.json',
  '../data/number_meanings.json',
  '../data/algorithms.json',
];

// ──────────────────────────────────────────────
// INSTALL — precache app shell + data
// ──────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    Promise.all([
      caches.open(CACHE_NAME).then(cache => {
        return cache.addAll(PRECACHE_STATIC).catch(err => {
          console.warn('[SW] Static precache partial fail:', err);
        });
      }),
      caches.open(CACHE_DATA).then(cache => {
        return cache.addAll(PRECACHE_DATA).catch(err => {
          console.warn('[SW] Data precache partial fail:', err);
        });
      }),
    ]).then(() => self.skipWaiting())
  );
});

// ──────────────────────────────────────────────
// ACTIVATE — clean up old cache versions
// ──────────────────────────────────────────────
self.addEventListener('activate', event => {
  const validCaches = [CACHE_NAME, CACHE_DATA, CACHE_API];
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => !validCaches.includes(k))
          .map(k => {
            console.log('[SW] Deleting old cache:', k);
            return caches.delete(k);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ──────────────────────────────────────────────
// FETCH — routing by URL pattern
// ──────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET, chrome-extension, etc.
  if (request.method !== 'GET') return;
  if (!url.protocol.startsWith('http')) return;

  // 1. API requests → Network-first
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request, CACHE_API));
    return;
  }

  // 2. Google Fonts → Stale-while-revalidate
  if (url.hostname.includes('fonts.googleapis.com') ||
      url.hostname.includes('fonts.gstatic.com')) {
    event.respondWith(staleWhileRevalidate(request, CACHE_NAME));
    return;
  }

  // 3. Data JSON files → Cache-first
  if (url.pathname.includes('/data/') && url.pathname.endsWith('.json')) {
    event.respondWith(cacheFirst(request, CACHE_DATA));
    return;
  }

  // 4. Everything else (HTML, CSS, JS, SVG icons) → Cache-first
  event.respondWith(cacheFirst(request, CACHE_NAME));
});

// ──────────────────────────────────────────────
// STRATEGY HELPERS
// ──────────────────────────────────────────────

/** Network-first: try network, fall back to cache */
async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch {
    const cached = await cache.match(request);
    if (cached) return cached;
    // Offline fallback for API
    return new Response(
      JSON.stringify({ error: 'offline', message: 'Нет соединения. Проверьте подключение к интернету.' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

/** Cache-first: try cache, fall back to network */
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch {
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      const offlinePage = await cache.match('/') || await cache.match('/index.html');
      if (offlinePage) return offlinePage;
    }
    return new Response('Offline — ресурс недоступен', { status: 503 });
  }
}

/** Stale-while-revalidate: return cache immediately, update in background */
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  const networkFetch = fetch(request).then(response => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  }).catch(() => cached);
  return cached || networkFetch;
}

// ──────────────────────────────────────────────
// MESSAGE — handle skip waiting from client
// ──────────────────────────────────────────────
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'CACHE_PURGE') {
    caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k))));
  }
});
