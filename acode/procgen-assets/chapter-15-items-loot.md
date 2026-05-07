# Chapter 15: Items and Loot

[← Ch 14](chapter-14-animation.md) | [Ch 16 →](chapter-16-performance.md)

---

## Juno's Request

> "Drift needs loot. Weapons, shields, engines. Each visually unique, appearance reflecting stats. High-damage = bigger blade. Rare items glow. And procedural names — 'Void Cleaver of the Nebula' not 'Sword #4827'."

---

## Modular Item Architecture

```typescript
import Alea from 'alea';

interface ItemStats { damage: number; speed: number; defense: number; rarity: 'common'|'uncommon'|'rare'|'epic'|'legendary'; }
interface GeneratedItem { name: string; stats: ItemStats; glowColor?: [number,number,number]; }

function generateWeapon(seed: string | number): GeneratedItem {
  const rng = Alea(seed);
  const stats: ItemStats = {
    damage: 10 + Math.floor(rng()*90), speed: 10 + Math.floor(rng()*90),
    defense: Math.floor(rng()*50), rarity: rollRarity(rng),
  };
  const colors = getRarityColors(stats.rarity);
  return {
    name: generateItemName(seed), stats,
    glowColor: stats.rarity === 'epic' || stats.rarity === 'legendary' ? colors.accent : undefined,
  };
}

function rollRarity(rng: () => number): ItemStats['rarity'] {
  const r = rng();
  if (r < 0.50) return 'common'; if (r < 0.75) return 'uncommon';
  if (r < 0.90) return 'rare'; if (r < 0.97) return 'epic'; return 'legendary';
}
```

---

## Stat-Driven Visuals

```
damage: 20 → small blade     damage: 80 → large blade
speed: 80 → thin, sleek      speed: 20 → thick, heavy
```

```typescript
function renderWeapon(item: GeneratedItem, size = 64): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = '#0a0a1a'; ctx.fillRect(0, 0, size, size);
  const cx = size/2, cy = size/2;
  const colors = getRarityColors(item.stats.rarity);

  // Blade (size from damage)
  const bladeH = 10 + (item.stats.damage/100) * 30;
  const bladeW = 3 + (item.stats.damage/100) * 10;
  const [br,bg,bb] = colors.primary;
  ctx.fillStyle = `rgb(${br},${bg},${bb})`;
  ctx.beginPath(); ctx.moveTo(cx, cy-bladeH);
  ctx.lineTo(cx+bladeW/2, cy); ctx.lineTo(cx-bladeW/2, cy); ctx.closePath(); ctx.fill();

  // Hilt (size from defense)
  const hiltW = 8 + (item.stats.defense/100) * 8;
  const [hr,hg,hb] = colors.secondary;
  ctx.fillStyle = `rgb(${hr},${hg},${hb})`;
  ctx.fillRect(cx-hiltW/2, cy, hiltW, 4);
  ctx.fillRect(cx-2, cy+4, 4, 10);

  // Gem for rare+
  if (item.stats.rarity !== 'common') {
    const [gr,gg,gb] = colors.accent;
    ctx.fillStyle = `rgb(${gr},${gg},${gb})`;
    ctx.beginPath(); ctx.arc(cx, cy+2, 3, 0, Math.PI*2); ctx.fill();
  }

  // Glow
  if (item.glowColor) {
    const [r,g,b] = item.glowColor;
    ctx.shadowColor = `rgb(${r},${g},${b})`; ctx.shadowBlur = 8;
    ctx.strokeStyle = `rgba(${r},${g},${b},0.3)`; ctx.lineWidth = 2;
    ctx.strokeRect(4, 4, size-8, size-8); ctx.shadowBlur = 0;
  }
  return canvas;
}
```

---

## Rarity Colors

```typescript
function getRarityColors(rarity: string): {primary:[number,number,number]; secondary:[number,number,number]; accent:[number,number,number]} {
  const schemes: Record<string, any> = {
    common:    { primary:[140,140,140], secondary:[100,80,60], accent:[160,160,160] },
    uncommon:  { primary:[60,180,80], secondary:[80,100,60], accent:[100,220,120] },
    rare:      { primary:[60,120,220], secondary:[80,80,120], accent:[100,160,255] },
    epic:      { primary:[160,60,220], secondary:[100,60,120], accent:[200,100,255] },
    legendary: { primary:[220,180,40], secondary:[140,100,20], accent:[255,220,80] },
  };
  return schemes[rarity] || schemes.common;
}
```

```
Common:     Uncommon:   Rare:       Epic:       Legendary:
  │           ╱╲        ╱╲          ╱╲         ✦╱╲✦
  │          ╱██╲      ╱██╲        ╱██╲        ╱██╲
──┼──       ──◇──     ──◆──       ──◆──       ──✦◆✦──
  │           │          │          │           │
(gray)      (green)    (blue)     (purple)    (gold glow)
```

---

## Procedural Names

```typescript
const NAMES = {
  prefixes: ['Void','Star','Nebula','Quantum','Plasma','Dark','Crystal','Shadow','Storm'],
  weapons: ['Cleaver','Slicer','Piercer','Crusher','Reaper','Fang','Edge','Blade'],
  suffixes: ['of the Cosmos','of Ruin','of the Void','of Starfire','of Eternity'],
};

function generateItemName(seed: string | number): string {
  const rng = Alea(seed + '-name');
  const prefix = NAMES.prefixes[Math.floor(rng()*NAMES.prefixes.length)];
  const base = NAMES.weapons[Math.floor(rng()*NAMES.weapons.length)];
  if (rng() > 0.5) {
    const suffix = NAMES.suffixes[Math.floor(rng()*NAMES.suffixes.length)];
    return `${prefix} ${base} ${suffix}`;
  }
  return `${prefix} ${base}`;
}
```

---

## Visual Result

```
"Iron Edge"    "Star Fang"    "Void Cleaver    "Nebula Reaper   "Quantum Crusher
 Common         Uncommon       of Ruin"          Epic             of Eternity"
                               Rare                               Legendary
```

---

## Parameter Tuning

| Parameter | Effect | Juno's Notes |
|-----------|--------|--------------|
| Damage → blade size | Visual power | "Guess damage from silhouette" |
| Speed → thickness | Thin=fast | "Inverse feels intuitive" |
| Rarity → glow | Hierarchy | "Legendary visible from across screen" |
| Name length | Rarity signal | "Common: 2 words. Legendary: 3-4" |

---

## Exercises

1. **Shield generator:** Frame shape (round/kite/tower) + emblem + material color from rarity. Defense stat = frame thickness.

2. **Loot table:** Generate 5 items with weighted rarity (50% common, 25% uncommon, 15% rare, 8% epic, 2% legendary).

3. **Item comparison:** Two weapons side by side with stat bars. Green if better, red if worse.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Modular composition | blade + hilt + gem, each with variants |
| Stat-driven visuals | Higher stat → bigger visual element |
| Rarity colors | Gray → Green → Blue → Purple → Gold |
| Procedural names | prefix + base + optional suffix |
| Glow | `shadowColor` + `shadowBlur` for rare+ |

---

[← Ch 14](chapter-14-animation.md) | [Ch 16 →](chapter-16-performance.md)
