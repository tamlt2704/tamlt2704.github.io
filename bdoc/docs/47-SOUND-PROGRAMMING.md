# Chapter 47: Sound Programming — Create Your Own Music & Sound Effects

## What you'll learn

- How digital audio works (samples, frequency, amplitude, waveforms)
- Web Audio API: synthesize sounds directly in the browser
- Tone.js: a music framework for creating instruments, beats, and melodies
- Building sound effects: whoosh, click, explosion, notification, transition
- Creating background music: loops, chords, arpeggios, drum patterns
- Exporting audio to WAV/MP3 files for YouTube
- Python alternative: pydub + numpy for programmatic audio generation
- Mixing and mastering basics (EQ, compression, reverb)

---

## PART 1: How Digital Audio Works

## 47.1 Sound fundamentals

```
Sound = vibrations in air (pressure waves)

        Amplitude (volume)
           ▲
           │    ╭──╮      ╭──╮
           │   ╱    ╲    ╱    ╲
     ──────┼──╱──────╲──╱──────╲──── Time →
           │ ╱        ╲╱        ╲
           │╱          ╰──╯      ╰──
           ▼

Frequency:  vibrations per second (Hz)
            220 Hz = A3 (low), 440 Hz = A4 (concert pitch), 880 Hz = A5 (high)

Amplitude:  how loud (0.0 = silence, 1.0 = maximum)

Waveform:   shape of the wave (determines tone/timbre)
```

**Waveforms (each sounds different at the same frequency):**
```
Sine:      smooth, pure tone (flute, whistle)
    ╭──╮      ╭──╮
   ╱    ╲    ╱    ╲
  ╱      ╲  ╱      ╲
 ╱        ╲╱        ╲

Square:    hollow, retro (NES, chiptune)
  ┌──────┐      ┌──────┐
  │      │      │      │
──┘      └──────┘      └──

Sawtooth:  bright, buzzy (synth lead, brass)
   /│    /│    /│
  / │   / │   / │
 /  │  /  │  /  │
/   │ /   │ /   │

Triangle:  soft, mellow (between sine and square)
   /\      /\
  /  \    /  \
 /    \  /    \
/      \/      \
```

## 47.2 Digital audio basics

```
Sample rate:  how many times per second the wave is measured
              44100 Hz (CD quality) = 44,100 samples per second
              48000 Hz (video standard) = 48,000 samples per second

Bit depth:    precision of each sample
              16-bit = 65,536 levels (CD)
              24-bit = 16 million levels (studio)
              32-bit float = Web Audio API default

Duration of 1 second of stereo audio at 44.1kHz, 16-bit:
  44100 samples × 2 channels × 2 bytes = 176,400 bytes ≈ 172 KB
```

---

## PART 2: Web Audio API — Synthesize in the Browser

## 47.3 Basic sound generation

```javascript
// Create audio context (the audio engine)
const ctx = new AudioContext();

// Play a simple tone
function playTone(frequency = 440, duration = 0.5, type = "sine") {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();

  osc.type = type;           // "sine", "square", "sawtooth", "triangle"
  osc.frequency.value = frequency;

  gain.gain.setValueAtTime(0.3, ctx.currentTime);                    // start volume
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration); // fade out

  osc.connect(gain);
  gain.connect(ctx.destination);  // destination = speakers

  osc.start(ctx.currentTime);
  osc.stop(ctx.currentTime + duration);
}

// Play A4 (concert pitch)
playTone(440, 1, "sine");

// Play a chord (multiple frequencies)
function playChord(frequencies, duration = 1) {
  frequencies.forEach(freq => playTone(freq, duration, "triangle"));
}

// C major chord: C4 + E4 + G4
playChord([261.63, 329.63, 392.00]);
```

## 47.4 Musical notes → frequencies

```javascript
// Formula: freq = 440 × 2^((note - 69) / 12)
// Where note is MIDI number (A4 = 69, C4 = 60)

function midiToFreq(midi) {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

// Note name to MIDI number
const NOTE_MAP = {
  "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
  "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11,
};

function noteToFreq(note, octave) {
  const midi = NOTE_MAP[note] + (octave + 1) * 12;
  return midiToFreq(midi);
}

// Examples
noteToFreq("A", 4);   // 440 Hz
noteToFreq("C", 4);   // 261.63 Hz
noteToFreq("E", 4);   // 329.63 Hz
```

## 47.5 Envelope (ADSR) — shaping sound over time

```
Volume
  ▲
  │     ╱╲
  │    ╱  ╲___________
  │   ╱    (sustain)   ╲
  │  ╱                   ╲
  │ ╱                     ╲
  └──────────────────────────→ Time
  A    D      S          R

A = Attack (how fast sound reaches full volume)
D = Decay (drop from peak to sustain level)
S = Sustain (volume while key is held)
R = Release (fade out after key released)
```

```javascript
function playWithEnvelope(freq, { attack = 0.05, decay = 0.1, sustain = 0.3, release = 0.3, duration = 1 } = {}) {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();

  osc.frequency.value = freq;
  osc.type = "sawtooth";

  const now = ctx.currentTime;
  const noteOff = now + duration;

  // ADSR envelope
  gain.gain.setValueAtTime(0, now);
  gain.gain.linearRampToValueAtTime(0.5, now + attack);           // Attack
  gain.gain.linearRampToValueAtTime(sustain, now + attack + decay); // Decay → Sustain
  gain.gain.setValueAtTime(sustain, noteOff);                       // Hold sustain
  gain.gain.linearRampToValueAtTime(0, noteOff + release);          // Release

  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(now);
  osc.stop(noteOff + release);
}
```

---

## PART 3: Sound Effects for YouTube

## 47.6 UI / Notification sounds

```javascript
// Click / tap
function clickSound() {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(1800, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.05);
  gain.gain.setValueAtTime(0.3, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
  osc.connect(gain).connect(ctx.destination);
  osc.start(); osc.stop(ctx.currentTime + 0.08);
}

// Success / level up (ascending tone)
function successSound() {
  [523, 659, 784].forEach((freq, i) => {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    const start = ctx.currentTime + i * 0.12;
    gain.gain.setValueAtTime(0, start);
    gain.gain.linearRampToValueAtTime(0.3, start + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, start + 0.3);
    osc.connect(gain).connect(ctx.destination);
    osc.start(start); osc.stop(start + 0.3);
  });
}

// Error / wrong (descending, dissonant)
function errorSound() {
  [400, 300].forEach((freq, i) => {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "square";
    osc.frequency.value = freq;
    const start = ctx.currentTime + i * 0.1;
    gain.gain.setValueAtTime(0.2, start);
    gain.gain.exponentialRampToValueAtTime(0.001, start + 0.2);
    osc.connect(gain).connect(ctx.destination);
    osc.start(start); osc.stop(start + 0.2);
  });
}

// Notification ping
function notificationSound() {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(880, ctx.currentTime);
  osc.frequency.setValueAtTime(1320, ctx.currentTime + 0.1);
  gain.gain.setValueAtTime(0.3, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
  osc.connect(gain).connect(ctx.destination);
  osc.start(); osc.stop(ctx.currentTime + 0.4);
}
```

## 47.7 Transition / cinematic sounds

```javascript
// Whoosh (sweep up)
function whooshSound() {
  const osc = ctx.createOscillator();
  const noise = createNoise(0.5);  // white noise burst
  const gain = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  filter.type = "bandpass";
  filter.frequency.setValueAtTime(200, ctx.currentTime);
  filter.frequency.exponentialRampToValueAtTime(4000, ctx.currentTime + 0.3);
  filter.Q.value = 2;

  gain.gain.setValueAtTime(0.4, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);

  noise.connect(filter).connect(gain).connect(ctx.destination);
}

// White noise generator
function createNoise(duration) {
  const bufferSize = ctx.sampleRate * duration;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = Math.random() * 2 - 1;  // random values between -1 and 1
  }
  const source = ctx.createBufferSource();
  source.buffer = buffer;
  source.start();
  return source;
}

// Deep impact / bass drop
function impactSound() {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(150, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(30, ctx.currentTime + 0.5);
  gain.gain.setValueAtTime(0.8, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.8);
  osc.connect(gain).connect(ctx.destination);
  osc.start(); osc.stop(ctx.currentTime + 0.8);
}

// Riser (tension builder — ascending noise before a drop)
function riserSound(duration = 3) {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sawtooth";
  osc.frequency.setValueAtTime(100, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(2000, ctx.currentTime + duration);
  gain.gain.setValueAtTime(0, ctx.currentTime);
  gain.gain.linearRampToValueAtTime(0.4, ctx.currentTime + duration);
  gain.gain.linearRampToValueAtTime(0, ctx.currentTime + duration + 0.1);
  osc.connect(gain).connect(ctx.destination);
  osc.start(); osc.stop(ctx.currentTime + duration + 0.1);
}
```

## 47.8 Game-style effects

```javascript
// Coin / pickup
function coinSound() {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "square";
  osc.frequency.setValueAtTime(987, ctx.currentTime);      // B5
  osc.frequency.setValueAtTime(1318, ctx.currentTime + 0.06); // E6
  gain.gain.setValueAtTime(0.2, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2);
  osc.connect(gain).connect(ctx.destination);
  osc.start(); osc.stop(ctx.currentTime + 0.2);
}

// Explosion (noise + low frequency rumble)
function explosionSound() {
  // Low rumble
  const osc = ctx.createOscillator();
  const oscGain = ctx.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(60, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(20, ctx.currentTime + 1);
  oscGain.gain.setValueAtTime(0.5, ctx.currentTime);
  oscGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
  osc.connect(oscGain).connect(ctx.destination);
  osc.start(); osc.stop(ctx.currentTime + 1.5);

  // Noise burst
  const noise = createNoise(1.5);
  const noiseGain = ctx.createGain();
  const noiseFilter = ctx.createBiquadFilter();
  noiseFilter.type = "lowpass";
  noiseFilter.frequency.setValueAtTime(5000, ctx.currentTime);
  noiseFilter.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 1);
  noiseGain.gain.setValueAtTime(0.6, ctx.currentTime);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
  noise.connect(noiseFilter).connect(noiseGain).connect(ctx.destination);
}

// Laser / zap
function laserSound() {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sawtooth";
  osc.frequency.setValueAtTime(1500, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.2);
  gain.gain.setValueAtTime(0.3, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
  osc.connect(gain).connect(ctx.destination);
  osc.start(); osc.stop(ctx.currentTime + 0.3);
}
```



---

## PART 4: Tone.js — Create Music

## 47.9 Setup

```bash
npm install tone
```

```javascript
import * as Tone from "tone";

// Must be triggered by user interaction (browser autoplay policy)
document.getElementById("start").addEventListener("click", async () => {
  await Tone.start();
  console.log("Audio ready");
});
```

## 47.10 Playing melodies

```javascript
// Create a synthesizer
const synth = new Tone.Synth({
  oscillator: { type: "triangle" },
  envelope: { attack: 0.05, decay: 0.2, sustain: 0.3, release: 0.5 },
}).toDestination();

// Play a single note
synth.triggerAttackRelease("C4", "8n"); // C4 for an eighth note duration

// Play a melody (sequence of notes)
const melody = [
  { note: "C4", duration: "8n" },
  { note: "E4", duration: "8n" },
  { note: "G4", duration: "8n" },
  { note: "C5", duration: "4n" },
  { note: "G4", duration: "8n" },
  { note: "E4", duration: "8n" },
  { note: "C4", duration: "2n" },
];

let time = Tone.now();
melody.forEach(({ note, duration }) => {
  synth.triggerAttackRelease(note, duration, time);
  time += Tone.Time(duration).toSeconds();
});
```

## 47.11 Drum patterns

```javascript
// Drum sounds
const kick = new Tone.MembraneSynth().toDestination();
const snare = new Tone.NoiseSynth({
  noise: { type: "white" },
  envelope: { attack: 0.001, decay: 0.2, sustain: 0 },
}).toDestination();
const hihat = new Tone.MetalSynth({
  frequency: 400, envelope: { attack: 0.001, decay: 0.05, release: 0.01 },
  harmonicity: 5.1, modulationIndex: 32, resonance: 4000,
}).toDestination();
hihat.volume.value = -10;

// Pattern: classic boom-bap
const drumPattern = new Tone.Loop((time) => {
  // This plays every beat
}, "4n");

// More control with Transport + sequences
Tone.Transport.bpm.value = 90;

// Kick pattern (quarter notes with some variation)
const kickSeq = new Tone.Sequence((time, note) => {
  if (note) kick.triggerAttackRelease(note, "8n", time);
}, ["C1", null, null, "C1", null, null, "C1", null], "8n").start(0);

// Snare on beats 2 and 4
const snareSeq = new Tone.Sequence((time, hit) => {
  if (hit) snare.triggerAttackRelease("8n", time);
}, [null, null, null, null, 1, null, null, null, null, null, null, null, 1, null, null, null], "16n").start(0);

// Hi-hat (every 8th note)
const hihatSeq = new Tone.Sequence((time, hit) => {
  if (hit) hihat.triggerAttackRelease("32n", time, 0.05);
}, [1, 1, 1, 1, 1, 1, 1, 1], "8n").start(0);

// Start/stop
Tone.Transport.start();
// Tone.Transport.stop();
```

## 47.12 Background music (looping chords + arpeggios)

```javascript
// Pad synth (atmospheric background)
const pad = new Tone.PolySynth(Tone.Synth, {
  oscillator: { type: "sine" },
  envelope: { attack: 1, decay: 0.5, sustain: 0.8, release: 2 },
}).toDestination();
pad.volume.value = -8;

// Chord progression: I - V - vi - IV in C major
const chords = [
  ["C3", "E3", "G3"],    // C major
  ["G3", "B3", "D4"],    // G major
  ["A3", "C4", "E4"],    // A minor
  ["F3", "A3", "C4"],    // F major
];

let chordIndex = 0;
const chordLoop = new Tone.Loop((time) => {
  const chord = chords[chordIndex % chords.length];
  pad.triggerAttackRelease(chord, "1n", time);  // whole note duration
  chordIndex++;
}, "1n").start(0);

// Arpeggio over the chords
const arp = new Tone.Synth({
  oscillator: { type: "triangle" },
  envelope: { attack: 0.01, decay: 0.1, sustain: 0.2, release: 0.3 },
}).toDestination();
arp.volume.value = -12;

const arpPattern = new Tone.Pattern((time, note) => {
  arp.triggerAttackRelease(note, "16n", time);
}, ["C4", "E4", "G4", "B4", "G4", "E4"], "upDown").start(0);

Tone.Transport.bpm.value = 75;
Tone.Transport.start();
```

## 47.13 Effects (reverb, delay, distortion)

```javascript
// Reverb (space/atmosphere)
const reverb = new Tone.Reverb({ decay: 3, wet: 0.4 }).toDestination();

// Delay (echo)
const delay = new Tone.FeedbackDelay("8n", 0.3).toDestination();

// Distortion
const distortion = new Tone.Distortion(0.4).toDestination();

// Chain: synth → delay → reverb → speakers
const synth = new Tone.Synth().chain(delay, reverb);
synth.triggerAttackRelease("A3", "4n");

// EQ (3-band equalizer)
const eq = new Tone.EQ3({
  low: -5,     // cut bass slightly
  mid: 2,      // boost mids
  high: -3,    // cut highs slightly
}).toDestination();

// Compressor (even out volume)
const compressor = new Tone.Compressor({
  threshold: -20, ratio: 4, attack: 0.003, release: 0.25,
}).toDestination();

// Full chain for a mastered sound:
// synth → EQ → compressor → reverb → destination
const mastered = new Tone.Synth().chain(eq, compressor, reverb);
```

---

## PART 5: Export Audio for YouTube

## 47.14 Record Web Audio to WAV (browser)

```javascript
// Use Tone.js Recorder
const recorder = new Tone.Recorder();
const synth = new Tone.Synth().connect(recorder);

// Start recording
recorder.start();

// Play your music...
synth.triggerAttackRelease("C4", "4n");
// ... wait for music to finish ...

// Stop and download
setTimeout(async () => {
  const recording = await recorder.stop();
  const url = URL.createObjectURL(recording);
  const a = document.createElement("a");
  a.href = url;
  a.download = "my-sound.webm";
  a.click();
}, 5000); // record for 5 seconds
```

## 47.15 Offline rendering (render without playing in real-time)

```javascript
// Render 10 seconds of audio instantly (no waiting)
const buffer = await Tone.Offline(({ transport }) => {
  const synth = new Tone.Synth().toDestination();

  // Schedule your music
  synth.triggerAttackRelease("C4", "4n", 0);
  synth.triggerAttackRelease("E4", "4n", 0.5);
  synth.triggerAttackRelease("G4", "4n", 1.0);
  synth.triggerAttackRelease("C5", "2n", 1.5);

  transport.start();
}, 10); // 10 seconds

// Convert to WAV and download
const wav = bufferToWav(buffer);
downloadBlob(wav, "music.wav");

// WAV encoder helper
function bufferToWav(audioBuffer) {
  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const length = audioBuffer.length;
  const buffer = new ArrayBuffer(44 + length * numChannels * 2);
  const view = new DataView(buffer);

  // WAV header
  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + length * numChannels * 2, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numChannels * 2, true);
  view.setUint16(32, numChannels * 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, "data");
  view.setUint32(40, length * numChannels * 2, true);

  // Write samples
  let offset = 44;
  for (let i = 0; i < length; i++) {
    for (let ch = 0; ch < numChannels; ch++) {
      const sample = audioBuffer.getChannelData(ch)[i];
      const clamped = Math.max(-1, Math.min(1, sample));
      view.setInt16(offset, clamped * 0x7fff, true);
      offset += 2;
    }
  }
  return new Blob([buffer], { type: "audio/wav" });
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++)
    view.setUint8(offset + i, string.charCodeAt(i));
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
```

## 47.16 Python alternative — generate audio with numpy

```python
import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100

def generate_tone(frequency, duration, amplitude=0.5, wave_type="sine"):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    if wave_type == "sine":
        wave = np.sin(2 * np.pi * frequency * t)
    elif wave_type == "square":
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    elif wave_type == "sawtooth":
        wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
    elif wave_type == "triangle":
        wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1

    # Apply fade in/out to avoid clicks
    fade_samples = int(0.01 * SAMPLE_RATE)
    wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
    wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return (wave * amplitude * 32767).astype(np.int16)

def generate_melody(notes, bpm=120):
    """Generate a melody from a list of (note_name, octave, beats) tuples."""
    beat_duration = 60 / bpm  # seconds per beat
    audio = np.array([], dtype=np.int16)

    NOTE_FREQS = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
                  "G": 392.00, "A": 440.00, "B": 493.88}

    for note, octave, beats in notes:
        freq = NOTE_FREQS[note] * (2 ** (octave - 4))
        duration = beat_duration * beats
        tone = generate_tone(freq, duration, wave_type="triangle")
        audio = np.concatenate([audio, tone])

    return audio

# Create a simple melody
melody = [
    ("C", 4, 1), ("E", 4, 1), ("G", 4, 1), ("C", 5, 2),
    ("G", 4, 1), ("E", 4, 1), ("C", 4, 2),
]

audio = generate_melody(melody, bpm=100)
wavfile.write("melody.wav", SAMPLE_RATE, audio)
print("Saved melody.wav")

# Generate white noise (transition whoosh)
def generate_noise(duration, amplitude=0.3):
    samples = int(SAMPLE_RATE * duration)
    noise = np.random.uniform(-1, 1, samples)
    # Apply envelope (fade in, then out)
    envelope = np.concatenate([
        np.linspace(0, 1, samples // 3),
        np.linspace(1, 0, samples - samples // 3),
    ])
    return (noise * envelope * amplitude * 32767).astype(np.int16)

whoosh = generate_noise(0.5)
wavfile.write("whoosh.wav", SAMPLE_RATE, whoosh)
```

## 47.17 Convert WAV to MP3 (using FFmpeg)

```bash
# High quality MP3
ffmpeg -i melody.wav -codec:a libmp3lame -q:a 0 melody.mp3

# Or use pydub in Python:
from pydub import AudioSegment
audio = AudioSegment.from_wav("melody.wav")
audio.export("melody.mp3", format="mp3", bitrate="320k")
```

---

## PART 6: Recipes — Complete YouTube Audio

## 47.18 Intro jingle (3 seconds)

```javascript
import * as Tone from "tone";

async function renderIntroJingle() {
  const buffer = await Tone.Offline(({ transport }) => {
    const synth = new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: "triangle" },
      envelope: { attack: 0.02, decay: 0.3, sustain: 0.1, release: 0.5 },
    }).toDestination();

    const reverb = new Tone.Reverb({ decay: 2, wet: 0.3 }).toDestination();
    synth.connect(reverb);

    // Bright ascending arpeggio
    const notes = ["E4", "G#4", "B4", "E5", "G#5"];
    notes.forEach((note, i) => {
      synth.triggerAttackRelease(note, "16n", i * 0.08);
    });

    // Final chord
    synth.triggerAttackRelease(["E4", "G#4", "B4", "E5"], "2n", 0.5);

    transport.start();
  }, 3);

  return buffer;
}
```

## 47.19 Background loop (30 seconds, loopable)

```javascript
async function renderBackgroundLoop() {
  const buffer = await Tone.Offline(({ transport }) => {
    // Soft pad
    const pad = new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: "sine" },
      envelope: { attack: 2, decay: 1, sustain: 0.6, release: 2 },
    }).toDestination();
    pad.volume.value = -10;

    // Chord progression (4 bars, each 2 beats at 70 BPM)
    const chords = [
      { time: "0:0", notes: ["C3", "E3", "G3", "B3"] },
      { time: "0:2", notes: ["A2", "C3", "E3", "G3"] },
      { time: "1:0", notes: ["F3", "A3", "C4", "E4"] },
      { time: "1:2", notes: ["G3", "B3", "D4", "F4"] },
    ];

    chords.forEach(({ time, notes }) => {
      pad.triggerAttackRelease(notes, "1n", Tone.Time(time).toSeconds());
    });

    transport.bpm.value = 70;
    transport.start();
  }, 30);

  return buffer;
}
```

## 47.20 Transition sound (scene change)

```javascript
async function renderTransitionSound() {
  const buffer = await Tone.Offline(() => {
    // Reverse cymbal (riser)
    const noise = new Tone.NoiseSynth({
      noise: { type: "white" },
      envelope: { attack: 0.8, decay: 0.1, sustain: 0, release: 0.1 },
    }).toDestination();

    const filter = new Tone.Filter({ frequency: 2000, type: "bandpass" }).toDestination();
    noise.connect(filter);
    noise.triggerAttackRelease("1n", 0);

    // Impact at the end
    const impact = new Tone.MembraneSynth({
      pitchDecay: 0.05, octaves: 4, envelope: { attack: 0.001, decay: 0.5, sustain: 0 },
    }).toDestination();
    impact.triggerAttackRelease("C1", "8n", 0.9);
  }, 1.5);

  return buffer;
}
```

---

## Summary

✅ Audio fundamentals: frequency, amplitude, waveforms (sine/square/saw/triangle)
✅ Web Audio API: oscillators, gain nodes, filters, envelope shaping
✅ Sound effects: click, success, error, notification, whoosh, impact, riser, explosion, laser, coin
✅ Tone.js: synths, sequences, drum patterns, chord progressions, arpeggios
✅ Effects chain: reverb, delay, distortion, EQ, compression
✅ Background music: looping pads + chords + arpeggios (I-V-vi-IV progression)
✅ Exporting: Tone.Offline rendering → WAV → MP3 (FFmpeg or pydub)
✅ Python alternative: numpy waveform generation, scipy.io.wavfile
✅ YouTube recipes: intro jingle, background loop, transition sounds

## Key takeaways

**All sound effects are just frequency + amplitude + time.** A "whoosh" is a noise burst with a rising bandpass filter. An "impact" is a low-frequency sine with fast attack. A "coin" is two quick high-pitched square wave notes. Once you understand this, you can design any sound.

**Tone.js is the music framework.** Web Audio API is low-level (individual oscillators, gain nodes, filters). Tone.js gives you musical abstractions: notes ("C4"), durations ("8n"), tempo (BPM), sequences, synths with ADSR envelopes. Use Tone.js for music, raw Web Audio for simple effects.

**Export with Offline rendering.** `Tone.Offline()` renders audio as fast as the CPU allows (not real-time). You get an AudioBuffer you can convert to WAV. Then FFmpeg converts to MP3. This is how you generate YouTube audio programmatically.

**You own everything you synthesize.** No licensing, no attribution, no copyright claims. Every sound in this chapter is generated from math — it's 100% yours to use commercially.

---

→ [Back to Chapter 46: FFmpeg](./46-FFMPEG.md)
