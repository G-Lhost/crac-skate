"""Simulation du jeu : etat, physique, obstacles, collisions.

Ce module ne connait ni pygame.display ni la moindre surface : il ne fait
qu'avancer un etat en fonction d'un pas de temps et d'entrees. C'est ce qui
permet de le tester en tete-a-tete et d'en garder un portage JavaScript
strictement equivalent pour la version mobile.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from . import config as C

# Duree d'un saut complet, utilisee pour verifier qu'un obstacle reste
# franchissable avant de le faire apparaitre.
AIRTIME = 2.0 * abs(C.JUMP_VELOCITY) / C.GRAVITY
JUMP_HEIGHT = C.JUMP_VELOCITY ** 2 / (2.0 * C.GRAVITY)

# nom du sprite -> (largeur, hauteur, ratio de marge de hitbox, peut voler)
OBSTACLES: dict[str, tuple[float, float, float, bool]] = {
    "frites":    (80.0,  80.0,  0.14, False),
    "alteres":   (75.6,  62.0,  0.12, False),
    "amaretto":  (46.0,  96.0,  0.16, False),
    "bequilles": (38.0, 104.0,  0.20, False),
    "bale":      (59.6,  88.0,  0.16, False),
    "ezgy":      (89.0,  88.0,  0.16, False),
    "drapeau":   (96.0,  64.0,  0.10, True),
}
KINDS = list(OBSTACLES)


@dataclass(slots=True)
class Obstacle:
    kind: str
    x: float
    y: float                 # sommet du sprite
    w: float
    h: float
    inset: float
    flying: bool = False
    base_y: float = 0.0      # altitude de reference des obstacles volants
    phase: float = 0.0       # pour l'ondulation du drapeau
    cluster: int = 0         # les obstacles d'un meme groupe comptent 1 point
    passed: bool = False

    @property
    def hit_left(self) -> float:
        return self.x + self.w * self.inset

    @property
    def hit_right(self) -> float:
        return self.x + self.w * (1.0 - self.inset)

    @property
    def hit_top(self) -> float:
        return self.y + self.h * self.inset * 0.5

    @property
    def hit_bottom(self) -> float:
        return self.y + self.h


@dataclass(slots=True)
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: tuple[int, int, int]
    gravity: float = 900.0


@dataclass(slots=True)
class Player:
    y: float = 0.0           # position du sol de la planche
    vy: float = 0.0
    on_ground: bool = True
    ducking: bool = False
    coyote: float = 0.0
    buffer: float = 0.0
    jump_held: bool = False
    lean: float = 0.0        # inclinaison visuelle (rad)
    wheel_spin: float = 0.0

    @property
    def airborne(self) -> bool:
        return not self.on_ground

    @property
    def height(self) -> float:
        """Hauteur de la hitbox (reduite quand Eduardo s'accroupit)."""
        full = C.BOARD_H + C.HEAD_H - 24
        return C.DUCK_HEIGHT if self.ducking and self.on_ground else full

    def hitbox(self) -> tuple[float, float, float, float]:
        left = C.PLAYER_X + C.HITBOX_INSET_X
        right = C.PLAYER_X + C.BOARD_W - C.HITBOX_INSET_X
        bottom = self.y
        top = bottom - self.height + C.HITBOX_INSET_Y
        return left, top, right, bottom


@dataclass
class World:
    """Etat complet d'une partie."""

    view_w: float = C.VIEW_W_DEFAULT
    rng: random.Random = field(default_factory=random.Random)

    player: Player = field(default_factory=Player)
    obstacles: list[Obstacle] = field(default_factory=list)
    particles: list[Particle] = field(default_factory=list)

    speed: float = C.SPEED_START
    distance: float = 0.0
    scroll: float = 0.0
    elapsed: float = 0.0
    score: int = 0
    cluster_seq: int = 0

    spawn_timer: float = 1.45
    dust_timer: float = 0.0
    dead: bool = False
    shake: float = 0.0
    near_miss: float = 0.0   # duree restante du flash "Chaud !"

    # evenements consommes par la couche presentation
    events: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.player.y = C.GROUND_Y

    # ------------------------------------------------------------------
    # entrees
    # ------------------------------------------------------------------
    def press_jump(self) -> None:
        self.player.buffer = C.JUMP_BUFFER
        self.player.jump_held = True

    def release_jump(self) -> None:
        self.player.jump_held = False
        if self.player.vy < 0.0:
            self.player.vy *= C.JUMP_CUT

    def set_duck(self, ducking: bool) -> None:
        self.player.ducking = ducking

    # ------------------------------------------------------------------
    # boucle de simulation
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.dead:
            self._update_particles(dt)
            self.shake = max(0.0, self.shake - dt * 60.0)
            return

        self.elapsed += dt
        self.speed = min(
            C.SPEED_MAX,
            C.SPEED_START + self.score * C.SPEED_GAIN + self.elapsed * C.SPEED_RAMP,
        )
        step = self.speed * dt
        self.distance += step
        self.scroll += step
        self.near_miss = max(0.0, self.near_miss - dt)
        self.shake = max(0.0, self.shake - dt * 60.0)

        self._update_player(dt)
        self._update_obstacles(dt, step)
        self._spawn(dt)
        self._update_particles(dt)
        self._check_collisions()

    # -- heros ----------------------------------------------------------
    def _update_player(self, dt: float) -> None:
        p = self.player

        p.coyote = p.coyote - dt if not p.on_ground else C.COYOTE_TIME
        p.buffer = max(0.0, p.buffer - dt)

        if p.buffer > 0.0 and (p.on_ground or p.coyote > 0.0):
            p.vy = C.JUMP_VELOCITY
            p.on_ground = False
            p.coyote = 0.0
            p.buffer = 0.0
            self.events.append("jump")
            self._burst(C.PLAYER_X + C.BOARD_W * 0.5, C.GROUND_Y, 10,
                        (206, 206, 214), spread=190.0, up=-120.0)

        if not p.on_ground:
            g = C.GRAVITY * (C.FAST_FALL if (p.ducking and p.vy > 0.0) else 1.0)
            p.vy = min(C.MAX_FALL, p.vy + g * dt)
            p.y += p.vy * dt
            if p.y >= C.GROUND_Y:
                p.y = C.GROUND_Y
                impact = p.vy
                p.vy = 0.0
                p.on_ground = True
                self.events.append("land")
                self._burst(C.PLAYER_X + C.BOARD_W * 0.5, C.GROUND_Y,
                            6 + int(impact / 260.0), (218, 218, 226),
                            spread=230.0, up=-90.0)

        # inclinaison : nez en l'air a la montee, plongee a la descente
        target = 0.0 if p.on_ground else max(-0.30, min(0.34, p.vy / 2600.0))
        p.lean += (target - p.lean) * min(1.0, dt * 12.0)
        p.wheel_spin += self.speed * dt / 22.0

        # poussiere sous les roues
        self.dust_timer -= dt
        if p.on_ground and self.dust_timer <= 0.0:
            self.dust_timer = 0.055
            self._burst(C.PLAYER_X + 18.0, C.GROUND_Y, 1, (198, 200, 210),
                        spread=40.0, up=-40.0, size=3.0, life=0.42)

    # -- obstacles ------------------------------------------------------
    def _update_obstacles(self, dt: float, step: float) -> None:
        px_left, _, px_right, _ = self.player.hitbox()
        alive: list[Obstacle] = []
        scored: set[int] = set()
        for o in self.obstacles:
            o.x -= step
            if o.flying:
                # l'ondulation bouge aussi la hitbox : ce qu'on voit est ce
                # qui touche.
                o.phase += dt * 6.0
                o.y = o.base_y + math.sin(o.phase) * 9.0
            if not o.passed and o.hit_right < px_left:
                o.passed = True
                if o.cluster not in scored:
                    scored.add(o.cluster)
            if o.x + o.w > -40.0:
                alive.append(o)
        self.obstacles = alive
        if scored:
            self.score += len(scored)
            self.events.append("score")

    def _spawn(self, dt: float) -> None:
        self.spawn_timer -= dt
        if self.spawn_timer > 0.0:
            return

        gap = self.rng.uniform(C.GAP_MIN_S, C.GAP_MAX_S)
        gap = max(C.GAP_FLOOR_S, gap - self.score * C.GAP_TIGHTEN)
        self.spawn_timer = gap

        self.cluster_seq += 1
        x = self.view_w + 40.0

        # un drapeau volant : il faut s'accroupir (ou sauter tres juste)
        if (self.score >= C.FLYER_CHANCE_FROM
                and self.rng.random() < 0.22):
            w, h, inset, _ = OBSTACLES["drapeau"]
            base = C.GROUND_Y - 96.0 - h
            self.obstacles.append(Obstacle(
                "drapeau", x, base, w, h, inset, flying=True, base_y=base,
                cluster=self.cluster_seq, phase=self.rng.random() * 6.28))
            return

        kind = self.rng.choice(KINDS)
        w, h, inset, _ = OBSTACLES[kind]
        self.obstacles.append(Obstacle(kind, x, C.GROUND_Y - h, w, h, inset,
                                       cluster=self.cluster_seq))

        # paire collee : seulement si un saut suffit encore a la franchir
        if self.score >= C.DOUBLE_CHANCE_FROM and self.rng.random() < 0.28:
            k2 = self.rng.choice(KINDS)
            w2, h2, i2, _ = OBSTACLES[k2]
            spacing = self.rng.uniform(14.0, 46.0)
            span = w + spacing + w2
            reach = AIRTIME * self.speed * 0.86
            if span + (C.BOARD_W - 2 * C.HITBOX_INSET_X) < reach:
                self.obstacles.append(Obstacle(
                    k2, x + w + spacing, C.GROUND_Y - h2, w2, h2, i2,
                    cluster=self.cluster_seq))
                self.spawn_timer += span / max(1.0, self.speed)

    # -- particules ------------------------------------------------------
    def _burst(self, x: float, y: float, n: int, color: tuple[int, int, int],
               spread: float = 200.0, up: float = -150.0, size: float = 4.0,
               life: float = 0.6, gravity: float = 900.0) -> None:
        r = self.rng
        for _ in range(max(0, n)):
            lf = life * r.uniform(0.6, 1.25)
            self.particles.append(Particle(
                x + r.uniform(-8.0, 8.0), y + r.uniform(-4.0, 2.0),
                r.uniform(-spread, spread * 0.25) - self.speed * 0.12,
                up * r.uniform(0.4, 1.3),
                lf, lf, size * r.uniform(0.7, 1.5), color, gravity))

    def _update_particles(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0.0:
                continue
            p.vy += p.gravity * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            if p.y > C.GROUND_Y + 6.0:
                p.y = C.GROUND_Y + 6.0
                p.vy *= -0.32
                p.vx *= 0.7
            alive.append(p)
        # borne de securite : jamais plus de 260 particules a l'ecran
        self.particles = alive[-260:]

    # -- collisions ------------------------------------------------------
    def _check_collisions(self) -> None:
        left, top, right, bottom = self.player.hitbox()
        for o in self.obstacles:
            if o.hit_right < left or o.hit_left > right:
                continue
            if o.hit_bottom <= top or o.hit_top >= bottom:
                # passe tout pres : petit frisson, pas de points
                margin = min(abs(o.hit_bottom - top), abs(o.hit_top - bottom))
                if margin < 26.0:
                    self.near_miss = 0.7
                continue
            self.kill()
            return

    def kill(self) -> None:
        if self.dead:
            return
        self.dead = True
        self.shake = C.SHAKE_ON_CRASH
        self.events.append("crash")
        cx = C.PLAYER_X + C.BOARD_W * 0.5
        cy = self.player.y - 60.0
        self._burst(cx, cy, 46, (255, 214, 120), spread=520.0, up=-420.0,
                    size=6.0, life=1.1, gravity=1250.0)
        self._burst(cx, cy, 22, (231, 76, 60), spread=430.0, up=-330.0,
                    size=5.0, life=0.9, gravity=1250.0)

    # -- utilitaires -----------------------------------------------------
    def drain_events(self) -> list[str]:
        ev, self.events = self.events, []
        return ev

    def shake_offset(self) -> tuple[float, float]:
        if self.shake <= 0.0:
            return 0.0, 0.0
        a = self.rng.uniform(0.0, math.tau)
        return math.cos(a) * self.shake, math.sin(a) * self.shake * 0.6
