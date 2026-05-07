# Chapter 3: The Walls

> **What you'll learn:** Positioning, rotation, scaling, and grouping objects together.

### Transforms — Position, Rotation, Scale

Every 3D object has three transforms:

```tsx
<mesh
  position={[x, y, z]}      // where it is
  rotation={[rx, ry, rz]}   // how it's tilted (radians)
  scale={[sx, sy, sz]}      // how big it is (multiplier)
>
```

All default to `[0, 0, 0]` for position/rotation and `[1, 1, 1]` for scale.

**Shorthand:** If all scale values are the same, use a single number: `scale={2}` = `scale={[2, 2, 2]}`.

### Grouping with `<group>`

A `<group>` is an invisible container. When you move/rotate a group, all children move/rotate with it. This is how you build complex objects from simple parts.

Think of it like framing a wall on the ground, then tilting it up — everything nailed to the frame moves together.

### Building the Full House

Let's expand `House.tsx` with walls, a roof, and a door:

**`src/components/House.tsx`**
```tsx
'use client'

export default function House() {
  return (
    <group position={[0, 0, 0]}>
      {/* Base / Floor */}
      <mesh position={[0, 0.05, 0]}>
        <boxGeometry args={[3, 0.1, 3]} />
        <meshStandardMaterial color="#8B7355" />
      </mesh>

      {/* Back wall */}
      <mesh position={[0, 1, -1.45]}>
        <boxGeometry args={[3, 2, 0.1]} />
        <meshStandardMaterial color="#d4a574" />
      </mesh>

      {/* Left wall */}
      <mesh position={[-1.45, 1, 0]}>
        <boxGeometry args={[0.1, 2, 3]} />
        <meshStandardMaterial color="#c49a6c" />
      </mesh>

      {/* Right wall */}
      <mesh position={[1.45, 1, 0]}>
        <boxGeometry args={[0.1, 2, 3]} />
        <meshStandardMaterial color="#c49a6c" />
      </mesh>

      {/* Front wall - left part */}
      <mesh position={[-0.85, 1, 1.45]}>
        <boxGeometry args={[1.2, 2, 0.1]} />
        <meshStandardMaterial color="#d4a574" />
      </mesh>

      {/* Front wall - right part */}
      <mesh position={[0.85, 1, 1.45]}>
        <boxGeometry args={[1.2, 2, 0.1]} />
        <meshStandardMaterial color="#d4a574" />
      </mesh>

      {/* Front wall - top part (above door) */}
      <mesh position={[0, 1.75, 1.45]}>
        <boxGeometry args={[0.5, 0.5, 0.1]} />
        <meshStandardMaterial color="#d4a574" />
      </mesh>

      {/* Door frame */}
      <mesh position={[0, 0.75, 1.46]}>
        <boxGeometry args={[0.6, 1.5, 0.05]} />
        <meshStandardMaterial color="#5c3a1e" />
      </mesh>

      {/* Roof */}
      <mesh position={[0, 2.6, 0]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[2.5, 1.2, 4]} />
        <meshStandardMaterial color="#8B0000" />
      </mesh>
    </group>
  )
}
```

### What's Happening Here

**The group** wraps everything. If you later want to move the entire house, change the group's position — all parts move together.

**Wall positioning:** Each wall is a thin box (`0.1` thick) placed at the edges. The front wall has a gap for the door — we use three pieces (left, right, top) to frame the opening.

**The roof** is a cone with 4 sides (`segments: 4`), rotated 45° around Y so the edges align with the walls. This creates a pyramid shape.

**Color variation:** The side walls are slightly darker (`#c49a6c` vs `#d4a574`) to give visual depth even before proper lighting.

### The Power of Groups — Nested Transforms

Groups can nest. Transforms are **relative to the parent**:

```tsx
<group position={[10, 0, 0]}>        {/* House at x=10 */}
  <mesh position={[0, 1, 0]}>         {/* Wall at x=10, y=1 (world coords) */}
    ...
  </mesh>
</group>
```

The wall's position `[0, 1, 0]` is relative to the group. In world space, it's at `[10, 1, 0]`. This is how you build reusable components — the House doesn't know or care where it's placed in the world.

### Try This

Duplicate the house at a different position:

```tsx
<House />
<group position={[8, 0, 0]}>
  <House />
</group>
```

You now have a neighborhood. Each house is self-contained because of grouping.

---

> **🏗 Progress:** Walls are up, roof is on. The house has structure. But it looks flat and lifeless — next, we add lighting to bring it to life.

---

[← Chapter 2: The Foundation](./02-the-foundation.md) | [Chapter 4: Wiring the Electricity →](./04-wiring-the-electricity.md)
