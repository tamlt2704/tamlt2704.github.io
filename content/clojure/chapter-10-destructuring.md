# Chapter 10: Destructuring and Pattern Matching

[prev: Namespaces](chapter-09-namespaces.md) | [next: Polymorphism](chapter-11-polymorphism.md)

## Destructuring

Instead of pulling data apart with `get`, `first`, `nth`, destructuring lets you bind names directly to parts of a data structure.

## Sequential Destructuring (Vectors, Lists)

```clojure
;; Without destructuring:
(defn distance [point]
  (let [x (first point)
        y (second point)]
    (Math/sqrt (+ (* x x) (* y y)))))

;; With destructuring:
(defn distance [[x y]]
  (Math/sqrt (+ (* x x) (* y y))))

(distance [3 4])  ;=> 5.0
```

### Ignoring elements with `_`

```clojure
(let [[_ second third] [1 2 3]]
  [second third])
;=> [2 3]
```

### Rest elements with `&`

```clojure
(let [[head & tail] [1 2 3 4 5]]
  {:head head :tail tail})
;=> {:head 1, :tail (2 3 4 5)}
```

### Keeping the whole with `:as`

```clojure
(let [[x y :as point] [3 4]]
  {:x x :y y :original point})
;=> {:x 3, :y 4, :original [3 4]}
```

## Map Destructuring

```clojure
;; Without:
(defn greet [person]
  (str "Hello, " (:name person) " from " (:city person)))

;; With:
(defn greet [{:keys [name city]}]
  (str "Hello, " name " from " city))

(greet {:name "Alice" :city "Singapore" :age 30})
;=> "Hello, Alice from Singapore"
```

### Specific keys

```clojure
;; String keys
(let [{:strs [name age]} {"name" "Bob" "age" 25}]
  [name age])
;=> ["Bob" 25]

;; Symbol keys
(let [{:syms [x y]} {'x 1 'y 2}]
  (+ x y))
;=> 3
```

### Defaults with `:or`

```clojure
(defn connect [{:keys [host port] :or {host "localhost" port 5432}}]
  (str host ":" port))

(connect {:host "db.example.com"})  ;=> "db.example.com:5432"
(connect {})                        ;=> "localhost:5432"
```

### Renaming with map syntax

```clojure
(let [{the-name :name the-age :age} {:name "Alice" :age 30}]
  (str the-name " is " the-age))
;=> "Alice is 30"
```

### Nested destructuring

```clojure
(defn order-summary [{:keys [id]
                      {:keys [name email]} :customer
                      [{:keys [product qty]}] :items}]
  (printf "Order #%s: %s (%s) ordered %dx %s%n" id name email qty product))

(order-summary {:id "ORD-1"
                :customer {:name "Alice" :email "a@b.com"}
                :items [{:product "Widget" :qty 3}]})
;; Order #ORD-1: Alice (a@b.com) ordered 3x Widget
```

## Destructuring in Function Arguments

Works everywhere bindings work: `let`, `fn`, `defn`, `for`, `doseq`, `loop`.

```clojure
;; In for
(for [{:keys [name score]} students
      :when (> score 90)]
  name)

;; In doseq
(doseq [[k v] {:a 1 :b 2 :c 3}]
  (println k "=>" v))

;; In loop
(loop [[head & rest] [1 2 3 4 5]
       acc 0]
  (if head
    (recur rest (+ acc head))
    acc))
;=> 15
```

## Multi-arity with Destructuring

```clojure
(defn http-request
  ([url] (http-request url {}))
  ([url {:keys [method headers body timeout]
         :or {method :get timeout 5000}}]
   {:url url :method method :headers headers :body body :timeout timeout}))

(http-request "https://api.example.com")
;=> {:url "https://api.example.com", :method :get, :headers nil, :body nil, :timeout 5000}

(http-request "https://api.example.com" {:method :post :body "{}"})
;=> {:url "...", :method :post, :headers nil, :body "{}", :timeout 5000}
```

## Pattern Matching with `core.match`

For more complex matching, use the `core.match` library:

```clojure
;; deps.edn: org.clojure/core.match {:mvn/version "1.1.0"}
(require '[clojure.core.match :refer [match]])

(defn describe [x]
  (match x
    [1 _ _]     "starts with 1"
    [_ _ 3]     "ends with 3"
    [a b c]     (str "three elements: " a ", " b ", " c)
    :else       "something else"))

(describe [1 2 3])  ;=> "starts with 1"
(describe [9 8 3])  ;=> "ends with 3"
(describe [4 5 6])  ;=> "three elements: 4, 5, 6"
```

### Matching maps

```clojure
(defn handle-event [event]
  (match event
    {:type :login :user user}
      (str user " logged in")
    {:type :purchase :amount amount :user user}
      (str user " bought $" amount)
    {:type :error :message msg}
      (str "Error: " msg)
    :else
      "Unknown event"))

(handle-event {:type :login :user "Alice"})
;=> "Alice logged in"
(handle-event {:type :purchase :user "Bob" :amount 42.0})
;=> "Bob bought $42.0"
```

## Practical: Config Parsing

```clojure
(defn start-server [{:keys [port host]
                     :or {port 3000 host "0.0.0.0"}
                     :as config}]
  (println "Starting server with config:" config)
  (println (str "Listening on " host ":" port)))

(start-server {:port 8080 :ssl true})
;; Starting server with config: {:port 8080, :ssl true}
;; Listening on 0.0.0.0:8080
```

## Key Takeaways

- Destructuring eliminates boilerplate `get`/`first`/`nth` calls
- `{:keys [a b c]}` for keyword maps (most common)
- `:or` for defaults, `:as` to keep the whole thing
- Works in `let`, `fn`, `defn`, `for`, `doseq`, `loop` — anywhere you bind
- Nest destructuring for deeply nested data
- `core.match` for complex pattern matching beyond what destructuring handles
