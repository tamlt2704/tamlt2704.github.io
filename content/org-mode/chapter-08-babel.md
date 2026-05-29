# Chapter 8: Babel — Literate Programming

[prev: Tables](chapter-07-tables.md) | [next: Export](chapter-09-export.md)

Org Babel lets you embed and execute code in your documents. Mix prose with live code in any language — the foundation of reproducible research and literate programming.

## Source Blocks

```org
#+begin_src python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(fibonacci(10))
#+end_src
```

| Keybinding | Action                                   |
| ---------- | ---------------------------------------- |
| `C-c C-c`  | Execute code block                       |
| `C-c '`    | Edit in language major mode              |
| `<s TAB`   | Insert source block template (org-tempo) |

## Executing Code

After `C-c C-c`, results appear below the block:

```org
#+begin_src python
return 2 + 2
#+end_src

#+RESULTS:
: 4
```

Enable languages in your config:

```org
#+begin_src elisp
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (emacs-lisp . t)
   (shell . t)
   (js . t)
   (sql . t)
   (R . t)
   (C . t)))
#+end_src
```

## Supported Languages

Python, Emacs Lisp, Shell (bash/sh), JavaScript, SQL, R, C/C++, Ruby, Perl, Haskell, Clojure, Lua, Octave, Gnuplot, Ditaa, PlantUML, and many more.

## Results Handling

### :results value (default)

Returns the value of the last expression:

```org
#+begin_src python :results value
x = [1, 2, 3, 4, 5]
sum(x)
#+end_src

#+RESULTS:
: 15
```

### :results output

Captures stdout:

```org
#+begin_src python :results output
for i in range(5):
    print(f"Line {i}")
#+end_src

#+RESULTS:
: Line 0
: Line 1
: Line 2
: Line 3
: Line 4
```

### Other result types

```org
#+begin_src python :results table
return [[1, "Alice"], [2, "Bob"], [3, "Charlie"]]
#+end_src

#+begin_src python :results file :file plot.png
import matplotlib.pyplot as plt
plt.plot([1,2,3], [1,4,9])
plt.savefig("plot.png")
"plot.png"
#+end_src
```

## Header Arguments

```org
#+begin_src python :var x=5 :results output
print(f"x = {x}")
#+end_src
```

Common header arguments:

| Argument                          | Purpose            |
| --------------------------------- | ------------------ |
| `:var name=value`                 | Pass variables     |
| `:results output/value`           | What to capture    |
| `:exports code/results/both/none` | What to export     |
| `:session name`                   | Persistent session |
| `:tangle filename`                | Extract to file    |
| `:dir /path`                      | Working directory  |
| `:cache yes`                      | Cache results      |

## Variables Between Blocks

```org
#+NAME: my-data
| x | y |
|---+---|
| 1 | 2 |
| 3 | 4 |

#+begin_src python :var data=my-data
return [row[0] + row[1] for row in data]
#+end_src

#+RESULTS:
| 3 | 7 |
```

## Tangling — Extract Code to Files

```org
#+begin_src python :tangle myapp.py
def main():
    print("Hello from tangled file!")

if __name__ == "__main__":
    main()
#+end_src
```

| Keybinding  | Action                                   |
| ----------- | ---------------------------------------- |
| `C-c C-v t` | Tangle current file (extract all blocks) |

## Noweb References

Reference other blocks by name:

```org
#+NAME: imports
#+begin_src python
import os
import sys
#+end_src

#+NAME: main
#+begin_src python :noweb yes :tangle app.py
<<imports>>

def main():
    print(sys.version)
    print(os.getcwd())

main()
#+end_src
```

## Sessions

Keep state between blocks:

```org
#+begin_src python :session mysession
x = 42
#+end_src

#+begin_src python :session mysession
print(x * 2)  # x persists from previous block
#+end_src

#+RESULTS:
: 84
```

## Exercises

1. Create and execute blocks in Python and Shell:

```org
#+begin_src shell :results output
echo "Today is $(date)"
ls -la | head -5
#+end_src

#+begin_src python :results value
import math
[math.factorial(n) for n in range(10)]
#+end_src
```

2. Pass a table as a variable to a code block
3. Tangle a multi-block file with `C-c C-v t`
4. Use a session to maintain state across blocks
5. Try `:results output` vs `:results value`
