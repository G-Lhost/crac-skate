"""Musique et bruitages, avec sourdine et degradation silencieuse.

Si le peripherique audio est indisponible (machine sans carte son, session
distante, CI), toutes les methodes deviennent des no-op au lieu de faire
planter le jeu -- ce qui arrivait avec l'appel direct a pygame.mixer.music.
"""

from __future__ import annotations

import math

import pygame

try:
    import numpy as _np
except ImportError:  # numpy est optionnel : sans lui, pas de bruitages generes
    _np = None

from .assets import Assets


def _tone(freq_start: float, freq_end: float, duration: float,
          volume: float = 0.35, wave: str = "sine",
          rate: int = 44100) -> "pygame.mixer.Sound | None":
    """Fabrique un petit bruitage (glissando) sans fichier audio.

    Les bruitages de saut / atterrissage / point n'existaient pas dans le jeu
    d'origine ; les synthetiser evite d'alourdir le depot avec des samples.
    """
    if _np is None or pygame.mixer.get_init() is None:
        return None
    n = max(1, int(rate * duration))
    t = _np.linspace(0.0, duration, n, endpoint=False)
    # frequence interpolee geometriquement -> glissando naturel a l'oreille
    freq = freq_start * (freq_end / freq_start) ** (t / duration)
    phase = 2.0 * math.pi * _np.cumsum(freq) / rate
    if wave == "square":
        sig = _np.sign(_np.sin(phase))
    elif wave == "noise":
        sig = _np.random.default_rng(1).uniform(-1.0, 1.0, n) * _np.sin(phase)
    else:
        sig = _np.sin(phase)
    env = _np.minimum(1.0, t / 0.006) * (1.0 - t / duration) ** 1.6
    sig = (sig * env * volume * 32767.0).astype(_np.int16)
    channels = pygame.mixer.get_init()[2]
    data = _np.repeat(sig[:, None], channels, axis=1) if channels > 1 else sig
    return pygame.sndarray.make_sound(_np.ascontiguousarray(data))


class Audio:
    def __init__(self, assets: Assets) -> None:
        self.assets = assets
        self.muted = False
        self.ok = pygame.mixer.get_init() is not None
        self._current: str | None = None
        self.music_volume = 0.45
        self.sfx_volume = 0.65
        self._generated: dict[str, pygame.mixer.Sound | None] = {}
        if self.ok:
            self._generated = {
                "jump": _tone(430, 860, 0.16, 0.30, "square"),
                "land": _tone(220, 90, 0.13, 0.34, "noise"),
                "score": _tone(880, 1320, 0.09, 0.16),
            }

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        if self.ok:
            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)
        return self.muted

    def music(self, name: str | None, loop: bool = True) -> None:
        if not self.ok:
            return
        if name is None:
            pygame.mixer.music.stop()
            self._current = None
            return
        if name == self._current and pygame.mixer.music.get_busy():
            return
        path = self.assets.music_path(name)
        if not path:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self._current = name
        except pygame.error:
            self.ok = False

    def fade_out(self, ms: int = 350) -> None:
        if self.ok:
            pygame.mixer.music.fadeout(ms)
            self._current = None

    def shutdown(self) -> None:
        """Coupe tout avant de rendre la main au systeme.

        pygame.quit() ne suffit pas toujours a arreter SDL_mixer sur macOS :
        le fil de lecture peut survivre a la fermeture de la fenetre et la
        musique continue dans le terminal. On coupe donc explicitement.
        """
        if not self.ok:
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.stop()
            pygame.mixer.quit()
        except pygame.error:
            pass
        self.ok = False
        self._current = None

    def sfx(self, name: str, volume: float = 1.0) -> None:
        if not self.ok or self.muted:
            return
        snd = self._generated.get(name) or self.assets.sound(name)
        if snd is None:
            return
        snd.set_volume(self.sfx_volume * volume)
        snd.play()
