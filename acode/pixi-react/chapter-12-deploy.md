# Chapter 12: Deploy — "Ship It to GitHub Pages"

[← Chapter 11: Levels & Scenes](chapter-11-levels-scenes.md)

---

## The Crisis

The jam deadline is in 3 hours. The game works on localhost. But nobody can play it until it's live on the internet. You need to build, deploy, and verify — fast.

Kai: "Just put it somewhere people can play it in a browser. GitHub Pages? It's free, right?"

Free. Static. Perfect for a Vite build.

## Vite Production Build

First, configure Vite for GitHub Pages. The key issue: GitHub Pages serves your site at `https://username.github.io/dungeonbit/`, not at the root. Asset paths need to account for this.

### vite.config.js

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/dungeonbit/',  // ← your repo name
  build: {
    outDir: 'dist',
    assetsInlineLimit: 0,  // don't inline any assets (keep sprites as files)
  },
});
```

The `base` option prepends `/dungeonbit/` to all asset URLs in the build. Without it, your sprites would 404.

## Asset Path Handling

With `base` set, Vite handles paths in your code automatically:

```jsx
// These work in both dev and production:
<Sprite image="./sprites/knight.png" />

// For dynamic paths, use the public directory:
// Files in public/ are served as-is at the base URL
// public/sprites/knight.png → /dungeonbit/sprites/knight.png (in prod)
// public/audio/coin.wav → /dungeonbit/audio/coin.wav (in prod)
```

For programmatic asset loading:

```jsx
// ✅ Works with Vite's base path
PIXI.Assets.load('./sprites/knight_sheet.json');

// ✅ Also works — Vite resolves relative paths
import knightSheet from '/sprites/knight_sheet.json?url';
PIXI.Assets.load(knightSheet);
```

## Build and Test Locally

```bash
npm run build
npm run preview
```

`npm run preview` serves the `dist/` folder locally with the correct base path. Open `http://localhost:4173/dungeonbit/` and verify everything works.

### Common Build Issues

| Problem | Fix |
|---|---|
| Sprites 404 | Check `base` in vite.config.js matches your repo name |
| Audio files missing | Put them in `public/audio/`, not `src/` |
| JSON spritesheets 404 | Put them in `public/sprites/` alongside the PNGs |
| Blank screen | Check browser console for path errors |
| Canvas not rendering | Ensure pixi.js is bundled (check `dist/assets/`) |

## GitHub Repository Setup

```bash
git init
git add .
git commit -m "DungeonBit - game jam submission"
git remote add origin https://github.com/yourusername/dungeonbit.git
git branch -M main
git push -u origin main
```

## GitHub Actions: Auto-Deploy on Push

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

### Enable GitHub Pages

1. Go to your repo → Settings → Pages
2. Source: **GitHub Actions**
3. Push to main → the workflow runs → site is live

Your game is now at: `https://yourusername.github.io/dungeonbit/`

## Performance Checklist

Before shipping, verify these:

### Rendering Performance

- [ ] **SCALE_MODES.NEAREST** set globally (no blurry scaling)
- [ ] **antialias: false** on Stage (saves GPU work)
- [ ] **Tile culling** enabled (only render visible tiles)
- [ ] **useRef** for frame-by-frame updates (not useState)
- [ ] **useMemo** on tile arrays and animation frame lists
- [ ] **Particles cleaned up** when they die (no memory leak)

### Asset Optimization

- [ ] Sprites are small PNGs (16×16 or 32×32 source)
- [ ] Spritesheets pack multiple sprites into one file (fewer HTTP requests)
- [ ] Audio files are compressed (WAV for short SFX, MP3/OGG for music)
- [ ] No unused assets in `public/`

### Bundle Size

```bash
# Check what's in your bundle
npm run build
ls -la dist/assets/
```

Expected sizes for a pixel art game:
- JavaScript bundle: ~200-400KB (pixi.js + React + your code)
- Sprites: ~50-200KB total (pixel art is tiny)
- Audio: ~500KB-2MB (depends on music length)
- Total: under 3MB for a jam game

### Mobile/Touch

- [ ] Touch events work (pointer events handle this)
- [ ] Canvas scales to fit mobile screens
- [ ] No scroll/zoom on mobile (add meta viewport tag)

Add to `index.html`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

## Responsive Canvas Scaling

Make the canvas fill the screen while maintaining aspect ratio:

```css
/* src/index.css */
body {
  margin: 0;
  background: #0a0a0a;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  overflow: hidden;
}

canvas {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  max-width: 100vw;
  max-height: 100vh;
  width: auto;
  height: auto;
  aspect-ratio: 480 / 320;
}
```

Or scale dynamically with JavaScript:

```jsx
function useCanvasScale() {
  useEffect(() => {
    function resize() {
      const canvas = document.querySelector('canvas');
      if (!canvas) return;

      const scaleX = window.innerWidth / 480;
      const scaleY = window.innerHeight / 320;
      const scale = Math.min(scaleX, scaleY);

      canvas.style.width = `${Math.floor(480 * scale)}px`;
      canvas.style.height = `${Math.floor(320 * scale)}px`;
    }

    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);
}
```

## Final Project Structure

```
dungeonbit/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── public/
│   ├── sprites/
│   │   ├── knight_sheet.png
│   │   ├── knight_sheet.json
│   │   ├── slime_sheet.png
│   │   ├── slime_sheet.json
│   │   ├── tiles.png
│   │   ├── tiles.json
│   │   ├── heart.png
│   │   ├── coin.png
│   │   ├── key.png
│   │   └── chest.png
│   └── audio/
│       ├── coin.wav
│       ├── hit.wav
│       ├── key.wav
│       ├── door.wav
│       ├── death.wav
│       ├── step.wav
│       ├── attack.wav
│       └── dungeon_loop.mp3
├── src/
│   ├── components/
│   │   ├── Player.jsx
│   │   ├── Enemy.jsx
│   │   ├── Tilemap.jsx
│   │   ├── HUD.jsx
│   │   ├── HealthBar.jsx
│   │   └── Particle.jsx
│   ├── hooks/
│   │   ├── useKeyboard.js
│   │   ├── useGameState.js
│   │   ├── useSound.js
│   │   ├── useScreenShake.js
│   │   └── useCollision.js
│   ├── scenes/
│   │   ├── TitleScreen.jsx
│   │   ├── Gameplay.jsx
│   │   ├── GameOverScreen.jsx
│   │   └── VictoryScreen.jsx
│   ├── data/
│   │   ├── levels.js
│   │   └── constants.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
├── package.json
└── README.md
```

## What We Built

Over 12 chapters, you and Kai built **DungeonBit** — a complete pixel art dungeon crawler:

| Feature | Chapter |
|---|---|
| Vite + React + PixiJS setup | 0 |
| Sprite rendering with crispy pixels | 1 |
| Scene organization with containers | 2 |
| Programmatic shapes (health bars, UI) | 3 |
| Game loop with useTick | 4 |
| Spritesheet animation (walk cycles) | 5 |
| Keyboard + touch controls | 6 |
| Tile-based dungeon rendering | 7 |
| Collision detection (walls, items, enemies) | 8 |
| Game state (health, score, inventory) | 9 |
| Sound effects + particles + screen shake | 10 |
| Multiple levels + scene management | 11 |
| GitHub Pages deployment | 12 |

## What's Next

The jam is over. You submitted. But if you want to keep going:

- **Pathfinding** — make enemies chase the player (A* algorithm)
- **Procedural generation** — random dungeon layouts
- **Save/load** — localStorage for progress
- **Multiplayer** — WebSocket co-op (ambitious but possible)
- **Mobile app** — wrap in Capacitor for iOS/Android
- **Migrate to v8** — when React 19 is your default, try `@pixi/react@8`

## The Jam Results

Kai texts you at 3am: "Submitted. 47 minutes to spare."

You refresh the jam page. DungeonBit is live. People are playing it. Someone left a comment: "Crispy pixels. Tight controls. Fun."

You built a game. With React. In 48 hours.

Not bad for a web developer.

---

[← Chapter 11: Levels & Scenes](chapter-11-levels-scenes.md)
