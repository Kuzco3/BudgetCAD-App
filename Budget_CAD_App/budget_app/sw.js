// ═══════════════════════════════════════════════════════════════
//  SERVICE WORKER — BudgetCAD PWA
//  Cache-first strategy pour fonctionnement 100% hors-ligne
// ═══════════════════════════════════════════════════════════════
const CACHE_NAME = 'budgetcad-v3';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
];

// ── Installation : mise en cache des assets ──────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS).catch(err => {
        console.warn('Cache partiel:', err);
      });
    })
  );
  self.skipWaiting();
});

// ── Activation : nettoyage des anciens caches ────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ── Fetch : cache-first avec fallback réseau ─────────────────
self.addEventListener('fetch', event => {
  // Ne pas intercepter les requêtes non-GET
  if (event.request.method !== 'GET') return;

  // Ne pas intercepter les extensions Chrome ou autres protocoles
  if (!event.request.url.startsWith('http')) return;

  // Stratégie : cache first, fallback network
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;

      return fetch(event.request.clone()).then(response => {
        // Mettre en cache les nouvelles ressources valides
        if (response && response.status === 200 && response.type === 'basic') {
          const toCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, toCache);
          });
        }
        return response;
      }).catch(() => {
        // Hors-ligne : retourner la page principale
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      });
    })
  );
});

// ── Push notifications (optionnel) ───────────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  self.registration.showNotification(data.title || 'BudgetCAD', {
    body: data.body || '',
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    tag: 'budgetcad',
    renotify: true,
  });
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(windowClients => {
      if (windowClients.length > 0) {
        windowClients[0].focus();
      } else {
        clients.openWindow('/');
      }
    })
  );
});
