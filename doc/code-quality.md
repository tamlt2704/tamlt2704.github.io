# Code Quality Setup — Prettier, ESLint, Format on Save, Git Hooks

Make your code look professional and consistent automatically.

---

## What We're Setting Up

| Tool               | What it does                                                |
| ------------------ | ----------------------------------------------------------- |
| **Prettier**       | Formats code (indentation, quotes, semicolons, line length) |
| **ESLint**         | Catches bugs and bad patterns (already installed)           |
| **Format on Save** | Auto-formats when you hit Ctrl+S                            |
| **Husky**          | Runs scripts on git commit (pre-commit hook)                |
| **lint-staged**    | Only checks files you're committing (fast)                  |

**The flow:**

```
You write messy code
       ↓
Hit Ctrl+S → Prettier formats it instantly
       ↓
You run `git commit`
       ↓
Husky triggers lint-staged
       ↓
lint-staged runs Prettier + ESLint on staged files only
       ↓
If errors → commit blocked (fix first)
If clean → commit goes through ✓
```

---

## Step 1: Install Prettier

```bash
npm install -D prettier eslint-config-prettier
```

| Package                  | Why                                                                      |
| ------------------------ | ------------------------------------------------------------------------ |
| `prettier`               | The formatter                                                            |
| `eslint-config-prettier` | Turns off ESLint rules that conflict with Prettier (so they don't fight) |

---

## Step 2: Create Prettier Config

Create `.prettierrc` in the project root:

```json
{
  "semi": false,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

| Option                        | What it does                                      | Example                          |
| ----------------------------- | ------------------------------------------------- | -------------------------------- |
| `semi: false`                 | No semicolons at end of lines                     | `const x = 1` not `const x = 1;` |
| `singleQuote: false`          | Use double quotes                                 | `"hello"` not `'hello'`          |
| `tabWidth: 2`                 | 2 spaces for indentation                          |                                  |
| `trailingComma: "all"`        | Comma after last item in lists                    | `[a, b, c,]`                     |
| `printWidth: 100`             | Wrap lines longer than 100 chars                  |                                  |
| `prettier-plugin-tailwindcss` | Auto-sorts Tailwind classes in a consistent order |                                  |

Install the Tailwind plugin:

```bash
npm install -D prettier-plugin-tailwindcss
```

---

## Step 3: Create Prettier Ignore

Create `.prettierignore` in the project root:

```
node_modules
.next
dist
build
package-lock.json
```

These files should never be formatted.

---

## Step 4: Add Prettier to ESLint

Update your `eslint.config.mjs` to include `eslint-config-prettier` — this disables ESLint formatting rules that clash with Prettier:

```js
import { defineConfig, globalIgnores } from "eslint/config"
import { FlatCompat } from "@eslint/eslintrc"
import { dirname } from "path"
import { fileURLToPath } from "url"

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const compat = new FlatCompat({ baseDirectory: __dirname })

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  ...compat.extends("prettier"),
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
])

export default eslintConfig
```

**What changed:** Added `...compat.extends("prettier")` after the other configs. It must be last so it overrides their formatting rules.

`compat.extends()` is needed because `eslint-config-prettier` uses the old config format — `FlatCompat` adapts it to the new flat config style.

---

## Step 5: Test It Works

Format the whole project once:

```bash
npx prettier --write .
```

Check for lint errors:

```bash
npm run lint
```

If both pass with no errors, you're good.

---

## Step 6: Format on Save (VS Code)

Create `.vscode/settings.json` in your project root:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

**Also install the VS Code extension:** Search for "Prettier - Code formatter" by Prettier (`esbenp.prettier-vscode`) and install it.

Now every time you press `Ctrl+S`, Prettier formats the file automatically.

**Why put this in the project (not global settings)?**

- Anyone who clones your repo gets the same settings
- Different projects can have different formatters
- It's committed to git — the team shares it

---

## Step 7: Install Husky + lint-staged

```bash
npm install -D husky lint-staged
npx husky init
```

`npx husky init` does two things:

1. Creates a `.husky/` folder
2. Adds a `prepare` script to `package.json` (runs `husky` on `npm install`)

---

## Step 8: Configure lint-staged

Add this to your `package.json`:

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["prettier --write", "eslint --fix"],
    "*.{json,css,md}": ["prettier --write"]
  }
}
```

**What this does:**

- When you commit `.ts/.tsx/.js/.jsx` files → format them AND lint them
- When you commit `.json/.css/.md` files → just format them
- `--write` and `--fix` modify the files in place before the commit goes through

---

## Step 9: Set Up the Pre-Commit Hook

Replace the content of `.husky/pre-commit` with:

```bash
npx lint-staged
```

**What happens now on every `git commit`:**

```
git commit -m "add navbar"
       ↓
Husky runs .husky/pre-commit
       ↓
lint-staged finds your staged files
       ↓
Runs prettier --write on them (formats)
       ↓
Runs eslint --fix on .ts/.tsx files (fixes lint issues)
       ↓
If eslint finds unfixable errors → commit BLOCKED ❌
       ↓
If all clean → commit goes through ✓
```

---

## Step 10: Test the Hook

```bash
# Stage a file
git add app/page.tsx

# Try to commit
git commit -m "test: check pre-commit hook"
```

You should see lint-staged output showing Prettier and ESLint running. If your code is clean, the commit succeeds.

---

## Step 11: Add Scripts to package.json

Add convenience scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

| Script                 | When to use                              |
| ---------------------- | ---------------------------------------- |
| `npm run format`       | Format everything now                    |
| `npm run format:check` | Check if anything is unformatted (CI/CD) |
| `npm run lint`         | Run ESLint on everything                 |

---

## Summary — What's in Your Project Now

```
javizhome/
├── .husky/
│   └── pre-commit          ← runs lint-staged before every commit
├── .vscode/
│   └── settings.json       ← format on save
├── .prettierrc             ← formatting rules
├── .prettierignore         ← files to skip
├── eslint.config.mjs       ← linting rules (includes "prettier")
├── package.json            ← lint-staged config + scripts
└── ...
```

**The developer experience:**

1. Write code however you want
2. Hit `Ctrl+S` → instantly formatted
3. `git commit` → automatically checked and fixed
4. Bad code can't get into git

---

## Common Questions

### Prettier vs ESLint — what's the difference?

|              | Prettier                              | ESLint                                               |
| ------------ | ------------------------------------- | ---------------------------------------------------- |
| **What**     | Formatting (how code looks)           | Logic (how code works)                               |
| **Examples** | Indentation, quotes, line breaks      | Unused variables, missing dependencies, bad patterns |
| **Opinion**  | Very opinionated — few config options | Highly configurable                                  |
| **Auto-fix** | Always (it rewrites the file)         | Sometimes (some rules can auto-fix)                  |

They work together — Prettier handles the look, ESLint handles correctness.

### What if Prettier and ESLint disagree?

That's what `eslint-config-prettier` does — it turns off all ESLint rules about formatting, so Prettier always wins on style questions. ESLint focuses only on bugs/logic.

### Can I change the style?

Edit `.prettierrc`. Common tweaks:

```json
{
  "semi": true, // add semicolons back
  "singleQuote": true, // use 'single' instead of "double"
  "printWidth": 80, // shorter lines
  "tabWidth": 4 // 4-space indent
}
```

After changing, run `npm run format` to reformat everything.

### What if the hook is annoying during quick experiments?

Skip it once with:

```bash
git commit -m "wip" --no-verify
```

`--no-verify` bypasses the pre-commit hook. Use sparingly — it's there to protect you.
