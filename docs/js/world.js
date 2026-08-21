// Simulation du jeu : portage 1:1 de python/crac/world.py.
// Aucune dependance au DOM ni au canvas : le meme fichier pourrait tourner
// dans un worker ou en Node pour rejouer une partie.

import * as C from './config.js';

export const AIRTIME = (2 * Math.abs(C.JUMP_VELOCITY)) / C.GRAVITY;
export const JUMP_HEIGHT = (C.JUMP_VELOCITY * C.JUMP_VELOCITY) / (2 * C.GRAVITY);

// nom du sprite -> [largeur, hauteur, marge de hitbox, peut voler]
export const OBSTACLES = {
  frites:    [80.0,  80.0, 0.14, false],
  alteres:   [75.6,  62.0, 0.12, false],
  amaretto:  [46.0,  96.0, 0.16, false],
  bequilles: [38.0, 104.0, 0.20, false],
  bale:      [59.6,  88.0, 0.16, false],
  ezgy:      [89.0,  88.0, 0.16, false],
  drapeau:   [96.0,  64.0, 0.10, true],
};
export const KINDS = Object.keys(OBSTACLES);

class Obstacle {
  constructor(kind, x, y, w, h, inset, opts = {}) {
    this.kind = kind;
    this.x = x; this.y = y; this.w = w; this.h = h; this.inset = inset;
    this.flying = opts.flying || false;
    this.baseY = opts.baseY !== undefined ? opts.baseY : y;
    this.phase = opts.phase || 0;
    this.cluster = opts.cluster || 0;
    this.passed = false;
  }
  get hitLeft()   { return this.x + this.w * this.inset; }
  get hitRight()  { return this.x + this.w * (1 - this.inset); }
  get hitTop()    { return this.y + this.h * this.inset * 0.5; }
  get hitBottom() { return this.y + this.h; }
}

class Player {
  constructor() {
    this.y = C.GROUND_Y;
    this.vy = 0;
    this.onGround = true;
    this.ducking = false;
    this.coyote = 0;
    this.buffer = 0;
    this.jumpHeld = false;
    this.lean = 0;
    this.wheelSpin = 0;
  }
  get height() {
    const full = C.BOARD_H + C.HEAD_H - 24;
    return (this.ducking && this.onGround) ? C.DUCK_HEIGHT : full;
  }
  hitbox() {
    return {
      left: C.PLAYER_X + C.HITBOX_INSET_X,
      right: C.PLAYER_X + C.BOARD_W - C.HITBOX_INSET_X,
      bottom: this.y,
      top: this.y - this.height + C.HITBOX_INSET_Y,
    };
  }
}

export class World {
  constructor(viewW = C.VIEW_W_DEFAULT) {
    this.viewW = viewW;
    this.player = new Player();
    this.obstacles = [];
    this.particles = [];
    this.speed = C.SPEED_START;
    this.distance = 0;
    this.scroll = 0;
    this.elapsed = 0;
    this.score = 0;
    this.clusterSeq = 0;
    this.spawnTimer = 1.45;
    this.dustTimer = 0;
    this.dead = false;
    this.shake = 0;
    this.nearMiss = 0;
    this.events = [];
  }

  // -- entrees ---------------------------------------------------------
  pressJump() {
    this.player.buffer = C.JUMP_BUFFER;
    this.player.jumpHeld = true;
  }
  releaseJump() {
    this.player.jumpHeld = false;
    if (this.player.vy < 0) this.player.vy *= C.JUMP_CUT;
  }
  setDuck(v) { this.player.ducking = v; }

  // -- boucle ----------------------------------------------------------
  update(dt) {
    if (this.dead) {
      this._updateParticles(dt);
      this.shake = Math.max(0, this.shake - dt * 60);
      return;
    }
    this.elapsed += dt;
    this.speed = Math.min(
      C.SPEED_MAX,
      C.SPEED_START + this.score * C.SPEED_GAIN + this.elapsed * C.SPEED_RAMP);
    const step = this.speed * dt;
    this.distance += step;
    this.scroll += step;
    this.nearMiss = Math.max(0, this.nearMiss - dt);
    this.shake = Math.max(0, this.shake - dt * 60);

    this._updatePlayer(dt);
    this._updateObstacles(dt, step);
    this._spawn(dt);
    this._updateParticles(dt);
    this._checkCollisions();
  }

  _updatePlayer(dt) {
    const p = this.player;
    p.coyote = p.onGround ? C.COYOTE_TIME : p.coyote - dt;
    p.buffer = Math.max(0, p.buffer - dt);

    if (p.buffer > 0 && (p.onGround || p.coyote > 0)) {
      p.vy = C.JUMP_VELOCITY;
      p.onGround = false;
      p.coyote = 0;
      p.buffer = 0;
      this.events.push('jump');
      this._burst(C.PLAYER_X + C.BOARD_W * 0.5, C.GROUND_Y, 10,
                  [206, 206, 214], { spread: 190, up: -120 });
    }

    if (!p.onGround) {
      const g = C.GRAVITY * ((p.ducking && p.vy > 0) ? C.FAST_FALL : 1);
      p.vy = Math.min(C.MAX_FALL, p.vy + g * dt);
      p.y += p.vy * dt;
      if (p.y >= C.GROUND_Y) {
        const impact = p.vy;
        p.y = C.GROUND_Y;
        p.vy = 0;
        p.onGround = true;
        this.events.push('land');
        this._burst(C.PLAYER_X + C.BOARD_W * 0.5, C.GROUND_Y,
                    6 + Math.floor(impact / 260), [218, 218, 226],
                    { spread: 230, up: -90 });
      }
    }

    const target = p.onGround ? 0 : Math.max(-0.30, Math.min(0.34, p.vy / 2600));
    p.lean += (target - p.lean) * Math.min(1, dt * 12);
    p.wheelSpin += (this.speed * dt) / 22;

    this.dustTimer -= dt;
    if (p.onGround && this.dustTimer <= 0) {
      this.dustTimer = 0.055;
      this._burst(C.PLAYER_X + 18, C.GROUND_Y, 1, [198, 200, 210],
                  { spread: 40, up: -40, size: 3, life: 0.42 });
    }
  }

  _updateObstacles(dt, step) {
    const hb = this.player.hitbox();
    const alive = [];
    const scored = new Set();
    for (const o of this.obstacles) {
      o.x -= step;
      if (o.flying) {
        o.phase += dt * 6;
        o.y = o.baseY + Math.sin(o.phase) * 9;
      }
      if (!o.passed && o.hitRight < hb.left) {
        o.passed = true;
        scored.add(o.cluster);
      }
      if (o.x + o.w > -40) alive.push(o);
    }
    this.obstacles = alive;
    if (scored.size) {
      this.score += scored.size;
      this.events.push('score');
    }
  }

  _spawn(dt) {
    this.spawnTimer -= dt;
    if (this.spawnTimer > 0) return;

    let gap = C.GAP_MIN_S + Math.random() * (C.GAP_MAX_S - C.GAP_MIN_S);
    gap = Math.max(C.GAP_FLOOR_S, gap - this.score * C.GAP_TIGHTEN);
    this.spawnTimer = gap;

    this.clusterSeq += 1;
    const x = this.viewW + 40;

    if (this.score >= C.FLYER_CHANCE_FROM && Math.random() < 0.22) {
      const [w, h, inset] = OBSTACLES.drapeau;
      const base = C.GROUND_Y - 96 - h;
      this.obstacles.push(new Obstacle('drapeau', x, base, w, h, inset, {
        flying: true, baseY: base, cluster: this.clusterSeq,
        phase: Math.random() * 6.28,
      }));
      return;
    }

    const kind = KINDS[(Math.random() * KINDS.length) | 0];
    const [w, h, inset] = OBSTACLES[kind];
    this.obstacles.push(new Obstacle(kind, x, C.GROUND_Y - h, w, h, inset,
                                     { cluster: this.clusterSeq }));

    if (this.score >= C.DOUBLE_CHANCE_FROM && Math.random() < 0.28) {
      const k2 = KINDS[(Math.random() * KINDS.length) | 0];
      const [w2, h2, i2] = OBSTACLES[k2];
      const spacing = 14 + Math.random() * 32;
      const span = w + spacing + w2;
      const reach = AIRTIME * this.speed * 0.86;
      if (span + (C.BOARD_W - 2 * C.HITBOX_INSET_X) < reach) {
        this.obstacles.push(new Obstacle(k2, x + w + spacing,
          C.GROUND_Y - h2, w2, h2, i2, { cluster: this.clusterSeq }));
        this.spawnTimer += span / Math.max(1, this.speed);
      }
    }
  }

  _burst(x, y, n, color, o = {}) {
    const spread = o.spread ?? 200, up = o.up ?? -150;
    const size = o.size ?? 4, life = o.life ?? 0.6, gravity = o.gravity ?? 900;
    for (let i = 0; i < Math.max(0, n); i++) {
      const lf = life * (0.6 + Math.random() * 0.65);
      this.particles.push({
        x: x + (Math.random() * 16 - 8),
        y: y + (Math.random() * 6 - 4),
        vx: (Math.random() * (spread * 1.25) - spread) - this.speed * 0.12,
        vy: up * (0.4 + Math.random() * 0.9),
        life: lf, maxLife: lf,
        size: size * (0.7 + Math.random() * 0.8),
        color, gravity,
      });
    }
  }

  _updateParticles(dt) {
    const alive = [];
    for (const p of this.particles) {
      p.life -= dt;
      if (p.life <= 0) continue;
      p.vy += p.gravity * dt;
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      if (p.y > C.GROUND_Y + 6) {
        p.y = C.GROUND_Y + 6;
        p.vy *= -0.32;
        p.vx *= 0.7;
      }
      alive.push(p);
    }
    this.particles = alive.length > 260 ? alive.slice(-260) : alive;
  }

  _checkCollisions() {
    const hb = this.player.hitbox();
    for (const o of this.obstacles) {
      if (o.hitRight < hb.left || o.hitLeft > hb.right) continue;
      if (o.hitBottom <= hb.top || o.hitTop >= hb.bottom) {
        const margin = Math.min(Math.abs(o.hitBottom - hb.top),
                                Math.abs(o.hitTop - hb.bottom));
        if (margin < 26) this.nearMiss = 0.7;
        continue;
      }
      this.kill();
      return;
    }
  }

  kill() {
    if (this.dead) return;
    this.dead = true;
    this.shake = C.SHAKE_ON_CRASH;
    this.events.push('crash');
    const cx = C.PLAYER_X + C.BOARD_W * 0.5;
    const cy = this.player.y - 60;
    this._burst(cx, cy, 46, [255, 214, 120],
                { spread: 520, up: -420, size: 6, life: 1.1, gravity: 1250 });
    this._burst(cx, cy, 22, [231, 76, 60],
                { spread: 430, up: -330, size: 5, life: 0.9, gravity: 1250 });
  }

  drainEvents() {
    const e = this.events;
    this.events = [];
    return e;
  }

  shakeOffset() {
    if (this.shake <= 0) return [0, 0];
    const a = Math.random() * Math.PI * 2;
    return [Math.cos(a) * this.shake, Math.sin(a) * this.shake * 0.6];
  }
}
