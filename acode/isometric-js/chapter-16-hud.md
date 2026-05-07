# Chapter 16: HUD

[← Chapter 15: Lighting](chapter-15-lighting.md) | [Chapter 17: Save & Load →](chapter-17-save-load.md)

---

## The Task

Riku opens the game and asks: "How much money do I have? How many people live here? Where's the build menu?" The game has no UI. No feedback. No information layer.

You need a HUD — heads-up display. Resource counters, a build menu, tooltips. The question: draw it on canvas, or use HTML overlaid on top?

## HTML Overlay vs Canvas-Drawn UI

Both approaches work. Here's the tradeoff:

| Approach | Pros | Cons |
|----------|------|------|
| **HTML overlay** | Native text rendering, accessibility, CSS styling, easy buttons | Harder to sync with canvas animations |
| **Canvas-drawn** | Pixel-perfect control, no DOM overhead, unified render pipeline | Manual text layout, no native accessibility |

For a game jam, the pragmatic choice: **HTML for menus and text, canvas for in-world indicators** (health bars, selection rings).

```html
<!-- index.html -->
<div id="game-container" style="position: relative; width: 960px; height: 640px;">
  <canvas id="game-canvas" width="960" height="640"></canvas>

  <!-- HUD overlay (positioned above canvas) -->
  <div id="hud" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
    <div id="resource-bar"></div>
    <div id="build-menu" style="pointer-events: auto;"></div>
    <div id="tooltip"></div>
  </div>
</div>
```

The key CSS: `pointer-events: none` on the HUD container lets clicks pass through to the canvas. Individual interactive elements get `pointer-events: auto`.

## Resource Bar

Display money, population, and power at the top of the screen:

```typescript
// src/ui/resource-bar.ts
export interface Resources {
  money: number;
  population: number;
  maxPopulation: number;
  power: number;
  maxPower: number;
}

export class ResourceBar {
  private element: HTMLElement;

  constructor(container: HTMLElement) {
    this.element = document.createElement('div');
    this.element.id = 'resource-bar';
    this.element.style.cssText = `
      position: absolute;
      top: 8px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 24px;
      padding: 8px 16px;
      background: rgba(0, 0, 0, 0.7);
      border-radius: 6px;
      font-family: monospace;
      font-size: 14px;
      color: #fff;
      pointer-events: none;
    `;
    container.appendChild(this.element);
  }

  update(resources: Resources) {
    this.element.innerHTML = `
      <span style="color: #ffd700;">💰 ${this.formatNumber(resources.money)}</span>
      <span style="color: #90ee90;">👥 ${resources.population}/${resources.maxPopulation}</span>
      <span style="color: #87ceeb;">⚡ ${resources.power}/${resources.maxPower}</span>
    `;
  }

  private formatNumber(n: number): string {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
    if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
    return n.toString();
  }
}
```

## Build Menu Panel

A panel at the bottom with building icons. Click one to enter build mode:

```typescript
// src/ui/build-menu.ts
export class BuildMenu {
  private element: HTMLElement;
  private onSelect: (building: BuildingDef) => void;

  constructor(container: HTMLElement, buildings: BuildingDef[], onSelect: (b: BuildingDef) => void) {
    this.onSelect = onSelect;

    this.element = document.createElement('div');
    this.element.style.cssText = `
      position: absolute;
      bottom: 12px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 8px;
      padding: 8px 12px;
      background: rgba(0, 0, 0, 0.8);
      border-radius: 8px;
      pointer-events: auto;
    `;

    for (const building of buildings) {
      const btn = this.createButton(building);
      this.element.appendChild(btn);
    }

    container.appendChild(this.element);
  }

  private createButton(building: BuildingDef): HTMLElement {
    const btn = document.createElement('button');
    btn.style.cssText = `
      width: 56px;
      height: 56px;
      border: 2px solid #555;
      border-radius: 6px;
      background: #222;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: border-color 0.15s;
    `;

    // Building icon (scaled-down sprite)
    const icon = document.createElement('img');
    icon.src = building.iconUrl;
    icon.style.cssText = 'width: 36px; height: 36px; image-rendering: pixelated;';
    icon.alt = building.name;

    // Cost label
    const cost = document.createElement('span');
    cost.textContent = `$${building.cost}`;
    cost.style.cssText = 'font-size: 9px; color: #ffd700; font-family: monospace;';

    btn.appendChild(icon);
    btn.appendChild(cost);

    btn.addEventListener('mouseenter', () => {
      btn.style.borderColor = '#88f';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.borderColor = '#555';
    });
    btn.addEventListener('click', () => {
      this.onSelect(building);
      this.highlightButton(btn);
    });

    return btn;
  }

  private highlightButton(active: HTMLElement) {
    for (const child of this.element.children) {
      (child as HTMLElement).style.borderColor = '#555';
    }
    active.style.borderColor = '#4f4';
  }

  deselect() {
    for (const child of this.element.children) {
      (child as HTMLElement).style.borderColor = '#555';
    }
  }
}
```

## Tooltip on Hover

When the player hovers over a building in the world, show a tooltip with info:

```typescript
// src/ui/tooltip.ts
export class Tooltip {
  private element: HTMLElement;
  private visible = false;

  constructor(container: HTMLElement) {
    this.element = document.createElement('div');
    this.element.style.cssText = `
      position: absolute;
      padding: 6px 10px;
      background: rgba(0, 0, 0, 0.85);
      border: 1px solid #666;
      border-radius: 4px;
      font-family: monospace;
      font-size: 12px;
      color: #fff;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.15s;
      white-space: nowrap;
      z-index: 100;
    `;
    container.appendChild(this.element);
  }

  show(screenX: number, screenY: number, text: string) {
    this.element.textContent = text;
    this.element.style.left = `${screenX + 12}px`;
    this.element.style.top = `${screenY - 30}px`;
    this.element.style.opacity = '1';
    this.visible = true;
  }

  hide() {
    if (!this.visible) return;
    this.element.style.opacity = '0';
    this.visible = false;
  }
}

// Usage in game loop:
function onMouseMove(screenX: number, screenY: number) {
  const { gridX, gridY } = screenToGrid(screenX, screenY, camera);
  const building = grid.getBuildingAt(gridX, gridY);

  if (building) {
    tooltip.show(screenX, screenY, `${building.def.name} (${building.def.width}×${building.def.height})`);
  } else {
    tooltip.hide();
  }
}
```

## Screen Space vs World Space

The critical distinction:

```
┌─────────────────────────────────────────────┐
│  SCREEN SPACE (fixed position)              │
│  ┌─────────────────────────────────────┐    │
│  │  💰 5,000  👥 12/50  ⚡ 8/20       │    │  ← Resource bar
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │                                     │    │
│  │     WORLD SPACE (moves with camera) │    │
│  │     ┌───┐                           │    │
│  │     │🏠│ ← Building                 │    │
│  │     └───┘                           │    │
│  │       ▲ "House" tooltip             │    │  ← World-anchored
│  │                                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  [🏠] [🏢] [🏭] [🛣️]              │    │  ← Build menu
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

Screen-space elements (resource bar, build menu) don't move when the camera pans. World-space elements (selection indicators, health bars) move with the world.

```typescript
// src/ui/world-label.ts
export function renderWorldLabel(
  ctx: CanvasRenderingContext2D,
  text: string,
  worldX: number,
  worldY: number,
  camera: Camera
) {
  // Convert world position to screen position
  const sx = (worldX - camera.x) * camera.zoom;
  const sy = (worldY - camera.y) * camera.zoom;

  ctx.save();
  ctx.font = '11px monospace';
  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
  ctx.fillRect(sx - 30, sy - 14, 60, 16);
  ctx.fillStyle = '#fff';
  ctx.fillText(text, sx, sy - 2);
  ctx.restore();
}
```

## Wiring the HUD to Game State

```typescript
// src/game/hud-controller.ts
export class HUDController {
  private resourceBar: ResourceBar;
  private buildMenu: BuildMenu;
  private tooltip: Tooltip;

  constructor(hudContainer: HTMLElement, buildMode: BuildMode, buildings: BuildingDef[]) {
    this.resourceBar = new ResourceBar(hudContainer);
    this.tooltip = new Tooltip(hudContainer);

    this.buildMenu = new BuildMenu(hudContainer, buildings, (building) => {
      buildMode.select(building);
    });

    // Cancel build mode → deselect menu
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.buildMenu.deselect();
      }
    });
  }

  update(resources: Resources) {
    this.resourceBar.update(resources);
  }

  showTooltip(x: number, y: number, text: string) {
    this.tooltip.show(x, y, text);
  }

  hideTooltip() {
    this.tooltip.hide();
  }
}
```

## Riku's Reaction

The game has a proper interface. Resources visible at a glance, buildings selectable from a menu, hover info on placed structures.

Riku: "This is playable now. But if I refresh the page, everything's gone. We need save and load."

You: "Serialization. JSON. localStorage. Let's persist the city."

## What You Built

- **HTML overlay** — positioned above canvas with pointer-events passthrough
- **Resource bar** — money, population, power with formatted numbers
- **Build menu** — icon buttons that trigger build mode
- **Tooltip** — follows cursor, shows building info on hover
- **Screen vs world space** — HUD stays fixed, world labels move with camera
- **HUD controller** — wires UI components to game state

The player has information. Next: making sure they don't lose their city.

---

[← Chapter 15: Lighting](chapter-15-lighting.md) | [Chapter 17: Save & Load →](chapter-17-save-load.md)
