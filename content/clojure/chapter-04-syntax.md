# Chapter 4: Syntax and Evaluation

[prev: A Contact Book](chapter-03-contact-book.md) | [next: Functions](chapter-05-functions.md)

## The Simplest Syntax in Programming

Clojure has almost no syntax. Everything is either:

- A **literal** (numbers, strings, keywords, collections)
- A **list** that gets evaluated as a function call: `(f arg1 arg2)`

That's it. No operator precedence, no special statement syntax, no semicolons.

## Literals

```clojure
;; Numbers
42              ; long
3.14            ; double
1/3             ; ratio (exact!)
42N             ; BigInteger
3.14M           ; BigDecimal

;; Strings
"hello world"   ; double-quoted, Java strings

;; Characters
\a \newline \space \tab

;; Keywords (like symbols that evaluate to themselves)
:name :age :status

;; Symbols (names that refer to values)
x my-function clojure.core/map

;; Booleans and nil
true false nil

;; Regular expressions
#"[a-z]+"
```

## Collections as Literals

```clojure
;; List (linked list)
'(1 2 3)

;; Vector (indexed array)
[1 2 3]

;; Map (hash map)
{:a 1 :b 2 :c 3}

;; Set (unique values)
#{:red :green :blue}
```

## Evaluation Rules

### Rule 1: Literals evaluate to themselves

```clojure
42          ;=> 42
"hello"     ;=> "hello"
:name       ;=> :name
[1 2 3]     ;=> [1 2 3]
```

### Rule 2: Symbols are looked up

```clojure
(def x 42)
x           ;=> 42 (looks up the value bound to x)
```

### Rule 3: Lists are function calls

```clojure
(+ 1 2)          ;=> 3       (calls +)
(str "a" "b")    ;=> "ab"    (calls str)
(inc 5)          ;=> 6       (calls inc)
```

The first element is the operator (function, macro, or special form). The rest are arguments.

### Rule 4: Collections evaluate their contents

```clojure
(def x 10)
[x (+ x 1) (+ x 2)]   ;=> [10 11 12]
{:a x :b (inc x)}      ;=> {:a 10, :b 11}
```

## Special Forms

Special forms are built into the language. They don't follow normal evaluation rules.

### `if`

```clojure
(if condition
  then-expression
  else-expression)

(if (> 5 3)
  "yes"
  "no")
;=> "yes"
```

No `else` means `nil`:

```clojure
(if false "yes")  ;=> nil
```

### `do` — Evaluate multiple expressions

```clojure
(do
  (println "first")
  (println "second")
  42)  ;=> 42 (returns last value)
```

### `let` — Local bindings

```clojure
(let [x 10
      y 20
      sum (+ x y)]
  (str "Sum is " sum))
;=> "Sum is 30"
```

Bindings are sequential — later bindings can use earlier ones.

### `def` — Create a global binding

```clojure
(def pi 3.14159)
```

### `fn` — Create a function

```clojure
(fn [x] (* x x))        ; anonymous function
((fn [x] (* x x)) 5)    ;=> 25
```

### `quote` — Prevent evaluation

```clojure
(quote (+ 1 2))   ;=> (+ 1 2) — a list, not 3
'(+ 1 2)          ;=> (+ 1 2) — shorthand
```

## Truthiness

Only `false` and `nil` are falsy:

```clojure
(if 0 :truthy :falsy)       ;=> :truthy
(if "" :truthy :falsy)      ;=> :truthy
(if [] :truthy :falsy)      ;=> :truthy
(if nil :truthy :falsy)     ;=> :falsy
(if false :truthy :falsy)   ;=> :falsy
```

## Flow Control

### `when` — if without else

```clojure
(when (pos? x)
  (println "positive!")
  x)
```

### `cond` — Multiple conditions

```clojure
(defn classify [n]
  (cond
    (neg? n)  :negative
    (zero? n) :zero
    (pos? n)  :positive))
```

### `case` — Value matching (fast)

```clojure
(case day
  :mon "Monday"
  :tue "Tuesday"
  :wed "Wednesday"
  "other")
```

### `when-let` — Bind and test

```clojure
(when-let [result (find-user id)]
  (println "Found:" (:name result))
  result)
```

## Threading Macros

These transform nested calls into readable pipelines:

### `->` Thread-first (insert as first arg)

```clojure
;; Without threading:
(clojure.string/upper-case (clojure.string/trim "  hello  "))

;; With threading:
(-> "  hello  "
    clojure.string/trim
    clojure.string/upper-case)
;=> "HELLO"
```

### `->>` Thread-last (insert as last arg)

```clojure
;; Without threading:
(reduce + (map inc (filter odd? [1 2 3 4 5])))

;; With threading:
(->> [1 2 3 4 5]
     (filter odd?)
     (map inc)
     (reduce +))
;=> 12
```

### `some->` Thread with nil short-circuit

```clojure
(some-> user :address :city clojure.string/upper-case)
;; Returns nil if any step is nil, instead of throwing
```

## Quoting and Syntax-Quote

```clojure
;; Quote: prevent evaluation
'(1 2 3)                ;=> (1 2 3)

;; Syntax-quote: like quote but namespace-qualifies symbols
`(map inc [1 2 3])      ;=> (clojure.core/map clojure.core/inc [1 2 3])

;; Unquote: evaluate inside syntax-quote
(let [x 5]
  `(+ 1 ~x))           ;=> (clojure.core/+ 1 5)

;; Unquote-splice: flatten a list
(let [args [1 2 3]]
  `(+ ~@args))          ;=> (clojure.core/+ 1 2 3)
```

These are essential for macros (chapter 14).

## Comments

```clojure
; Single line comment

(comment
  ;; Rich comment block — code here is never evaluated
  ;; but your editor can still evaluate individual forms
  (+ 1 2)
  (some-experiment))

#_ (this form is ignored)  ; reader discard
```

## Key Takeaways

- Clojure syntax = literals + lists. That's all.
- `(f arg1 arg2)` — first element is always the operator
- Special forms (`if`, `let`, `do`, `fn`, `def`) have special evaluation rules
- Only `nil` and `false` are falsy
- Threading macros (`->`, `->>`) make nested calls readable
- Syntax-quote (`` ` ``) and unquote (`~`) are for metaprogramming
