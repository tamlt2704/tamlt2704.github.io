# Algorithm Visualiser — Tutorial Guide

## Who is this for?

You're a developer who knows Java or Python. You understand arrays, loops, recursion. You might have heard of React or Next.js but haven't built anything serious with them. That's fine — this tutorial starts from zero on the frontend side.

## What are we building?

A web page with two panels:

```
┌─────────────────────────────┬──────────────────────────────────┐
│                             │                                  │
│   Java/Python code          │    Visual animation              │
│   with highlighted line     │    (bars, nodes, arrows)         │
│                             │                                  │
│   public void bubbleSort()  │    ██ ████ ██ ████████ ██████   │
│ > if (arr[j] > arr[j+1])   │       ↑↑                        │
│     swap(arr, j, j+1)      │    comparing these two           │
│                             │                                  │
├─────────────────────────────┴──────────────────────────────────┤
│          [ ◀ Prev ]  [ Next ▶ ]  [ ▶ Play ]  [ ↺ Reset ]      │
└────────────────────────────────────────────────────────────────┘
```

You click "Next" and the code highlights the next line while the visualisation animates the corresponding operation (a swap, a comparison, a node being visited).

## Why these technology choices?

| Choice | Why | Alternatives considered |
|--------|-----|------------------------|
| **Next.js** | Gives us routing, fast dev server, and easy deployment to GitHub Pages. It's React under the hood — you learn React naturally as we go. | Plain HTML+JS (no components, hard to scale), Vite+React (no routing out of the box), Vue/Svelte (smaller ecosystem for visualisation libraries) |
| **D3.js** | The gold standard for data visualisation on the web. Gives us precise control over SVG elements — we can animate individual bars, nodes, edges exactly how we want. | Chart.js (too high-level, can't animate individual elements), Canvas API (no DOM, harder to debug), Three.js (overkill — we don't need 3D) |
| **Rough.js** | Makes visualisations look hand-drawn/sketchy — less intimidating for learners, feels like a whiteboard. We'll combine it with D3 so D3 handles positioning/data and Rough.js handles rendering style. | Plain SVG (clinical look), CSS animations (limited to DOM elements, can't draw paths) |
| **Tailwind CSS** | Already included in this project. Lets us style without writing CSS files — just add classes. | Plain CSS (more files to manage), styled-components (React-specific, overkill for our use) |
| **TypeScript** | Catches bugs before you run the code. Next.js already set it up for us. | Plain JavaScript (no autocomplete, no type errors caught early) |

## Chapter overview

Each chapter introduces ONE new concept. No chapter introduces D3 and state management and animations all at once.

| # | Chapter | What you'll learn | What you'll build |
|---|---------|-------------------|-------------------|
| 01 | Project Setup | Install libraries, understand the file structure | A working dev server with D3 + Rough.js ready |
| 02 | Your First Component | What a React component is, props, JSX | A static two-panel layout |
| 03 | State and Interactivity | `useState`, event handlers, re-rendering | Working Prev/Next/Play/Reset buttons |
| 04 | Displaying Code | Rendering code with line highlighting | Code panel that highlights the current line |
| 05 | D3 Fundamentals | SVG basics, selections, binds, scales | A static bar chart from an array |
| 06 | Animating with D3 | Transitions, enter/update/exit pattern | Bars that animate on data change |
| 07 | Adding Rough.js | Combining D3 layout with Rough.js rendering | Hand-drawn style bars |
| 08 | The Step Engine | Connecting code lines → visual states | Full bubble sort with synced code + visualisation |
| 09 | Sorting Algorithms | Selection sort, merge sort | Multiple algorithms sharing the same framework |
| 10 | Graph Visualisation | Force layout, node/edge rendering, BFS/DFS | Interactive graph traversal |
| 11 | Multi-language Support | Language tabs, dynamic code loading | Toggle between Java and Python |
| 12 | Polish and Deploy | Speed control, keyboard shortcuts, GitHub Pages | Production-ready page |

## How to use this tutorial

1. Read a chapter
2. Type the code yourself — don't copy-paste (you'll understand it better)
3. Run `npm run dev` and see the result at `http://localhost:3000`
4. If something breaks, compare your code with the chapter's final code
5. Move to the next chapter only when the current one works

## Prerequisites

- Node.js 18+ installed (`node --version` to check)
- A text editor (VS Code recommended)
- A terminal/command prompt
- Basic programming knowledge (variables, loops, functions, arrays)

## Let's start

→ [Chapter 01: Project Setup](./01-PROJECT-SETUP.md)
