# Chapter 2: Markup — Rich Text and Links

[prev: Basics](chapter-01-basics.md) | [next: TODOs](chapter-03-todos.md)

Org Mode provides lightweight markup for rich text, a powerful linking system, and special blocks for structured content.

## Text Formatting

```org
*bold*
/italic/
_underline_
=verbatim=
~code~
+strikethrough+
```

Markers must be at word boundaries — no space between marker and text.

## Links

Org links: `[[target][description]]` or `[[target]]`

### External Links

```org
[[https://orgmode.org][Org Mode website]]
[[mailto:user@example.com][Send email]]
```

### File Links

```org
[[file:~/documents/notes.org][My notes]]
[[file:./chapter-01.org::*Headings][Jump to Headings]]
```

### Internal Links

```org
* Target Heading

Link to it: [[Target Heading][click here]]

Dedicated targets:
<<my-anchor>>
[[my-anchor][Jump to anchor]]
```

| Keybinding | Action                       |
| ---------- | ---------------------------- |
| `C-c C-l`  | Insert/edit link             |
| `C-c C-o`  | Open link at point           |
| `C-c &`    | Go back after following link |

## Images

```org
#+ATTR_ORG: :width 400
[[file:./images/diagram.png]]
```

| Keybinding    | Action                      |
| ------------- | --------------------------- |
| `C-c C-x C-v` | Toggle inline image display |

## Footnotes

```org
The Org manual[fn:1] is comprehensive.

[fn:1] See https://orgmode.org/manual/
```

| Keybinding  | Action                                |
| ----------- | ------------------------------------- |
| `C-c C-x f` | Insert footnote                       |
| `C-c C-c`   | Jump between reference and definition |

## Special Blocks

### Quote Block

```org
#+begin_quote
The only way to do great work is to love what you do.
— Steve Jobs
#+end_quote
```

### Verse Block (preserves line breaks)

```org
#+begin_verse
Great clouds overhead
Tiny black birds rise and fall
Snow covers Emacs
#+end_verse
```

### Center Block

```org
#+begin_center
This text will be centered in export.
#+end_center
```

### Example Block (no processing)

```org
#+begin_example
Displayed exactly as typed.
  Indentation preserved.
  No *markup* processing.
#+end_example
```

### Source Block

```org
#+begin_src python
def hello():
    print("Hello from Org!")
#+end_src
```

Single-line example with colon-space:

```org
: This line is an example block
```

## Horizontal Rules

Five or more dashes:

```org
-----
```

## Exercises

1. Create a document using all formatting types
2. Insert a link with `C-c C-l` and follow it with `C-c C-o`
3. Add a footnote with `C-c C-x f`
4. Toggle inline images with `C-c C-x C-v`
5. Write a source block and an example block
