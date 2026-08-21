// Chargement des images et de la police, avec suivi de progression.

export const EXPORT_SCALE = 2.5;   // cf. tools/prepare_assets.py

export const IMAGE_NAMES = [
  'eduardo_tete', 'skate', 'route', 'frites', 'alteres', 'amaretto',
  'bequilles', 'bale', 'ezgy', 'drapeau', 'eduardo_casse',
];

export class Assets {
  constructor() {
    this.images = {};
    this.ready = false;
  }

  /** Taille du sprite dans le repere virtuel du jeu (600 px de haut). */
  size(name) {
    const img = this.images[name];
    return img
      ? { w: img.naturalWidth / EXPORT_SCALE, h: img.naturalHeight / EXPORT_SCALE }
      : { w: 0, h: 0 };
  }

  async load(onProgress) {
    let done = 0;
    const total = IMAGE_NAMES.length;
    await Promise.all(IMAGE_NAMES.map((name) => new Promise((resolve) => {
      const img = new Image();
      img.decoding = 'async';
      img.onload = img.onerror = () => {
        this.images[name] = img;
        done += 1;
        if (onProgress) onProgress(done / total);
        resolve();
      };
      img.src = `assets/img/${name}.png`;
    })));

    // La police doit etre prete avant le premier fillText, sinon le premier
    // rendu utilise la police de secours puis "saute".
    if (document.fonts) {
      try {
        await document.fonts.load('40px BradBunR');
        await document.fonts.ready;
      } catch (_) { /* police de secours */ }
    }
    this.ready = true;
  }
}
