# Canvas Basics

[prev: Overview](./chapter-00-overview.md) | [next: Game Loop](./chapter-02-game-loop.md)

The HTML Canvas API is the foundation of all 2D browser games. Even frameworks like Phaser use it under the hood. Understanding it gives you full control.

## Setting Up the Canvas

```typescript
const canvas = document.getElementById("game") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;

// Set internal resolution (small for pixel art)
canvas.width = 160;
canvas.height = 144;
```

The canvas has two sizes:

- **Internal resolution** (`canvas.width/height`) — the actual pixel grid you draw on
- **Display size** (CSS `width/height`) — how large it appears on screen

## Pixel-Perfect Rendering

```css
canvas {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  width: 640px;
  height: 576px;
  display: block;
}
```

Also disable smoothing in JavaScript:

```typescript
ctx.imageSmoothingEnabled = false;
```

## Drawing Primitives

```typescript
// Single pixel
ctx.fillStyle = "#ff0000";
ctx.fillRect(10, 10, 1, 1);

// Rectangle
ctx.fillStyle = "#00ff00";
ctx.fillRect(20, 20, 8, 8);

// Outline
ctx.strokeStyle = "#0000ff";
ctx.lineWidth = 1;
ctx.strokeRect(30, 30, 16, 16);

// Clear a region
ctx.clearRect(20, 20, 8, 8);
```

## Drawing Pixel Art from Arrays

Define sprites as 2D arrays:

```typescript
const heart = [
  [0, 1, 1, 0, 1, 1, 0],
  [1, 1, 1, 1, 1, 1, 1],
  [1, 1, 1, 1, 1, 1, 1],
  [0, 1, 1, 1, 1, 1, 0],
  [0, 0, 1, 1, 1, 0, 0],
  [0, 0, 0, 1, 0, 0, 0],
];

const palette = ["transparent", "#e94560"];

function drawSprite(data: number[][], x: number, y: number) {
  for (let row = 0; row < data.length; row++) {
    for (let col = 0; col < data[row].length; col++) {
      const color = palette[data[row][col]];
      if (color === "transparent") continue;
      ctx.fillStyle = color;
      ctx.fillRect(x + col, y + row, 1, 1);
    }
  }
}

drawSprite(heart, 10, 10);
```

## ImageData for Direct Pixel Access

For maximum performance, manipulate pixels directly:

```typescript
const imageData = ctx.createImageData(canvas.width, canvas.height);
const pixels = imageData.data; // Uint8ClampedArray [R,G,B,A, ...]

function setPixel(x: number, y: number, r: number, g: number, b: number) {
  const i = (y * canvas.width + x) * 4;
  pixels[i] = r;
  pixels[i + 1] = g;
  pixels[i + 2] = b;
  pixels[i + 3] = 255;
}

for (let x = 0; x < canvas.width; x++) {
  for (let y = 0; y < canvas.height; y++) {
    setPixel(x, y, x, y, 128);
  }
}
ctx.putImageData(imageData, 0, 0);
```

```
Memory layout of ImageData:
+---+---+---+---+---+---+---+---+
| R | G | B | A | R | G | B | A |  ...
+---+---+---+---+---+---+---+---+
|   pixel 0     |   pixel 1     |
```

## Loading and Drawing Images

```typescript
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

async function main() {
  const playerImg = await loadImage("player.png");

  // Draw full image
  ctx.drawImage(playerImg, 10, 10);

  // Draw a sub-region (sprite from sheet)
  // drawImage(img, srcX, srcY, srcW, srcH, destX, destY, destW, destH)
  ctx.drawImage(playerImg, 0, 0, 16, 16, 50, 50, 16, 16);
}
main();
```

## The Basic Game Loop

```typescript
let playerX = 80;
let lastTime = performance.now();

function gameLoop(currentTime: number) {
  const dt = (currentTime - lastTime) / 1000;
  lastTime = currentTime;

  // Update
  playerX += 60 * dt;
  if (playerX > canvas.width) playerX = 0;

  // Render
  ctx.fillStyle = "#1a1a2e";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#e94560";
  ctx.fillRect(Math.floor(playerX), 72, 8, 8);

  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

Use `Math.floor()` when drawing to keep pixels aligned to the grid. Sub-pixel positions cause blurry rendering.

## Key Takeaways

- Use a small canvas (128x128, 160x144, 320x240) and scale with CSS
- Always set `image-rendering: pixelated` and `imageSmoothingEnabled = false`
- Use `Math.floor()` for pixel-perfect positioning
- `requestAnimationFrame` is your game loop driver
- `drawImage` with source rect lets you slice sprite sheets

[prev: Overview](./chapter-00-overview.md) | [next: Game Loop](./chapter-02-game-loop.md)
