# Chapter 11: Polymorphism Without Inheritance

[prev: Destructuring](chapter-10-destructuring.md) | [next: A REST API](chapter-12-rest-api.md)

## Dispatch Without Classes

Clojure gives you polymorphism (same function name, different behavior) without class hierarchies. Two mechanisms: **multimethods** (open, flexible dispatch) and **protocols** (fast, type-based dispatch).

## Multimethods

Dispatch on any function of the arguments — not just type.

```clojure
;; Dispatch on :type key
(defmulti area :shape)

(defmethod area :circle [{:keys [radius]}]
  (* Math/PI radius radius))

(defmethod area :rectangle [{:keys [width height]}]
  (* width height))

(defmethod area :triangle [{:keys [base height]}]
  (/ (* base height) 2))

(defmethod area :default [shape]
  (throw (ex-info "Unknown shape" {:shape shape})))

(area {:shape :circle :radius 5})         ;=> 78.54
(area {:shape :rectangle :width 3 :height 4})  ;=> 12
(area {:shape :triangle :base 6 :height 3})    ;=> 9
```

### Dispatching on Multiple Values

```clojure
(defmulti encounter (fn [x y] [(:species x) (:species y)]))

(defmethod encounter [:bunny :bunny] [x y]
  "They mate")
(defmethod encounter [:lion :bunny] [x y]
  "The lion eats the bunny")
(defmethod encounter [:bunny :lion] [x y]
  "The bunny runs away")

(encounter {:species :lion} {:species :bunny})
;=> "The lion eats the bunny"
```

### Custom Dispatch Functions

```clojure
(defmulti tax-rate (fn [income country] country))

(defmethod tax-rate :sg [income _]
  (cond (< income 20000) 0.0
        (< income 40000) 0.02
        :else 0.07))

(defmethod tax-rate :vn [income _]
  (cond (< income 60000000) 0.05
        :else 0.20))

(tax-rate 50000 :sg)  ;=> 0.07
```

### Hierarchies

```clojure
(derive :savings :account)
(derive :checking :account)
(derive :credit :account)

(defmulti fee :account-type)
(defmethod fee :savings [_] 0)
(defmethod fee :checking [_] 5)
(defmethod fee :account [_] 10)  ;; default for any :account

(fee {:account-type :savings})   ;=> 0
(fee {:account-type :credit})    ;=> 10 (matches parent :account)
```

## Protocols

Like Java interfaces, but you can extend them to existing types after the fact.

```clojure
(defprotocol Stringify
  (to-string [this]))

(extend-protocol Stringify
  String
  (to-string [s] s)

  Long
  (to-string [n] (str n))

  clojure.lang.IPersistentMap
  (to-string [m] (str "{" (clojure.string/join ", " (map #(str (key %) "=" (val %)) m)) "}"))

  nil
  (to-string [_] "nil"))

(to-string "hello")       ;=> "hello"
(to-string 42)            ;=> "42"
(to-string {:a 1 :b 2})   ;=> "{:a=1, :b=2}"
(to-string nil)            ;=> "nil"
```

### Protocols with Records

```clojure
(defprotocol Shape
  (area [this])
  (perimeter [this]))

(defrecord Circle [radius]
  Shape
  (area [_] (* Math/PI radius radius))
  (perimeter [_] (* 2 Math/PI radius)))

(defrecord Rectangle [width height]
  Shape
  (area [_] (* width height))
  (perimeter [_] (* 2 (+ width height))))

(area (->Circle 5))            ;=> 78.54
(perimeter (->Rectangle 3 4))  ;=> 14
```

### Extending Existing Types

```clojure
(defprotocol Serializable
  (serialize [this]))

;; Extend Java's String — after the fact!
(extend-type String
  Serializable
  (serialize [s] (str "\"" s "\"")))

(extend-type java.util.Date
  Serializable
  (serialize [d] (str "\"" (.toInstant d) "\"")))

(serialize "hello")              ;=> "\"hello\""
(serialize (java.util.Date.))    ;=> "\"2024-01-15T...\""
```

## When to Use Which

| Use Case                        | Mechanism              |
| ------------------------------- | ---------------------- |
| Dispatch on type                | Protocol               |
| Dispatch on value/multiple args | Multimethod            |
| Performance-critical hot path   | Protocol               |
| Open extension by third parties | Both work              |
| Ad-hoc hierarchies              | Multimethod + `derive` |

## Practical Example: Event System

```clojure
(defmulti handle-event :type)

(defmethod handle-event :user/created [{:keys [user-id email]}]
  (println "Send welcome email to" email)
  (println "Create default settings for" user-id))

(defmethod handle-event :order/placed [{:keys [order-id amount]}]
  (println "Process payment for order" order-id "amount" amount))

(defmethod handle-event :order/shipped [{:keys [order-id tracking]}]
  (println "Notify customer: order" order-id "shipped, tracking:" tracking))

(defmethod handle-event :default [event]
  (println "Unhandled event:" (:type event)))

;; Usage
(handle-event {:type :user/created :user-id 1 :email "a@b.com"})
(handle-event {:type :order/placed :order-id "ORD-1" :amount 99.99})
```

## Key Takeaways

- Multimethods: dispatch on any function of args, open for extension
- Protocols: type-based dispatch, fast, like interfaces you can add later
- No inheritance hierarchies needed — composition over inheritance
- `derive` creates ad-hoc hierarchies for multimethods
- Both are open — new methods can be added without modifying existing code
