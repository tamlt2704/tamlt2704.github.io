# Chapter 2: Lather, Rinse, Repeat — The REPL

[prev: Why Clojure?](chapter-01-why-clojure.md) | [next: A Contact Book](chapter-03-contact-book.md)

## Installing Clojure

### macOS

```bash
brew install clojure/tools/clojure
```

### Linux

```bash
curl -L -O https://github.com/clojure/brew-install/releases/latest/download/linux-install.sh
chmod +x linux-install.sh
sudo ./linux-install.sh
```

### Windows

```powershell
winget install --id Clojure.Clojure
```

Verify:

```bash
clj --version
# Clojure CLI version 1.12.x
```

## Starting the REPL

```bash
clj
```

You'll see:

```
Clojure 1.12.0
user=>
```

Type expressions, get results immediately:

```clojure
user=> (+ 1 2 3)
6
user=> (str "Hello" " " "World")
"Hello World"
user=> (* (+ 2 3) (- 10 4))
30
```

## The REPL Is Not a Shell

In most languages, the REPL is a toy for testing snippets. In Clojure, the REPL **is** your development environment. You:

1. Write code in your editor
2. Send it to a running REPL (one keystroke)
3. See the result instantly
4. Iterate

Your program is alive the whole time. You never restart it during development.

## Editor Setup

### VS Code + Calva (Recommended for beginners)

1. Install VS Code
2. Install the "Calva" extension
3. Open a Clojure project folder
4. `Ctrl+Shift+P` → "Calva: Start a Project REPL and Connect"
5. Write code, press `Ctrl+Enter` to evaluate

### Emacs + CIDER

```elisp
;; In your init.el
(use-package cider
  :ensure t)
```

Open a `.clj` file, `M-x cider-jack-in`. Evaluate with `C-c C-e`.

### IntelliJ + Cursive

Install the Cursive plugin. Create a Clojure project. REPL starts automatically.

## REPL Basics

### Arithmetic

```clojure
(+ 1 2)        ;=> 3
(- 10 3)       ;=> 7
(* 4 5)        ;=> 20
(/ 10 3)       ;=> 10/3 (a ratio!)
(/ 10.0 3)     ;=> 3.3333333333333335
(quot 10 3)    ;=> 3 (integer division)
(rem 10 3)     ;=> 1 (remainder)
```

### Strings

```clojure
(str "age: " 25)              ;=> "age: 25"
(clojure.string/upper-case "hello")  ;=> "HELLO"
(clojure.string/split "a,b,c" #",")  ;=> ["a" "b" "c"]
(count "hello")               ;=> 5
(subs "hello" 1 3)            ;=> "el"
```

### Booleans and Nil

```clojure
true            ;=> true
false           ;=> false
nil             ;=> nil (like null — means "nothing")

;; Only false and nil are falsy. Everything else is truthy:
(if 0 "yes" "no")      ;=> "yes" (0 is truthy!)
(if "" "yes" "no")     ;=> "yes" (empty string is truthy!)
(if nil "yes" "no")    ;=> "no"
```

### Defining Things

```clojure
(def x 42)              ;; bind a name to a value
(def name "Alice")

(defn square [n]        ;; define a function
  (* n n))

(square 5)              ;=> 25
```

### Collections (preview — more in chapter 6)

```clojure
;; Vector (ordered, indexed)
[1 2 3 4 5]

;; Map (key-value pairs)
{:name "Alice" :age 30}

;; Set (unique values)
#{:a :b :c}

;; List (for code, rarely for data)
'(1 2 3)
```

## Exploring at the REPL

### `doc` — Read documentation

```clojure
(doc map)
;; -------------------------
;; clojure.core/map
;; ([f] [f coll] [f c1 c2] ...)
;;   Returns a lazy sequence...

(doc +)
(doc filter)
```

### `source` — Read source code

```clojure
(source not)
;; (defn not [x] (if x false true))
```

### `type` — What is this thing?

```clojure
(type 42)           ;=> java.lang.Long
(type "hello")      ;=> java.lang.String
(type [1 2 3])      ;=> clojure.lang.PersistentVector
(type {:a 1})       ;=> clojure.lang.PersistentArrayMap
```

### `find-doc` — Search documentation

```clojure
(find-doc "reduce")   ;; finds all docs mentioning "reduce"
```

## Creating a Project

```bash
mkdir my-project && cd my-project
```

Create `deps.edn`:

```clojure
{:deps {org.clojure/clojure {:mvn/version "1.12.0"}}
 :paths ["src"]}
```

Create `src/my_project/core.clj`:

```clojure
(ns my-project.core)

(defn -main []
  (println "Hello from Clojure!"))
```

Run it:

```bash
clj -M -m my-project.core
;; Hello from Clojure!
```

Or start a REPL in the project:

```bash
clj
user=> (require '[my-project.core :as app])
user=> (app/-main)
;; Hello from Clojure!
```

## The Development Workflow

```
1. Start REPL (once, keep it running for hours/days)
2. Write/edit code in your editor
3. Evaluate the form under cursor (Ctrl+Enter in Calva)
4. See result immediately
5. If wrong, edit and re-evaluate
6. When a function works, move on to the next
```

You don't save → compile → run → check. You just evaluate and see. This changes how you think about programming.

## Key Takeaways

- The REPL is your primary development tool, not just a calculator
- Clojure uses prefix notation: `(function arg1 arg2)`
- Everything returns a value — there are no "statements"
- `nil` and `false` are falsy; everything else (including 0 and "") is truthy
- Use `doc`, `source`, and `type` to explore at the REPL
- Projects use `deps.edn` for dependencies and configuration
