# Chapter 17: Save & Load

[← Chapter 16: HUD](chapter-16-hud.md) | [Chapter 18: Audio →](chapter-18-audio.md)

---

## The Task

Riku spends 20 minutes building a city. Refreshes the page. Gone. "I need save and load. Auto-save. And let me export my city as a file so I can share it."

Persistence. The game state lives in memory — you need to serialize it to something durable.

## What to Save

Not everything needs saving. Derived state (screen positions, animation frames) can be reconstructed. Save the *source of truth*:

```typescript
// src/game/save-types.ts
export interface SaveData {
  version: number;
  timestamp: number;
  grid: GridSaveData;
  buildings: BuildingSaveData[];
  resources: ResourcesSaveData;
  camera: CameraSaveData;
  dayCycle: { hour: number };
}

interface GridSaveData {
  width: number;
  height: number;
  terrain: number[];  // Flat array, row-major
}

interface BuildingSaveData {
  id: string;        // Building type ID
  gridX: number;
  gridY: number;
}

interface ResourcesSaveData {
  money: number;
  population: number;
  maxPopulation: number;
  power: number;
  maxPower: number;
}

interface CameraSaveData {
  x: number;
  y: number;
  zoom: number;
}
```

## Serializing Game State to JSON

```typescript
// src/game/save-system.ts
const SAVE_VERSION = 1;

export function serializeGameState(game: GameState): SaveData {
  return {
    version: SAVE_VERSION,
    timestamp: Date.now(),
    grid: {
      width: game.grid.width,
      height: game.grid.height,
      terrain: game.grid.getTerrainFlat(), // Returns number[]
    },
    buildings: game.buildings.map(b => ({
      id: b.def.id,
      gridX: b.gridX,
      gridY: b.gridY,
    })),
    resources: { ...game.resources },
    camera: {
      x: game.camera.x,
      y: game.camera.y,
      zoom: game.camera.zoom,
    },
    dayCycle: {
      hour: game.dayCycle.hour,
    },
  };
}

export function deserializeGameState(data: SaveData, buildingDefs: Map<string, BuildingDef>): GameState {
  // Reconstruct grid
  const grid = new GameGrid(data.grid.width, data.grid.height);
  grid.setTerrainFlat(data.grid.terrain);

  // Reconstruct buildings
  const buildings: PlacedBuilding[] = [];
  for (const saved of data.buildings) {
    const def = buildingDefs.get(saved.id);
    if (!def) {
      console.warn(`Unknown building type: ${saved.id}, skipping`);
      continue;
    }

    const building = new PlacedBuilding(def, saved.gridX, saved.gridY);
    buildings.push(building);

    // Mark grid cells as occupied
    for (let dx = 0; dx < def.width; dx++) {
      for (let dy = 0; dy < def.height; dy++) {
        grid.setOccupied(saved.gridX + dx, saved.gridY + dy, saved.id);
      }
    }
  }

  // Reconstruct camera
  const camera = new Camera();
  camera.x = data.camera.x;
  camera.y = data.camera.y;
  camera.zoom = data.camera.zoom;

  // Reconstruct day cycle
  const dayCycle = new DayCycle();
  dayCycle.hour = data.dayCycle.hour;

  return {
    grid,
    buildings,
    resources: { ...data.resources },
    camera,
    dayCycle,
  };
}
```

## localStorage for Auto-Save

Auto-save every 30 seconds to localStorage:

```typescript
// src/game/autosave.ts
const AUTOSAVE_KEY = 'tinytown_autosave';
const AUTOSAVE_INTERVAL = 30_000; // 30 seconds

export class AutoSave {
  private timer: number | null = null;
  private game: GameState;

  constructor(game: GameState) {
    this.game = game;
  }

  start() {
    this.timer = window.setInterval(() => {
      this.save();
    }, AUTOSAVE_INTERVAL);

    // Also save when the page is about to close
    window.addEventListener('beforeunload', () => {
      this.save();
    });
  }

  stop() {
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  save() {
    try {
      const data = serializeGameState(this.game);
      const json = JSON.stringify(data);
      localStorage.setItem(AUTOSAVE_KEY, json);
      console.log(`Auto-saved (${(json.length / 1024).toFixed(1)} KB)`);
    } catch (e) {
      // localStorage might be full (5MB limit)
      console.warn('Auto-save failed:', e);
    }
  }

  load(): SaveData | null {
    try {
      const json = localStorage.getItem(AUTOSAVE_KEY);
      if (!json) return null;
      return JSON.parse(json) as SaveData;
    } catch {
      return null;
    }
  }

  hasAutoSave(): boolean {
    return localStorage.getItem(AUTOSAVE_KEY) !== null;
  }

  clearAutoSave() {
    localStorage.removeItem(AUTOSAVE_KEY);
  }
}
```

Load on startup:

```typescript
// src/main.ts
async function init() {
  const autoSave = new AutoSave(game);

  if (autoSave.hasAutoSave()) {
    const data = autoSave.load();
    if (data) {
      const loaded = deserializeGameState(data, buildingDefs);
      game.restore(loaded);
      console.log('Restored auto-save from', new Date(data.timestamp).toLocaleString());
    }
  }

  autoSave.start();
}
```

## Export/Import as Downloadable File

Let players share their cities:

```typescript
// src/game/file-save.ts
export function exportSave(game: GameState) {
  const data = serializeGameState(game);
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `tinytown-${formatDate(data.timestamp)}.json`;
  a.click();

  URL.revokeObjectURL(url);
}

export function importSave(buildingDefs: Map<string, BuildingDef>): Promise<SaveData | null> {
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.addEventListener('change', async () => {
      const file = input.files?.[0];
      if (!file) {
        resolve(null);
        return;
      }

      try {
        const text = await file.text();
        const data = JSON.parse(text) as SaveData;

        // Validate before loading
        if (!validateSaveData(data)) {
          alert('Invalid save file');
          resolve(null);
          return;
        }

        resolve(data);
      } catch {
        alert('Could not read save file');
        resolve(null);
      }
    });

    input.click();
  });
}

function formatDate(timestamp: number): string {
  const d = new Date(timestamp);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
```

## Validating Save Data

Never trust user-provided files. Validate structure before loading:

```typescript
// src/game/save-validation.ts
export function validateSaveData(data: unknown): data is SaveData {
  if (!data || typeof data !== 'object') return false;

  const d = data as Record<string, unknown>;

  if (typeof d.version !== 'number') return false;
  if (typeof d.timestamp !== 'number') return false;

  // Validate grid
  const grid = d.grid as Record<string, unknown>;
  if (!grid || typeof grid.width !== 'number' || typeof grid.height !== 'number') return false;
  if (!Array.isArray(grid.terrain)) return false;
  if (grid.terrain.length !== grid.width * grid.height) return false;

  // Validate buildings array
  if (!Array.isArray(d.buildings)) return false;
  for (const b of d.buildings) {
    if (typeof b.id !== 'string') return false;
    if (typeof b.gridX !== 'number' || typeof b.gridY !== 'number') return false;
  }

  // Validate resources
  const res = d.resources as Record<string, unknown>;
  if (!res || typeof res.money !== 'number') return false;

  return true;
}
```

## Versioning the Save Format

Games evolve. The save format from week 1 won't match week 4. Version the format and migrate:

```typescript
// src/game/save-migration.ts
export function migrateSaveData(data: SaveData): SaveData {
  let current = data;

  // Version 1 → 2: added power resource
  if (current.version === 1) {
    current = {
      ...current,
      version: 2,
      resources: {
        ...current.resources,
        power: current.resources.power ?? 0,
        maxPower: current.resources.maxPower ?? 10,
      },
    };
  }

  // Version 2 → 3: added NPC data
  if (current.version === 2) {
    current = {
      ...current,
      version: 3,
      npcs: [], // New field, empty for old saves
    };
  }

  return current;
}

// Usage:
function loadSave(json: string, buildingDefs: Map<string, BuildingDef>): GameState | null {
  try {
    let data = JSON.parse(json) as SaveData;

    if (data.version < SAVE_VERSION) {
      data = migrateSaveData(data);
    }

    if (data.version > SAVE_VERSION) {
      console.warn('Save file is from a newer version of the game');
      return null;
    }

    return deserializeGameState(data, buildingDefs);
  } catch {
    return null;
  }
}
```

## Multiple Save Slots

For players who want multiple cities:

```typescript
// src/game/save-slots.ts
const SLOT_PREFIX = 'tinytown_slot_';
const MAX_SLOTS = 5;

export class SaveSlots {
  getSavedSlots(): { slot: number; timestamp: number; name: string }[] {
    const slots: { slot: number; timestamp: number; name: string }[] = [];

    for (let i = 0; i < MAX_SLOTS; i++) {
      const json = localStorage.getItem(`${SLOT_PREFIX}${i}`);
      if (json) {
        try {
          const data = JSON.parse(json) as SaveData;
          slots.push({
            slot: i,
            timestamp: data.timestamp,
            name: `City ${i + 1}`,
          });
        } catch { /* skip corrupted */ }
      }
    }

    return slots;
  }

  saveToSlot(slot: number, game: GameState) {
    const data = serializeGameState(game);
    localStorage.setItem(`${SLOT_PREFIX}${slot}`, JSON.stringify(data));
  }

  loadFromSlot(slot: number): SaveData | null {
    const json = localStorage.getItem(`${SLOT_PREFIX}${slot}`);
    if (!json) return null;
    try {
      return JSON.parse(json) as SaveData;
    } catch {
      return null;
    }
  }

  deleteSlot(slot: number) {
    localStorage.removeItem(`${SLOT_PREFIX}${slot}`);
  }
}
```

## Riku's Reaction

Riku builds a city, refreshes — it's still there. Exports it, sends the JSON to a friend. They import it and see the same city.

Riku: "The game is silent. I want a satisfying *thunk* when I place a building. Background music. Sound effects."

You: "Web Audio API. Let's add ears to TinyTown."

## What You Built

- **Serialization** — game state → JSON with only source-of-truth data
- **Deserialization** — JSON → reconstructed game state
- **Auto-save** — localStorage every 30 seconds + on page close
- **File export** — download city as .json file
- **File import** — load and validate user-provided save files
- **Validation** — type-check structure before trusting data
- **Version migration** — upgrade old save formats to current
- **Save slots** — multiple cities in localStorage

The city persists. Next: making it sound good.

---

[← Chapter 16: HUD](chapter-16-hud.md) | [Chapter 18: Audio →](chapter-18-audio.md)
