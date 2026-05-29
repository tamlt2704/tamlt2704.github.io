# Installation & Python Version Management

[prev: Overview](chapter-00-overview.md) | [next: Project Management](chapter-02-projects.md)

## Installing uv

### Linux / macOS (recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Via pip

```bash
pip install uv
```

### Via Homebrew

```bash
brew install uv
```

### Via Cargo

```bash
cargo install --git https://github.com/astral-sh/uv uv
```

## Verify Installation

```bash
uv --version
```

Output:

```
uv 0.7.x
```

## Upgrading uv

```bash
uv self update
```

## Shell Completion

```bash
# Bash
uv generate-shell-completion bash >> ~/.bashrc

# Zsh
uv generate-shell-completion zsh >> ~/.zshrc

# Fish
uv generate-shell-completion fish > ~/.config/fish/completions/uv.fish

# PowerShell
uv generate-shell-completion powershell >> $PROFILE
```

## Python Version Management

uv replaces pyenv entirely. It downloads prebuilt Python binaries — no compilation, no build dependencies, installs in seconds.

### Install Python versions

```bash
# Install latest stable
uv python install

# Install specific version
uv python install 3.12

# Install multiple versions
uv python install 3.11 3.12 3.13
```

Output:

```
Installed Python 3.12.7 in 3.2s
 + cpython-3.12.7-linux-x86_64
```

### List available and installed versions

```bash
uv python list
```

Output:

```
cpython-3.13.0    /home/user/.local/share/uv/python/cpython-3.13.0/bin/python3
cpython-3.12.7    /home/user/.local/share/uv/python/cpython-3.12.7/bin/python3
cpython-3.11.10   <download available>
```

### Pin a Python version for a project

```bash
uv python pin 3.12
```

Creates `.python-version`:

```
3.12
```

All subsequent `uv` commands in this directory use Python 3.12 automatically.

### Where Python is installed

```bash
uv python dir
```

## Comparison with pyenv

| Task                | pyenv                | uv                       |
| ------------------- | -------------------- | ------------------------ |
| Install Python      | `pyenv install 3.12` | `uv python install 3.12` |
| List versions       | `pyenv versions`     | `uv python list`         |
| Set local version   | `pyenv local 3.12`   | `uv python pin 3.12`     |
| Shims needed        | Yes                  | No                       |
| Compile from source | Yes (slow)           | No (prebuilt binaries)   |
