# Chapter 9: Rocks and Crystals

[← Ch 8](chapter-08-lsystems.md) | [Ch 10 →](chapter-10-buildings.md)

---

## Juno's Request

> "Asteroids, crystal formations, rocky debris. Not circles, not squares. Rocks should look like rocks: irregular polygons. Crystals should be faceted and geometric. Asteroids should look battered."

---

## Voronoi Diagrams

Given seed points, Voronoi divides space into cells — each containing all points closest to one seed:

```typescript
import Alea from 'alea';

interface Point { x: number; y: number; }

function nearestPoint(x: number, y: number, points: Point[]): number {
  let minDist = Infinity, nearest = 0;
  for (let i = 0; i < points.length; i++) {
    const dist = (x-points[i].x)**2 + (y-points[i].y)**2;
    if (dist < minDist) { minDist = dist; nearest = i; }
  }
  return nearest;
}
```

---

## Rock Shape Generation

Irregular polygon using random radius per angle:

```typescript
function generateRockShape(seed: string | number, radius = 40, vertices = 12, roughness = 0.3): Point[] {
  const rng = Alea(seed);
  const points: Point[] = [];
  for (let i = 0; i < vertices; i++) {
    const angle = (i / vertices) * Math.PI * 2;
    const r = radius * (1 - roughness + rng() * roughness * 2);
    points.push({ x: Math.cos(angle) * r, y: Math.sin(angle) * r });
  }
  return points;
}

function subdividePolygon(points: Point[], rng: () => number, displacement = 5): Point[] {
  const result: Point[] = [];
  for (let i = 0; i < points.length; i++) {
    const next = points[(i+1) % points.length];
    result.push(points[i]);
    result.push({
      x: (points[i].x + next.x)/2 + (rng()-0.5) * displacement,
      y: (points[i].y + next.y)/2 + (rng()-0.5) * displacement,
    });
  }
  return result;
}
```

```
Base (8 vertices):     After subdivision:
      ╱╲                    ╱╲╱╲
     ╱  ╲                  ╱╲  ╱╲
    │    │                ╱  ╲╱  ╲
     ╲  ╱                 ╲╱╲╱╲╱
      ╲╱                    ╲╱
   (smooth)              (rough, natural)
```

---

## Crystal Facets with Voronoi

```typescript
function generateCrystal(seed: string | number, size = 128, facets = 8): HTMLCanvasElement {
  const rng = Alea(seed);
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(size, size);

  // Clustered facet centers
  const points: Point[] = [];
  for (let i = 0; i < facets; i++) {
    points.push({ x: size/2 + (rng()-0.5)*size*0.6, y: size/2 + (rng()-0.5)*size*0.6 });
  }

  // Color per facet
  const baseHue = rng() * 360;
  const colors = points.map((_, i) => hslToRgb(baseHue + rng()*20, 60+rng()*20, 30+(i/facets)*40));

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = (x-size/2)/(size/2), dy = (y-size/2)/(size/2);
      if (Math.sqrt(dx*dx+dy*dy) > 0.8) { const i=(y*size+x)*4; imageData.data[i+3]=0; continue; }

      const nearest = nearestPoint(x, y, points);
      const rightNearest = x < size-1 ? nearestPoint(x+1, y, points) : nearest;
      const downNearest = y < size-1 ? nearestPoint(x, y+1, points) : nearest;
      const isEdge = rightNearest !== nearest || downNearest !== nearest;

      const [r,g,b] = colors[nearest];
      const i = (y*size+x)*4;
      if (isEdge) {
        imageData.data[i]=Math.min(255,r+80); imageData.data[i+1]=Math.min(255,g+80); imageData.data[i+2]=Math.min(255,b+80);
      } else {
        imageData.data[i]=r; imageData.data[i+1]=g; imageData.data[i+2]=b;
      }
      imageData.data[i+3] = 255;
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

---

## Asteroid Shapes

Irregular radius + craters + directional lighting:

```typescript
function generateAsteroid(seed: string | number, size = 64): HTMLCanvasElement {
  const rng = Alea(seed);
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const imageData = ctx.createImageData(size, size);
  const cx = size/2, cy = size/2, baseR = size * 0.35;

  // Irregular radius per angle
  const steps = 32;
  const radii = Array.from({length: steps}, () => baseR * (0.7 + rng() * 0.6));

  // Craters
  const craters = Array.from({length: 2 + Math.floor(rng()*4)}, () => ({
    x: cx + (rng()-0.5)*baseR, y: cy + (rng()-0.5)*baseR, r: 3 + rng()*6
  }));

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = x-cx, dy = y-cy;
      const dist = Math.sqrt(dx*dx+dy*dy);
      const angle = Math.atan2(dy, dx);
      const aIdx = ((angle/(Math.PI*2)+1)%1) * steps;
      const i0 = Math.floor(aIdx) % steps, i1 = (i0+1) % steps;
      const radius = radii[i0]*(1-(aIdx-Math.floor(aIdx))) + radii[i1]*(aIdx-Math.floor(aIdx));

      const i = (y*size+x)*4;
      if (dist > radius) { imageData.data[i+3]=0; continue; }

      let light = Math.max(0.3, 1 - dist/radius*0.5 - dx/radius*0.3);
      for (const c of craters) {
        const cd = Math.sqrt((x-c.x)**2+(y-c.y)**2);
        if (cd < c.r) light *= 1 - (1-cd/c.r)*0.4;
      }
      imageData.data[i]=Math.floor(90*light); imageData.data[i+1]=Math.floor(80*light);
      imageData.data[i+2]=Math.floor(70*light); imageData.data[i+3]=255;
    }
  }
  ctx.putImageData(imageData, 0, 0);
  return canvas;
}
```

---

## Visual Result

```
Rock:              Crystal:           Asteroid:
┌──────────┐       ┌──────────┐       ┌──────────┐
│  ╱──╲    │       │   ╱│╲    │       │  ▓▓▓▓▓  │
│ ╱    ╲   │       │  ╱─┼─╲   │       │ ▓░▓▓▓▓▓ │
│ │    │   │       │  ╲─┼─╱   │       │▓▓▓▓░▓▓▓▓│
│ ╲    ╱   │       │   ╲│╱    │       │  ▓▓▓▓▓  │
│  ╲──╱    │       │          │       │          │
└──────────┘       └──────────┘       └──────────┘
 (irregular)        (faceted)          (cratered)
```

---

## Parameter Tuning

| Parameter | Low | High | Effect |
|-----------|-----|------|--------|
| Rock vertices | 6 | 20 | Chunky vs smooth |
| Roughness | 0.1 | 0.5 | Subtle vs dramatic |
| Crystal facets | 4 | 15 | Large faces vs shattered |
| Asteroid craters | 1 | 8 | Fresh vs bombarded |

**Juno's notes:**

> "Rocks: 10-14 vertices, roughness 0.3. Crystals: 6-10 facets with bright edges — they need to glow. Asteroids: high radius variance with 3-5 craters."

---

## Exercises

1. **Crystal cluster:** 3-7 overlapping crystals of varying sizes and rotations, layered back-to-front.

2. **Asteroid field:** 20 asteroids at different sizes on a starfield background (Ch 1).

3. **Geode:** Voronoi inside a circle — outer ring "rock" (brown), inner cells "crystal" (colored facets).

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Voronoi | Space divided by nearest seed point |
| Rock polygon | Random radius per angle, connect vertices |
| Subdivision | Insert displaced midpoints for detail |
| Crystal facets | Voronoi cells with bright edge detection |
| Asteroid | Irregular radius + craters + directional lighting |
| Edge detection | Compare cell ID of pixel vs neighbor |

---

[← Ch 8](chapter-08-lsystems.md) | [Ch 10 →](chapter-10-buildings.md)
