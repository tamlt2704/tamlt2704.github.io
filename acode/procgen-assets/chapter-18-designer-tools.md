# Chapter 18: Designer Tools

[← Ch 17](chapter-17-export.md) | [Ch 19 →](chapter-19-world-generation.md)

---

## Juno's Request

> "I can't tweak parameters by editing code. I need sliders. Live preview. A seed browser showing 20 variations at once. Save presets. This is my workflow — generate, tweak, compare, save."

---

## Parameter UI with lil-gui

```typescript
import GUI from 'lil-gui';

interface PlanetParams {
  seed: string; scale: number; octaves: number;
  persistence: number; waterLevel: number; biomeType: string; size: number;
}

const params: PlanetParams = {
  seed: 'drift-42', scale: 0.03, octaves: 5,
  persistence: 0.5, waterLevel: 0.4, biomeType: 'earth', size: 128,
};

function setupGUI(onUpdate: () => void): GUI {
  const gui = new GUI({ title: 'Planet Generator' });
  gui.add(params, 'seed').onChange(onUpdate);
  gui.add(params, 'scale', 0.005, 0.08, 0.001).onChange(onUpdate);
  gui.add(params, 'octaves', 1, 8, 1).onChange(onUpdate);
  gui.add(params, 'persistence', 0.1, 0.9, 0.05).onChange(onUpdate);
  gui.add(params, 'waterLevel', 0.1, 0.7, 0.05).onChange(onUpdate);
  gui.add(params, 'biomeType', ['earth','desert','ice','toxic','alien']).onChange(onUpdate);
  return gui;
}
```

---

## Live Preview

```typescript
const previewCanvas = document.createElement('canvas');
previewCanvas.width = 256; previewCanvas.height = 256;
previewCanvas.style.imageRendering = 'pixelated';
const previewCtx = previewCanvas.getContext('2d')!;

let timeout: number;
function debouncedUpdate(): void {
  clearTimeout(timeout);
  timeout = window.setTimeout(() => {
    const texture = generatePlanetTexture(params.seed, params.size);
    previewCtx.imageSmoothingEnabled = false;
    previewCtx.clearRect(0, 0, 256, 256);
    previewCtx.drawImage(texture, 0, 0, 256, 256);
  }, 50);
}

const gui = setupGUI(debouncedUpdate);
```

---

## Seed Browser

Grid of variations — same params, different seeds:

```typescript
function renderSeedBrowser(container: HTMLElement, baseParams: PlanetParams, count = 20): void {
  container.innerHTML = '';
  container.style.display = 'grid';
  container.style.gridTemplateColumns = 'repeat(5, 1fr)';
  container.style.gap = '4px';

  for (let i = 0; i < count; i++) {
    const seed = `${baseParams.seed}-var-${i}`;
    const texture = generatePlanetTexture(seed, 64);
    const display = document.createElement('canvas');
    display.width = 64; display.height = 64;
    display.style.width = '80px'; display.style.cursor = 'pointer';
    display.style.imageRendering = 'pixelated';
    display.getContext('2d')!.drawImage(texture, 0, 0);

    display.addEventListener('click', () => {
      params.seed = seed;
      gui.controllers.forEach(c => c.updateDisplay());
      debouncedUpdate();
    });
    container.appendChild(display);
  }
}
```

---

## Preset System

```typescript
interface Preset { name: string; params: PlanetParams; timestamp: number; }

class PresetManager {
  private key = 'procgen-presets';
  save(name: string, p: PlanetParams): void {
    const all = this.loadAll();
    all.push({ name, params: {...p}, timestamp: Date.now() });
    localStorage.setItem(this.key, JSON.stringify(all));
  }
  loadAll(): Preset[] { return JSON.parse(localStorage.getItem(this.key) || '[]'); }
  load(name: string): PlanetParams | null {
    return this.loadAll().find(p => p.name === name)?.params || null;
  }
}
```

---

## Designer Workflow Layout

```
┌──────────────┬──────────────────────────┬───────────────────────┐
│ PARAMETERS   │      LIVE PREVIEW        │    SEED BROWSER       │
│              │                          │                       │
│ Seed: ______ │    ┌──────────────┐      │  ┌──┐┌──┐┌──┐┌──┐  │
│ Scale: ═══●  │    │   Generated  │      │  │  ││  ││  ││  │  │
│ Octaves: 5   │    │    Planet    │      │  └──┘└──┘└──┘└──┘  │
│ Water: ══●   │    │   Preview    │      │  ┌──┐┌──┐┌──┐┌──┐  │
│ Biome: [▼]   │    └──────────────┘      │  │  ││  ││  ││  │  │
│              │                          │  └──┘└──┘└──┘└──┘  │
│ PRESETS      │    Gen time: 12ms        │                       │
│ [Save] [Load]│                          │  [Regenerate All]     │
├──────────────┴──────────────────────────┴───────────────────────┤
│ [Export PNG]  [Copy Seed]  [Randomize]                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Keyboard Shortcuts

```typescript
document.addEventListener('keydown', (e) => {
  if (e.key === 'r' && !e.ctrlKey) {
    params.seed = `drift-${Math.floor(Math.random()*99999)}`;
    gui.controllers.forEach(c => c.updateDisplay());
    debouncedUpdate();
  }
  if (e.key === 's' && e.ctrlKey) {
    e.preventDefault();
    presetManager.save(`auto-${Date.now()}`, params);
  }
});
```

---

## Performance Display

```typescript
function timedUpdate(): void {
  const start = performance.now();
  const texture = generatePlanetTexture(params.seed, params.size);
  const ms = performance.now() - start;
  previewCtx.drawImage(texture, 0, 0, 256, 256);
  timeDisplay.textContent = `${ms.toFixed(1)}ms`;
  timeDisplay.style.color = ms > 16 ? '#f44' : ms > 8 ? '#fa4' : '#4f4';
}
```

---

## Parameter Tuning

| Feature | Implementation | Notes |
|---------|---------------|-------|
| Sliders | `gui.add(obj, prop, min, max, step)` | Real-time |
| Dropdowns | `gui.add(obj, prop, options)` | Enum params |
| Debounce | 50ms timeout | Prevents lag during drag |
| Presets | localStorage JSON | Persist across sessions |
| Shortcuts | R=randomize, Ctrl+S=save | Fast workflow |

**Juno's workflow:**

> "Randomize until interesting. Fine-tune with sliders. Save preset. The seed browser is the killer feature — 20 options at once beats clicking randomize one at a time."

---

## Exercises

1. **Comparison mode:** Lock current preview on left, new generation on right. A/B test changes.

2. **History/undo:** Store last 20 states. Ctrl+Z/Y navigates. Show timeline thumbnails.

3. **Export presets:** Download all presets as JSON. Import button merges with existing.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| lil-gui | Lightweight parameter UI |
| Live preview | Regenerate on change (debounced) |
| Seed browser | Grid of small previews, click to select |
| Presets | Save/load to localStorage |
| Timing | Show generation time, color by budget |

---

[← Ch 17](chapter-17-export.md) | [Ch 19 →](chapter-19-world-generation.md)
