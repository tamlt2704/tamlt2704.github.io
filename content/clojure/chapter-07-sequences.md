# Chapter 7: Sequences and Laziness

[prev: Data Structures](chapter-06-data-structures.md) | [next: A Data Pipeline](chapter-08-data-pipeline.md)

## The Seq Abstraction

Clojure unifies all collections (and more) behind one interface: the **sequence**. If something can produce elements one at a time, you can use `map`, `filter`, `reduce` on it — vectors, maps, sets, strings, files, even infinite generators.

```clojure
(seq [1 2 3])         ;=> (1 2 3)
(seq {:a 1 :b 2})     ;=> ([:a 1] [:b 2])
(seq #{:x :y :z})     ;=> (:x :y :z)
(seq "hello")         ;=> (\h \e \l \l \o)
(seq nil)             ;=> nil
```

`first` and `rest` work on anything seq-able:

```clojure
(first [10 20 30])    ;=> 10
(rest [10 20 30])     ;=> (20 30)
(first {:a 1 :b 2})   ;=> [:a 1]
(first "hello")       ;=> \h
```

## Lazy Sequences

Most sequence operations in Clojure are **lazy** — they don't compute results until needed. This lets you work with sequences larger than memory.

```clojure
;; This doesn't compute 1 billion results:
(def big (map inc (range 1000000000)))

;; Only computes what you ask for:
(take 5 big)  ;=> (1 2 3 4 5)
```

### `range` — Infinite numbers

```clojure
(range)           ; 0, 1, 2, 3, ... (infinite!)
(range 5)         ;=> (0 1 2 3 4)
(range 1 10 2)    ;=> (1 3 5 7 9) (start, end, step)
```

### `repeat` and `repeatedly`

```clojure
(take 3 (repeat "ha"))         ;=> ("ha" "ha" "ha")
(take 3 (repeatedly rand))     ;=> (0.234... 0.891... 0.123...)
```

### `iterate` — Build from a function

```clojure
(take 10 (iterate #(* 2 %) 1))
;=> (1 2 4 8 16 32 64 128 256 512)

(take 5 (iterate inc 0))
;=> (0 1 2 3 4)
```

### `cycle` — Repeat a sequence forever

```clojure
(take 7 (cycle [:a :b :c]))
;=> (:a :b :c :a :b :c :a)
```

## Core Sequence Operations

### Transforming

```clojure
(map inc [1 2 3])                ;=> (2 3 4)
(mapcat #(vector % (* % 2)) [1 2 3])  ;=> (1 2 2 4 3 6)
(map-indexed vector [:a :b :c]) ;=> ([0 :a] [1 :b] [2 :c])
(keep #(when (odd? %) (* % 10)) [1 2 3 4 5])  ;=> (10 30 50)
```

### Filtering

```clojure
(filter pos? [-2 -1 0 1 2])     ;=> (1 2)
(remove pos? [-2 -1 0 1 2])     ;=> (-2 -1 0)
(take-while pos? [3 2 1 0 -1])  ;=> (3 2 1)
(drop-while pos? [3 2 1 0 -1])  ;=> (0 -1)
(distinct [1 2 1 3 2 4])        ;=> (1 2 3 4)
(dedupe [1 1 2 2 2 3 1 1])      ;=> (1 2 3 1) (consecutive dupes)
```

### Slicing

```clojure
(take 3 [1 2 3 4 5])            ;=> (1 2 3)
(drop 3 [1 2 3 4 5])            ;=> (4 5)
(take-last 2 [1 2 3 4 5])       ;=> (4 5)
(partition 2 [1 2 3 4 5 6])     ;=> ((1 2) (3 4) (5 6))
(partition-by odd? [1 3 2 4 5]) ;=> ((1 3) (2 4) (5))
(split-at 3 [1 2 3 4 5])        ;=> [(1 2 3) (4 5)]
```

### Reducing

```clojure
(reduce + [1 2 3 4 5])                  ;=> 15
(reduce-kv (fn [m k v] (assoc m k (inc v))) {} {:a 1 :b 2})  ;=> {:a 2, :b 3}
(reductions + [1 2 3 4 5])              ;=> (1 3 6 10 15) (running total)
```

### Checking

```clojure
(some even? [1 3 5 6 7])        ;=> true
(every? pos? [1 2 3])           ;=> true
(not-any? neg? [1 2 3])         ;=> true
(some #(when (> % 3) %) [1 2 3 4 5])  ;=> 4 (first match)
```

## Building Sequences

```clojure
;; concat
(concat [1 2] [3 4] [5 6])     ;=> (1 2 3 4 5 6)

;; interleave
(interleave [:a :b :c] [1 2 3])  ;=> (:a 1 :b 2 :c 3)

;; interpose
(interpose ", " ["a" "b" "c"])  ;=> ("a" ", " "b" ", " "c")
(apply str (interpose ", " ["a" "b" "c"]))  ;=> "a, b, c"
;; or simpler:
(clojure.string/join ", " ["a" "b" "c"])    ;=> "a, b, c"
```

## Transducers (Composable, No Intermediate Sequences)

Regular sequence operations create intermediate lazy sequences at each step. Transducers compose the operations into one pass:

```clojure
;; Without transducers (3 intermediate sequences):
(->> data
     (filter active?)
     (map :score)
     (take 100))

;; With transducers (single pass, no intermediates):
(def xf (comp (filter active?) (map :score) (take 100)))

(into [] xf data)         ; apply to a collection
(transduce xf + data)     ; apply and reduce
(sequence xf data)        ; lazy transduced sequence
```

Creating transducers — just call seq functions with no collection:

```clojure
(filter odd?)      ; returns a transducer
(map inc)          ; returns a transducer
(take 5)           ; returns a transducer

;; Compose them:
(def pipeline (comp (filter odd?) (map #(* % %)) (take 3)))
(into [] pipeline (range 100))  ;=> [1 9 25]
```

## Eager vs Lazy

| Lazy (returns seq) | Eager (returns concrete) |
| ------------------ | ------------------------ |
| `map`              | `mapv`                   |
| `filter`           | `filterv`                |
| `for`              | `into [] ...`            |
| `concat`           | `into [] ...`            |

Use eager when you need the result now (e.g., in a `let` binding that you'll use multiple times). Use lazy when processing large or infinite data.

## `for` — Sequence Comprehension

```clojure
(for [x [1 2 3]
      y [10 20]]
  (* x y))
;=> (10 20 20 40 30 60)

;; With filtering:
(for [x (range 10)
      :when (odd? x)
      :let [sq (* x x)]]
  sq)
;=> (1 9 25 49 81)
```

## Working with Files Lazily

```clojure
(with-open [rdr (clojure.java.io/reader "large-file.txt")]
  (->> (line-seq rdr)
       (filter #(clojure.string/includes? % "ERROR"))
       (take 10)
       (doall)))  ; force evaluation before reader closes
```

## Key Takeaways

- The seq abstraction unifies all collections behind `first`/`rest`
- Most operations are lazy — they compose without memory pressure
- Transducers eliminate intermediate sequences for better performance
- `for` is a sequence comprehension (like Python's list comprehension)
- Use `doall` or `into` when you need to force lazy evaluation
- Infinite sequences are fine — just `take` what you need
