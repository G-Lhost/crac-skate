#!/usr/bin/env python3
"""
CRAC! - Pipeline de preparation des assets.

Reconstruit tous les sprites du jeu a partir des sources d'origine de
"Eduardo_fait_du_skate", en privilegiant les versions haute resolution
(fond blanc) plutot que les vignettes 80x80 aplaties sur le fond bleu.

  - detourage automatique du fond (remplissage par diffusion depuis les bords)
  - recadrage sur le sujet
  - reechantillonnage Lanczos vers une taille "retina" (2.5x la taille logique)
  - export PNG avec canal alpha

Usage:
    python3 tools/prepare_assets.py [--src DOSSIER] [--force]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Le jeu raisonne dans un repere virtuel de 600 px de haut. On exporte les
# sprites a RETINA fois leur taille logique pour rester nets sur un ecran
# d'iPhone (jusqu'a 3x) puis on redimensionne une seule fois au chargement.
RETINA = 2.5


# --------------------------------------------------------------------------
# Detourage
# --------------------------------------------------------------------------

def _border_pixels(w: int, h: int, step: int = 1):
    for x in range(0, w, step):
        yield x, 0
        yield x, h - 1
    for y in range(0, h, step):
        yield 0, y
        yield w - 1, y


def dominant_border_color(im: Image.Image) -> tuple[int, int, int]:
    """Couleur mediane du liseré de 1 px : c'est le fond dans 100% des sources."""
    w, h = im.size
    arr = np.array(im.convert("RGB"))
    edge = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]])
    return tuple(int(v) for v in np.median(edge, axis=0))


def cutout(im: Image.Image, thresh: int = 32, erode: int = 1,
           feather: float = 0.6) -> Image.Image:
    """Rend le fond transparent.

    On part des pixels de bordure qui ressemblent a la couleur de fond et on
    diffuse avec tolerance. Contrairement a un simple seuillage global, cela
    ne perce pas de trous dans le sujet (la chemise blanche de Bale, les
    halteres gris clair sur fond blanc...).
    """
    im = im.convert("RGB")
    w, h = im.size
    bg = dominant_border_color(im)
    key = (255, 0, 255)

    work = im.copy()
    px = work.load()
    for x, y in _border_pixels(w, h):
        c = px[x, y]
        if c == key:
            continue
        if sum(abs(a - b) for a, b in zip(c, bg)) > thresh * 3:
            continue  # seed sur le sujet : on ne diffuse pas depuis la
        ImageDraw.floodfill(work, (x, y), key, thresh=thresh)

    arr = np.array(work)
    mask = np.all(arr == np.array(key, dtype=np.uint8), axis=-1)
    alpha = np.where(mask, 0, 255).astype(np.uint8)

    a = Image.fromarray(alpha, "L")
    if erode:
        # MinFilter ronge le contour : supprime le lisere de fond restant.
        a = a.filter(ImageFilter.MinFilter(1 + 2 * erode))
    if feather:
        a = a.filter(ImageFilter.GaussianBlur(feather))

    out = im.convert("RGBA")
    out.putalpha(a)
    return out


def autocrop(im: Image.Image, pad: int = 0) -> Image.Image:
    bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if not bbox:
        return im
    if pad:
        l, t, r, b = bbox
        bbox = (max(0, l - pad), max(0, t - pad),
                min(im.width, r + pad), min(im.height, b + pad))
    return im.crop(bbox)


def fit(im: Image.Image, logical_w: float | None, logical_h: float | None) -> Image.Image:
    """Redimensionne vers la taille logique * RETINA en gardant le ratio."""
    tw = logical_w * RETINA if logical_w else None
    th = logical_h * RETINA if logical_h else None
    if tw and th:
        scale = min(tw / im.width, th / im.height)
    elif tw:
        scale = tw / im.width
    else:
        scale = th / im.height
    size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    return im.resize(size, Image.LANCZOS)


def seamless_h(im: Image.Image, blend: int = 90) -> Image.Image:
    """Rend une texture raccordable horizontalement (fondu croise des bords)."""
    w, h = im.size
    blend = min(blend, w // 4)
    arr = np.asarray(im.convert("RGB"), dtype=np.float32)
    left = arr[:, :blend].copy()
    right = arr[:, w - blend:].copy()
    ramp = np.linspace(0.0, 1.0, blend, dtype=np.float32)[None, :, None]
    merged = right * (1.0 - ramp) + left * ramp
    arr[:, :blend] = merged
    arr = arr[:, : w - blend]  # on supprime la zone dupliquee
    return Image.fromarray(arr.astype(np.uint8), "RGB")


# --------------------------------------------------------------------------
# Recettes : quel fichier source pour quel sprite
# --------------------------------------------------------------------------
# (nom de sortie, [sources par ordre de preference], largeur, hauteur, options)
SPRITES = [
    # Heros
    ("eduardo_tete", ["Tete d Ed.png", "tete.png"],            None, 110, {}),
    ("skate",        ["http_%2F%2Fg-ecx.images-amazon.com%2Fimages%2FG%2F01%2F"
                      "aplusautomation%2Fvendorimages%2Fc2441330-6644-4d60-b5c2-"
                      "e1ceac2b49ca._CB323379867_.jpg",
                      "imgserver (2).jpg", "skateboard.jpg"],  192, None, {}),
    # Obstacles
    ("alteres",   ["Alteres.jpg", "Altères.jpg"],              None, 62,  {}),
    ("amaretto",  ["Bouteille_amareto.jpg", "amaretto.jpg"],   None, 96,  {}),
    ("bequilles", ["Béquilles.jpg", "bequilles.jpg"],          None, 104, {}),
    ("bale",      ["Bale.jpg", "foot.jpg"],                    None, 88,  {}),
    ("ezgy",      ["Ezgy.jpg"],                                None, 88,  {"thresh": 46}),
    ("drapeau",   ["http_%2F%2Fwww.drapeauxdespays.fr%2Fdata%2Fflags%2Fbig%2Fit.png",
                   "Drapeau.jpg"],                             96,   None, {"cut": False}),
    ("frites",    ["frites.png"],                              80,   None, {"cut": False}),
    # Ecran de game over
    ("eduardo_casse", ["Eduardo_casse.jpg"],                   None, 320, {"cut": False}),
]

# (nom de sortie, fichier source, embarque dans la version web ?)
AUDIO = [
    ("hymne", "Hymne.mp3", True),        # musique de jeu
    ("mamma_mia", "mama_mia.mp3", True), # game over
    ("game_over", "Son_gameOver.mp3", False),
]

FONT = ("brad.ttf", "BradBunR.ttf")


def build_sprites(src: Path, out_dirs: list[Path]) -> None:
    for name, candidates, lw, lh, opt in SPRITES:
        source = next((src / c for c in candidates if (src / c).exists()), None)
        if source is None:
            print(f"  !! aucune source pour {name} ({candidates[0]})")
            continue
        im = Image.open(source)
        if opt.get("cut", True):
            im = cutout(im, thresh=opt.get("thresh", 32),
                        erode=opt.get("erode", 1))
            im = autocrop(im, pad=1)
        else:
            im = im.convert("RGBA")
        im = fit(im, lw, lh)
        for d in out_dirs:
            im.save(d / f"{name}.png", optimize=True)
        print(f"  {name:16s} <- {source.name[:34]:36s} {im.size[0]}x{im.size[1]}")

    # Route : texture raccordable
    road = Image.open(src / "route.jpg")
    road = seamless_h(road, blend=110)
    road = road.resize((round(road.width * 1.2), 500), Image.LANCZOS)
    for d in out_dirs:
        road.save(d / "route.png", optimize=True)
    print(f"  {'route':16s} <- route.jpg (raccordable)          "
          f"{road.size[0]}x{road.size[1]}")


def build_audio(src: Path, py_dir: Path, web_dir: Path) -> None:
    for name, fname, on_web in AUDIO:
        s = src / fname
        if not s.exists():
            print(f"  !! audio manquant : {fname}")
            continue
        shutil.copy2(s, py_dir / f"{name}.mp3")
        if not on_web:
            print(f"  {name:16s} bureau uniquement")
            continue
        # Version web : AAC 64 kbit/s mono, ~3x plus legere a telecharger.
        dst = web_dir / f"{name}.m4a"
        ok = False
        if shutil.which("afconvert"):
            r = subprocess.run(
                ["afconvert", "-f", "m4af", "-d", "aac", "-b", "64000",
                 "--mix", "-c", "1", str(s), str(dst)],
                capture_output=True)
            ok = r.returncode == 0 and dst.exists()
        if not ok:
            shutil.copy2(s, web_dir / f"{name}.mp3")
            print(f"  {name:16s} mp3 copie tel quel ({s.stat().st_size // 1024} Ko)")
        else:
            print(f"  {name:16s} mp3 {s.stat().st_size // 1024} Ko "
                  f"-> m4a {dst.stat().st_size // 1024} Ko")


def build_icons(src: Path, web_icons: Path) -> None:
    """Icones PWA / iOS a partir de la tete d'Eduardo sur fond bleu."""
    head = cutout(Image.open(src / "Tete d Ed.png"))
    head = autocrop(head)
    for size in (180, 192, 512, 1024):
        canvas = Image.new("RGBA", (size, size), (77, 84, 181, 255))
        h = head.copy()
        h.thumbnail((int(size * 0.78), int(size * 0.78)), Image.LANCZOS)
        canvas.alpha_composite(h, ((size - h.width) // 2,
                                   (size - h.height) // 2))
        canvas.convert("RGB").save(web_icons / f"icon-{size}.png", optimize=True)
    # Icone "maskable" : marge de securite pour le rognage Android.
    size = 512
    canvas = Image.new("RGBA", (size, size), (77, 84, 181, 255))
    h = head.copy()
    h.thumbnail((int(size * 0.55), int(size * 0.55)), Image.LANCZOS)
    canvas.alpha_composite(h, ((size - h.width) // 2, (size - h.height) // 2))
    canvas.convert("RGB").save(web_icons / "icon-maskable-512.png", optimize=True)
    print(f"  icones PWA/iOS   180, 192, 512, 1024 + maskable")


def build_mons_js(root: Path) -> None:
    """Genere web/js/mons.js a partir de python/crac/mons.py.

    Les silhouettes de Mons ne sont decrites qu'une fois, du cote Python. Ce
    generateur garantit que la version navigateur affiche exactement la meme
    ville, sans avoir a maintenir deux listes de coordonnees.
    """
    sys.path.insert(0, str(root / "python"))
    from crac import mons  # noqa: PLC0415

    def js_num(v: float) -> str:
        return str(int(v)) if float(v).is_integer() else repr(round(float(v), 3))

    def js_part(part) -> str:
        tint = part[-1]
        if part[0] == "rect":
            _, x, y, w, h, _ = part
            nums = ", ".join(js_num(v) for v in (x, y, w, h))
            return f'["rect", {nums}, "{tint}"]'
        if part[0] == "poly":
            pts = ", ".join(f"[{js_num(a)}, {js_num(b)}]" for a, b in part[1])
            return f'["poly", [{pts}], "{tint}"]'
        _, cx, cy, r, _ = part
        nums = ", ".join(js_num(v) for v in (cx, cy, r))
        return f'["circle", {nums}, "{tint}"]'

    def js_palette(pal: dict) -> str:
        items = ", ".join(f'{k}: "rgb({c[0]},{c[1]},{c[2]})"' for k, c in pal.items())
        return "{ " + items + " }"

    lines = [
        "// Silhouettes de Mons : beffroi, collegiale Sainte-Waudru, hotel de",
        "// ville de la Grand-Place, gare Calatrava, maisons a pignons.",
        "//",
        "// FICHIER GENERE -- ne pas modifier a la main.",
        "// Source : python/crac/mons.py, converti par tools/prepare_assets.py.",
        "",
        "export const BUILDINGS = {",
    ]
    for name, b in mons.BUILDINGS.items():
        lines.append(f'  {name}: {{')
        lines.append(f'    w: {js_num(b["w"])}, h: {js_num(b["h"])},')
        lines.append("    parts: [")
        for part in b["parts"]:
            lines.append(f"      {js_part(part)},")
        lines.append("    ],")
        lines.append("  },")
    lines.append("};")
    lines.append("")
    seq = lambda names: "[" + ", ".join(f"'{n}'" for n in names) + "]"
    lines.append(f"export const FAR_SEQUENCE = {seq(mons.FAR_SEQUENCE)};")
    lines.append(f"export const NEAR_SEQUENCE = {seq(mons.NEAR_SEQUENCE)};")
    lines.append(f"export const FAR_PALETTE = {js_palette(mons.FAR_PALETTE)};")
    lines.append(f"export const NEAR_PALETTE = {js_palette(mons.NEAR_PALETTE)};")
    lines.append(f"export const FAR_GAP = [{js_num(mons.FAR_GAP[0])}, {js_num(mons.FAR_GAP[1])}];")
    lines.append(f"export const NEAR_GAP = [{js_num(mons.NEAR_GAP[0])}, {js_num(mons.NEAR_GAP[1])}];")
    lines.append("export const MONUMENTS = new Set("
                 + seq(sorted(mons.MONUMENTS)) + ");")
    lines.append(f"export const FILLER_JITTER = [{js_num(mons.FILLER_JITTER[0])}, "
                 f"{js_num(mons.FILLER_JITTER[1])}];")
    lines.append("""
/** Generateur pseudo-aleatoire deterministe, identique cote Python
 *  (voir mons.mulberry32) : c'est lui qui garantit que les deux versions
 *  affichent la meme ville, batiment par batiment. */
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
""")
    out = root / "web" / "js" / "mons.js"
    out.write_text("\n".join(lines), "utf-8")
    n = sum(len(b["parts"]) for b in mons.BUILDINGS.values())
    print(f"  {len(mons.BUILDINGS)} batiments, {n} primitives -> web/js/mons.js")


def inject_legacy_best(src: Path, config_js: Path) -> int:
    """Recopie le record de la base SQLite de 2016 dans la config web.

    La version navigateur ne peut pas lire le fichier "Donnees" ; on fige donc
    la valeur dans config.js au moment de la preparation des assets.
    """
    best = 0
    db = src / "Données"
    if db.exists():
        try:
            with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
                row = conn.execute("select max(score) from membres").fetchone()
            best = int(row[0]) if row and row[0] is not None else 0
        except (sqlite3.Error, TypeError, ValueError):
            best = 0
    if config_js.exists():
        text = config_js.read_text("utf-8")
        new = re.sub(r"export const LEGACY_BEST = \d+;",
                     f"export const LEGACY_BEST = {best};", text)
        if new != text:
            config_js.write_text(new, "utf-8")
    return best


def build_font(src: Path, py_dir: Path, web_dir: Path) -> None:
    """Copie la police et en produit une version acceptee par les navigateurs.

    Le BradBunR.ttf d'origine (Brady Bunch Remastered, 2001) embarque des
    tables PCLT/hdmx que le controleur de polices de Chrome et Safari
    refusent : la @font-face passe alors en erreur et le jeu retombe sur
    Impact. On la reconstruit avec fontTools et on exporte aussi un WOFF.
    """
    out, fname = FONT
    source = src / fname
    if not source.exists():
        print(f"  !! police introuvable : {fname}")
        return
    shutil.copy2(source, py_dir / out)          # pygame accepte l'original
    made_woff = False
    try:
        from fontTools.ttLib import TTFont

        font = TTFont(str(source))
        for table in ("PCLT", "hdmx"):
            if table in font:
                del font[table]
        font.save(str(web_dir / out))
        font.flavor = "woff"
        font.save(str(web_dir / "brad.woff"))
        made_woff = True
    except Exception as exc:                    # noqa: BLE001
        shutil.copy2(source, web_dir / out)
        print(f"  fontTools indisponible ({exc.__class__.__name__}) : copie brute")
    print(f"  {fname} -> {out}" + (" + brad.woff (nettoyee)" if made_woff else ""))


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=root.parent,
                    help="dossier du jeu d'origine")
    args = ap.parse_args()

    src: Path = args.src
    if not (src / "Ed_Skate.py").exists():
        print(f"Sources introuvables dans {src}", file=sys.stderr)
        return 1

    py_img = root / "python" / "assets" / "img"
    web_img = root / "web" / "assets" / "img"
    py_audio = root / "python" / "assets" / "audio"
    web_audio = root / "web" / "assets" / "audio"
    icons = root / "web" / "icons"
    for d in (py_img, web_img, py_audio, web_audio, icons,
              root / "python" / "assets" / "font", root / "web" / "assets" / "font"):
        d.mkdir(parents=True, exist_ok=True)

    print(f"Sources : {src}")
    print("Sprites :")
    build_sprites(src, [py_img, web_img])
    print("Audio :")
    build_audio(src, py_audio, web_audio)
    print("Icones :")
    build_icons(src, icons)

    print("Decor de Mons :")
    build_mons_js(root)

    best = inject_legacy_best(src, root / "web" / "js" / "config.js")
    print(f"Record 2016 : {best} (injecte dans web/js/config.js)")

    print("Police :")
    build_font(src, root / "python" / "assets" / "font",
               root / "web" / "assets" / "font")
    print("\nTermine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
