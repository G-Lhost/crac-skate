// Clavier + tactile.
//
// Sur telephone : un appui dans le tiers bas de l'ecran fait s'accroupir,
// partout ailleurs il fait sauter. Le multi-touch est gere (on peut garder
// le doigt en bas et taper en haut).

export class Input {
  constructor(canvas, handlers) {
    this.h = handlers;
    this.canvas = canvas;
    this.pointers = new Map();
    this.hasTouch = window.matchMedia('(pointer: coarse)').matches
                 || 'ontouchstart' in window;
    this._bindKeyboard();
    this._bindPointer();
  }

  get duckZoneTop() { return this.canvas.clientHeight * 0.62; }

  _bindKeyboard() {
    const JUMP = new Set(['Space', 'ArrowUp', 'KeyW', 'KeyZ', 'Enter', 'NumpadEnter']);
    const DUCK = new Set(['ArrowDown', 'KeyS', 'ControlLeft', 'ControlRight']);
    window.addEventListener('keydown', (e) => {
      if (e.repeat) return;
      if (JUMP.has(e.code)) { e.preventDefault(); this.h.jumpDown(); }
      else if (DUCK.has(e.code)) { e.preventDefault(); this.h.duck(true); }
      else if (e.code === 'KeyP') this.h.pause();
      else if (e.code === 'KeyM') this.h.mute();
      else if (e.code === 'Escape') this.h.back();
      else if (e.code === 'KeyF') this.h.fullscreen();
    });
    window.addEventListener('keyup', (e) => {
      if (JUMP.has(e.code)) this.h.jumpUp();
      else if (DUCK.has(e.code)) this.h.duck(false);
    });
  }

  _bindPointer() {
    const el = this.canvas;
    const down = (e) => {
      el.setPointerCapture?.(e.pointerId);
      const duck = e.clientY > this.duckZoneTop;
      this.pointers.set(e.pointerId, duck);
      if (duck) this.h.duck(true); else this.h.jumpDown();
      e.preventDefault();
    };
    const up = (e) => {
      const wasDuck = this.pointers.get(e.pointerId);
      this.pointers.delete(e.pointerId);
      if (wasDuck) {
        if (![...this.pointers.values()].some(Boolean)) this.h.duck(false);
      } else {
        this.h.jumpUp();
      }
      e.preventDefault();
    };
    el.addEventListener('pointerdown', down);
    el.addEventListener('pointerup', up);
    el.addEventListener('pointercancel', up);
    // Bloque le zoom par double-tap et le rebond de defilement iOS.
    el.addEventListener('touchstart', (e) => e.preventDefault(), { passive: false });
    el.addEventListener('touchmove', (e) => e.preventDefault(), { passive: false });
    el.addEventListener('contextmenu', (e) => e.preventDefault());
    el.addEventListener('dblclick', (e) => e.preventDefault());
  }
}
