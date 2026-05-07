# Chapter 7: Publish Anywhere — Export to HTML, PDF, and Markdown

[← Ch 6](chapter-06-links-attachments.md) | [Ch 8 →](chapter-08-babel.md)

---

## The Problem

You write documentation in org-mode. It's great for *you*. But your team needs a README on GitHub (Markdown). Your manager wants a PDF report. The blog needs HTML. You're maintaining the same content in three formats, and they're already out of sync.

---

## The Naive Attempt

You write in org-mode, then manually reformat for each output:
- Copy to a `.md` file, convert `*` headings to `#` headings
- Copy to Google Docs, add formatting, export PDF
- Copy to your blog CMS, add HTML tags

Every update means updating three places. You stop updating two of them.

---

## Nadia's Way: Write Once, Export Everywhere

> "I write everything in org. Blog posts, documentation, reports, presentations. When I need output, I press `C-c C-e` and pick a format. One source of truth. The export handles formatting."

---

## The Export Dispatcher

Press `C-c C-e` to open the export dispatcher:

```
Export:
[h] HTML        [l] LaTeX/PDF     [m] Markdown
[a] ASCII       [o] ODT           [t] Plain text

Options:
[b] Body only   [s] Subtree only  [v] Visible only
```

Each format has sub-options:
- `h h` — Export to HTML file
- `h o` — Export to HTML and open in browser
- `l p` — Export to PDF (via LaTeX)
- `m m` — Export to Markdown file

---

## HTML Export

The most common export for developers. Write docs in org, publish as HTML.

```org
#+TITLE: API Documentation
#+AUTHOR: Your Name
#+DATE: 2026-01-15
#+OPTIONS: toc:2 num:t

* Authentication
  All endpoints require a Bearer token in the Authorization header.

** Getting a Token
   #+BEGIN_SRC bash
   curl -X POST https://api.example.com/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "secret"}'
   #+END_SRC

   Response:
   #+BEGIN_SRC json
   {
     "token": "eyJhbGciOiJIUzI1NiIs...",
     "expires_in": 3600
   }
   #+END_SRC

** Using the Token
   Include in all requests:
   #+BEGIN_SRC bash
   curl https://api.example.com/projects \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
   #+END_SRC

* Endpoints
** GET /projects
   Returns all projects for the authenticated user.

   | Parameter | Type   | Required | Description          |
   |-----------+--------+----------+----------------------|
   | page      | int    | no       | Page number (def: 1) |
   | limit     | int    | no       | Items per page (def: 20) |
   | status    | string | no       | Filter by status     |
```

Press `C-c C-e h o` — opens a styled HTML page in your browser. Table of contents, syntax-highlighted code blocks, formatted tables. Zero CSS work.

---

## Export Options

Control export behavior with `#+OPTIONS` at the top of your file:

```org
#+TITLE: My Document
#+AUTHOR: Your Name
#+DATE: 2026-01-15
#+DESCRIPTION: A brief description
#+OPTIONS: toc:2 num:t author:t date:t
```

| Option | Values | Effect |
|---|---|---|
| `toc:` | `t`, `nil`, `2` | Table of contents (t=yes, nil=no, 2=depth) |
| `num:` | `t`, `nil` | Section numbering |
| `author:` | `t`, `nil` | Show author |
| `date:` | `t`, `nil` | Show date |
| `H:` | number | Heading levels to export |
| `^:` | `t`, `nil`, `{}` | Interpret `_` and `^` as sub/superscript |
| `broken-links:` | `t`, `mark` | How to handle broken links |

---

## PDF Export (via LaTeX)

For professional-looking documents:

```
C-c C-e l p
```

This converts org → LaTeX → PDF. You need a LaTeX distribution installed:

```bash
# Ubuntu/Debian
sudo apt install texlive-full

# macOS
brew install --cask mactex

# Or minimal:
sudo apt install texlive-latex-base texlive-fonts-recommended
```

Customize the PDF:

```org
#+TITLE: Sprint 14 Report
#+AUTHOR: Engineering Team
#+DATE: January 2026
#+LATEX_CLASS: article
#+LATEX_HEADER: \usepackage{geometry}
#+LATEX_HEADER: \geometry{margin=1in}
```

---

## Markdown Export

For GitHub READMEs, wikis, and anything that expects Markdown:

```
C-c C-e m m
```

This creates a `.md` file from your `.org` file. Your org headings become `#` headings, links convert, code blocks convert.

### Practical: Write README in Org, Export for GitHub

```org
#+TITLE: Dashboard API
#+OPTIONS: toc:nil num:nil

* Dashboard API

  A real-time project management API built with FastAPI.

** Quick Start

   #+BEGIN_SRC bash
   git clone https://github.com/company/dashboard-api
   cd dashboard-api
   docker-compose up -d
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   #+END_SRC

** Features

   - JWT authentication
   - Real-time WebSocket updates
   - File upload with chunking
   - Comprehensive API documentation at ~/docs~

** API Reference

   | Endpoint          | Method | Description        |
   |-------------------+--------+--------------------|
   | ~/auth/login~     | POST   | Get access token   |
   | ~/projects~       | GET    | List projects      |
   | ~/projects~       | POST   | Create project     |
   | ~/projects/{id}~  | GET    | Get project detail |
   | ~/tasks~          | POST   | Create task        |

** License

   MIT
```

Export with `C-c C-e m m` → produces `README.md` ready for GitHub.

---

## Selective Export

### Export Only a Subtree

Put cursor on a heading, then `C-c C-e` and press `s` before choosing format:

```
C-c C-e s h o    → export only current subtree to HTML
C-c C-e s m m    → export only current subtree to Markdown
```

### Export Only Visible Content

Fold your document to show only what you want, then:

```
C-c C-e v h o    → export only visible content to HTML
```

---

## Excluding Sections from Export

Tag a heading with `:noexport:` to skip it:

```org
* Public Documentation
  This gets exported.

* Internal Notes :noexport:
  This stays private.
  
* Draft Ideas :noexport:
  Not ready for publication.
```

---

## Custom HTML Styling

Add CSS to your HTML export:

```org
#+HTML_HEAD: <link rel="stylesheet" type="text/css" href="style.css" />
#+HTML_HEAD_EXTRA: <style>body { max-width: 800px; margin: auto; }</style>
```

Or use a built-in theme:

```org
#+SETUPFILE: https://fniessen.github.io/org-html-themes/org/theme-readtheorg.setup
```

---

## Blog Post Workflow

Nadia's blog workflow:

```org
#+TITLE: Understanding Async/Await in Python
#+DATE: <2026-01-15 Wed>
#+FILETAGS: :python:async:tutorial:
#+OPTIONS: toc:t num:nil

* Introduction
  If you've ever written ~await asyncio.sleep(1)~ and wondered
  what's actually happening...

* The Event Loop
  ...

* Practical Examples
  #+BEGIN_SRC python
  import asyncio

  async def fetch_data(url: str) -> dict:
      async with aiohttp.ClientSession() as session:
          async with session.get(url) as response:
              return await response.json()
  #+END_SRC

* Conclusion
  ...
```

Export to HTML for the blog. The same file is her draft, her published post, and her reference notes.

---

## Key Bindings Summary

| Binding | Action |
|---|---|
| `C-c C-e` | Open export dispatcher |
| `C-c C-e h h` | Export to HTML file |
| `C-c C-e h o` | Export to HTML and open |
| `C-c C-e l p` | Export to PDF (via LaTeX) |
| `C-c C-e m m` | Export to Markdown |
| `C-c C-e t a` | Export to plain text (ASCII) |
| `C-c C-e s` | Subtree export (prefix) |
| `C-c C-e v` | Visible-only export (prefix) |

---

## Exercise: Export Your Documentation

1. Take one of your org files (project notes, sprint plan, or create a new one).
2. Add proper export headers (`#+TITLE`, `#+AUTHOR`, `#+OPTIONS`).
3. Export it three ways:
   - `C-c C-e h o` — view as HTML in browser
   - `C-c C-e m m` — check the Markdown output
   - `C-c C-e t a` — see the plain text version
4. Create a simple project README in org format and export to Markdown.
5. Add a `:noexport:` section with private notes that don't appear in output.

> **Nadia's tip:** "I write my blog posts, project docs, and reports all in org. The source file has my drafts, notes, and TODOs mixed in — tagged `:noexport:`. The exported version is clean. One file, two purposes: working document AND published output."

---

[← Ch 6](chapter-06-links-attachments.md) | [Ch 8: Code Blocks and Literate Programming →](chapter-08-babel.md)
