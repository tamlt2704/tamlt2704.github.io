# Chapter 8: Projects

[prev: Advanced Techniques](./chapter-07-techniques.md) | [next: Overview](./chapter-00-overview.md)

Complete, copy-paste projects combining techniques from previous chapters. Each project builds a real-world animation you can use in production.

## Project 1: Animated Logo Reveal (Line Draw + Fill)

A logo that draws its outline, then fills with color.

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        display: grid;
        place-items: center;
        min-height: 100vh;
        background: #1a1a2e;
      }
    </style>
  </head>
  <body>
    <svg width="300" height="200" viewBox="0 0 300 200">
      <style>
        .logo-stroke {
          fill: none;
          stroke: #00d4ff;
          stroke-width: 2;
          stroke-linecap: round;
          stroke-linejoin: round;
          stroke-dasharray: 400;
          stroke-dashoffset: 400;
          animation: draw 2s ease forwards;
        }
        .logo-fill {
          fill: #00d4ff;
          opacity: 0;
          animation: fill-in 0.8s ease forwards 2s;
        }
        @keyframes draw {
          to {
            stroke-dashoffset: 0;
          }
        }
        @keyframes fill-in {
          to {
            opacity: 1;
          }
        }
      </style>

      <!-- Triangle part of logo -->
      <path class="logo-stroke" d="M 80,150 L 150,40 L 220,150 Z" />
      <path class="logo-fill" d="M 80,150 L 150,40 L 220,150 Z" stroke="none" />

      <!-- Inner detail -->
      <path
        class="logo-stroke"
        d="M 120,150 L 150,90 L 180,150"
        style="animation-delay: 0.5s;
    stroke-dasharray: 200; stroke-dashoffset: 200;"
      />

      <!-- Text -->
      <text
        x="150"
        y="185"
        text-anchor="middle"
        font-family="sans-serif"
        font-size="18"
        fill="#00d4ff"
        opacity="0"
        style="animation: fill-in 0.8s ease forwards 2.5s;"
      >
        BRAND
      </text>
    </svg>
  </body>
</html>
```

Visually: A triangular logo outline draws itself in cyan on a dark background (2 seconds). An inner triangle detail draws next. Then the shapes fill with solid cyan color, and the brand name fades in below — a polished logo reveal sequence.

## Project 2: Loading Animations

### Spinner

```html
<svg width="50" height="50" viewBox="0 0 50 50">
  <style>
    .spinner-ring {
      fill: none;
      stroke: #3498db;
      stroke-width: 4;
      stroke-linecap: round;
      stroke-dasharray: 90 150;
      animation: spin 1.2s linear infinite;
      transform-origin: 25px 25px;
    }
    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  </style>
  <circle class="spinner-ring" cx="25" cy="25" r="20" />
</svg>
```

Visually: A blue arc spinning continuously — the standard loading spinner.

### Progress Bar

```html
<svg width="200" height="20" viewBox="0 0 200 20">
  <style>
    .track {
      fill: #eee;
    }
    .bar {
      fill: #2ecc71;
      animation: progress 3s ease forwards;
    }
    @keyframes progress {
      from {
        width: 0;
      }
      to {
        width: 180px;
      }
    }
  </style>
  <rect class="track" x="0" y="0" width="200" height="20" rx="10" />
  <rect class="bar" x="10" y="5" width="0" height="10" rx="5" />
</svg>
```

Visually: A grey rounded track with a green bar that fills from left to right over 3 seconds.

### Skeleton Loader

```html
<svg width="300" height="120" viewBox="0 0 300 120">
  <style>
    .skeleton {
      fill: #e0e0e0;
      animation: shimmer 1.5s ease-in-out infinite;
    }
    .skeleton:nth-child(2) {
      animation-delay: 0.1s;
    }
    .skeleton:nth-child(3) {
      animation-delay: 0.2s;
    }
    .skeleton:nth-child(4) {
      animation-delay: 0.3s;
    }
    @keyframes shimmer {
      0%,
      100% {
        opacity: 1;
      }
      50% {
        opacity: 0.4;
      }
    }
  </style>
  <!-- Avatar -->
  <circle class="skeleton" cx="30" cy="30" r="20" />
  <!-- Title line -->
  <rect class="skeleton" x="60" y="15" width="150" height="12" rx="6" />
  <!-- Subtitle -->
  <rect class="skeleton" x="60" y="35" width="100" height="10" rx="5" />
  <!-- Body lines -->
  <rect class="skeleton" x="10" y="70" width="280" height="10" rx="5" />
  <rect class="skeleton" x="10" y="90" width="240" height="10" rx="5" />
  <rect class="skeleton" x="10" y="110" width="200" height="10" rx="5" />
</svg>
```

Visually: A card-shaped skeleton placeholder with a circle (avatar), rectangles (text lines) all pulsing with a shimmer effect — the standard content loading state.

## Project 3: Scroll-Triggered Infographic

A bar chart and trend line that animate when scrolled into view.

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        margin: 0;
        font-family: sans-serif;
      }
      .spacer {
        height: 100vh;
        display: grid;
        place-items: center;
        background: #f5f5f5;
      }
      .chart-section {
        display: grid;
        place-items: center;
        padding: 4rem 0;
      }
    </style>
  </head>
  <body>
    <div class="spacer"><h1>Scroll Down</h1></div>
    <div class="chart-section">
      <svg id="chart" width="500" height="300" viewBox="0 0 500 300">
        <!-- Axes -->
        <line x1="50" y1="250" x2="450" y2="250" stroke="#ccc" stroke-width="1" />
        <line x1="50" y1="50" x2="50" y2="250" stroke="#ccc" stroke-width="1" />

        <!-- Bars -->
        <rect class="chart-bar" x="80" y="250" width="50" height="0" fill="#3498db" rx="4" />
        <rect class="chart-bar" x="160" y="250" width="50" height="0" fill="#2ecc71" rx="4" />
        <rect class="chart-bar" x="240" y="250" width="50" height="0" fill="#e74c3c" rx="4" />
        <rect class="chart-bar" x="320" y="250" width="50" height="0" fill="#f39c12" rx="4" />
        <rect class="chart-bar" x="400" y="250" width="50" height="0" fill="#9b59b6" rx="4" />

        <!-- Trend line -->
        <path
          id="trend"
          d="M 105,200 L 185,120 L 265,160 L 345,80 L 425,100"
          fill="none"
          stroke="#e74c3c"
          stroke-width="3"
          stroke-linecap="round"
        />

        <!-- Labels -->
        <text x="105" y="270" text-anchor="middle" font-size="11" fill="#666">Jan</text>
        <text x="185" y="270" text-anchor="middle" font-size="11" fill="#666">Feb</text>
        <text x="265" y="270" text-anchor="middle" font-size="11" fill="#666">Mar</text>
        <text x="345" y="270" text-anchor="middle" font-size="11" fill="#666">Apr</text>
        <text x="425" y="270" text-anchor="middle" font-size="11" fill="#666">May</text>
      </svg>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
    <script>
      gsap.registerPlugin(ScrollTrigger);

      const barHeights = [100, 160, 130, 190, 150];

      gsap.to(".chart-bar", {
        height: (i) => barHeights[i],
        y: (i) => -barHeights[i],
        duration: 0.8,
        ease: "back.out(1.4)",
        stagger: 0.12,
        scrollTrigger: { trigger: "#chart", start: "top 75%" },
      });

      const trend = document.getElementById("trend");
      const len = trend.getTotalLength();
      gsap.set(trend, { strokeDasharray: len, strokeDashoffset: len });
      gsap.to(trend, {
        strokeDashoffset: 0,
        duration: 1.5,
        ease: "power2.out",
        scrollTrigger: { trigger: "#chart", start: "top 70%" },
      });
    </script>
  </body>
</html>
```

Visually: Scroll down and the chart springs to life — five colored bars grow upward with bouncy stagger, then a red trend line draws itself across the tops. Nothing animates until the chart enters the viewport.

## Project 4: Interactive Map with Hover States

```html
<svg width="500" height="400" viewBox="0 0 500 400">
  <style>
    .region {
      fill: #bdc3c7;
      stroke: white;
      stroke-width: 2;
      transition:
        fill 0.3s ease,
        transform 0.2s ease;
      transform-origin: center;
      cursor: pointer;
    }
    .region:hover {
      fill: #3498db;
      transform: scale(1.03);
    }
    .region:active {
      fill: #2980b9;
    }
    .tooltip {
      opacity: 0;
      transition: opacity 0.2s;
      pointer-events: none;
    }
    .region:hover + .tooltip {
      opacity: 1;
    }
  </style>

  <!-- Simplified map regions -->
  <path class="region" d="M 50,100 L 150,80 L 200,150 L 120,180 Z" />
  <text class="tooltip" x="120" y="70" text-anchor="middle" font-size="12" fill="#333">North</text>

  <path class="region" d="M 200,150 L 300,100 L 350,180 L 280,220 L 200,200 Z" />
  <text class="tooltip" x="270" y="90" text-anchor="middle" font-size="12" fill="#333">East</text>

  <path class="region" d="M 120,180 L 200,200 L 220,300 L 100,280 Z" />
  <text class="tooltip" x="160" y="310" text-anchor="middle" font-size="12" fill="#333">South</text>

  <path class="region" d="M 280,220 L 350,180 L 400,250 L 350,320 L 260,290 Z" />
  <text class="tooltip" x="330" y="340" text-anchor="middle" font-size="12" fill="#333">
    Central
  </text>

  <path class="region" d="M 50,200 L 120,180 L 100,280 L 60,300 Z" />
  <text class="tooltip" x="80" y="320" text-anchor="middle" font-size="12" fill="#333">West</text>
</svg>
```

Visually: A simplified map with grey regions. Hovering a region highlights it blue and slightly enlarges it, with a label appearing. Clicking darkens the region. Pure CSS — no JavaScript needed.

## Project 5: Animated Icon Set

### Hamburger to X

```html
<svg width="48" height="48" viewBox="0 0 24 24" id="menu-icon" style="cursor:pointer;">
  <style>
    #menu-icon line {
      stroke: #333;
      stroke-width: 2;
      stroke-linecap: round;
      transition: all 0.3s ease;
      transform-origin: 12px 12px;
    }
    #menu-icon.open .top {
      transform: rotate(45deg) translate(0px, 5px);
    }
    #menu-icon.open .mid {
      opacity: 0;
    }
    #menu-icon.open .bot {
      transform: rotate(-45deg) translate(0px, -5px);
    }
  </style>
  <line class="top" x1="4" y1="7" x2="20" y2="7" />
  <line class="mid" x1="4" y1="12" x2="20" y2="12" />
  <line class="bot" x1="4" y1="17" x2="20" y2="17" />
</svg>

<script>
  document.getElementById("menu-icon").addEventListener("click", function () {
    this.classList.toggle("open");
  });
</script>
```

Visually: Three horizontal lines (hamburger menu). Click and the top/bottom lines rotate to form an X while the middle line fades out. Click again to reverse.

### Play to Pause

```html
<svg width="48" height="48" viewBox="0 0 24 24" id="play-pause" style="cursor:pointer;">
  <style>
    #play-pause path {
      transition: d 0.3s ease;
      fill: #333;
    }
  </style>
  <path id="pp-left" d="M 6,4 L 6,20 L 12,16 L 12,8 Z" />
  <path id="pp-right" d="M 12,8 L 12,16 L 18,12 L 18,12 Z" />
</svg>

<script>
  let playing = false;
  document.getElementById("play-pause").addEventListener("click", function () {
    playing = !playing;
    const left = document.getElementById("pp-left");
    const right = document.getElementById("pp-right");
    if (playing) {
      left.setAttribute("d", "M 5,4 L 5,20 L 9,20 L 9,4 Z");
      right.setAttribute("d", "M 15,4 L 15,20 L 19,20 L 19,4 Z");
    } else {
      left.setAttribute("d", "M 6,4 L 6,20 L 12,16 L 12,8 Z");
      right.setAttribute("d", "M 12,8 L 12,16 L 18,12 L 18,12 Z");
    }
  });
</script>
```

Visually: A play triangle that morphs into two pause bars when clicked. The triangle splits and reshapes into parallel rectangles. Click again to morph back to play.

## Project 6: Hero Section with Floating Elements

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        margin: 0;
        overflow: hidden;
        background: #0f0f23;
      }
    </style>
  </head>
  <body>
    <svg width="100%" height="100vh" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice">
      <style>
        .float-1 {
          animation: float1 6s ease-in-out infinite;
        }
        .float-2 {
          animation: float2 8s ease-in-out infinite;
        }
        .float-3 {
          animation: float3 7s ease-in-out infinite;
        }
        .twinkle {
          animation: twinkle 3s ease-in-out infinite;
        }

        @keyframes float1 {
          0%,
          100% {
            transform: translate(0, 0) rotate(0deg);
          }
          50% {
            transform: translate(20px, -30px) rotate(5deg);
          }
        }
        @keyframes float2 {
          0%,
          100% {
            transform: translate(0, 0);
          }
          33% {
            transform: translate(-15px, -20px);
          }
          66% {
            transform: translate(10px, -10px);
          }
        }
        @keyframes float3 {
          0%,
          100% {
            transform: translate(0, 0) scale(1);
          }
          50% {
            transform: translate(-10px, 20px) scale(1.05);
          }
        }
        @keyframes twinkle {
          0%,
          100% {
            opacity: 0.3;
          }
          50% {
            opacity: 1;
          }
        }
      </style>

      <!-- Background gradient -->
      <defs>
        <radialGradient id="hero-glow" cx="50%" cy="40%">
          <stop offset="0%" stop-color="#1a1a4e" />
          <stop offset="100%" stop-color="#0f0f23" />
        </radialGradient>
      </defs>
      <rect width="800" height="600" fill="url(#hero-glow)" />

      <!-- Stars -->
      <circle class="twinkle" cx="100" cy="80" r="1.5" fill="white" style="animation-delay:0s;" />
      <circle class="twinkle" cx="250" cy="120" r="1" fill="white" style="animation-delay:0.5s;" />
      <circle class="twinkle" cx="600" cy="90" r="1.5" fill="white" style="animation-delay:1s;" />
      <circle class="twinkle" cx="700" cy="200" r="1" fill="white" style="animation-delay:1.5s;" />
      <circle class="twinkle" cx="450" cy="50" r="1" fill="white" style="animation-delay:2s;" />

      <!-- Floating geometric shapes -->
      <g class="float-1">
        <polygon
          points="150,200 180,150 210,200"
          fill="none"
          stroke="#00d4ff"
          stroke-width="1.5"
          opacity="0.6"
        />
      </g>
      <g class="float-2">
        <rect
          x="600"
          y="150"
          width="50"
          height="50"
          rx="5"
          fill="none"
          stroke="#ff6b9d"
          stroke-width="1.5"
          opacity="0.5"
          transform="rotate(15, 625, 175)"
        />
      </g>
      <g class="float-3">
        <circle
          cx="680"
          cy="400"
          r="25"
          fill="none"
          stroke="#ffd93d"
          stroke-width="1.5"
          opacity="0.4"
        />
      </g>
      <g class="float-1" style="animation-delay: -3s;">
        <polygon
          points="100,450 115,420 130,450 115,440"
          fill="none"
          stroke="#6bcb77"
          stroke-width="1.5"
          opacity="0.5"
        />
      </g>

      <!-- Hero text -->
      <text
        x="400"
        y="300"
        text-anchor="middle"
        font-family="sans-serif"
        font-size="48"
        fill="white"
        font-weight="bold"
      >
        Build Amazing
      </text>
      <text
        x="400"
        y="360"
        text-anchor="middle"
        font-family="sans-serif"
        font-size="48"
        fill="#00d4ff"
        font-weight="bold"
      >
        Animations
      </text>
      <text
        x="400"
        y="420"
        text-anchor="middle"
        font-family="sans-serif"
        font-size="16"
        fill="#888"
      >
        SVG motion for the modern web
      </text>
    </svg>
  </body>
</html>
```

Visually: A dark space-themed hero section with twinkling stars, floating geometric shapes (triangle, square, circle, diamond) drifting gently in different patterns, and bold centered text. The shapes float independently with different timing, creating depth and life without being distracting.

## Project 7: Data Visualization Animation (Chart Bars Growing)

A complete animated bar chart with labels, values, grid lines, and staggered entrance.

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        display: grid;
        place-items: center;
        min-height: 100vh;
        background: #f8f9fa;
        font-family: sans-serif;
      }
    </style>
  </head>
  <body>
    <svg width="500" height="350" viewBox="0 0 500 350">
      <style>
        .grid-line {
          stroke: #e9ecef;
          stroke-width: 1;
        }
        .axis {
          stroke: #adb5bd;
          stroke-width: 1.5;
        }
        .bar-group rect {
          transition: opacity 0.2s;
        }
        .bar-group:hover rect {
          opacity: 0.8;
        }
        .bar-group:hover text {
          opacity: 1;
        }
        .value-label {
          opacity: 0;
          transition: opacity 0.2s;
          font-size: 12px;
          fill: #333;
        }
      </style>

      <!-- Grid lines -->
      <line class="grid-line" x1="60" y1="60" x2="460" y2="60" />
      <line class="grid-line" x1="60" y1="110" x2="460" y2="110" />
      <line class="grid-line" x1="60" y1="160" x2="460" y2="160" />
      <line class="grid-line" x1="60" y1="210" x2="460" y2="210" />
      <line class="grid-line" x1="60" y1="260" x2="460" y2="260" />

      <!-- Y-axis labels -->
      <text x="50" y="65" text-anchor="end" font-size="10" fill="#868e96">100</text>
      <text x="50" y="115" text-anchor="end" font-size="10" fill="#868e96">80</text>
      <text x="50" y="165" text-anchor="end" font-size="10" fill="#868e96">60</text>
      <text x="50" y="215" text-anchor="end" font-size="10" fill="#868e96">40</text>
      <text x="50" y="265" text-anchor="end" font-size="10" fill="#868e96">20</text>

      <!-- Axes -->
      <line class="axis" x1="60" y1="50" x2="60" y2="310" />
      <line class="axis" x1="60" y1="310" x2="470" y2="310" />

      <!-- Bar groups with labels -->
      <g class="bar-group">
        <rect class="data-bar" x="90" y="310" width="45" height="0" fill="#4263eb" rx="3" />
        <text class="value-label" x="112" y="0">85</text>
        <text x="112" y="328" text-anchor="middle" font-size="11" fill="#495057">React</text>
      </g>
      <g class="bar-group">
        <rect class="data-bar" x="165" y="310" width="45" height="0" fill="#0ca678" rx="3" />
        <text class="value-label" x="187" y="0">72</text>
        <text x="187" y="328" text-anchor="middle" font-size="11" fill="#495057">Vue</text>
      </g>
      <g class="bar-group">
        <rect class="data-bar" x="240" y="310" width="45" height="0" fill="#f76707" rx="3" />
        <text class="value-label" x="262" y="0">91</text>
        <text x="262" y="328" text-anchor="middle" font-size="11" fill="#495057">Svelte</text>
      </g>
      <g class="bar-group">
        <rect class="data-bar" x="315" y="310" width="45" height="0" fill="#ae3ec9" rx="3" />
        <text class="value-label" x="337" y="0">65</text>
        <text x="337" y="328" text-anchor="middle" font-size="11" fill="#495057">Angular</text>
      </g>
      <g class="bar-group">
        <rect class="data-bar" x="390" y="310" width="45" height="0" fill="#e8590c" rx="3" />
        <text class="value-label" x="412" y="0">78</text>
        <text x="412" y="328" text-anchor="middle" font-size="11" fill="#495057">Solid</text>
      </g>

      <!-- Title -->
      <text x="260" y="30" text-anchor="middle" font-size="16" fill="#212529" font-weight="bold">
        Developer Satisfaction 2024
      </text>
    </svg>

    <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
    <script>
      const values = [85, 72, 91, 65, 78];
      const maxHeight = 250; // pixels for 100%
      const bars = document.querySelectorAll(".data-bar");
      const labels = document.querySelectorAll(".value-label");

      gsap.to(bars, {
        height: (i) => (values[i] / 100) * maxHeight,
        y: (i) => -(values[i] / 100) * maxHeight,
        duration: 1,
        ease: "back.out(1.2)",
        stagger: 0.12,
        delay: 0.3,
      });

      // Position value labels above bars after animation
      gsap.to(labels, {
        y: (i) => 310 - (values[i] / 100) * maxHeight - 8,
        opacity: 1,
        duration: 0.4,
        stagger: 0.12,
        delay: 1.2,
      });
    </script>
  </body>
</html>
```

Visually: A polished bar chart titled "Developer Satisfaction 2024" with five colored bars (React, Vue, Svelte, Angular, Solid). On load, bars grow upward with bouncy stagger timing. After bars finish, value labels fade in above each bar. Hovering a bar dims it slightly and shows the value. Grid lines and axis labels provide context.

## Summary

These projects demonstrate the full range of SVG animation:

| Project         | Techniques Used                                          |
| --------------- | -------------------------------------------------------- |
| Logo Reveal     | stroke-dasharray, fill animation, sequencing with delays |
| Loading Set     | rotation, scale, opacity, stagger                        |
| Infographic     | GSAP ScrollTrigger, stagger, line drawing                |
| Interactive Map | CSS transitions, :hover, transform                       |
| Icon Set        | path morphing, class toggling, CSS transitions           |
| Hero Section    | floating keyframes, twinkle, multiple timing             |
| Data Viz        | GSAP stagger, back easing, dynamic values                |

Each project is self-contained and copy-paste ready. Combine techniques across projects to build your own custom animations.
