// Musique et bruitages.
//
// Contraintes mobiles : iOS et Android n'autorisent la lecture audio qu'apres
// une interaction de l'utilisateur. On cree donc l'AudioContext au premier
// appui, et on "deverrouille" les elements <audio> en les demarrant puis en
// les mettant aussitot en pause.

const MUSIC = {
  hymne: { loop: true, volume: 0.45 },
  mamma_mia: { loop: false, volume: 0.7 },
};

export class Audio2 {
  constructor() {
    this.muted = localStorage.getItem('crac.muted') === '1';
    this.ctx = null;
    this.unlocked = false;
    this.current = null;
    this.elements = {};
    for (const [name, cfg] of Object.entries(MUSIC)) {
      const el = document.createElement('audio');
      el.src = `assets/audio/${name}.m4a`;
      el.preload = 'auto';
      el.loop = cfg.loop;
      el.volume = cfg.volume;
      this.elements[name] = el;
    }
  }

  /** A appeler depuis un gestionnaire d'evenement declenche par l'utilisateur. */
  unlock() {
    if (this.unlocked) return;
    this.unlocked = true;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) {
      try { this.ctx = new AC(); } catch (_) { this.ctx = null; }
    }
    if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume();
    for (const el of Object.values(this.elements)) {
      const p = el.play();
      if (p && p.then) p.then(() => { el.pause(); el.currentTime = 0; }, () => {});
      else { el.pause(); el.currentTime = 0; }
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    localStorage.setItem('crac.muted', this.muted ? '1' : '0');
    for (const [name, el] of Object.entries(this.elements)) {
      el.volume = this.muted ? 0 : MUSIC[name].volume;
    }
    return this.muted;
  }

  music(name, { restart = true } = {}) {
    if (this.current && this.current !== name) this.stop(this.current);
    if (!name) { this.current = null; return; }
    const el = this.elements[name];
    if (!el) return;
    el.volume = this.muted ? 0 : MUSIC[name].volume;
    if (restart) el.currentTime = 0;
    const p = el.play();
    if (p && p.catch) p.catch(() => {});
    this.current = name;
  }

  stop(name) {
    const el = this.elements[name];
    if (el) { el.pause(); el.currentTime = 0; }
    if (this.current === name) this.current = null;
  }

  /** Bruitage synthetise : aucun fichier a telecharger. */
  tone(freqStart, freqEnd, duration, volume = 0.3, type = 'square') {
    if (!this.ctx || this.muted || this.ctx.state !== 'running') return;
    const t0 = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freqStart, t0);
    osc.frequency.exponentialRampToValueAtTime(Math.max(1, freqEnd), t0 + duration);
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(volume, t0 + 0.008);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);
    osc.connect(gain).connect(this.ctx.destination);
    osc.start(t0);
    osc.stop(t0 + duration + 0.02);
  }

  sfx(name) {
    if (name === 'jump') this.tone(430, 860, 0.16, 0.16, 'square');
    else if (name === 'land') this.tone(220, 90, 0.13, 0.13, 'triangle');
    else if (name === 'score') this.tone(880, 1320, 0.09, 0.07, 'sine');
  }
}
