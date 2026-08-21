"""Boucle principale et enchainement des ecrans."""

from __future__ import annotations

import random
import sys

import pygame

from . import config as C
from .assets import Assets
from .audio import Audio
from .render import Renderer
from .scores import Scores
from .world import World

MENU, PLAY, PAUSE, DEAD = "menu", "play", "pause", "dead"

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w, pygame.K_z,
             pygame.K_RETURN, pygame.K_KP_ENTER)
DUCK_KEYS = (pygame.K_DOWN, pygame.K_s, pygame.K_LCTRL, pygame.K_RCTRL)


class Game:
    def __init__(self, windowed_size: tuple[int, int] = (1280, 700),
                 fullscreen: bool = False) -> None:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        pygame.display.set_caption(f"{C.TITLE} {C.SUBTITLE}")
        self.windowed_size = windowed_size
        self.fullscreen = fullscreen
        self.screen = self._make_screen()

        self.assets = Assets()
        self.audio = Audio(self.assets)
        self.scores = Scores()
        self.renderer = Renderer(self.screen, self.assets)
        self.renderer.resize(self.screen.get_size())
        self.assets.preload()

        self.clock = pygame.time.Clock()
        self.state = MENU
        self.blink = 0.0
        self.show_fps = False
        self.dead_timer = 0.0
        self.record = False
        self.world = self._new_world()
        self.running = True

    # ------------------------------------------------------------------
    def _make_screen(self) -> pygame.Surface:
        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
            size = (0, 0)
        else:
            flags |= pygame.RESIZABLE
            size = self.windowed_size
        try:
            return pygame.display.set_mode(size, flags, vsync=1)
        except pygame.error:
            return pygame.display.set_mode(size, flags)

    def _toggle_fullscreen(self) -> None:
        if not self.fullscreen:
            self.windowed_size = self.screen.get_size()
        self.fullscreen = not self.fullscreen
        self.screen = self._make_screen()
        self.renderer.screen = self.screen
        self.renderer.resize(self.screen.get_size())

    def _new_world(self) -> World:
        return World(view_w=self.renderer.vp.view_w,
                     rng=random.Random())

    def start_run(self) -> None:
        self.world = self._new_world()
        self.state = PLAY
        self.record = False
        self.dead_timer = 0.0
        self.audio.music("hymne", loop=True)

    # ------------------------------------------------------------------
    # entrees
    # ------------------------------------------------------------------
    def _jump_pressed(self) -> None:
        if self.state == MENU:
            self.start_run()
        elif self.state == PLAY:
            self.world.press_jump()
        elif self.state == PAUSE:
            self.state = PLAY
        elif self.state == DEAD and self.dead_timer > 0.85:
            self.start_run()

    def _jump_released(self) -> None:
        if self.state == PLAY:
            self.world.release_jump()

    def _escape(self) -> None:
        if self.state in (PLAY, PAUSE):
            self.state = MENU
            self.audio.music(None)
        elif self.state == DEAD:
            self.state = MENU
            self.audio.music(None)
        else:
            self.running = False

    def handle_events(self) -> None:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False

            elif e.type == pygame.VIDEORESIZE and not self.fullscreen:
                self.renderer.resize((e.w, e.h))
                self.world.view_w = self.renderer.vp.view_w

            elif e.type == pygame.KEYDOWN:
                if e.key in JUMP_KEYS:
                    self._jump_pressed()
                elif e.key in DUCK_KEYS and self.state == PLAY:
                    self.world.set_duck(True)
                elif e.key == pygame.K_p and self.state in (PLAY, PAUSE):
                    self.state = PAUSE if self.state == PLAY else PLAY
                elif e.key == pygame.K_m:
                    self.audio.toggle_mute()
                elif e.key == pygame.K_F3:
                    self.show_fps = not self.show_fps
                elif e.key == pygame.K_F11 or (
                        e.key == pygame.K_f and (e.mod & pygame.KMOD_ALT)):
                    self._toggle_fullscreen()
                elif e.key == pygame.K_ESCAPE:
                    self._escape()

            elif e.type == pygame.KEYUP:
                if e.key in JUMP_KEYS:
                    self._jump_released()
                elif e.key in DUCK_KEYS and self.state == PLAY:
                    self.world.set_duck(False)

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # moitie basse de l'ecran = s'accroupir (pense pour le tactile)
                if self.state == PLAY and e.pos[1] > self.screen.get_height() * 0.68:
                    self.world.set_duck(True)
                else:
                    self._jump_pressed()

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self._jump_released()
                if self.state == PLAY:
                    self.world.set_duck(False)

    # ------------------------------------------------------------------
    def _consume_world_events(self) -> None:
        for ev in self.world.drain_events():
            if ev == "jump":
                self.audio.sfx("jump")
            elif ev == "land":
                self.audio.sfx("land", 0.7)
            elif ev == "score":
                self.audio.sfx("score", 0.5)
            elif ev == "crash":
                self.audio.fade_out(120)
                self.audio.music("mamma_mia", loop=False)
                self.record = self.scores.submit(self.world.score)
                self.state = DEAD
                self.dead_timer = 0.0

    def update(self, dt: float) -> None:
        self.blink += dt
        if self.state == PLAY:
            self.world.update(dt)
            self._consume_world_events()
        elif self.state == DEAD:
            self.dead_timer += dt
            self.world.update(dt)     # laisse retomber les debris
            self.world.drain_events()

    def draw(self) -> None:
        w = self.world
        shake = w.shake_offset()
        self.renderer.draw_background(w.scroll, shake)
        self.renderer.draw_road(w.scroll, shake)
        self.renderer.draw_obstacles(w, shake)
        if not (self.state == DEAD and self.dead_timer > 0.25):
            self.renderer.draw_player(w, shake)
        self.renderer.draw_particles(w, shake)

        if self.state == MENU:
            self.renderer.draw_menu(self.scores.best, self.blink)
        else:
            self.renderer.draw_hud(w, self.scores.best, self.audio.muted,
                                   self.clock.get_fps(), self.show_fps)
            if self.state == PAUSE:
                self.renderer.draw_pause()
            elif self.state == DEAD:
                self.renderer.draw_gameover(w, self.scores.best, self.record,
                                            self.blink, self.dead_timer > 0.85)
        pygame.display.flip()

    def run(self) -> int:
        try:
            while self.running:
                dt = min(C.MAX_DT, self.clock.tick(C.TARGET_FPS) / 1000.0)
                self.handle_events()
                self.update(dt)
                self.draw()
        finally:
            # Meme en cas de plantage : on ne laisse pas l'Hymne tourner.
            self.audio.shutdown()
            pygame.quit()
        return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    return Game(fullscreen="--fullscreen" in argv or "-f" in argv).run()
