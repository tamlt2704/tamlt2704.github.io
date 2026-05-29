# Chapter 1: SVG Basics

[prev: Overview](./chapter-00-overview.md) | [next: CSS Animation](./chapter-02-css-animation.md)

Before animating SVGs, you need to understand how they work. SVG (Scalable Vector Graphics) uses XML to describe 2D graphics. Every shape, line, and curve is defined mathematically — making them perfect for animation.

## The SVG Element and ViewBox

The `viewBox` defines the internal coordinate system. The `width`/`height` attributes set the display size. The viewBox maps the internal coordinates to the display area.

```svg
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <!-- viewBox="minX minY width height" -->
  <!-- Origin (0,0) is top-left -->
  <!-- X increases rightward, Y increases downward -->
</svg>
```

The viewBox creates a virtual canvas. If your viewBox is `"0 0 100 100"` but your SVG is displayed at 400x400px, everything scales up 4x without losing quality.

```svg
<!-- Same content, different display sizes — both sharp -->
<svg width="100" height="100" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#e74c3c"/>
</svg>

<svg width="400" height="400" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#e74c3c"/>
</svg>
```

## Basic Shapes

### Rectangle

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <!-- Basic rectangle -->
  <rect x="20" y="20" width="160" height="120" fill="#3498db"/>

  <!-- Rounded rectangle -->
  <rect x="20" y="20" width="160" height="120" rx="15" ry="15" fill="#9b59b6"/>
</svg>
```

Visually: A blue rectangle positioned 20px from the top-left, 160px wide and 120px tall. The rounded version has 15px corner radius.

### Circle and Ellipse

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <!-- Circle: center (cx, cy) and radius (r) -->
  <circle cx="100" cy="100" r="80" fill="#e74c3c"/>

  <!-- Ellipse: center and two radii -->
  <ellipse cx="100" cy="100" rx="90" ry="50" fill="#f39c12"/>
</svg>
```

Visually: A red circle centered in the SVG. The ellipse is wider than it is tall — like a squashed circle.

### Line, Polyline, Polygon

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <!-- Line: two points -->
  <line x1="10" y1="10" x2="190" y2="190" stroke="#2ecc71" stroke-width="3"/>

  <!-- Polyline: connected points, not closed -->
  <polyline points="20,180 60,40 100,120 140,20 180,100"
            fill="none" stroke="#e74c3c" stroke-width="2"/>

  <!-- Polygon: closed shape -->
  <polygon points="100,10 190,190 10,190" fill="#3498db" stroke="#2c3e50" stroke-width="2"/>
</svg>
```

Visually: A diagonal green line. A red zigzag line (like a stock chart). A blue triangle.

## The Path Element

The `path` element is the most powerful SVG shape. Every other shape can be expressed as a path. It uses a mini-language of commands.

### Path Commands

| Command | Name             | Parameters                         | Description                   |
| ------- | ---------------- | ---------------------------------- | ----------------------------- |
| M/m     | MoveTo           | x, y                               | Move pen without drawing      |
| L/l     | LineTo           | x, y                               | Draw straight line            |
| H/h     | Horizontal       | x                                  | Horizontal line               |
| V/v     | Vertical         | y                                  | Vertical line                 |
| C/c     | Cubic Bezier     | x1,y1 x2,y2 x,y                    | Curve with two control points |
| Q/q     | Quadratic Bezier | x1,y1 x,y                          | Curve with one control point  |
| A/a     | Arc              | rx,ry rotation large-arc sweep x,y | Elliptical arc                |
| Z/z     | ClosePath        | —                                  | Close path back to start      |

Uppercase = absolute coordinates. Lowercase = relative to current position.

### Path Examples

```svg
<svg width="300" height="300" viewBox="0 0 300 300">
  <!-- Triangle using lines -->
  <path d="M 150,20 L 280,250 L 20,250 Z"
        fill="none" stroke="#e74c3c" stroke-width="2"/>

  <!-- Smooth curve using cubic bezier -->
  <path d="M 20,150 C 20,50 280,50 280,150"
        fill="none" stroke="#3498db" stroke-width="3"/>

  <!-- Heart shape -->
  <path d="M 150,250
           C 150,250 80,190 80,140
           C 80,90 120,70 150,100
           C 180,70 220,90 220,140
           C 220,190 150,250 150,250 Z"
        fill="#e74c3c"/>
</svg>
```

Visually: A red triangle outline, a blue arch curve, and a filled red heart shape.

### Arc Command Deep Dive

The arc is the most complex command: `A rx ry x-rotation large-arc-flag sweep-flag x y`

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <!-- Small arc (large-arc=0, sweep=1) -->
  <path d="M 50,100 A 50,50 0 0,1 150,100" fill="none" stroke="#3498db" stroke-width="2"/>

  <!-- Large arc (large-arc=1, sweep=1) -->
  <path d="M 50,100 A 50,50 0 1,1 150,100" fill="none" stroke="#e74c3c" stroke-width="2"/>

  <!-- Semicircle -->
  <path d="M 180,100 A 40,40 0 1,0 260,100" fill="#9b59b6"/>
</svg>
```

Visually: A small blue arc (less than half circle), a large red arc (more than half circle), and a purple filled semicircle.

## Stroke and Fill

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <!-- Fill only -->
  <circle cx="60" cy="100" r="40" fill="#3498db"/>

  <!-- Stroke only -->
  <circle cx="160" cy="100" r="40" fill="none" stroke="#e74c3c" stroke-width="4"/>

  <!-- Both with opacity -->
  <circle cx="260" cy="100" r="40" fill="#2ecc71" fill-opacity="0.5"
          stroke="#27ae60" stroke-width="3" stroke-opacity="0.8"/>
</svg>
```

### Stroke Properties

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <!-- Dashed stroke -->
  <line x1="20" y1="30" x2="280" y2="30"
        stroke="#333" stroke-width="3" stroke-dasharray="10,5"/>

  <!-- Dotted stroke -->
  <line x1="20" y1="70" x2="280" y2="70"
        stroke="#333" stroke-width="3" stroke-dasharray="2,8" stroke-linecap="round"/>

  <!-- Stroke linecap: butt, round, square -->
  <line x1="50" y1="120" x2="250" y2="120" stroke="#e74c3c" stroke-width="12" stroke-linecap="butt"/>
  <line x1="50" y1="150" x2="250" y2="150" stroke="#3498db" stroke-width="12" stroke-linecap="round"/>
  <line x1="50" y1="180" x2="250" y2="180" stroke="#2ecc71" stroke-width="12" stroke-linecap="square"/>
</svg>
```

Visually: A dashed line, a dotted line, then three thick lines showing different end cap styles — flat, rounded, and squared-off.

## Transforms

SVG transforms work similarly to CSS transforms but use attribute syntax.

```svg
<svg width="400" height="300" viewBox="0 0 400 300">
  <!-- Translate: move position -->
  <rect x="0" y="0" width="50" height="50" fill="#3498db" transform="translate(20, 20)"/>

  <!-- Rotate: degrees around point -->
  <rect x="150" y="100" width="80" height="80" fill="#e74c3c" transform="rotate(45, 190, 140)"/>

  <!-- Scale: multiply size -->
  <circle cx="320" cy="80" r="20" fill="#2ecc71" transform="scale(1.5)"/>

  <!-- Combined transforms -->
  <rect x="0" y="0" width="40" height="40" fill="#9b59b6"
        transform="translate(300, 200) rotate(30) scale(1.2)"/>
</svg>
```

Visually: A blue square shifted from origin. A red square rotated 45 degrees (appearing as a diamond). A green circle scaled 1.5x larger. A purple square that's moved, rotated, and scaled.

## Groups and Reuse

### Groups (g)

Groups let you apply transforms and styles to multiple elements at once.

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <!-- Group with shared transform -->
  <g transform="translate(50, 50)" fill="#3498db" opacity="0.8">
    <rect x="0" y="0" width="40" height="40"/>
    <rect x="50" y="0" width="40" height="40"/>
    <rect x="100" y="0" width="40" height="40"/>
  </g>

  <!-- Nested groups -->
  <g transform="translate(50, 130)">
    <g fill="#e74c3c">
      <circle cx="20" cy="20" r="15"/>
      <circle cx="60" cy="20" r="15"/>
    </g>
    <g fill="#2ecc71">
      <circle cx="100" cy="20" r="15"/>
      <circle cx="140" cy="20" r="15"/>
    </g>
  </g>
</svg>
```

Visually: Three blue semi-transparent squares in a row. Below them, two red circles followed by two green circles.

### Defs and Use

`defs` defines reusable elements that aren't rendered until referenced with `use`.

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <!-- Define a star shape once -->
    <polygon id="star" points="12,2 15,9 22,9 16,14 18,21 12,17 6,21 8,14 2,9 9,9"
             fill="#f1c40f"/>

    <!-- Define a gradient -->
    <linearGradient id="sunset" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#e74c3c"/>
      <stop offset="100%" stop-color="#f39c12"/>
    </linearGradient>
  </defs>

  <!-- Reuse the star at different positions and sizes -->
  <use href="#star" x="20" y="20"/>
  <use href="#star" x="60" y="40" transform="scale(1.5)"/>
  <use href="#star" x="80" y="10" transform="scale(2)"/>

  <!-- Use the gradient -->
  <rect x="20" y="120" width="260" height="60" rx="10" fill="url(#sunset)"/>
</svg>
```

Visually: Three yellow stars of increasing size scattered across the top. Below, a rounded rectangle with a red-to-orange gradient.

## Putting It All Together

Here's a complete SVG illustration combining all concepts:

```svg
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#2c3e50"/>
      <stop offset="100%" stop-color="#3498db"/>
    </linearGradient>
    <radialGradient id="sun-glow">
      <stop offset="0%" stop-color="#f39c12"/>
      <stop offset="100%" stop-color="#e74c3c" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Sky background -->
  <rect width="400" height="300" fill="url(#sky)"/>

  <!-- Sun with glow -->
  <circle cx="320" cy="80" r="60" fill="url(#sun-glow)"/>
  <circle cx="320" cy="80" r="25" fill="#f1c40f"/>

  <!-- Mountains -->
  <polygon points="0,300 80,150 160,300" fill="#1a252f"/>
  <polygon points="100,300 200,120 300,300" fill="#2c3e50"/>
  <polygon points="220,300 320,170 400,300" fill="#1a252f"/>

  <!-- Trees (using groups) -->
  <g transform="translate(50, 220)">
    <rect x="-3" y="0" width="6" height="30" fill="#5d4037"/>
    <polygon points="0,-30 -15,0 15,0" fill="#27ae60"/>
    <polygon points="0,-45 -12,-10 12,-10" fill="#2ecc71"/>
  </g>
  <g transform="translate(340, 230)">
    <rect x="-3" y="0" width="6" height="25" fill="#5d4037"/>
    <polygon points="0,-25 -12,0 12,0" fill="#27ae60"/>
    <polygon points="0,-38 -10,-8 10,-8" fill="#2ecc71"/>
  </g>

  <!-- Stars -->
  <circle cx="50" cy="40" r="1.5" fill="white"/>
  <circle cx="120" cy="60" r="1" fill="white"/>
  <circle cx="200" cy="30" r="1.5" fill="white"/>
  <circle cx="250" cy="55" r="1" fill="white"/>
</svg>
```

Visually: A night mountain scene with a dark-to-blue gradient sky, a glowing sun/moon, layered mountain silhouettes, two pine trees, and scattered stars.

## Key Takeaways

- The `viewBox` creates a scalable coordinate system independent of display size
- Basic shapes cover most needs: `rect`, `circle`, `ellipse`, `line`, `polygon`
- The `path` element with its command language can draw anything
- Transforms (`translate`, `rotate`, `scale`) position and modify elements
- `defs`/`use` enable reusable components
- Groups (`g`) batch transforms and styles

Next, we'll bring these static shapes to life with CSS animations.
