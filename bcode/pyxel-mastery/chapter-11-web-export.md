# Chapter 11 — Publishing to Web

## How It Works

Pyxel compiles your game to WebAssembly (WASM) and packages it as a single HTML file that runs in any browser. No server needed — just static file hosting.

## Step 1: Package Your Game

```bash
# From your game directory
pyxel package . main.py
```

This creates `main.pyxapp` — a bundled Pyxel application containing your code and resources.

Structure expected:

```
my_game/
├── main.py          # entry point
├── assets.pyxres    # resources (if any)
└── other_module.py  # additional files (if any)
```

## Step 2: Convert to HTML

```bash
pyxel app2html main.pyxapp
```

This produces `main.html` — a self-contained file with your game embedded.

## Step 3: Host It

**GitHub Pages (free):**

```bash
mkdir docs
cp main.html docs/index.html
git add docs/
git commit -m "Add web build"
git push
# Enable GitHub Pages from Settings → Pages → Source: /docs
```

**Netlify / Vercel:**
Just drag the HTML file into their dashboard.

**itch.io:**
1. Go to itch.io → Dashboard → Create new project
2. Kind of project: HTML
3. Upload a zip containing your `index.html`
4. Set viewport to 160x120 (or your game resolution × scale)

## One-Liner

```bash
pyxel package . main.py && pyxel app2html main.pyxapp
```

## Custom HTML Wrapper

The generated HTML is self-contained but basic. You can wrap it:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Pyxel Game</title>
    <style>
        body {
            background: #1a1c2c;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        canvas {
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }
    </style>
</head>
<body>
    <!-- Embed the pyxel app -->
    <script src="https://cdn.jsdelivr.net/gh/kitao/pyxel/wasm/pyxel.js"></script>
    <pyxel-run root="." name="main.pyxapp"></pyxel-run>
</body>
</html>
```

## Sharing via Pyxel's CDN

You can also host `.pyxapp` files and load them directly:

```html
<script src="https://cdn.jsdelivr.net/gh/kitao/pyxel/wasm/pyxel.js"></script>
<pyxel-run root="https://your-site.com/games/" name="main.pyxapp"></pyxel-run>
```

## Limitations on Web

- No file system access (can't save to disk — use browser localStorage via JS interop if needed)
- Sound may require user interaction to start (browser autoplay policy)
- Performance is slightly lower than native
- Gamepad support depends on browser

## Testing Locally

```bash
# Python's built-in server
python -m http.server 8000
# Open http://localhost:8000/main.html
```

## Running .pyxapp Natively

```bash
pyxel play main.pyxapp
```

## Full Workflow

```bash
# 1. Develop
python main.py

# 2. Package
pyxel package . main.py

# 3. Test packaged version
pyxel play main.pyxapp

# 4. Export to web
pyxel app2html main.pyxapp

# 5. Test in browser
python -m http.server 8000

# 6. Deploy
cp main.html /path/to/your/site/index.html
```

## Exercise

Take any game from previous chapters and:
1. Package it as a `.pyxapp`
2. Export to HTML
3. Host it (GitHub Pages or just test locally)

## Next

Chapter 12: Building a complete Space Shooter game from scratch.
