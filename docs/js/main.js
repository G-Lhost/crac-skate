// Boucle principale de la version web / mobile.

import * as C from './config.js';
import { World } from './world.js';
import { Assets } from './assets.js';
import { Renderer } from './render.js';
import { Audio2 } from './audio.js';
import { Input } from './input.js';

const MENU = 'menu', PLAY = 'play', PAUSE = 'pause', DEAD = 'dead';
const KEY_BEST = 'crac.best';

class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.assets = new Assets();
    this.renderer = new Renderer(canvas, this.assets);
    this.audio = new Audio2();
    this.state = MENU;
    this.blink = 0;
    this.deadTimer = 0;
    this.record = false;
    this.best = Math.max(parseInt(localStorage.getItem(KEY_BEST) || '0', 10) || 0,
                         C.LEGACY_BEST);
    this.world = new World(C.VIEW_W_DEFAULT);
    this.last = 0;
    this.touch = false;
  }

  async boot(onProgress) {
    await this.assets.load(onProgress);
    this.resize();
    window.addEventListener('resize', () => this.resize());
    window.addEventListener('orientationchange', () => setTimeout(() => this.resize(), 250));
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', () => this.resize());
    }
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && this.state === PLAY) this.setState(PAUSE);
    });

    this.input = new Input(this.canvas, {
      jumpDown: () => this.jumpDown(),
      jumpUp: () => this.jumpUp(),
      duck: (v) => this.setDuck(v),
      pause: () => this.togglePause(),
      mute: () => this.audio.toggleMute(),
      back: () => this.back(),
      fullscreen: () => this.toggleFullscreen(),
    });
    this.touch = this.input.hasTouch;
    requestAnimationFrame((t) => this.frame(t));
  }

  resize() {
    const dpr = Math.min(3, window.devicePixelRatio || 1);
    const w = this.canvas.clientWidth || window.innerWidth;
    const h = this.canvas.clientHeight || window.innerHeight;
    this._lastSize = `${w}x${h}x${dpr}`;
    this.renderer.resize(w, h, dpr);
    this.world.viewW = this.renderer.vp.viewW;
    // En portrait on affiche l'invitation a tourner l'appareil : la partie se
    // met en pause pour qu'Eduardo ne s'ecrase pas pendant la rotation.
    const portrait = h > w;
    document.body.classList.toggle('portrait', portrait);
    if (portrait && this.state === PLAY) this.state = PAUSE;
  }

  // -- etats -----------------------------------------------------------
  setState(s) { this.state = s; }

  startRun() {
    this.world = new World(this.renderer.vp.viewW);
    this.state = PLAY;
    this.record = false;
    this.deadTimer = 0;
    this.audio.music('hymne');
  }

  jumpDown() {
    this.audio.unlock();
    if (this.state === MENU) this.startRun();
    else if (this.state === PLAY) this.world.pressJump();
    else if (this.state === PAUSE) this.state = PLAY;
    else if (this.state === DEAD && this.deadTimer > 0.85) this.startRun();
  }
  jumpUp() { if (this.state === PLAY) this.world.releaseJump(); }
  setDuck(v) {
    this.audio.unlock();
    if (this.state === PLAY) this.world.setDuck(v);
    else if (v) this.jumpDown();          // un appui en bas depuis un menu vaut "valider"
  }
  togglePause() {
    if (this.state === PLAY) this.state = PAUSE;
    else if (this.state === PAUSE) this.state = PLAY;
  }
  back() {
    if (this.state === PLAY || this.state === PAUSE || this.state === DEAD) {
      this.state = MENU;
      this.audio.music(null);
    }
  }
  toggleFullscreen() {
    const el = document.documentElement;
    if (!document.fullscreenElement) el.requestFullscreen?.().catch(() => {});
    else document.exitFullscreen?.();
  }

  consumeEvents() {
    for (const ev of this.world.drainEvents()) {
      if (ev === 'jump') this.audio.sfx('jump');
      else if (ev === 'land') this.audio.sfx('land');
      else if (ev === 'score') this.audio.sfx('score');
      else if (ev === 'crash') {
        this.audio.music('mamma_mia');
        this.record = this.world.score > this.best;
        if (this.record) {
          this.best = this.world.score;
          localStorage.setItem(KEY_BEST, String(this.best));
        }
        this.state = DEAD;
        this.deadTimer = 0;
      }
    }
  }

  // -- boucle ----------------------------------------------------------
  frame(now) {
    requestAnimationFrame((t) => this.frame(t));
    const dt = Math.min(C.MAX_DT, this.last ? (now - this.last) / 1000 : 0);
    this.last = now;
    this.blink += dt;

    // Filet de securite : sur iOS en mode application, l'evenement resize
    // arrive parfois en retard (voire pas du tout) apres une rotation. On
    // compare donc les dimensions a chaque image -- deux lectures de
    // proprietes, aucun cout mesurable.
    const dpr = Math.min(3, window.devicePixelRatio || 1);
    if (`${this.canvas.clientWidth}x${this.canvas.clientHeight}x${dpr}` !== this._lastSize) {
      this.resize();
    }

    if (this.state === PLAY) {
      this.world.update(dt);
      this.consumeEvents();
    } else if (this.state === DEAD) {
      this.deadTimer += dt;
      this.world.update(dt);
      this.world.drainEvents();
    }

    const w = this.world;
    const shake = w.shakeOffset();
    const r = this.renderer;
    r.drawBackground(w.scroll, shake);
    r.drawRoad(w.scroll, shake);
    r.drawObstacles(w, shake);
    if (!(this.state === DEAD && this.deadTimer > 0.25)) r.drawPlayer(w, shake);
    r.drawParticles(w, shake);

    if (this.state === MENU) {
      r.drawMenu(this.best, this.blink, this.touch);
    } else {
      r.drawHud(w, this.best, this.audio.muted);
      if (this.state === PAUSE) r.drawPause(this.touch);
      else if (this.state === DEAD) {
        r.drawGameOver(w, this.best, this.record, this.blink,
                       this.deadTimer > 0.85, this.touch);
      }
    }
  }
}

// --- demarrage ---------------------------------------------------------
const canvas = document.getElementById('game');
const loader = document.getElementById('loader');
const bar = document.getElementById('bar');
const game = new Game(canvas);
// Point d'entree pour la console du navigateur (mise au point, captures).
window.CRAC = game;

game.boot((p) => { bar.style.width = `${Math.round(p * 100)}%`; }).then(() => {
  loader.classList.add('gone');
  setTimeout(() => loader.remove(), 400);
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}
