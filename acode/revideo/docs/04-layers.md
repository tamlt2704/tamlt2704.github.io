# Layers

[← Project Settings](03-project-settings.md) | [Easing Functions →](05-easing-functions.md)

---

## Node Ordering

Nodes are rendered in the order they're added. Later nodes appear **on top** of earlier ones.

```tsx
view.add(
  <>
    <Circle size={200} fill="red" />     {/* bottom */}
    <Circle size={200} fill="blue" x={50} y={50} />  {/* on top */}
  </>
);
```

The blue circle overlaps the red one because it was added second.

**Manim equivalent:** In Manim, `self.add(a, b)` renders `b` on top of `a`.

## `zIndex`

To control ordering without changing add order, use `zIndex`:

```tsx
view.add(
  <>
    <Circle size={200} fill="red" zIndex={2} />     {/* on top (higher z) */}
    <Circle size={200} fill="blue" x={50} zIndex={1} />  {/* behind */}
  </>
);
```

Higher `zIndex` = closer to the viewer. Default is `0`.

### Animating zIndex

```tsx
// Bring to front over 0.5 seconds
yield* circle().zIndex(10, 0.5);
```

**Manim equivalent:**

```python
# Manim
circle.set_z_index(2)
# or
self.bring_to_front(circle)
```

## Practical Example: Overlapping Cards

```tsx
const cards = createRefArray<Rect>();

view.add(
  <>
    {[0, 1, 2].map(i => (
      <Rect
        ref={cards}
        x={i * 80 - 80}
        width={200}
        height={280}
        fill={['#ff5f57', '#febc2e', '#28c840'][i]}
        radius={12}
        zIndex={i}
      />
    ))}
  </>
);

// Bring the first card to front
yield* cards[0].zIndex(10, 0.3);
```

---

[← Project Settings](03-project-settings.md) | [Easing Functions →](05-easing-functions.md)
