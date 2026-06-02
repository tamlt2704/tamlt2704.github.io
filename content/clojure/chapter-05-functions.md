# Chapter 5: Functions

[prev: Syntax and Evaluation](chapter-04-syntax.md) | [next: Data Structures](chapter-06-data-structures.md)

## Functions Are Everything

In Clojure, functions are first-class values. You can pass them as arguments, return them from other functions, and store them in data structures. Most of your code will be functions calling functions.

## Defining Functions

### `defn` — Named functions

```clojure
(defn greet [name]
  (str "Hello, " name "!"))

(greet "World")  ;=> "Hello, World!"
```

### Docstrings

```clojure
(defn area
  "Calculates the area of a circle given its radius."
  [radius]
  (* Math/PI radius radius))

(doc area)
;; -------------------------
;; user/area
;;   Calculates the area of a circle given its radius.
```

### Multiple Arities

```clojure
(defn greet
  ([] (greet "World"))
  ([name] (str "Hello, " name "!"))
  ([first-name last-name] (str "Hello, " first-name " " last-name "!")))

(greet)              ;=> "Hello, World!"
(greet "Alice")      ;=> "Hello, Alice!"
(greet "Alice" "B")  ;=> "Hello, Alice B!"
```

### Variadic Functions

```clojure
(defn sum [& numbers]
  (reduce + 0 numbers))

(sum 1 2 3 4 5)  ;=> 15
(sum)            ;=> 0
```

```clojure
(defn log [level & messages]
  (println (str "[" level "]") (apply str messages)))

(log :info "Server started on port " 8080)
;; [:info] Server started on port 8080
```

## Anonymous Functions

### `fn` form

```clojure
(fn [x] (* x x))

(map (fn [x] (* x x)) [1 2 3 4 5])
;=> (1 4 9 16 25)
```

### `#()` reader macro (shorthand)

```clojure
#(* % %)           ; single arg: %
#(+ %1 %2)        ; multiple args: %1, %2, ...
#(str %1 " " %2)

(map #(* % %) [1 2 3 4 5])
;=> (1 4 9 16 25)

(filter #(> % 3) [1 2 3 4 5])
;=> (4 5)
```

## Higher-Order Functions

Functions that take or return functions.

### `map` — Transform each element

```clojure
(map inc [1 2 3])           ;=> (2 3 4)
(map str [1 2 3])           ;=> ("1" "2" "3")
(map + [1 2 3] [10 20 30]) ;=> (11 22 33)
```

### `filter` and `remove`

```clojure
(filter even? [1 2 3 4 5 6])  ;=> (2 4 6)
(remove even? [1 2 3 4 5 6])  ;=> (1 3 5)
```

### `reduce` — Fold into a single value

```clojure
(reduce + [1 2 3 4 5])         ;=> 15
(reduce + 100 [1 2 3 4 5])    ;=> 115 (with initial value)

;; Build a map from pairs
(reduce (fn [m [k v]] (assoc m k v))
        {}
        [[:a 1] [:b 2] [:c 3]])
;=> {:a 1, :b 2, :c 3}
```

### `apply` — Spread a collection as arguments

```clojure
(apply + [1 2 3 4 5])    ;=> 15 (same as (+ 1 2 3 4 5))
(apply str ["a" "b" "c"]) ;=> "abc"
(apply max [3 1 4 1 5])   ;=> 5
```

## Composition

### `comp` — Compose functions (right to left)

```clojure
(def loud-greeting (comp clojure.string/upper-case #(str "hello, " %)))
(loud-greeting "world")  ;=> "HELLO, WORLD"

(def process (comp (partial map inc) (partial filter odd?)))
(process [1 2 3 4 5])  ;=> (2 4 6)
```

### `partial` — Fix some arguments

```clojure
(def add-10 (partial + 10))
(add-10 5)   ;=> 15
(add-10 20)  ;=> 30

(def greet-hello (partial str "Hello, "))
(greet-hello "Alice")  ;=> "Hello, Alice"
```

### `juxt` — Apply multiple functions to same args

```clojure
((juxt inc dec) 5)          ;=> [6 4]
((juxt :name :age) {:name "Alice" :age 30})  ;=> ["Alice" 30]

;; Useful for sorting
(sort-by (juxt :last-name :first-name) people)
```

## Closures

Functions capture their environment:

```clojure
(defn make-counter []
  (let [count (atom 0)]
    (fn [] (swap! count inc))))

(def c (make-counter))
(c)  ;=> 1
(c)  ;=> 2
(c)  ;=> 3
```

```clojure
(defn make-adder [n]
  (fn [x] (+ x n)))

(def add-5 (make-adder 5))
(add-5 10)  ;=> 15
```

## Recursion

Clojure doesn't have traditional loops. Use recursion with `recur`:

```clojure
(defn factorial [n]
  (loop [i n
         acc 1]
    (if (<= i 1)
      acc
      (recur (dec i) (* acc i)))))

(factorial 10)  ;=> 3628800
```

`recur` is mandatory for tail recursion (no stack overflow):

```clojure
;; This would stack overflow for large n:
(defn bad-factorial [n]
  (if (<= n 1) 1 (* n (bad-factorial (dec n)))))

;; This won't — recur reuses the stack frame:
(defn good-factorial [n]
  (loop [i n, acc 1]
    (if (<= i 1) acc (recur (dec i) (* acc i)))))
```

## Multi-method Dispatch (Preview)

```clojure
(defmulti area :shape)

(defmethod area :circle [{:keys [radius]}]
  (* Math/PI radius radius))

(defmethod area :rectangle [{:keys [width height]}]
  (* width height))

(area {:shape :circle :radius 5})       ;=> 78.53...
(area {:shape :rectangle :width 3 :height 4})  ;=> 12
```

## Useful Built-in Functions

```clojure
;; Identity and constants
(identity 42)        ;=> 42
(constantly 5)       ;=> returns a fn that always returns 5

;; Predicates
(some? nil)          ;=> false
(some? 0)            ;=> true
(empty? [])          ;=> true
(every? pos? [1 2 3]) ;=> true
(some even? [1 2 3])  ;=> true

;; Transformation
(update {:a 1} :a inc)         ;=> {:a 2}
(update-in {:a {:b 1}} [:a :b] inc)  ;=> {:a {:b 2}}
(mapv inc [1 2 3])             ;=> [2 3 4] (eager, returns vector)

;; Grouping
(group-by :type [{:type :a :v 1} {:type :b :v 2} {:type :a :v 3}])
;=> {:a [{:type :a, :v 1} {:type :a, :v 3}], :b [{:type :b, :v 2}]}

(frequencies ["a" "b" "a" "c" "a" "b"])
;=> {"a" 3, "b" 2, "c" 1}
```

## Key Takeaways

- `defn` for named functions, `fn` or `#()` for anonymous
- Multiple arities and variadic args (`& rest`) are built-in
- `map`, `filter`, `reduce` are your core tools
- `comp`, `partial`, `juxt` compose functions without writing new ones
- `recur` for safe tail recursion (no stack overflow)
- Functions are closures — they capture their lexical environment
- Keywords (`:name`) are themselves functions that look up values in maps
