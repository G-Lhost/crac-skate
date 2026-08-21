"""Chargement des images, polices et sons.

Point cle de l'optimisation : les sprites sont exportes a EXPORT_SCALE fois
leur taille logique, puis redimensionnes **une seule fois** vers la taille
reelle a l'ecran au moment du chargement. Pendant la partie, chaque blit est
donc un copier 1:1 sans aucune mise a l'echelle -- la version d'origine
redimensionnait implicitement a chaque image et rechargeait des surfaces non
converties, ce qui coutait tres cher.
"""

from __future__ import annotations

from pathlib import Path

import pygame

EXPORT_SCALE = 2.5  # doit rester synchronise avec tools/prepare_assets.py

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "assets" / "img"
SND_DIR = ROOT / "assets" / "audio"
FONT_DIR = ROOT / "assets" / "font"

class Assets:
    """Cache de surfaces et de polices, indexe par facteur d'echelle."""

    def __init__(self) -> None:
        self.scale = 1.0
        self._raw: dict[str, pygame.Surface] = {}
        self._scaled: dict[tuple[str, int], pygame.Surface] = {}
        self._fonts: dict[tuple[str, int], pygame.font.Font] = {}
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._font_path = FONT_DIR / "brad.ttf"

    # -- echelle -----------------------------------------------------------
    def set_scale(self, scale: float) -> None:
        """Change le facteur d'echelle ; purge les caches derives."""
        if abs(scale - self.scale) < 1e-4:
            return
        self.scale = scale
        self._scaled.clear()
        self._fonts.clear()

    # -- images ------------------------------------------------------------
    def _load_raw(self, name: str) -> pygame.Surface:
        surf = self._raw.get(name)
        if surf is None:
            surf = pygame.image.load(str(IMG_DIR / f"{name}.png")).convert_alpha()
            self._raw[name] = surf
        return surf

    def logical_size(self, name: str) -> tuple[float, float]:
        """Taille du sprite dans le repere virtuel du jeu."""
        w, h = self._load_raw(name).get_size()
        return w / EXPORT_SCALE, h / EXPORT_SCALE

    def sprite(self, name: str) -> pygame.Surface:
        """Sprite pret a blitter, a la taille exacte de l'ecran."""
        key = (name, int(self.scale * 1000))
        surf = self._scaled.get(key)
        if surf is not None:
            return surf
        raw = self._load_raw(name)
        lw, lh = self.logical_size(name)
        size = (max(1, round(lw * self.scale)), max(1, round(lh * self.scale)))
        surf = pygame.transform.smoothscale(raw, size).convert_alpha()
        self._scaled[key] = surf
        return surf

    def sprite_h(self, name: str, logical_h: float) -> pygame.Surface:
        """Variante a hauteur logique imposee (menu, ecran de fin...)."""
        key = (f"{name}@{logical_h:.1f}", int(self.scale * 1000))
        surf = self._scaled.get(key)
        if surf is not None:
            return surf
        raw = self._load_raw(name)
        h = max(1, round(logical_h * self.scale))
        w = max(1, round(raw.get_width() * h / raw.get_height()))
        surf = pygame.transform.smoothscale(raw, (w, h)).convert_alpha()
        self._scaled[key] = surf
        return surf

    # -- polices -----------------------------------------------------------
    def font(self, logical_size: float) -> pygame.font.Font:
        px = max(8, round(logical_size * self.scale))
        key = ("brad", px)
        f = self._fonts.get(key)
        if f is None:
            if self._font_path.exists():
                f = pygame.font.Font(str(self._font_path), px)
            else:
                f = pygame.font.SysFont("impact,arialblack,sans", px, bold=True)
            self._fonts[key] = f
        return f

    # -- sons --------------------------------------------------------------
    def sound(self, name: str) -> pygame.mixer.Sound | None:
        if name in self._sounds:
            return self._sounds[name]
        path = SND_DIR / f"{name}.mp3"
        snd: pygame.mixer.Sound | None = None
        try:
            if path.exists():
                snd = pygame.mixer.Sound(str(path))
        except pygame.error:
            snd = None
        self._sounds[name] = snd
        return snd

    def music_path(self, name: str) -> str | None:
        p = SND_DIR / f"{name}.mp3"
        return str(p) if p.exists() else None

    def preload(self) -> None:
        """Force le chargement de tout ce qui sert en jeu (evite les micro-freezes)."""
        for name in ("eduardo_tete", "skate", "route", "frites", "alteres",
                     "amaretto", "bequilles", "bale", "ezgy", "drapeau",
                     "eduardo_casse"):
            self.sprite(name)
        for size in (18, 22, 28, 42, 120):
            self.font(size)
