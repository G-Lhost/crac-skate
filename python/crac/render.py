"""Couche de presentation : decors, sprites, HUD, ecrans.

Toutes les coordonnees manipulees par le jeu sont "logiques" (repere de
600 px de haut). Le viewport les convertit en pixels ecran. Les decors
paralaxes et le degrade de ciel sont pre-rendus dans des surfaces mises en
cache et simplement decales : on ne redessine jamais un degrade pixel par
pixel dans la boucle.
"""

from __future__ import annotations

import math

import pygame

from . import config as C
from . import mons
from .assets import Assets
from .world import World


class Viewport:
    """Conversion repere logique -> pixels ecran, avec bandes noires si besoin."""

    def __init__(self, size: tuple[int, int]) -> None:
        self.scale = 1.0
        self.view_w = float(C.VIEW_W_DEFAULT)
        self.ox = self.oy = 0.0
        self.win_w, self.win_h = size
        self.resize(size)

    def resize(self, size: tuple[int, int]) -> None:
        w, h = max(1, size[0]), max(1, size[1])
        self.win_w, self.win_h = w, h
        scale = h / C.VIEW_H
        view_w = w / scale
        if view_w < C.VIEW_W_MIN:            # ecran trop etroit : on dezoome
            scale = w / C.VIEW_W_MIN
            view_w = C.VIEW_W_MIN
        elif view_w > C.VIEW_W_MAX:          # ecran tres large : bandes laterales
            view_w = C.VIEW_W_MAX
        self.scale = scale
        self.view_w = view_w
        self.ox = (w - view_w * scale) * 0.5
        self.oy = (h - C.VIEW_H * scale) * 0.5

    # conversions
    def x(self, v: float) -> float:
        return self.ox + v * self.scale

    def y(self, v: float) -> float:
        return self.oy + v * self.scale

    def s(self, v: float) -> float:
        return v * self.scale

    def rect(self, x: float, y: float, w: float, h: float) -> pygame.Rect:
        return pygame.Rect(round(self.x(x)), round(self.y(y)),
                           max(1, round(w * self.scale)),
                           max(1, round(h * self.scale)))


def _vgradient(size: tuple[int, int], top: tuple[int, int, int],
               bottom: tuple[int, int, int]) -> pygame.Surface:
    """Degrade vertical : rendu 1 px de large puis etire (rapide et lisse)."""
    strip = pygame.Surface((1, size[1]), pygame.SRCALPHA)
    for i in range(size[1]):
        t = i / max(1, size[1] - 1)
        strip.set_at((0, i), (
            round(top[0] + (bottom[0] - top[0]) * t),
            round(top[1] + (bottom[1] - top[1]) * t),
            round(top[2] + (bottom[2] - top[2]) * t), 255))
    return pygame.transform.smoothscale(strip, size).convert()


class Backdrop:
    """Decors paralaxes pre-rendus, regeneres seulement si le viewport change."""

    def __init__(self) -> None:
        self._key: tuple[int, int] | None = None
        self.sky: pygame.Surface | None = None
        self.far: pygame.Surface | None = None
        self.near: pygame.Surface | None = None
        self.sun: pygame.Surface | None = None

    def ensure(self, vp: Viewport) -> None:
        key = (round(vp.view_w), round(vp.scale * 1000))
        if key == self._key:
            return
        self._key = key
        w = max(1, round(vp.view_w * vp.scale))
        h = max(1, round(C.VIEW_H * vp.scale))
        self.sky = _vgradient((w, h), C.SKY_TOP, C.SKY_BOT)
        self.far = self._cityscape(vp, mons.FAR_SEQUENCE, mons.FAR_PALETTE,
                                   mons.FAR_GAP, seed=7)
        self.near = self._cityscape(vp, mons.NEAR_SEQUENCE, mons.NEAR_PALETTE,
                                    mons.NEAR_GAP, seed=21)
        self.sun = self._sun(vp)

    @staticmethod
    def _sun(vp: Viewport, logical_r: float = 62.0) -> pygame.Surface:
        """Disque + halo a decroissance douce, rendu une fois pour toutes.

        Dessine en petit puis agrandi : le lissage de smoothscale fait
        disparaitre les anneaux qu'on obtient en empilant des cercles.
        """
        n = 128
        small = pygame.Surface((n, n), pygame.SRCALPHA)
        cx = cy = n / 2.0
        for r in range(n // 2, 0, -1):
            t = r / (n / 2.0)
            if t <= 0.30:
                col = (255, 238, 196, 255)
            else:
                k = (1.0 - (t - 0.30) / 0.70) ** 2.4
                col = (255, 206, 138, int(150 * k))
            pygame.draw.circle(small, col, (cx, cy), r)
        size = max(4, round(logical_r * 4.0 * vp.scale))
        return pygame.transform.smoothscale(small, (size, size)).convert_alpha()

    @staticmethod
    def _cityscape(vp: Viewport, sequence: list[str], palette: dict,
                   gap_range: tuple[float, float], seed: int) -> pygame.Surface:
        """Bande de decor montois, large de deux ecrans et raccordable.

        Les monuments viennent de crac/mons.py : beffroi, collegiale
        Sainte-Waudru, hotel de ville de la Grand-Place, gare Calatrava.
        """
        rng = mons.mulberry32(seed)
        lw = vp.view_w * 2.0
        surf = pygame.Surface((round(lw * vp.scale), round(C.VIEW_H * vp.scale)),
                              pygame.SRCALPHA)
        k = vp.scale

        for name, x0, vs in mons.layout(sequence, lw, gap_range, rng):
            for part in mons.BUILDINGS[name]["parts"]:
                colour = palette[part[-1]]
                if part[0] == "rect":
                    _, x, y, w, h, _ = part
                    pygame.draw.rect(surf, colour, pygame.Rect(
                        round((x0 + x) * k),
                        round((C.GROUND_Y - (y + h) * vs) * k),
                        max(1, round(w * k)), max(1, round(h * vs * k))))
                elif part[0] == "poly":
                    pts = [(round((x0 + px) * k),
                            round((C.GROUND_Y - py * vs) * k))
                           for px, py in part[1]]
                    if len(pts) >= 3:
                        pygame.draw.polygon(surf, colour, pts)
                elif part[0] == "circle":
                    _, cx, cy, rad, _ = part
                    pygame.draw.circle(surf, colour,
                                       (round((x0 + cx) * k),
                                        round((C.GROUND_Y - cy * vs) * k)),
                                       max(1, round(rad * k)))
        return surf.convert_alpha()


class Renderer:
    def __init__(self, screen: pygame.Surface, assets: Assets) -> None:
        self.screen = screen
        self.assets = assets
        self.vp = Viewport(screen.get_size())
        self.backdrop = Backdrop()
        self._rot_cache: dict[tuple[str, int, int], pygame.Surface] = {}
        self._dot_cache: dict[tuple, pygame.Surface] = {}
        self._veil: pygame.Surface | None = None

    def resize(self, size: tuple[int, int]) -> None:
        self.vp.resize(size)
        self.assets.set_scale(self.vp.scale)
        self._rot_cache.clear()
        self._dot_cache.clear()
        self._veil = None

    # ------------------------------------------------------------------
    # utilitaires
    # ------------------------------------------------------------------
    def _rotated(self, name: str, angle_deg: float,
                 squash: float = 1.0) -> pygame.Surface:
        """Sprite tourne (par pas de 2 degres) et eventuellement ecrase.

        Le resultat est memorise : sans cela, chaque image du jeu paierait une
        rotation et un smoothscale, les deux operations les plus couteuses de
        pygame.
        """
        q = int(round(angle_deg / 2.0)) * 2
        key = (name, q, int(self.vp.scale * 1000), round(squash * 100))
        surf = self._rot_cache.get(key)
        if surf is not None:
            return surf
        base = self.assets.sprite(name)
        if squash != 1.0:
            base = pygame.transform.smoothscale(
                base, (max(1, round(base.get_width() * (2.0 - squash) ** 0.35)),
                       max(1, round(base.get_height() * squash))))
        surf = base if q == 0 else pygame.transform.rotate(base, q)
        self._rot_cache[key] = surf
        return surf

    def _dot(self, color: tuple[int, int, int], size: int,
             alpha: int) -> pygame.Surface:
        """Petit carre translucide reutilise pour les particules."""
        key = (color, size, alpha >> 5)
        surf = self._dot_cache.get(key)
        if surf is None:
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            surf.fill((*color, ((alpha >> 5) << 5) | 31))
            self._dot_cache[key] = surf
        return surf

    def text(self, s: str, size: float, x: float, y: float,
             color: tuple[int, int, int] = C.WHITE, center: bool = False,
             shadow: bool = True, alpha: int = 255,
             right: bool = False) -> pygame.Rect:
        """Ecrit un texte ; (x, y) est en coordonnees logiques.

        center : (x, y) est le centre. right : (x, y) est le coin haut-droit.
        """
        font = self.assets.font(size)
        surf = font.render(s, True, color)
        if alpha < 255:
            surf = surf.copy()
            surf.set_alpha(alpha)
        rect = surf.get_rect()
        px, py = self.vp.x(x), self.vp.y(y)
        if center:
            rect.center = (round(px), round(py))
        elif right:
            rect.topright = (round(px), round(py))
        else:
            rect.topleft = (round(px), round(py))
        if shadow:
            sh = font.render(s, True, C.SHADOW)
            if alpha < 255:
                sh = sh.copy()
                sh.set_alpha(alpha // 2)
            off = max(1, round(self.vp.s(2.5)))
            self.screen.blit(sh, (rect.x + off, rect.y + off))
        self.screen.blit(surf, rect)
        return rect

    def dim(self, alpha: int = 165) -> None:
        if self._veil is None or self._veil.get_size() != self.screen.get_size():
            self._veil = pygame.Surface(self.screen.get_size()).convert()
            self._veil.fill((10, 12, 30))
        self._veil.set_alpha(alpha)
        self.screen.blit(self._veil, (0, 0))

    # ------------------------------------------------------------------
    # decor
    # ------------------------------------------------------------------
    def draw_background(self, scroll: float, shake: tuple[float, float]) -> None:
        vp = self.vp
        self.backdrop.ensure(vp)
        self.screen.fill((6, 7, 20))
        sx, sy = self.vp.s(shake[0]), self.vp.s(shake[1])
        self.screen.blit(self.backdrop.sky, (round(vp.ox + sx), round(vp.oy + sy)))

        # soleil bas sur l'horizon
        sun = self.backdrop.sun
        cx, cy = vp.x(vp.view_w * 0.78) + sx, vp.y(168) + sy
        self.screen.blit(sun, (round(cx - sun.get_width() / 2),
                               round(cy - sun.get_height() / 2)))

        self._parallax(self.backdrop.far, scroll * 0.12, sx, sy)
        self._parallax(self.backdrop.near, scroll * 0.34, sx, sy)

    def _parallax(self, layer: pygame.Surface, offset: float,
                  sx: float, sy: float) -> None:
        w = layer.get_width()
        off = -(self.vp.s(offset) % w)
        y = round(self.vp.oy + sy)
        x = round(self.vp.ox + off + sx)
        self.screen.blit(layer, (x, y))
        if x + w < self.vp.ox + self.vp.view_w * self.vp.scale:
            self.screen.blit(layer, (x + w, y))

    def draw_road(self, scroll: float, shake: tuple[float, float]) -> None:
        vp = self.vp
        road = self.assets.sprite("route")
        w = road.get_width()
        sx, sy = vp.s(shake[0]), vp.s(shake[1])
        y = round(vp.y(C.GROUND_Y) + sy)
        start = round(vp.ox + sx - (vp.s(scroll) % w))
        end = vp.ox + vp.view_w * vp.scale
        x = start
        while x < end:
            self.screen.blit(road, (x, y))
            x += w
        # bordure de trottoir
        pygame.draw.line(self.screen, (232, 232, 240),
                         (vp.ox, y), (end, y), max(1, round(vp.s(3))))
        pygame.draw.line(self.screen, (120, 122, 150),
                         (vp.ox, y + vp.s(4)), (end, y + vp.s(4)),
                         max(1, round(vp.s(1.5))))
        # marquage au sol qui defile
        dash, gap = 70.0, 58.0
        period = dash + gap
        first = -(scroll % period)
        yy = round(vp.y(C.GROUND_Y + 118) + sy)
        th = max(1, round(vp.s(7)))
        dx = first
        while dx < vp.view_w + period:
            pygame.draw.rect(self.screen, (238, 216, 132), pygame.Rect(
                round(vp.x(dx) + sx), yy, max(1, round(vp.s(dash))), th))
            dx += period

    # ------------------------------------------------------------------
    # entites
    # ------------------------------------------------------------------
    def draw_player(self, w: World, shake: tuple[float, float]) -> None:
        vp, p = self.vp, w.player
        sx, sy = vp.s(shake[0]), vp.s(shake[1])
        board = self._rotated("skate", -math.degrees(p.lean))

        bw, bh = self.assets.logical_size("skate")
        hw, hh = self.assets.logical_size("eduardo_tete")

        duck = p.ducking and p.on_ground
        squash = 0.62 if duck else 1.0

        # ombre portee, resserree quand Eduardo est haut
        alt = max(0.0, C.GROUND_Y - p.y)
        t = min(1.0, alt / 220.0)
        shw = vp.s(bw * (1.0 - 0.45 * t))
        sha = int(120 * (1.0 - 0.65 * t))
        if sha > 4:
            sh = pygame.Surface((max(2, round(shw)), max(2, round(vp.s(14)))),
                                pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (12, 14, 40, sha), sh.get_rect())
            self.screen.blit(sh, (round(vp.x(C.PLAYER_X + bw * 0.5) - shw / 2 + sx),
                                  round(vp.y(C.GROUND_Y - 4) + sy)))

        # planche
        brect = board.get_rect()
        brect.center = (round(vp.x(C.PLAYER_X + bw * 0.5) + sx),
                        round(vp.y(p.y - bh * 0.5) + sy))
        self.screen.blit(board, brect)

        # tete : accroupi = tete plus basse et legerement ecrasee
        head_h = hh * squash
        head = self._rotated("eduardo_tete", -math.degrees(p.lean) * 0.5, squash)
        cx = vp.x(C.PLAYER_X + bw * 0.5) + sx + vp.s(math.sin(p.wheel_spin * 0.5) * 1.6)
        cy = (vp.y(p.y - bh * 0.72 - head_h * 0.5) + sy
              + vp.s(abs(math.sin(p.wheel_spin * 0.5)) * 1.4))
        self.screen.blit(head, head.get_rect(center=(round(cx), round(cy))))

    def draw_obstacles(self, w: World, shake: tuple[float, float]) -> None:
        vp = self.vp
        sx, sy = vp.s(shake[0]), vp.s(shake[1])
        for o in w.obstacles:
            if o.x > vp.view_w + 60 or o.x + o.w < -60:
                continue
            sprite = self.assets.sprite(o.kind)
            y = o.y
            # ombre au sol
            t = min(1.0, max(0.0, (C.GROUND_Y - (y + o.h)) / 220.0))
            if o.flying:
                shw = vp.s(o.w * (1.0 - 0.4 * t))
                sh = pygame.Surface((max(2, round(shw)), max(2, round(vp.s(12)))),
                                    pygame.SRCALPHA)
                pygame.draw.ellipse(sh, (12, 14, 40, int(90 * (1 - t))), sh.get_rect())
                self.screen.blit(sh, (round(vp.x(o.x + o.w * 0.5) - shw / 2 + sx),
                                      round(vp.y(C.GROUND_Y - 4) + sy)))
            else:
                shw = vp.s(o.w * 0.9)
                sh = pygame.Surface((max(2, round(shw)), max(2, round(vp.s(12)))),
                                    pygame.SRCALPHA)
                pygame.draw.ellipse(sh, (12, 14, 40, 110), sh.get_rect())
                self.screen.blit(sh, (round(vp.x(o.x + o.w * 0.5) - shw / 2 + sx),
                                      round(vp.y(C.GROUND_Y - 5) + sy)))
            self.screen.blit(sprite, (round(vp.x(o.x) + sx), round(vp.y(y) + sy)))

    def draw_particles(self, w: World, shake: tuple[float, float]) -> None:
        vp = self.vp
        sx, sy = vp.s(shake[0]), vp.s(shake[1])
        for p in w.particles:
            a = max(0.0, min(1.0, p.life / p.max_life))
            size = max(1, round(vp.s(p.size * (0.4 + 0.6 * a))))
            surf = self._dot(p.color, size, int(235 * a))
            self.screen.blit(surf, (round(vp.x(p.x) + sx - size / 2),
                                    round(vp.y(p.y) + sy - size / 2)))

    # ------------------------------------------------------------------
    # HUD et ecrans
    # ------------------------------------------------------------------
    def draw_hud(self, w: World, best: int, muted: bool, fps: float,
                 show_fps: bool) -> None:
        vp = self.vp
        self.text(f"SCORE {w.score}", 30, 22, 12)
        self.text(f"RECORD {best}", 24, vp.view_w - 22, 16, C.CREAM, right=True)

        kmh = w.speed * 0.075
        self.text(f"{kmh:4.0f} km/h", 20, 24, 48, (198, 206, 255))
        if muted:
            self.text("SOURDINE (M)", 18, 24, 74, (170, 176, 220))
        if show_fps:
            self.text(f"{fps:3.0f} fps", 18, vp.view_w - 22, 48,
                      (150, 158, 210), right=True)
        if w.near_miss > 0.0:
            a = int(255 * min(1.0, w.near_miss / 0.7))
            self.text("CHAUD !", 34, vp.view_w * 0.5, 118, C.AMBER,
                      center=True, alpha=a)

    def draw_menu(self, best: int, blink: float) -> None:
        vp = self.vp
        self.dim(120)
        cx = vp.view_w * 0.5
        self.text(C.TITLE, 150, cx, 176, C.WHITE, center=True)
        self.text(C.SUBTITLE, 40, cx, 262, C.AMBER, center=True)
        self.text("ESPACE / CLIC : sauter     BAS : s'accroupir", 22, cx, 320,
                  C.CREAM, center=True)
        self.text("P : pause     M : sourdine     ECHAP : quitter", 22, cx, 350,
                  (196, 202, 246), center=True)
        if best:
            self.text(f"Record a battre : {best}", 26, cx, 400, C.WHITE, center=True)
        if blink % 1.0 < 0.62:
            self.text("Appuyez sur ESPACE pour lancer Eduardo", 30, cx, 486,
                      C.WHITE, center=True)

    def draw_pause(self) -> None:
        vp = self.vp
        self.dim(170)
        self.text("PAUSE", 120, vp.view_w * 0.5, 250, C.WHITE, center=True)
        self.text("P ou ESPACE pour reprendre", 26, vp.view_w * 0.5, 340,
                  C.CREAM, center=True)

    def draw_gameover(self, w: World, best: int, record: bool, blink: float,
                      ready: bool) -> None:
        vp = self.vp
        self.dim(150)
        cx = vp.view_w * 0.5
        casse = self.assets.sprite_h("eduardo_casse", 232)
        rect = casse.get_rect()
        rect.midtop = (round(vp.x(cx)), round(vp.y(128)))
        frame = rect.inflate(round(vp.s(10)), round(vp.s(10)))
        pygame.draw.rect(self.screen, (255, 255, 255), frame,
                         border_radius=round(vp.s(6)))
        self.screen.blit(casse, rect)

        self.text("CRAC !", 126, cx, 62, C.RED, center=True)
        self.text(f"Score : {w.score}", 40, cx, 396, C.WHITE, center=True)
        if record:
            self.text("NOUVEAU RECORD !", 34, cx, 442, C.AMBER, center=True)
        else:
            self.text(f"Record : {best}", 26, cx, 444, C.CREAM, center=True)
        if ready and blink % 1.0 < 0.62:
            self.text("ESPACE : rejouer      ECHAP : menu", 26, cx, 500,
                      C.WHITE, center=True)
