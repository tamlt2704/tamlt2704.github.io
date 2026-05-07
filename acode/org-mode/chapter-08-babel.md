# Chapter 8: Code Blocks and Literate Programming — Executable Documents

[← Ch 7](chapter-07-export.md) | [Ch 9 →](chapter-09-clocking.md)

---

## The Problem

You're writing documentation for your API. It includes code examples. But are they correct? You wrote them three months ago. The API changed. The examples are probably broken, but you won't know until someone complains.

Or: you're doing a data analysis. Your notes describe the steps, but the actual code is in a Jupyter notebook. The narrative and the code are in different places. When you update one, the other gets stale.

---

## The Naive Attempt

You keep code examples in your docs and manually test them:
1. Copy code from docs
2. Paste into terminal/REPL
3. Run it
4. Check output
5. Update docs if output changed
6. Forget to do this for 6 months

Or you use Jupyter notebooks — but they're JSON blobs that don't diff well, can't be grepped, and mix presentation with execution in awkward ways.

---

## Nadia's Way: Code That Runs Inside Your Documents

> "Org Babel lets you embed code blocks in your documents and *execute them*. The results appear inline. Your documentation is always up-to-date because it literally runs. And you can mix languages — Python for data processing, SQL for queries, shell for deployment — all in one document."

---

## Source Blocks

A code block in org-mode:

```org
#+BEGIN_SRC python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
#+END_SRC
```

This is just formatted code — it gets syntax highlighting and exports nicely. But with Babel, it also *executes*.

---

## Executing Code Blocks

Put your cursor inside a source block and press `C-c C-c`:

```org
#+BEGIN_SRC python
import math
print(math.sqrt(144))
#+END_SRC

#+RESULTS:
: 12.0
```

The `#+RESULTS:` block appears automatically with the output. Every time you press `C-c C-c`, it re-runs and updates the result.

First time you run code, Emacs asks: "Evaluate this code block? (yes or no)". To skip this confirmation:

```elisp
(setq org-confirm-babel-evaluate nil)  ;; trust all blocks (careful!)
```

Or selectively:

```elisp
(setq org-confirm-babel-evaluate
      (lambda (lang body)
        (not (member lang '("python" "emacs-lisp" "shell")))))
```

---

## Enabling Languages

By default, only Emacs Lisp is enabled. Add languages in your config:

```elisp
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (shell . t)
   (js . t)
   (sql . t)
   (ruby . t)
   (C . t)
   (emacs-lisp . t)))
```

---

## Block Headers: Controlling Execution

```org
#+BEGIN_SRC python :results output
print("This captures stdout")
print("Line 2")
#+END_SRC

#+RESULTS:
: This captures stdout
: Line 2
```

```org
#+BEGIN_SRC python :results value
import math
math.pi
#+END_SRC

#+RESULTS:
: 3.141592653589793
```

| Header | Effect |
|---|---|
| `:results output` | Capture stdout |
| `:results value` | Return value of last expression |
| `:results table` | Format result as org table |
| `:results file` | Result is a filename (for images) |
| `:exports code` | Export only the code (not results) |
| `:exports results` | Export only the results |
| `:exports both` | Export code AND results |
| `:exports none` | Don't export this block |

---

## Variables: Passing Data Between Blocks

```org
#+NAME: project-count
#+BEGIN_SRC python
projects = ["Dashboard", "API", "Mobile"]
len(projects)
#+END_SRC

#+RESULTS: project-count
: 3

#+BEGIN_SRC python :var count=project-count
print(f"We have {count} active projects")
#+END_SRC

#+RESULTS:
: We have 3 active projects
```

Name a block with `#+NAME:`, then reference it with `:var`. Data flows between blocks.

---

## Multiple Languages in One Document

This is where Babel shines. A deployment runbook:

```org
#+TITLE: Deployment Runbook

* Pre-deployment Checks

** Check current version
   #+BEGIN_SRC shell
   curl -s https://api.example.com/health | jq .version
   #+END_SRC

** Run tests
   #+BEGIN_SRC shell :dir ~/code/project
   python -m pytest tests/ -q
   #+END_SRC

* Database Migration

** Check pending migrations
   #+BEGIN_SRC sql :engine postgresql :dbhost localhost :database myapp
   SELECT version, description FROM schema_migrations
   ORDER BY version DESC LIMIT 5;
   #+END_SRC

* Deploy

** Build and push
   #+BEGIN_SRC shell :dir ~/code/project
   docker build -t myapp:latest .
   docker push registry.example.com/myapp:latest
   #+END_SRC

* Post-deployment

** Verify health
   #+BEGIN_SRC python
   import requests
   r = requests.get("https://api.example.com/health")
   print(f"Status: {r.status_code}")
   print(f"Version: {r.json()['version']}")
   #+END_SRC
```

Shell, SQL, Python — all in one document. Execute each block as you go through the runbook.

---

## Tangling: Extract Code from Documents

"Tangling" means extracting code blocks from your org file into standalone source files. This is literate programming — your documentation IS your source code.

```org
#+TITLE: Configuration Module
#+PROPERTY: header-args :tangle config.py

* Configuration

** Environment Variables
   #+BEGIN_SRC python
   import os

   DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
   SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
   DEBUG = os.getenv("DEBUG", "false").lower() == "true"
   #+END_SRC

** Application Settings
   #+BEGIN_SRC python
   APP_NAME = "Dashboard API"
   API_VERSION = "v1"
   MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
   #+END_SRC

** Logging Configuration
   #+BEGIN_SRC python
   import logging

   LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
   LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

   logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
   logger = logging.getLogger(APP_NAME)
   #+END_SRC
```

Run `C-c C-v t` (tangle) — org-mode extracts all code blocks and writes `config.py`:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

APP_NAME = "Dashboard API"
API_VERSION = "v1"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

import logging

LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(APP_NAME)
```

Your documentation and code are the same file. Update the docs, tangle, and the code updates.

---

## Practical: Reproducible Analysis

```org
#+TITLE: Sprint 14 Velocity Analysis

* Data
  #+NAME: sprint-data
  | Sprint | Planned | Completed |
  |--------+---------+-----------|
  |     11 |      34 |        30 |
  |     12 |      32 |        32 |
  |     13 |      35 |        28 |
  |     14 |      30 |        27 |

* Analysis
  #+BEGIN_SRC python :var data=sprint-data :results output
  import statistics

  planned = [row[1] for row in data]
  completed = [row[2] for row in data]
  velocity = [c/p*100 for p, c in zip(planned, completed)]

  print(f"Average planned: {statistics.mean(planned):.1f}")
  print(f"Average completed: {statistics.mean(completed):.1f}")
  print(f"Average velocity: {statistics.mean(velocity):.1f}%")
  print(f"Trend: {'improving' if velocity[-1] > velocity[-2] else 'declining'}")
  #+END_SRC

  #+RESULTS:
  : Average planned: 32.8
  : Average completed: 29.2
  : Average velocity: 89.3%
  : Trend: improving
```

The table IS the data. The code reads from the table. Update the table, re-run the code, results update. Reproducible.

---

## Inline Code

For quick calculations in text:

```org
The sprint has src_python{7 * 5} working days.
```

Exports as: "The sprint has 35 working days."

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c C-c` | Execute code block at point |
| `C-c C-v t` | Tangle (extract code to files) |
| `C-c C-v b` | Execute all blocks in buffer |
| `C-c C-v k` | Clear results |
| `C-c '` | Edit block in native mode (dedicated buffer) |
| `<s Tab` | Insert source block template (org-tempo) |

---

## Exercise: Executable Documentation

1. Create `~/org/babel-test.org` with code blocks in at least 2 languages.
2. Execute each block with `C-c C-c` and verify results appear.
3. Create a block that reads from an org table (use `:var data=table-name`).
4. Write a small literate program:
   - Create an org file that documents a simple script
   - Add `:tangle script.py` to the header
   - Write the code in blocks with explanatory text between them
   - Tangle with `C-c C-v t` and verify the output file works

5. Bonus: Create a "runbook" with shell commands for a common task (deploy, setup, etc.) that you can execute step by step.

> **Nadia's tip:** "Babel changed how I write documentation. My API docs have live examples — I run them before publishing to make sure they still work. My deployment runbooks are executable — I literally step through them block by block. And my analysis reports are reproducible — anyone can re-run the code and verify the numbers."

---

[← Ch 7](chapter-07-export.md) | [Ch 9: Where Does My Time Go? →](chapter-09-clocking.md)
