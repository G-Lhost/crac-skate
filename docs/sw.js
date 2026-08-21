// Service worker : le jeu doit se lancer sans reseau une fois installe.
//
// Deux strategies complementaires :
//   - navigation (la page elle-meme) : reseau d'abord, cache en secours.
//     Sans cela, une version installee sur l'ecran d'accueil resterait figee
//     pour toujours, meme apres une nouvelle publication.
//   - le reste (scripts, images, sons) : cache d'abord, c'est ce qui rend le
//     jeu instantane et jouable en mode avion.
//
// Le nom du cache porte un horodatage reecrit a chaque publication par
// tools/publier.sh : un nouveau nom = un nouveau cache = anciens fichiers
// effaces au moment de l'activation.

const CACHE = 'crac-20260821111415';

const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './js/main.js',
  './js/config.js',
  './js/world.js',
  './js/mons.js',
  './js/render.js',
  './js/assets.js',
  './js/audio.js',
  './js/input.js',
  './assets/font/brad.woff',
  './assets/font/brad.ttf',
  './assets/img/eduardo_tete.png',
  './assets/img/skate.png',
  './assets/img/route.png',
  './assets/img/frites.png',
  './assets/img/alteres.png',
  './assets/img/amaretto.png',
  './assets/img/bequilles.png',
  './assets/img/bale.png',
  './assets/img/ezgy.png',
  './assets/img/drapeau.png',
  './assets/img/eduardo_casse.png',
  './assets/audio/hymne.m4a',
  './assets/audio/mamma_mia.m4a',
  './icons/icon-180.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      // addAll echoue en bloc si un seul fichier manque : on tolere les absents.
      .then((c) => Promise.all(SHELL.map((u) => c.add(u).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function keep(request, response) {
  if (response && response.ok
      && new URL(request.url).origin === location.origin) {
    const copy = response.clone();
    caches.open(CACHE).then((c) => c.put(request, copy));
  }
  return response;
}

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;

  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .then((res) => keep(e.request, res))
        .catch(() => caches.match(e.request)
          .then((hit) => hit || caches.match('./index.html')))
    );
    return;
  }

  e.respondWith(
    caches.match(e.request).then((hit) => hit
      || fetch(e.request)
        .then((res) => keep(e.request, res))
        .catch(() => caches.match('./index.html')))
  );
});
