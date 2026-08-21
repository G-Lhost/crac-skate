// Silhouettes de Mons : beffroi, collegiale Sainte-Waudru, hotel de
// ville de la Grand-Place, gare Calatrava, maisons a pignons.
//
// FICHIER GENERE -- ne pas modifier a la main.
// Source : python/crac/mons.py, converti par tools/prepare_assets.py.

export const BUILDINGS = {
  beffroi: {
    w: 64, h: 246,
    parts: [
      ["rect", 0, 0, 64, 10, "base"],
      ["rect", 5, 10, 54, 40, "base"],
      ["rect", 13, 50, 38, 100, "base"],
      ["rect", 19, 72, 8, 22, "win"],
      ["rect", 37, 72, 8, 22, "win"],
      ["rect", 19, 108, 8, 22, "win"],
      ["rect", 37, 108, 8, 22, "win"],
      ["rect", 8, 150, 48, 10, "base"],
      ["rect", 3, 152, 11, 32, "base"],
      ["poly", [[2, 184], [15, 184], [8.5, 200]], "base"],
      ["rect", 50, 152, 11, 32, "base"],
      ["poly", [[49, 184], [62, 184], [55.5, 200]], "base"],
      ["rect", 14, 160, 36, 36, "base"],
      ["rect", 20, 167, 9, 21, "win"],
      ["rect", 35, 167, 9, 21, "win"],
      ["poly", [[14, 196], [10, 203], [12, 212], [18, 219], [25, 224], [32, 226], [39, 224], [46, 219], [52, 212], [54, 203], [50, 196]], "base"],
      ["rect", 26, 226, 12, 10, "base"],
      ["poly", [[24, 236], [32, 244], [40, 236]], "base"],
      ["rect", 31.2, 242, 1.6, 4, "base"],
    ],
  },
  waudru: {
    w: 144, h: 194,
    parts: [
      ["rect", 2, 0, 48, 162, "base"],
      ["rect", 0, 162, 52, 9, "base"],
      ["rect", 0, 171, 9, 13, "base"],
      ["poly", [[-1, 184], [10, 184], [4.5, 194]], "base"],
      ["rect", 43, 171, 9, 13, "base"],
      ["poly", [[42, 184], [53, 184], [47.5, 194]], "base"],
      ["rect", 18, 0, 16, 28, "win"],
      ["rect", 13, 62, 26, 56, "win"],
      ["rect", 12, 130, 9, 20, "win"],
      ["rect", 31, 130, 9, 20, "win"],
      ["rect", 50, 0, 80, 80, "base"],
      ["rect", 64, 30, 8, 44, "win"],
      ["rect", 82, 30, 8, 44, "win"],
      ["rect", 100, 30, 8, 44, "win"],
      ["rect", 46, 80, 88, 6, "base"],
      ["rect", 50, 86, 80, 30, "roof"],
      ["rect", 48, 116, 84, 4, "roof"],
      ["rect", 56, 0, 6, 96, "base"],
      ["poly", [[54, 96], [64, 96], [59, 116]], "base"],
      ["rect", 74, 0, 6, 96, "base"],
      ["poly", [[72, 96], [82, 96], [77, 116]], "base"],
      ["rect", 92, 0, 6, 96, "base"],
      ["poly", [[90, 96], [100, 96], [95, 116]], "base"],
      ["rect", 110, 0, 6, 96, "base"],
      ["poly", [[108, 96], [118, 96], [113, 116]], "base"],
      ["rect", 128, 0, 14, 78, "base"],
      ["rect", 126, 78, 18, 5, "base"],
      ["poly", [[126, 83], [135, 100], [144, 83]], "roof"],
      ["rect", 132, 24, 8, 34, "win"],
    ],
  },
  hotel_de_ville: {
    w: 112, h: 146,
    parts: [
      ["rect", 0, 0, 112, 74, "base"],
      ["rect", 0, 74, 112, 7, "base"],
      ["rect", 4, 81, 104, 16, "roof"],
      ["rect", 20, 84, 11, 11, "base"],
      ["rect", 81, 84, 11, 11, "base"],
      ["rect", 10, 6, 12, 22, "win"],
      ["rect", 30, 6, 12, 22, "win"],
      ["rect", 50, 6, 12, 22, "win"],
      ["rect", 70, 6, 12, 22, "win"],
      ["rect", 90, 6, 12, 22, "win"],
      ["rect", 14, 40, 10, 24, "win"],
      ["rect", 34, 40, 10, 24, "win"],
      ["rect", 68, 40, 10, 24, "win"],
      ["rect", 88, 40, 10, 24, "win"],
      ["rect", 48, 97, 16, 24, "base"],
      ["poly", [[46, 121], [44, 126], [47, 132], [51, 136], [56, 138], [61, 136], [65, 132], [68, 126], [66, 121]], "base"],
      ["rect", 51, 138, 10, 5, "base"],
      ["rect", 55.2, 143, 1.6, 3, "base"],
    ],
  },
  gare: {
    w: 186, h: 104,
    parts: [
      ["rect", 0, 0, 186, 14, "base"],
      ["rect", 20, 14, 146, 34, "win"],
      ["rect", 38, 14, 4, 66, "light"],
      ["rect", 84, 14, 4, 82, "light"],
      ["rect", 130, 14, 4, 72, "light"],
      ["poly", [[4, 12], [12, 40], [28, 66], [50, 86], [78, 98], [108, 100], [140, 88], [168, 62], [182, 30], [184, 12], [172, 12], [166, 36], [144, 64], [114, 84], [86, 90], [58, 82], [34, 60], [20, 34], [16, 12]], "light"],
    ],
  },
  maison_escalier: {
    w: 36, h: 76,
    parts: [
      ["rect", 0, 0, 36, 50, "base"],
      ["poly", [[0, 50], [0, 56], [6, 56], [6, 61], [12, 61], [12, 66], [18, 72], [24, 66], [24, 61], [30, 61], [30, 56], [36, 56], [36, 50]], "base"],
      ["rect", 6, 9, 9, 13, "win"],
      ["rect", 21, 9, 9, 13, "win"],
      ["rect", 6, 29, 9, 13, "win"],
      ["rect", 21, 29, 9, 13, "win"],
    ],
  },
  maison_pointue: {
    w: 30, h: 68,
    parts: [
      ["rect", 0, 0, 30, 46, "base"],
      ["poly", [[0, 46], [15, 68], [30, 46]], "roof"],
      ["rect", 5, 10, 8, 14, "win"],
      ["rect", 17, 10, 8, 14, "win"],
      ["rect", 11, 31, 8, 11, "win"],
    ],
  },
  maison_cloche: {
    w: 42, h: 88,
    parts: [
      ["rect", 0, 0, 42, 58, "base"],
      ["poly", [[0, 58], [2, 66], [9, 70], [12, 76], [17, 82], [21, 86], [25, 82], [30, 76], [33, 70], [40, 66], [42, 58]], "base"],
      ["rect", 6, 10, 10, 16, "win"],
      ["rect", 26, 10, 10, 16, "win"],
      ["rect", 6, 34, 10, 16, "win"],
      ["rect", 26, 34, 10, 16, "win"],
    ],
  },
  hotel_maitre: {
    w: 56, h: 128,
    parts: [
      ["rect", 0, 0, 56, 100, "base"],
      ["rect", -2, 100, 60, 7, "base"],
      ["poly", [[0, 107], [6, 122], [50, 122], [56, 107]], "roof"],
      ["rect", 24, 122, 8, 6, "base"],
      ["rect", 8, 14, 11, 16, "win"],
      ["rect", 37, 14, 11, 16, "win"],
      ["rect", 8, 42, 11, 16, "win"],
      ["rect", 22, 42, 11, 16, "win"],
      ["rect", 37, 42, 11, 16, "win"],
      ["rect", 8, 70, 11, 16, "win"],
      ["rect", 37, 70, 11, 16, "win"],
      ["rect", 24, 110, 9, 9, "win"],
    ],
  },
  beguinage: {
    w: 74, h: 112,
    parts: [
      ["rect", 0, 0, 74, 86, "base"],
      ["rect", -2, 86, 78, 6, "base"],
      ["poly", [[2, 92], [10, 108], [64, 108], [72, 92]], "roof"],
      ["rect", 14, 108, 7, 4, "base"],
      ["rect", 54, 108, 7, 4, "base"],
      ["rect", 9, 12, 10, 15, "win"],
      ["rect", 32, 12, 10, 15, "win"],
      ["rect", 55, 12, 10, 15, "win"],
      ["rect", 9, 38, 10, 15, "win"],
      ["rect", 32, 38, 10, 15, "win"],
      ["rect", 55, 38, 10, 15, "win"],
      ["rect", 20, 64, 10, 15, "win"],
      ["rect", 44, 64, 10, 15, "win"],
    ],
  },
};

export const FAR_SEQUENCE = ['hotel_maitre', 'beffroi', 'beguinage', 'hotel_maitre', 'waudru', 'beguinage', 'gare', 'hotel_maitre', 'hotel_de_ville', 'beguinage'];
export const NEAR_SEQUENCE = ['maison_escalier', 'maison_pointue', 'maison_cloche', 'maison_escalier', 'maison_pointue', 'maison_cloche', 'maison_pointue', 'maison_escalier'];
export const FAR_PALETTE = { base: "rgb(54,60,132)", roof: "rgb(41,46,106)", light: "rgb(172,180,228)", win: "rgb(94,99,162)" };
export const NEAR_PALETTE = { base: "rgb(32,36,88)", roof: "rgb(23,26,68)", light: "rgb(104,110,164)", win: "rgb(74,77,118)" };
export const FAR_GAP = [16, 46];
export const NEAR_GAP = [4, 26];
export const MONUMENTS = new Set(['beffroi', 'gare', 'hotel_de_ville', 'waudru']);
export const FILLER_JITTER = [0.84, 1.16];

/** Generateur pseudo-aleatoire deterministe, identique cote Python. */
export function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Portage de mons.layout() : repartit la sequence sans couper un batiment. */
export function layout(sequence, totalW, gapRange, rng) {
  const chosen = [];
  let used = 0;
  let i = 0;
  for (;;) {
    const name = sequence[i % sequence.length];
    const w = BUILDINGS[name].w;
    const gap = gapRange[0] + rng() * (gapRange[1] - gapRange[0]);
    if (used + w + gap > totalW) break;
    const vscale = MONUMENTS.has(name)
      ? 1
      : FILLER_JITTER[0] + rng() * (FILLER_JITTER[1] - FILLER_JITTER[0]);
    chosen.push([name, gap, vscale]);
    used += w + gap;
    i += 1;
  }
  if (!chosen.length) return [];
  const extra = (totalW - used) / chosen.length;
  const placed = [];
  let x = 0;
  for (const [name, gap, vscale] of chosen) {
    placed.push([name, x, vscale]);
    x += BUILDINGS[name].w + gap + extra;
  }
  return placed;
}
