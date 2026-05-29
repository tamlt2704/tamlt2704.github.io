# Chapter 9: Export — Publishing Documents

[prev: Babel](chapter-08-babel.md) | [next: Workflows](chapter-10-workflows.md)

Org Mode exports to HTML, PDF (via LaTeX), Markdown, ODT, reveal.js slides, and more — all from the same source file.

## Export Dispatcher

| Keybinding    | Action                    |
| ------------- | ------------------------- |
| `C-c C-e`     | Open export dispatcher    |
| `C-c C-e h h` | Export to HTML file       |
| `C-c C-e h o` | Export to HTML and open   |
| `C-c C-e l l` | Export to LaTeX file      |
| `C-c C-e l p` | Export to PDF (via LaTeX) |
| `C-c C-e m m` | Export to Markdown        |
| `C-c C-e o o` | Export to ODT             |

## Export Options

Set at the top of your file:

```org
#+TITLE: My Document
#+AUTHOR: Your Name
#+DATE: 2024-03-20
#+LANGUAGE: en
#+OPTIONS: toc:2 num:t H:4 ^:nil
```

Common OPTIONS:

| Option       | Meaning                                        |
| ------------ | ---------------------------------------------- |
| `toc:2`      | Table of contents depth 2 (nil to disable)     |
| `num:t`      | Numbered headings (nil to disable)             |
| `H:4`        | Heading levels to export (deeper becomes list) |
| `^:nil`      | Don't interpret underscores as subscripts      |
| `author:nil` | Don't include author                           |
| `date:nil`   | Don't include date                             |
| `email:t`    | Include email                                  |

## HTML Export

```org
#+TITLE: Project Report
#+HTML_HEAD: <link rel="stylesheet" type="text/css" href="style.css"/>
#+HTML_HEAD_EXTRA: <style>body { max-width: 800px; margin: auto; }</style>

* Introduction

Content here...
```

### Custom CSS

```org
#+HTML_HEAD: <link rel="stylesheet" href="https://example.com/org.css"/>
```

### Per-element HTML attributes

```org
#+ATTR_HTML: :class highlight :id intro
* Introduction

#+ATTR_HTML: :width 600
[[file:image.png]]
```

## LaTeX/PDF Export

Requires a LaTeX distribution (TeX Live, MiKTeX).

```org
#+TITLE: Academic Paper
#+AUTHOR: Researcher
#+LATEX_CLASS: article
#+LATEX_HEADER: \usepackage{geometry}
#+LATEX_HEADER: \geometry{margin=1in}

* Abstract

This paper explores...
```

LaTeX classes: `article`, `report`, `book`, `beamer`.

## Markdown Export

```org
#+OPTIONS: toc:nil
#+TITLE: README
```

`C-c C-e m m` produces a `.md` file.

## Reveal.js Slides

Install `ox-reveal`:

```org
#+begin_src elisp
(require 'ox-reveal)
#+end_src
```

```org
#+TITLE: My Presentation
#+REVEAL_ROOT: https://cdn.jsdelivr.net/npm/reveal.js
#+REVEAL_THEME: moon
#+OPTIONS: toc:nil num:nil

* Slide 1

First slide content

* Slide 2

** Vertical slide 2.1

Nested headings become vertical slides

** Vertical slide 2.2

More content

* Slide 3

#+ATTR_REVEAL: :frag roll-in
- Point 1
- Point 2
- Point 3
```

## Beamer Presentations (PDF slides)

```org
#+TITLE: Beamer Talk
#+LATEX_CLASS: beamer
#+BEAMER_THEME: Madrid
#+OPTIONS: H:2

* Section One

** Frame Title

- Bullet one
- Bullet two

** Another Frame

Content with a code block:

#+begin_src python
print("Hello Beamer!")
#+end_src
```

## Publishing Projects

Publish entire directories of Org files as a website:

```org
#+begin_src elisp
(setq org-publish-project-alist
      '(("my-site-pages"
         :base-directory "~/org/site/"
         :base-extension "org"
         :publishing-directory "~/public_html/"
         :publishing-function org-html-publish-to-html
         :with-toc nil
         :section-numbers nil
         :html-head "<link rel=\"stylesheet\" href=\"style.css\"/>")
        ("my-site-static"
         :base-directory "~/org/site/"
         :base-extension "css\\|js\\|png\\|jpg"
         :publishing-directory "~/public_html/"
         :publishing-function org-publish-attachment)
        ("my-site" :components ("my-site-pages" "my-site-static"))))
#+end_src
```

| Keybinding    | Action                  |
| ------------- | ----------------------- |
| `C-c C-e P p` | Publish current project |
| `C-c C-e P a` | Publish all projects    |
| `C-c C-e P f` | Publish current file    |

## Selective Export

Exclude headings with tags:

```org
#+EXCLUDE_TAGS: noexport

* This gets exported
* This does not :noexport:
```

Export only specific subtree: place cursor on heading, `C-c C-e` then check "Subtree" option.

## Exercises

1. Export a document to HTML with `C-c C-e h o`
2. Add custom CSS via `#+HTML_HEAD`
3. Create a reveal.js presentation with 5 slides
4. Set up a publishing project for a directory
5. Try exporting the same file to HTML, PDF, and Markdown
