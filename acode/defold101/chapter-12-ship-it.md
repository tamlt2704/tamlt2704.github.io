# Chapter 12: Ship It — "Before the Deadline"

[← Chapter 11: Performance](chapter-11-performance.md)

---

## The Crisis

The jam clock reads 08:00:00. The game works. It's fun. Mika's art is beautiful. The boss explodes in a cascade of fireballs. But it's running on your laptop. It needs to be on itch.io in 8 hours.

"Bundle it. Upload it. Submit it. Then sleep."

## HTML5 Build (Web)

The fastest path to "playable by anyone with a browser":

### From the Editor

1. Project → Bundle → HTML5 Application
2. Choose output folder
3. Click Bundle

You get:
```
space-survivor-html5/
├── index.html
├── dmloader.js          ← Defold's loader
├── space-survivor.wasm  ← compiled game (WebAssembly)
└── archive/             ← game data (textures, sounds, scripts)
```

Total size: **~2-3MB**. Compare that to a React app.

### Customizing the HTML Shell

The default `index.html` is bare. Customize it:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Space Survivor</title>
    <style>
        body { margin: 0; background: #000; overflow: hidden; }
        #game-container { width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; }
        #game-canvas { max-width: 100%; max-height: 100%; }
    </style>
</head>
<body>
    <div id="game-container">
        <canvas id="game-canvas"></canvas>
    </div>
    <script src="dmloader.js"></script>
    <script>
        var extra_params = {
            archive_location_filter: function(path) { return "archive/" + path; },
            engine_arguments: ["--verify-graphics-calls=false"],
            splash_image: "splash.png",
            custom_heap_size: 268435456,
        };
        Module.canvas = document.getElementById("game-canvas");
    </script>
</body>
</html>
```

## Upload to itch.io

1. Create an account on [itch.io](https://itch.io)
2. Dashboard → Create new project
3. Settings:
   - **Kind of project**: HTML
   - **Embed options**: Click to play, Fullscreen button
   - **Viewport dimensions**: 960 × 540
4. Upload the HTML5 bundle as a zip
5. Check "This file will be played in the browser"
6. Save & view page

Your game is live. Anyone with a browser can play it.

## Mobile Builds

### Android

1. Project → Bundle → Android Application
2. You need a **keystore** for signing:

```bash
keytool -genkey -v -keystore space-survivor.keystore -alias game -keyalg RSA -keysize 2048 -validity 10000
```

3. In bundle settings:
   - Keystore: `space-survivor.keystore`
   - Keystore password: (your password)
   - Key password: (your password)

4. Bundle → produces `space-survivor.apk`

APK size: **~2MB**. Yes, really.

### iOS

1. Project → Bundle → iOS Application
2. Requires:
   - macOS
   - Apple Developer account ($99/year)
   - Provisioning profile + signing certificate
3. Bundle → produces `.ipa`
4. Upload via Xcode or Transporter

## Desktop Builds

```
Project → Bundle → macOS Application  → .app bundle
Project → Bundle → Windows Application → .exe + .dll
Project → Bundle → Linux Application   → binary
```

All under 5MB.

## Command-Line Builds (CI/CD)

For automated builds, use **Bob** (Defold's build tool):

```bash
# Download Bob
curl -L https://github.com/defold/defold/releases/download/1.9.0/bob.jar -o bob.jar

# Build HTML5
java -jar bob.jar --platform=js-web --archive bundle

# Build Android
java -jar bob.jar --platform=armv7-android --archive bundle \
  --keystore=space-survivor.keystore \
  --keystore-pass=password

# Build Windows
java -jar bob.jar --platform=x86_64-win32 --archive bundle
```

## GitHub Actions for Auto-Build

```yaml
# .github/workflows/build.yml
name: Build Game

on:
  push:
    tags: ["v*"]

jobs:
  build-html5:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: 17
          distribution: temurin

      - name: Download Bob
        run: curl -L https://github.com/defold/defold/releases/download/1.9.0/bob.jar -o bob.jar

      - name: Build HTML5
        run: java -jar bob.jar --platform=js-web --archive bundle

      - name: Upload to itch.io
        uses: manleydev/butler-publish-itchio-action@master
        env:
          BUTLER_CREDENTIALS: ${{ secrets.BUTLER_API_KEY }}
          CHANNEL: html5
          ITCH_GAME: space-survivor
          ITCH_USER: your-username
          PACKAGE: build/default/space-survivor
```

## Game Settings for Release

Update `game.project` for production:

```ini
[project]
title = Space Survivor
version = 1.0.0

[display]
width = 960
height = 540
fullscreen = 0
update_frequency = 60

[html5]
show_fullscreen_button = 1
show_made_with_defold = 1
scale_mode = fit

[android]
package = com.yourname.spacesurvivor
minimum_sdk_version = 21

[ios]
bundle_identifier = com.yourname.spacesurvivor

[sound]
gain = 1.0

[profiler]
track_cpu = 0
```

## The Jam Submission

itch.io jam submission checklist:

| Item | Status |
|---|---|
| Game runs in browser | ✓ |
| Controls explained on page | ✓ |
| Screenshots (3+) | ✓ |
| Cover image (630×500) | ✓ |
| Description with theme connection | ✓ |
| Credits (Mika's art, sound sources) | ✓ |
| Source code link (optional) | ✓ |

## What You Built in 72 Hours

```
Space Survivor
├── 3 levels + boss fight
├── Player movement + shooting
├── Collision system
├── Animated sprites + explosions
├── Message-based architecture
├── GUI (HUD + menus)
├── Camera with parallax + shake
├── Sound effects + music
├── Level loading/unloading
├── Object pooling
├── Published on itch.io
└── Total size: 2.1MB
```

## What You Learned

| Chapter | Concept | Web Equivalent |
|---|---|---|
| 0 | Editor + project structure | VS Code + package.json |
| 1 | Game objects + sprites + atlases | DOM elements + images + sprite sheets |
| 2 | Lua scripting + input + update loop | JavaScript + event listeners + rAF |
| 3 | Factories (runtime spawning) | createElement + appendChild |
| 4 | Collision objects + groups/masks | Intersection Observer + event delegation |
| 5 | Flip-book animation + tweening | CSS @keyframes + transitions |
| 6 | Message passing | Custom events + postMessage |
| 7 | GUI system | Fixed-position HTML overlay |
| 8 | Camera + parallax | CSS transforms + scroll effects |
| 9 | Sound components + groups | Web Audio API |
| 10 | Collection proxies (level loading) | React Router + lazy loading |
| 11 | Profiler + optimization | Chrome DevTools + performance |
| 12 | Multi-platform builds + deploy | Webpack + CI/CD |

## The Jam Results

You submit with 45 minutes to spare. Mika high-fives you. You sleep for 14 hours.

A week later, the jam results come in. You didn't win. But you placed in the top 20%. People left comments: "Smooth controls." "Love the boss fight." "How is this only 2MB?"

More importantly: you shipped a game. From zero game dev experience to a published, playable game in 72 hours. The engine is 5MB. The game is 2MB. It runs everywhere.

Mika texts: "Next jam is in 3 weeks. I have an idea for a roguelike..."

You say yes. This time, you know what you're doing.

---

[← Chapter 11: Performance](chapter-11-performance.md)
