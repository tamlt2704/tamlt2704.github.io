# Layout

[← Import Assets](06-assets.md) | [Text →](08-text.md)

---

Revideo uses **CSS Flexbox** for layout. This is the equivalent of Manim's `VGroup` with `arrange()`.

## Enabling Layout

Add `layout` to any container node:

```tsx
<Rect layout direction="row" gap={20}>
  <Circle size={80} fill="red" />
  <Circle size={80} fill="green" />
  <Circle size={80} fill="blue" />
</Rect>
```

Without `layout`, children are positioned absolutely (using `x`, `y`). With `layout`, children are arranged automatically.

## Direction

```tsx
// Horizontal (default)
<Rect layout direction="row" gap={20}>...</Rect>

// Vertical
<Rect layout direction="column" gap={20}>...</Rect>
```

**Manim equivalent:**

```python
VGroup(a, b, c).arrange(RIGHT, buff=0.5)   # row
VGroup(a, b, c).arrange(DOWN, buff=0.5)    # column
```

## Gap, Padding, Margin

```tsx
<Rect layout direction="row" gap={20} padding={40}>
  <Circle size={80} fill="red" />
  <Circle size={80} fill="blue" />
</Rect>
```

- `gap` — space between children
- `padding` — space inside the container, around children
- `margin` — space outside the container (on individual children)

## Alignment

```tsx
<Rect layout direction="row" alignItems="center" justifyContent="center"
      width={800} height={400} fill="#252526">
  <Txt text="Centered" fill="white" fontSize={32} />
</Rect>
```

| Property | Values | Controls |
|---|---|---|
| `justifyContent` | `start`, `center`, `end`, `space-between`, `space-around` | Main axis |
| `alignItems` | `start`, `center`, `end`, `stretch` | Cross axis |

## Wrapping

```tsx
<Rect layout direction="row" wrap="wrap" gap={12} width={600}>
  {items.map(item => (
    <Rect padding={[8, 16]} fill="#333" radius={6}>
      <Txt text={item} fill="white" fontSize={14} />
    </Rect>
  ))}
</Rect>
```

Items wrap to the next line when they exceed the container width.

## Grow

```tsx
<Rect layout direction="row" width={800} height={400}>
  <Rect grow={1} fill="red" />    {/* takes 1/3 */}
  <Rect grow={2} fill="blue" />   {/* takes 2/3 */}
</Rect>
```

`grow` works like CSS `flex-grow`.

## Manim Equivalent: VGroup

```python
# Manim
group = VGroup(circle, square, triangle)
group.arrange(RIGHT, buff=0.5)
group.move_to(ORIGIN)
```

```tsx
// Revideo
<Rect layout direction="row" gap={50} justifyContent="center">
  <Circle size={100} fill="red" />
  <Rect size={100} fill="blue" />
  <Polygon ... />
</Rect>
```

---

[← Import Assets](06-assets.md) | [Text →](08-text.md)
