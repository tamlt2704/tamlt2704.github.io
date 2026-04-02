let _ctx: AudioContext | null = null;

function ctx(): AudioContext | null {
  if (typeof window === "undefined") return null;
  if (!_ctx) _ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
  if (_ctx.state === "suspended") _ctx.resume();
  return _ctx;
}

export function tone(freq: number, dur: number, type: OscillatorType = "sine", vol = 0.15) {
  const c = ctx();
  if (!c) return;
  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(vol, c.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + dur);
  osc.connect(gain).connect(c.destination);
  osc.start();
  osc.stop(c.currentTime + dur);
}

// --- Common sound effects ---

/** Soft pop — placing an item */
export function sfxPop() { tone(600 + Math.random() * 200, 0.1, "sine", 0.12); }

/** Soft click — removing / undo */
export function sfxRemove() { tone(300, 0.08, "triangle", 0.08); }

/** Rising chime C-E-G — correct answer */
export function sfxCorrect() {
  tone(523, 0.15, "sine", 0.15);
  setTimeout(() => tone(659, 0.15, "sine", 0.15), 100);
  setTimeout(() => tone(784, 0.25, "sine", 0.18), 200);
}

/** Low buzz — wrong answer */
export function sfxWrong() {
  tone(200, 0.2, "sawtooth", 0.1);
  setTimeout(() => tone(160, 0.3, "sawtooth", 0.1), 150);
}

/** Fanfare C-E-G-C — streak / big win */
export function sfxFanfare() {
  [523, 659, 784, 1047].forEach((f, i) =>
    setTimeout(() => tone(f, 0.18, "sine", 0.13), i * 80)
  );
}

/** Whoosh — launch / fly */
export function sfxWhoosh() {
  const c = ctx();
  if (!c) return;
  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = "sawtooth";
  osc.frequency.setValueAtTime(300, c.currentTime);
  osc.frequency.exponentialRampToValueAtTime(80, c.currentTime + 0.4);
  gain.gain.setValueAtTime(0.08, c.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.4);
  osc.connect(gain).connect(c.destination);
  osc.start();
  osc.stop(c.currentTime + 0.4);
}

/** Thud — landing / impact */
export function sfxThud() {
  const c = ctx();
  if (!c) return;
  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(120, c.currentTime);
  osc.frequency.exponentialRampToValueAtTime(40, c.currentTime + 0.2);
  gain.gain.setValueAtTime(0.2, c.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.2);
  osc.connect(gain).connect(c.destination);
  osc.start();
  osc.stop(c.currentTime + 0.2);
}

/** Electric zap — circuit complete */
export function sfxZap() {
  [800, 1200, 1600].forEach((f, i) =>
    setTimeout(() => tone(f, 0.08, "square", 0.06), i * 40)
  );
}

/** Tick — pendulum / clock */
export function sfxTick() { tone(1200, 0.03, "sine", 0.1); }

/** Slide — slider change */
export function sfxSlide() { tone(440 + Math.random() * 100, 0.05, "sine", 0.06); }

/** Explosion — asteroid destroy */
export function sfxExplode() {
  const c = ctx();
  if (!c) return;
  const bufSize = c.sampleRate * 0.15;
  const buf = c.createBuffer(1, bufSize, c.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / bufSize);
  const src = c.createBufferSource();
  const gain = c.createGain();
  src.buffer = buf;
  gain.gain.setValueAtTime(0.12, c.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.15);
  src.connect(gain).connect(c.destination);
  src.start();
}

/** Game over — descending tones */
export function sfxGameOver() {
  [400, 350, 300, 200].forEach((f, i) =>
    setTimeout(() => tone(f, 0.25, "sine", 0.12), i * 150)
  );
}

/** Draw line — turtle step */
export function sfxDraw() { tone(500 + Math.random() * 300, 0.06, "triangle", 0.06); }

/** Place shape on grid */
export function sfxPlace() { tone(700, 0.08, "sine", 0.1); }
