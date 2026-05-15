# Manim IDE — Teach Programming Visually

Build animated programming tutorials with a VSCode-like IDE on the left and visual output on the right. Teach anything: LeetCode, Pandas, Java, Python.

## Setup with uv

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Python via uv

uv manages Python installations — no need for pyenv or system Python:

```bash
# Install Python 3.12 (recommended for manim compatibility)
uv python install 3.12

# Verify it's available
uv python list
```

### Create Project with Pinned Python

```bash
uv init manim-ide --python 3.12
cd manim-ide
```

This creates the project AND sets `.python-version` to `3.12`, which uv uses for the venv.

### Create the Virtual Environment

uv auto-creates the venv on first `uv add` or `uv sync`, but you can be explicit:

```bash
# Creates .venv/ using Python 3.12
uv venv --python 3.12
```

The `.python-version` file pins it for the team:

```bash
cat .python-version
# 3.12
```

### Add Dependencies

```bash
uv add manim
uv add "manim-voiceover[gtts]"
```

For better voice quality (Azure/ElevenLabs):

```bash
uv add "manim-voiceover[azure]"
# or
uv add "manim-voiceover[elevenlabs]"
```

### Verify

```bash
# Check Python version in the venv
uv run python --version
# Python 3.12.x

# Check manim
uv run manim --version
```

### Project Structure

```
manim-ide/
├── pyproject.toml
├── src/
│   ├── ide.py          # IDE component (this file)
│   ├── scenes/
│   │   ├── leetcode.py
│   │   ├── pandas_demo.py
│   │   └── java_basics.py
│   └── helpers.py
└── media/              # rendered output
```

### Render a Scene

```bash
uv run manim -pqh src/ide.py IDEDemo
```

---

## The IDE Class

Below is the core `IDE` class — a VSCode-like code editor component for Manim.
