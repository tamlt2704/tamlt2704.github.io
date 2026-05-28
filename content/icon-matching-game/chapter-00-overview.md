# Chapter 0: The Game That Teaches React

## Chapters

- [Chapter 0: Overview (this page)](/blog/icon-matching-game/chapter-00-overview)
- [Chapter 1: First Icons on Screen](/blog/icon-matching-game/chapter-01-setup)
- [Chapter 2: The Card Grid](/blog/icon-matching-game/chapter-02-grid)
- [Chapter 3: Flip & Match Logic](/blog/icon-matching-game/chapter-03-flip-logic)
- [Chapter 4: Polish & Features](/blog/icon-matching-game/chapter-04-polish)

---

## The Idea

You've seen those memory card games. Flip two cards, find a match, repeat until the board is clear. Simple enough that a five-year-old can play. Complex enough that building one teaches you real React patterns.

We're going to build one with icons — animals, tech logos, sports, food — because variety makes it fun and `react-icons` gives us hundreds to choose from.

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   ┌────┐  ┌────┐  ┌────┐  ┌────┐              │
│   │ ?  │  │ 🐱 │  │ ?  │  │ ?  │              │
│   └────┘  └────┘  └────┘  └────┘              │
│   ┌────┐  ┌────┐  ┌────┐  ┌────┐              │
│   │ 🐘 │  │ ?  │  │ ?  │  │ 🐘 │  ← matched! │
│   └────┘  └────┘  └────┘  └────┘              │
│   ┌────┐  ┌────┐  ┌────┐  ┌────┐              │
│   │ ?  │  │ ?  │  │ 🐱 │  │ ?  │              │
│   └────┘  └────┘  └────┘  └────┘              │
│                                                 │
│   Moves: 7    Topic: 🐾 Animals    Grid: 4×4   │
│                                                 │
└─────────────────────────────────────────────────┘
```

## What You'll Build

The final game has these features:

| Feature                 | Description                                    |
| ----------------------- | ---------------------------------------------- |
| Grid sizes 4×4 to 20×20 | Even and odd sizes supported                   |
| 4 icon topics           | Tech, Animals, Sports, Food — mix and match    |
| Secret card             | On odd grids, one hidden treasure card to find |
| Reveal All              | Show all cards for previewing or printing      |
| Print to A4             | Cards auto-size to fit paper                   |
| B&W mode                | Black and white for printer-friendly output    |
| Move counter            | Track how many flips it takes                  |
| Win detection           | Celebration when all pairs matched             |

## What You'll Learn

Each chapter introduces React concepts through game features:

| Chapter | Feature            | React Concept                                      |
| ------- | ------------------ | -------------------------------------------------- |
| 1       | Icons on screen    | Components, imports, multiple icon sets            |
| 2       | The card grid      | `useState`, arrays, shuffle, dynamic sizing        |
| 3       | Flip & match logic | `useEffect`, `useCallback`, event handlers, timers |
| 4       | Topics, print, B&W | Derived state, multi-select, CSS print media       |

## Project Structure

```
app/
└── games/
    └── matching/
        ├── page.tsx           ← route entry (metadata)
        └── MatchingGame.tsx   ← all game logic (~250 lines)
```

One component file. No external state library. No backend. Just React fundamentals.

## Prerequisites

- Next.js project with App Router
- React 18+ (hooks)
- TypeScript
- Tailwind CSS

---

## Ready?

Let's get icons on screen.

[Chapter 1: First Icons on Screen →](/blog/icon-matching-game/chapter-01-setup)
