# Chapter 6: Data Structures

[prev: Functions](chapter-05-functions.md) | [next: Sequences and Laziness](chapter-07-sequences.md)

## Immutable and Persistent

All Clojure data structures are immutable. When you "modify" one, you get a new version. The old one remains unchanged. Under the hood, they share structure — creating a new version is O(log32 n), not O(n).

## Vectors

Ordered, indexed, most common collection for data.

```clojure
;; Creation
[1 2 3 4 5]
(vector 1 2 3)
(vec '(1 2 3))       ; convert list to vector

;; Access
(get [10 20 30] 1)   ;=> 20
([10 20 30] 1)       ;=> 20 (vectors are functions of their index)
(nth [10 20 30] 1)   ;=> 20
(first [10 20 30])   ;=> 10
(last [10 20 30])    ;=> 30
(peek [10 20 30])    ;=> 30 (last for vectors)

;; "Modification" (returns new vector)
(conj [1 2 3] 4)         ;=> [1 2 3 4] (adds to end)
(assoc [10 20 30] 1 99)  ;=> [10 99 30]
(subvec [10 20 30 40 50] 1 4)  ;=> [20 30 40]
(pop [1 2 3])             ;=> [1 2] (remove last)

;; Size
(count [1 2 3])  ;=> 3
(empty? [])      ;=> true
```

## Maps

Key-value pairs. The workhorse of Clojure data modeling.

```clojure
;; Creation
{:name "Alice" :age 30 :city "Singapore"}
(hash-map :a 1 :b 2)
(sorted-map :b 2 :a 1 :c 3)  ;=> {:a 1, :b 2, :c 3}

;; Access
(get {:a 1 :b 2} :a)          ;=> 1
(get {:a 1 :b 2} :c "default") ;=> "default"
({:a 1 :b 2} :a)              ;=> 1 (maps are functions)
(:a {:a 1 :b 2})              ;=> 1 (keywords are functions!)
(:c {:a 1 :b 2})              ;=> nil

;; Nested access
(get-in {:a {:b {:c 42}}} [:a :b :c])  ;=> 42

;; "Modification"
(assoc {:a 1} :b 2)               ;=> {:a 1, :b 2}
(assoc {:a 1} :a 99)              ;=> {:a 99}
(dissoc {:a 1 :b 2} :b)           ;=> {:a 1}
(merge {:a 1} {:b 2} {:c 3})      ;=> {:a 1, :b 2, :c 3}
(update {:a 1} :a inc)            ;=> {:a 2}
(update-in {:a {:b 1}} [:a :b] + 10) ;=> {:a {:b 11}}
(assoc-in {:a {:b 1}} [:a :c] 99)    ;=> {:a {:b 1, :c 99}}

;; Useful operations
(keys {:a 1 :b 2})     ;=> (:a :b)
(vals {:a 1 :b 2})     ;=> (1 2)
(select-keys {:a 1 :b 2 :c 3} [:a :c])  ;=> {:a 1, :c 3}
(contains? {:a 1} :a)  ;=> true
(find {:a 1 :b 2} :a)  ;=> [:a 1] (returns map entry)
```

## Sets

Unique values, fast membership testing.

```clojure
;; Creation
#{1 2 3}
(set [1 2 2 3 3 3])       ;=> #{1 2 3}
(sorted-set 3 1 2)        ;=> #{1 2 3}

;; Membership
(contains? #{:a :b :c} :a)  ;=> true
(#{:a :b :c} :a)            ;=> :a (sets are functions!)
(#{:a :b :c} :d)            ;=> nil

;; Operations (clojure.set namespace)
(require '[clojure.set :as set])
(set/union #{1 2} #{2 3})          ;=> #{1 2 3}
(set/intersection #{1 2 3} #{2 3 4})  ;=> #{2 3}
(set/difference #{1 2 3} #{2 3})      ;=> #{1}
(set/subset? #{1 2} #{1 2 3})         ;=> true

;; "Modification"
(conj #{1 2} 3)     ;=> #{1 2 3}
(disj #{1 2 3} 2)   ;=> #{1 3}
```

## Lists

Linked lists. Rarely used for data — mainly in macros and code-as-data.

```clojure
'(1 2 3)
(list 1 2 3)

(first '(1 2 3))     ;=> 1
(rest '(1 2 3))      ;=> (2 3)
(conj '(1 2 3) 0)    ;=> (0 1 2 3) (adds to front!)
(cons 0 '(1 2 3))    ;=> (0 1 2 3)
```

## Keywords as Data

Keywords are interned strings that are fast to compare and evaluate to themselves. They're the idiomatic way to name things in maps.

```clojure
:name                    ; simple keyword
:user/name               ; namespaced keyword
::name                   ; auto-resolved to current namespace

;; Keywords are functions:
(:name {:name "Alice" :age 30})  ;=> "Alice"

;; Use as enum-like values:
(def status :active)
(= status :active)  ;=> true
```

## Nested Data

Real-world data is deeply nested. Clojure handles this well:

```clojure
(def order
  {:id "ORD-001"
   :customer {:name "Alice" :email "alice@test.com"}
   :items [{:product "Widget" :qty 3 :price 9.99}
           {:product "Gadget" :qty 1 :price 24.99}]
   :status :pending})

;; Access
(:name (:customer order))              ;=> "Alice"
(get-in order [:customer :email])      ;=> "alice@test.com"
(get-in order [:items 0 :product])     ;=> "Widget"

;; Update deeply nested
(update-in order [:items 0 :qty] inc)
;=> {...:items [{:product "Widget" :qty 4 ...} ...]}

(assoc-in order [:customer :phone] "555-1234")
;=> {...:customer {:name "Alice" :email "..." :phone "555-1234"}}
```

## Structural Sharing (Why Immutability is Fast)

```
Original: [a b c d e]

After (assoc v 2 X):
  New:      [a b X d e]

  Under the hood, a and b, d and e are SHARED — not copied.
  Only the path to the changed node is new.
```

For a vector of 1 million elements, creating a "modified" version copies ~6 nodes (log32 of 1M), not 1 million.

## Records (Typed Maps)

When you want map semantics with better performance and explicit fields:

```clojure
(defrecord Customer [name email phone])

(def alice (->Customer "Alice" "alice@test.com" "555-1234"))
;; or:
(def bob (map->Customer {:name "Bob" :email "bob@test.com" :phone "555-5678"}))

(:name alice)     ;=> "Alice"
(assoc alice :vip true)  ;=> still works like a map
```

## Choosing the Right Collection

| Need                           | Use                                  |
| ------------------------------ | ------------------------------------ |
| Ordered, indexed access        | Vector `[]`                          |
| Key-value lookup               | Map `{}`                             |
| Unique values, membership test | Set `#{}`                            |
| Build code in macros           | List `'()`                           |
| FIFO queue                     | `clojure.lang.PersistentQueue/EMPTY` |

## Key Takeaways

- All collections are immutable — "modifications" return new values
- Vectors for ordered data, maps for named fields, sets for uniqueness
- Keywords are functions: `(:key map)` is idiomatic
- `get-in`, `assoc-in`, `update-in` for nested data access
- Structural sharing makes immutability efficient (not O(n) copies)
- Records give you typed maps with better performance
