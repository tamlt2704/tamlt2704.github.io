# TypeCraft: A TypeScript Survival Story

You've been writing JavaScript for two years. It works. Mostly. Until it doesn't — at 2am, in production, when `undefined is not a function` takes down the checkout page.

Then **Ren**, the tech lead at **ShipFast** — a scrappy logistics startup that tracks packages across 30 countries — pings you:

> "We're rewriting the API in TypeScript. The JavaScript codebase has 47 `// @ts-ignore` comments from the last person who tried. You start Monday."

You show up. The codebase is 12,000 lines of JavaScript with no types, no docs, and variable names like `d`, `tmp2`, and `processStuff`. The previous developer's only comment is `// TODO: fix this later`. That was 18 months ago.

Your mission: learn TypeScript by migrating this mess — one file at a time, one type error at a time.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Junior Developer | "I know JavaScript. How different can it be?" |
| **Ren** | Tech Lead | Types everything. Reviews PRs in 4 minutes. Speaks in generics. |
| **The Compiler** | tsc | Sees all. Forgives nothing. Your strictest teacher. |
| **Legacy Larry** | The Old Codebase | 12,000 lines. No types. Full of `any`. Haunted. |
| **Null** | The Villain | Lurks in every object. Crashes every demo. |
| **Captain Deploy** | CI/CD Pipeline | "Build failed. 47 type errors." |

---

## The Tools

Everything runs on your laptop. No cloud needed.

| Tool | What It Does |
|---|---|
| **Node.js 20+** | JavaScript runtime |
| **TypeScript 5+** | The language (compiles to JavaScript) |
| **tsc** | TypeScript compiler — checks types, emits JS |
| **VS Code** | Editor with built-in TypeScript intelligence |
| **tsx** | Runs TypeScript directly (no compile step for dev) |
| **vitest** | Fast test runner with TypeScript support |

---

## How to Read This

Every chapter follows the same loop:

```
  💥 Something breaks (runtime error, wrong data, impossible bug)
   │
   ▼
  🤔 You figure out what JavaScript let you get away with
   │
   ▼
  🛡️  You learn the TypeScript concept that prevents it
   │
   ▼
  ✓  The compiler catches it at build time — never reaches production
   │
   ▼
  💥 Next thing breaks
```

No concept shows up before you need it. You won't hear about generics until you're copy-pasting the same function for different types. You won't touch discriminated unions until a `switch` statement silently drops a case.

The bugs come first. The types follow.

---

## The Roadmap

| Ch | The Disaster | What You Learn |
|---|---|---|
| 1 | `undefined is not a function` in prod | Basic types, type annotations, `tsc`, `tsconfig.json` |
| 2 | A string sneaks into a number field | Primitives, literal types, type narrowing |
| 3 | An object is missing a field | Interfaces, optional properties, readonly |
| 4 | A function returns the wrong shape | Function types, overloads, void vs undefined |
| 5 | You copy-paste the same function 4 times | Generics — type parameters, constraints |
| 6 | A status field has 47 possible values | Union types, discriminated unions, exhaustive checks |
| 7 | The API response doesn't match the code | Type guards, `unknown`, runtime validation |
| 8 | A refactor breaks 200 files silently | Utility types, mapped types, `keyof`, `typeof` |
| 9 | A library has no types | Declaration files, `@types/*`, module augmentation |
| 10 | The migration is done | Strict mode, the full `tsconfig.json`, what's next |

---

## Prerequisites

Three things: Node.js, a terminal, and an editor.

### Node.js 20+

```bash
# Windows (winget)
winget install OpenJS.NodeJS.LTS

# macOS
brew install node@20

# Linux
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Project Setup

```bash
mkdir shipfast && cd shipfast
npm init -y

# Install TypeScript
npm install --save-dev typescript tsx vitest @types/node

# Initialize tsconfig
npx tsc --init
```

This creates `tsconfig.json` — the compiler's configuration. We'll start lenient and tighten it chapter by chapter.

### Minimal `tsconfig.json` (Chapter 1)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"]
}
```

`strict: false` for now. We'll turn it on when we're ready. (Chapter 10.)

### Verify

```bash
echo 'const msg: string = "TypeScript works"; console.log(msg);' > src/hello.ts
npx tsx src/hello.ts
```

```
TypeScript works
```

If that prints, you're ready.

---

## The Codebase

Throughout this series, we'll migrate ShipFast's package tracking API. The core domain:

```
Packages move through statuses:
  CREATED → PICKED_UP → IN_TRANSIT → OUT_FOR_DELIVERY → DELIVERED

Each package has:
  - tracking ID (string, like "SF-2024-00042")
  - origin / destination (addresses)
  - weight (kg), dimensions
  - current status
  - history of status changes (timestamp + location)
  - estimated delivery date
```

The JavaScript version works. It also lets you set a package's weight to `"banana"`, ship to `undefined`, and deliver a package that was never created. TypeScript will make these impossible.

---

[Next: Chapter 1 — "undefined is not a function" →](chapter-01-first-types.md)
