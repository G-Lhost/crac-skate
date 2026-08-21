// Rendu Canvas 2D. Meme decoupage que python/crac/render.py.

import * as C from './config.js';
import * as MONS from './mons.js';

export class Viewport {
  constructor() { this.scale = 1; this.viewW = C.VIEW_W_DEFAULT; this.ox = 0; this.oy = 0; }

  resize(w, h) {
    let scale = h / C.VIEW_H;
    let viewW = w / scale;
    if (viewW < C.VIEW_W_MIN) { scale = w / C.VIEW_W_MIN; viewW = C.VIEW_W_MIN; }
    else if (viewW > C.VIEW_W_MAX) { viewW = C.VIEW_W_MAX; }
    this.scale = scale;
    this.viewW = viewW;
    this.ox = (w - viewW * scale) * 0.5;
    this.oy = (h - C.VIEW_H * scale) * 0.5;
  }
  x(v) { return this.ox + v * this.scale; }
  y(v) { return this.oy + v * this.scale; }
  s(v) { return v * this.scale; }
}

/** Bande de decor montois, large de deux ecrans et raccordable bord a bord.
 *
 * Les silhouettes viennent de mons.js, genere depuis python/crac/mons.py :
 * beffroi, collegiale Sainte-Waudru, hotel de ville, gare Calatrava.
 */
function buildCityscape(vp, sequence, palette, gapRange, seed) {
  const rng = MONS.mulberry32(seed);
  const lw = vp.viewW * 2;
  const cv = document.createElement('canvas');
  cv.width = Math.max(1, Math.round(lw * vp.scale));
  cv.height = Math.max(1, Math.round(C.VIEW_H * vp.scale));
  const g = cv.getContext('2d');
  const k = vp.scale;

  for (const [name, x0, vs] of MONS.layout(sequence, lw, gapRange, rng)) {
    for (const part of MONS.BUILDINGS[name].parts) {
      g.fillStyle = palette[part[part.length - 1]];
      if (part[0] === 'rect') {
        const [, x, y, w, h] = part;
        g.fillRect(Math.round((x0 + x) * k),
                   Math.round((C.GROUND_Y - (y + h) * vs) * k),
                   Math.max(1, Math.round(w * k)),
                   Math.max(1, Math.round(h * vs * k)));
      } else if (part[0] === 'poly') {
        const pts = part[1];
        if (pts.length < 3) continue;
        g.beginPath();
        pts.forEach(([px, py], i) => {
          const X = Math.round((x0 + px) * k);
          const Y = Math.round((C.GROUND_Y - py * vs) * k);
          if (i === 0) g.moveTo(X, Y); else g.lineTo(X, Y);
        });
        g.closePath();
        g.fill();
      } else if (part[0] === 'circle') {
        const [, cx, cy, r] = part;
        g.beginPath();
        g.arc(Math.round((x0 + cx) * k), Math.round((C.GROUND_Y - cy * vs) * k),
              Math.max(1, Math.round(r * k)), 0, Math.PI * 2);
        g.fill();
      }
    }
  }
  return cv;
}

export class Renderer {
  constructor(canvas, assets) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d', { alpha: false });
    this.assets = assets;
    this.vp = new Viewport();
    this.dpr = 1;
    this._layers = null;
    this._layerKey = null;
  }

  resize(cssW, cssH, dpr) {
    this.dpr = dpr;
    const w = Math.round(cssW * dpr);
    const h = Math.round(cssH * dpr);
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }
    this.vp.resize(w, h);
  }

  _ensureLayers() {
    const vp = this.vp;
    const key = `${Math.round(vp.viewW)}:${Math.round(vp.scale * 1000)}`;
    if (key === this._layerKey) return;
    this._layerKey = key;
    this._layers = {
      far: buildCityscape(vp, MONS.FAR_SEQUENCE, MONS.FAR_PALETTE,
                          MONS.FAR_GAP, 7),
      near: buildCityscape(vp, MONS.NEAR_SEQUENCE, MONS.NEAR_PALETTE,
                           MONS.NEAR_GAP, 21),
    };
  }

  // -- decor -----------------------------------------------------------
  drawBackground(scroll, shake) {
    const { ctx, vp } = this;
    this._ensureLayers();
    const [shx, shy] = [vp.s(shake[0]), vp.s(shake[1])];
    ctx.fillStyle = '#060714';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    const top = vp.y(0) + shy;
    const grad = ctx.createLinearGradient(0, top, 0, top + vp.s(C.VIEW_H));
    grad.addColorStop(0, C.SKY_TOP);
    grad.addColorStop(1, C.SKY_BOT);
    ctx.fillStyle = grad;
    ctx.fillRect(vp.ox + shx, top, vp.s(vp.viewW), vp.s(C.VIEW_H));

    // soleil : degrade radial, coeur opaque et halo qui s'eteint en douceur
    const cx = vp.x(vp.viewW * 0.78) + shx;
    const cy = vp.y(168) + shy;
    const r = vp.s(124);
    const sun = ctx.createRadialGradient(cx, cy, vp.s(6), cx, cy, r);
    sun.addColorStop(0.00, 'rgba(255,238,196,1)');
    sun.addColorStop(0.30, 'rgba(255,238,196,1)');
    sun.addColorStop(0.34, 'rgba(255,214,150,0.52)');
    sun.addColorStop(1.00, 'rgba(255,206,138,0)');
    ctx.fillStyle = sun;
    ctx.fillRect(cx - r, cy - r, r * 2, r * 2);

    this._parallax(this._layers.far, scroll * 0.12, shx, shy);
    this._parallax(this._layers.near, scroll * 0.34, shx, shy);
  }

  _parallax(layer, offset, shx, shy) {
    const { ctx, vp } = this;
    const w = layer.width;
    const off = -(((vp.s(offset) % w) + w) % w);
    const y = vp.oy + shy;
    let x = vp.ox + off + shx;
    const end = vp.ox + vp.s(vp.viewW);
    while (x < end) { ctx.drawImage(layer, x, y); x += w; }
  }

  drawRoad(scroll, shake) {
    const { ctx, vp } = this;
    const img = this.assets.images.route;
    if (!img) return;
    const [shx, shy] = [vp.s(shake[0]), vp.s(shake[1])];
    const { w: lw, h: lh } = this.assets.size('route');
    const tw = vp.s(lw), th = vp.s(lh);
    const y = vp.y(C.GROUND_Y) + shy;
    const end = vp.ox + vp.s(vp.viewW);
    let x = vp.ox + shx - (((vp.s(scroll) % tw) + tw) % tw);
    while (x < end) { ctx.drawImage(img, x, y, tw, th); x += tw; }

    ctx.fillStyle = '#e8e8f0';
    ctx.fillRect(vp.ox, y, vp.s(vp.viewW), Math.max(1, vp.s(3)));
    ctx.fillStyle = '#787a96';
    ctx.fillRect(vp.ox, y + vp.s(4), vp.s(vp.viewW), Math.max(1, vp.s(1.5)));

    const dash = 70, gap = 58, period = dash + gap;
    const yy = vp.y(C.GROUND_Y + 118) + shy;
    const h = Math.max(1, vp.s(7));
    ctx.fillStyle = '#eed884';
    for (let d = -(((scroll % period) + period) % period);
         d < vp.viewW + period; d += period) {
      ctx.fillRect(vp.x(d) + shx, yy, vp.s(dash), h);
    }
  }

  // -- entites ---------------------------------------------------------
  _shadow(cx, groundY, width, alpha) {
    const { ctx, vp } = this;
    if (alpha <= 0.02) return;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = '#0c0e28';
    ctx.beginPath();
    ctx.ellipse(cx, groundY, width * 0.5, vp.s(7), 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  drawPlayer(w, shake) {
    const { ctx, vp } = this;
    const p = w.player;
    const [shx, shy] = [vp.s(shake[0]), vp.s(shake[1])];
    const board = this.assets.images.skate;
    const head = this.assets.images.eduardo_tete;
    const bs = this.assets.size('skate');
    const hs = this.assets.size('eduardo_tete');
    const duck = p.ducking && p.onGround;
    const squash = duck ? 0.62 : 1;

    const alt = Math.max(0, C.GROUND_Y - p.y);
    const t = Math.min(1, alt / 220);
    this._shadow(vp.x(C.PLAYER_X + bs.w * 0.5) + shx, vp.y(C.GROUND_Y - 2) + shy,
                 vp.s(bs.w * (1 - 0.45 * t)), 0.47 * (1 - 0.65 * t));

    // planche
    const bcx = vp.x(C.PLAYER_X + bs.w * 0.5) + shx;
    const bcy = vp.y(p.y - bs.h * 0.5) + shy;
    ctx.save();
    ctx.translate(bcx, bcy);
    ctx.rotate(p.lean);
    ctx.drawImage(board, -vp.s(bs.w) / 2, -vp.s(bs.h) / 2, vp.s(bs.w), vp.s(bs.h));
    ctx.restore();

    // tete
    const headH = hs.h * squash;
    const headW = hs.w * Math.pow(2 - squash, 0.35);
    const hcx = bcx + vp.s(Math.sin(p.wheelSpin * 0.5) * 1.6);
    const hcy = vp.y(p.y - bs.h * 0.72 - headH * 0.5) + shy
              + vp.s(Math.abs(Math.sin(p.wheelSpin * 0.5)) * 1.4);
    ctx.save();
    ctx.translate(hcx, hcy);
    ctx.rotate(p.lean * 0.5);
    ctx.drawImage(head, -vp.s(headW) / 2, -vp.s(headH) / 2,
                  vp.s(headW), vp.s(headH));
    ctx.restore();
  }

  drawObstacles(w, shake) {
    const { ctx, vp } = this;
    const [shx, shy] = [vp.s(shake[0]), vp.s(shake[1])];
    for (const o of w.obstacles) {
      if (o.x > vp.viewW + 60 || o.x + o.w < -60) continue;
      const img = this.assets.images[o.kind];
      if (!img) continue;
      if (o.flying) {
        const t = Math.min(1, Math.max(0, (C.GROUND_Y - (o.y + o.h)) / 220));
        this._shadow(vp.x(o.x + o.w * 0.5) + shx, vp.y(C.GROUND_Y - 2) + shy,
                     vp.s(o.w * (1 - 0.4 * t)), 0.35 * (1 - t));
      } else {
        this._shadow(vp.x(o.x + o.w * 0.5) + shx, vp.y(C.GROUND_Y - 3) + shy,
                     vp.s(o.w * 0.9), 0.42);
      }
      ctx.drawImage(img, vp.x(o.x) + shx, vp.y(o.y) + shy,
                    vp.s(o.w), vp.s(o.h));
    }
  }

  drawParticles(w, shake) {
    const { ctx, vp } = this;
    const [shx, shy] = [vp.s(shake[0]), vp.s(shake[1])];
    for (const p of w.particles) {
      const a = Math.max(0, Math.min(1, p.life / p.maxLife));
      const size = Math.max(1, vp.s(p.size * (0.4 + 0.6 * a)));
      ctx.globalAlpha = 0.92 * a;
      ctx.fillStyle = `rgb(${p.color[0]},${p.color[1]},${p.color[2]})`;
      ctx.fillRect(vp.x(p.x) + shx - size / 2, vp.y(p.y) + shy - size / 2,
                   size, size);
    }
    ctx.globalAlpha = 1;
  }

  // -- texte et ecrans --------------------------------------------------
  text(str, size, x, y, color = C.WHITE, align = 'left', alpha = 1) {
    const { ctx, vp } = this;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.font = `${Math.max(8, vp.s(size))}px BradBunR, Impact, "Arial Black", sans-serif`;
    ctx.textAlign = align === 'center' ? 'center' : (align === 'right' ? 'right' : 'left');
    ctx.textBaseline = align === 'center' ? 'middle' : 'top';
    const px = vp.x(x), py = vp.y(y);
    const off = Math.max(1, vp.s(2.5));
    ctx.fillStyle = 'rgba(28,30,62,0.75)';
    ctx.fillText(str, px + off, py + off);
    ctx.fillStyle = color;
    ctx.fillText(str, px, py);
    ctx.restore();
  }

  dim(alpha = 0.65) {
    const { ctx } = this;
    ctx.fillStyle = `rgba(10,12,30,${alpha})`;
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawHud(w, best, muted) {
    const vp = this.vp;
    this.text(`SCORE ${w.score}`, 30, 22, 12);
    this.text(`RECORD ${best}`, 24, vp.viewW - 22, 16, C.CREAM, 'right');
    this.text(`${Math.round(w.speed * 0.075)} km/h`, 20, 24, 48, '#c6ceff');
    if (muted) this.text('SOURDINE', 18, 24, 74, '#aab0dc');
    if (w.nearMiss > 0) {
      this.text('CHAUD !', 34, vp.viewW * 0.5, 118, C.AMBER, 'center',
                Math.min(1, w.nearMiss / 0.7));
    }
  }

  drawMenu(best, blink, touch) {
    const vp = this.vp;
    this.dim(0.47);
    const cx = vp.viewW * 0.5;
    this.text(C.TITLE, 150, cx, 176, C.WHITE, 'center');
    this.text(C.SUBTITLE, 40, cx, 262, C.AMBER, 'center');
    if (touch) {
      this.text("Touchez l'ecran pour sauter", 24, cx, 322, C.CREAM, 'center');
      this.text('Maintenez le bas de l’ecran pour vous accroupir', 22, cx, 352,
                '#c4caf6', 'center');
    } else {
      this.text('ESPACE / CLIC : sauter     BAS : s’accroupir', 22, cx, 322,
                C.CREAM, 'center');
      this.text('P : pause     M : sourdine', 22, cx, 352, '#c4caf6', 'center');
    }
    if (best) this.text(`Record a battre : ${best}`, 26, cx, 400, C.WHITE, 'center');
    if (blink % 1 < 0.62) {
      this.text(touch ? 'Touchez pour lancer Eduardo'
                      : 'Appuyez sur ESPACE pour lancer Eduardo',
                30, cx, 488, C.WHITE, 'center');
    }
  }

  drawPause(touch) {
    const vp = this.vp;
    this.dim(0.68);
    this.text('PAUSE', 120, vp.viewW * 0.5, 250, C.WHITE, 'center');
    this.text(touch ? 'Touchez pour reprendre' : 'P ou ESPACE pour reprendre',
              26, vp.viewW * 0.5, 340, C.CREAM, 'center');
  }

  drawGameOver(w, best, record, blink, ready, touch) {
    const { ctx, vp } = this;
    this.dim(0.6);
    const cx = vp.viewW * 0.5;
    const img = this.assets.images.eduardo_casse;
    if (img) {
      const h = 232, imgW = (img.naturalWidth / img.naturalHeight) * h;
      const x = vp.x(cx - imgW / 2), y = vp.y(128);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(x - vp.s(5), y - vp.s(5), vp.s(imgW) + vp.s(10), vp.s(h) + vp.s(10));
      ctx.drawImage(img, x, y, vp.s(imgW), vp.s(h));
    }
    this.text('CRAC !', 126, cx, 62, C.RED, 'center');
    this.text(`Score : ${w.score}`, 40, cx, 396, C.WHITE, 'center');
    if (record) this.text('NOUVEAU RECORD !', 34, cx, 442, C.AMBER, 'center');
    else this.text(`Record : ${best}`, 26, cx, 444, C.CREAM, 'center');
    if (ready && blink % 1 < 0.62) {
      this.text(touch ? 'Touchez pour rejouer' : 'ESPACE : rejouer   ECHAP : menu',
                26, cx, 500, C.WHITE, 'center');
    }
  }
}
