# Chapter 0: Setting Up — Your Frontend Workbench

[Chapter 1: First Component →](chapter-01-project-setup.md)

---

## The Problem

Captain Deadline points at the 65-inch TV running `curl -N`. "I want buttons. Colors. A progress bar. Something my mother could use."

You've never built a frontend. You open your laptop. You don't have Node. You don't know what npm is. VS Code has zero extensions installed. The terminal says `node: command not found`.

Let's fix that.

## VS Code

Download from [code.visualstudio.com](https://code.visualstudio.com/) or:

```bash
# macOS
brew install --cask visual-studio-code

# Ubuntu/Debian
sudo snap install code --classic
```

### Essential Extensions

Open VS Code, press `Ctrl+Shift+X` (Extensions), install these:

| Extension | Why |
|---|---|
| **ESLint** | Catches bugs and style issues in real time |
| **Prettier** | Auto-formats on save — no more arguing about semicolons |
| **Tailwind CSS IntelliSense** | Autocomplete for Tailwind classes |
| **TypeScript Importer** | Auto-imports when you type a component name |
| **Error Lens** | Shows errors inline, not just in the gutter |

### Settings

Press `Ctrl+,` → Open Settings (JSON) → paste:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.tabSize": 2,
  "editor.bracketPairColorization.enabled": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "emmet.includeLanguages": { "typescriptreact": "html" }
}
```

Format on save means you never think about formatting again. Prettier decides. You obey.

## Node.js

You need Node 20+ and npm (comes with Node).

```bash
# macOS
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or use nvm (recommended — lets you switch versions)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
nvm install 22
nvm use 22
```

Verify:

```bash
node -v   # → v22.x.x
npm -v    # → 10.x.x
```

## The Terminal

VS Code has a built-in terminal: `` Ctrl+` ``. Use it. You'll live in it.

Quick test — create a file and run it:

```bash
echo 'console.log("Hello from Node")' > test.js
node test.js
# → Hello from Node
rm test.js
```

If that works, you're ready.

## Linting & Formatting

You'll set these up properly in Chapter 1 when you scaffold the project. But here's what they do:

- **ESLint** — finds bugs: unused variables, missing dependencies in hooks, accessibility issues
- **Prettier** — formats code: indentation, quotes, trailing commas
- **TypeScript** — catches type errors before you run the code

Together they mean: if your code has a problem, you'll see a red squiggly line *before* you save. Not after you deploy. Not after Karen reports a bug.

## Quick Check

```bash
node -v && npm -v && code --version
```

If all three print version numbers, you're good. Let's build something.

---

[Chapter 1: First Component →](chapter-01-project-setup.md)
