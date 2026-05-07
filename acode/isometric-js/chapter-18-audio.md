# Chapter 18: Audio

[← Chapter 17: Save & Load](chapter-17-save-load.md) | [Chapter 19: Mobile Touch →](chapter-19-mobile-touch.md)

---

## The Task

Riku plays the game in silence. "It feels dead. I want a *thunk* when I place a building. A *crunch* when I demolish. Gentle background music. Maybe sounds get louder when you zoom in."

Audio is the most underrated part of game feel. A single sound effect on placement makes the game feel 10× more responsive.

## Web Audio API Basics

The browser's built-in audio engine. More powerful than `<audio>` elements — supports mixing, effects, spatial positioning:

```typescript
// src/engine/audio.ts
export class AudioEngine {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private buffers: Map<string, AudioBuffer> = new Map();

  async init() {
    // AudioContext must be created after user interaction (browser policy)
    this.ctx = new AudioContext();
    this.masterGain = this.ctx.createGain();
    this.masterGain.connect(this.ctx.destination);
    this.masterGain.gain.value = 0.7;
  }

  async loadSound(name: string, url: string) {
    if (!this.ctx) return;

    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.ctx.decodeAudioData(arrayBuffer);
    this.buffers.set(name, audioBuffer);
  }

  play(name: string, volume = 1, pitch = 1) {
    if (!this.ctx || !this.masterGain) return;

    const buffer = this.buffers.get(name);
    if (!buffer) return;

    const source = this.ctx.createBufferSource();
    source.buffer = buffer;
    source.playbackRate.value = pitch;

    const gain = this.ctx.createGain();
    gain.gain.value = volume;

    source.connect(gain);
    gain.connect(this.masterGain);
    source.start(0);
  }

  setMasterVolume(volume: number) {
    if (this.masterGain) {
      this.masterGain.gain.value = Math.max(0, Math.min(1, volume));
    }
  }

  // Resume after user interaction (required by browsers)
  resume() {
    if (this.ctx?.state === 'suspended') {
      this.ctx.resume();
    }
  }
}
```

## Loading and Playing Sound Effects

```typescript
// src/game/game-audio.ts
const audio = new AudioEngine();

async function initAudio() {
  await audio.init();

  // Load all sound effects
  await Promise.all([
    audio.loadSound('place', '/assets/audio/place.wav'),
    audio.loadSound('demolish', '/assets/audio/demolish.wav'),
    audio.loadSound('click', '/assets/audio/click.wav'),
    audio.loadSound('error', '/assets/audio/error.wav'),
    audio.loadSound('coins', '/assets/audio/coins.wav'),
  ]);
}

// Play on game events
function onBuildingPlaced() {
  // Slight pitch variation for natural feel
  const pitch = 0.95 + Math.random() * 0.1;
  audio.play('place', 0.8, pitch);
  audio.play('coins', 0.3, 1);
}

function onBuildingDemolished() {
  audio.play('demolish', 0.9, 0.9 + Math.random() * 0.2);
}

function onInvalidPlacement() {
  audio.play('error', 0.5, 1);
}

function onMenuClick() {
  audio.play('click', 0.4, 1.1);
}
```

## Handling the Autoplay Policy

Browsers block audio until the user interacts with the page. Handle this gracefully:

```typescript
// src/engine/audio-unlock.ts
export function setupAudioUnlock(audio: AudioEngine) {
  const unlock = () => {
    audio.resume();
    document.removeEventListener('click', unlock);
    document.removeEventListener('keydown', unlock);
    document.removeEventListener('touchstart', unlock);
  };

  document.addEventListener('click', unlock);
  document.addEventListener('keydown', unlock);
  document.addEventListener('touchstart', unlock);
}
```

## Background Music with Volume Control

Background music loops continuously. Use a separate gain node for independent volume control:

```typescript
// src/engine/music-player.ts
export class MusicPlayer {
  private ctx: AudioContext;
  private gainNode: GainNode;
  private source: AudioBufferSourceNode | null = null;
  private buffer: AudioBuffer | null = null;
  private _volume = 0.3;
  private isPlaying = false;

  constructor(ctx: AudioContext, destination: AudioNode) {
    this.ctx = ctx;
    this.gainNode = ctx.createGain();
    this.gainNode.gain.value = this._volume;
    this.gainNode.connect(destination);
  }

  async load(url: string) {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    this.buffer = await this.ctx.decodeAudioData(arrayBuffer);
  }

  play() {
    if (!this.buffer || this.isPlaying) return;

    this.source = this.ctx.createBufferSource();
    this.source.buffer = this.buffer;
    this.source.loop = true;
    this.source.connect(this.gainNode);
    this.source.start(0);
    this.isPlaying = true;
  }

  stop() {
    if (this.source) {
      this.source.stop();
      this.source = null;
    }
    this.isPlaying = false;
  }

  set volume(v: number) {
    this._volume = Math.max(0, Math.min(1, v));
    this.gainNode.gain.value = this._volume;
  }

  get volume(): number {
    return this._volume;
  }

  fadeIn(duration = 2) {
    this.gainNode.gain.setValueAtTime(0, this.ctx.currentTime);
    this.gainNode.gain.linearRampToValueAtTime(this._volume, this.ctx.currentTime + duration);
    this.play();
  }

  fadeOut(duration = 2) {
    this.gainNode.gain.linearRampToValueAtTime(0, this.ctx.currentTime + duration);
    setTimeout(() => this.stop(), duration * 1000);
  }
}
```

## Spatial Audio (Distance-Based Volume)

Sounds should be louder when zoomed in (closer to the action) and quieter when zoomed out:

```typescript
// src/engine/spatial-audio.ts
export class SpatialAudio {
  private audioEngine: AudioEngine;
  private camera: Camera;
  private listenerX = 0;
  private listenerY = 0;

  constructor(audioEngine: AudioEngine, camera: Camera) {
    this.audioEngine = audioEngine;
    this.camera = camera;
  }

  updateListener() {
    // Listener is at the center of the screen in world space
    const centerScreen = {
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    };
    const world = this.camera.screenToWorld(centerScreen.x, centerScreen.y);
    this.listenerX = world.wx;
    this.listenerY = world.wy;
  }

  playAt(name: string, worldX: number, worldY: number, baseVolume = 1) {
    // Calculate distance from listener
    const dx = worldX - this.listenerX;
    const dy = worldY - this.listenerY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Attenuation based on distance and zoom
    const maxDistance = 500 / this.camera.zoom; // Hear further when zoomed out
    const attenuation = Math.max(0, 1 - distance / maxDistance);

    // Zoom affects base volume (zoomed in = louder)
    const zoomFactor = Math.min(1, this.camera.zoom * 0.7);

    const finalVolume = baseVolume * attenuation * zoomFactor;

    if (finalVolume > 0.01) {
      this.audioEngine.play(name, finalVolume);
    }
  }
}

// Usage:
function onBuildingPlaced(gridX: number, gridY: number) {
  const { screenX, screenY } = cartToIso(gridX, gridY);
  const worldX = screenX + worldOffsetX;
  const worldY = screenY + worldOffsetY;

  spatialAudio.playAt('place', worldX, worldY, 0.8);
}
```

## Audio Sprite (Multiple Sounds in One File)

Loading 20 separate .wav files is slow. Pack them into one file with offset markers:

```typescript
// src/engine/audio-sprite.ts
interface SpriteRegion {
  start: number;  // Seconds
  end: number;    // Seconds
}

export class AudioSprite {
  private ctx: AudioContext;
  private buffer: AudioBuffer | null = null;
  private regions: Map<string, SpriteRegion> = new Map();
  private gainNode: GainNode;

  constructor(ctx: AudioContext, destination: AudioNode) {
    this.ctx = ctx;
    this.gainNode = ctx.createGain();
    this.gainNode.connect(destination);
  }

  async load(url: string, regions: Record<string, SpriteRegion>) {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    this.buffer = await this.ctx.decodeAudioData(arrayBuffer);

    for (const [name, region] of Object.entries(regions)) {
      this.regions.set(name, region);
    }
  }

  play(name: string, volume = 1) {
    if (!this.buffer) return;

    const region = this.regions.get(name);
    if (!region) return;

    const source = this.ctx.createBufferSource();
    source.buffer = this.buffer;

    const gain = this.ctx.createGain();
    gain.gain.value = volume;
    source.connect(gain);
    gain.connect(this.gainNode);

    const duration = region.end - region.start;
    source.start(0, region.start, duration);
  }
}

// Usage:
const sfxSprite = new AudioSprite(audioCtx, masterGain);
await sfxSprite.load('/assets/audio/sfx-sprite.ogg', {
  'place':    { start: 0.0, end: 0.5 },
  'demolish': { start: 0.5, end: 1.2 },
  'click':    { start: 1.2, end: 1.4 },
  'error':    { start: 1.4, end: 1.8 },
  'coins':    { start: 1.8, end: 2.3 },
  'whoosh':   { start: 2.3, end: 2.8 },
});

// One file, six sounds, one network request
sfxSprite.play('place', 0.8);
```

## Volume Settings UI

```typescript
// src/ui/audio-settings.ts
export function createAudioSettings(
  container: HTMLElement,
  audioEngine: AudioEngine,
  musicPlayer: MusicPlayer
) {
  const panel = document.createElement('div');
  panel.innerHTML = `
    <div style="padding: 12px; background: rgba(0,0,0,0.8); border-radius: 6px;">
      <label style="color: #fff; font-size: 12px; display: block; margin-bottom: 8px;">
        🔊 Master
        <input type="range" id="vol-master" min="0" max="100" value="70" style="width: 100px;">
      </label>
      <label style="color: #fff; font-size: 12px; display: block; margin-bottom: 8px;">
        🎵 Music
        <input type="range" id="vol-music" min="0" max="100" value="30" style="width: 100px;">
      </label>
      <label style="color: #fff; font-size: 12px; display: block;">
        💥 SFX
        <input type="range" id="vol-sfx" min="0" max="100" value="80" style="width: 100px;">
      </label>
    </div>
  `;

  panel.querySelector('#vol-master')!.addEventListener('input', (e) => {
    const value = (e.target as HTMLInputElement).valueAsNumber / 100;
    audioEngine.setMasterVolume(value);
  });

  panel.querySelector('#vol-music')!.addEventListener('input', (e) => {
    const value = (e.target as HTMLInputElement).valueAsNumber / 100;
    musicPlayer.volume = value;
  });

  container.appendChild(panel);
}
```

## Riku's Reaction

*Thunk.* A building lands on the grid. Gentle piano music plays in the background. Demolish a building — *crunch*. Zoom in and the ambient sounds get louder.

Riku: "It feels real now. But I tried it on my phone and... nothing works. No hover, no right-click, no scroll wheel."

You: "Touch controls. Pinch to zoom, tap to place, one-finger pan. Different input model entirely."

## What You Built

- **AudioEngine** — Web Audio API wrapper with buffer loading and playback
- **Autoplay unlock** — resume AudioContext on first user interaction
- **Sound effects** — place, demolish, click with pitch variation
- **MusicPlayer** — looping background music with fade in/out
- **Spatial audio** — distance-based volume attenuation
- **Audio sprite** — multiple sounds packed in one file
- **Volume controls** — master, music, and SFX sliders

The city has a voice. Next: making it work on phones.

---

[← Chapter 17: Save & Load](chapter-17-save-load.md) | [Chapter 19: Mobile Touch →](chapter-19-mobile-touch.md)
