# Chapter 13: Concurrency and State

[prev: A REST API](chapter-12-rest-api.md) | [next: Macros](chapter-14-macros.md)

## The Problem with Shared Mutable State

In most languages, concurrency means threads fighting over shared data, protected by locks you'll get wrong. Clojure takes a different approach: immutable data by default, and managed references for the rare cases where you need state.

## The Four Reference Types

| Type  | For                    | Coordination         | Update             |
| ----- | ---------------------- | -------------------- | ------------------ |
| Atom  | Independent state      | Uncoordinated        | `swap!`, `reset!`  |
| Ref   | Coordinated state      | Transactional (STM)  | `alter`, `ref-set` |
| Agent | Async state            | Uncoordinated, async | `send`, `send-off` |
| Var   | Thread-local rebinding | Per-thread           | `binding`          |

## Atoms: Independent State

The workhorse. Thread-safe, uncoordinated, synchronous.

```clojure
(def counter (atom 0))

@counter          ;=> 0 (deref)
(swap! counter inc)    ;=> 1
(swap! counter + 10)   ;=> 11
(reset! counter 0)     ;=> 0

;; swap! retries if another thread changed it (compare-and-swap):
;; (swap! atom f) = (reset! atom (f @atom)) but thread-safe
```

### Atoms with complex state

```clojure
(def app-state (atom {:users {} :session-count 0}))

(swap! app-state update :session-count inc)
(swap! app-state assoc-in [:users "alice"] {:role :admin})

;; Watch for changes
(add-watch app-state :logger
  (fn [key ref old-val new-val]
    (when (not= (:session-count old-val) (:session-count new-val))
      (println "Sessions:" (:session-count new-val)))))
```

## Refs: Coordinated Transactions (STM)

When multiple pieces of state must change together atomically:

```clojure
(def account-a (ref 1000))
(def account-b (ref 2000))

;; Transfer money — both accounts change atomically
(defn transfer! [from to amount]
  (dosync
    (alter from - amount)
    (alter to + amount)))

(transfer! account-a account-b 300)
@account-a  ;=> 700
@account-b  ;=> 2300
```

If any ref is modified by another transaction while yours is running, yours retries automatically. No deadlocks possible.

```clojure
;; commute — for commutative operations (order doesn't matter)
(def hit-counter (ref 0))
(dosync (commute hit-counter inc))  ;; faster, less retries
```

## Agents: Async State

Fire-and-forget updates. Good for I/O-bound work:

```clojure
(def log-agent (agent []))

(send log-agent conj {:time (System/currentTimeMillis) :msg "Started"})
(send log-agent conj {:time (System/currentTimeMillis) :msg "Processing"})

;; send is async — returns immediately
;; Actions are queued and executed in order on a thread pool

@log-agent  ;=> [{:time ... :msg "Started"} {:time ... :msg "Processing"}]

;; send-off for I/O-bound (uses unbounded thread pool)
(def file-writer (agent nil))
(send-off file-writer (fn [_] (spit "log.txt" "hello\n" :append true)))
```

### Error handling with agents

```clojure
(def a (agent 0))
(send a (fn [_] (/ 1 0)))  ;; causes error

(agent-error a)  ;=> ArithmeticException
(restart-agent a 0)  ;; fix it
```

## Futures and Promises

### Futures: Run something in another thread

```clojure
(def result (future
              (Thread/sleep 2000)
              (+ 1 2 3)))

;; Do other work...
@result  ;=> 6 (blocks until ready)
(realized? result)  ;=> true/false
```

### Promises: A value that will be delivered later

```clojure
(def p (promise))

;; In another thread:
(future (Thread/sleep 1000) (deliver p 42))

@p  ;=> 42 (blocks until delivered)
```

## Parallel Processing

### `pmap` — Parallel map

```clojure
;; Sequential:
(time (doall (map expensive-fn (range 10))))  ;; ~10 seconds

;; Parallel:
(time (doall (pmap expensive-fn (range 10)))) ;; ~1 second
```

### `pcalls` and `pvalues`

```clojure
(pcalls #(fetch-url "a.com") #(fetch-url "b.com") #(fetch-url "c.com"))
;; Returns results in order, computed in parallel
```

## core.async: CSP-Style Channels

Go-like channels and goroutines:

```clojure
(require '[clojure.core.async :as async :refer [go chan <! >! <!! >!! close!]])

;; Create a channel
(def ch (chan 10))  ;; buffered channel, capacity 10

;; Put and take (blocking versions for main thread)
(>!! ch "hello")
(<!! ch)  ;=> "hello"

;; go blocks — lightweight "goroutines"
(go
  (>! ch "from goroutine")
  (println "sent!"))

(go
  (let [msg (<! ch)]
    (println "received:" msg)))
```

### Pipeline pattern

```clojure
(defn process-pipeline [input-ch]
  (let [validated (chan 100)
        enriched (chan 100)
        output (chan 100)]

    ;; Stage 1: Validate
    (go-loop []
      (when-let [item (<! input-ch)]
        (when (valid? item)
          (>! validated item))
        (recur)))

    ;; Stage 2: Enrich
    (go-loop []
      (when-let [item (<! validated)]
        (>! enriched (enrich item))
        (recur)))

    ;; Stage 3: Save
    (go-loop []
      (when-let [item (<! enriched)]
        (>! output (save! item))
        (recur)))

    output))
```

### Timeouts

```clojure
(go
  (let [[result ch] (async/alts! [data-ch (async/timeout 5000)])]
    (if result
      (println "Got data:" result)
      (println "Timed out!"))))
```

## Practical: Concurrent Web Fetcher

```clojure
(require '[clojure.core.async :as async])

(defn fetch-urls [urls]
  (let [ch (chan (count urls))]
    (doseq [url urls]
      (async/go
        (let [response (try (slurp url) (catch Exception e (.getMessage e)))]
          (async/>! ch {:url url :result response}))))
    ;; Collect results
    (loop [results [] remaining (count urls)]
      (if (zero? remaining)
        results
        (recur (conj results (async/<!! ch)) (dec remaining))))))

(fetch-urls ["https://httpbin.org/get" "https://httpbin.org/ip"])
```

## Key Takeaways

- Atoms for independent, synchronous state (90% of cases)
- Refs + `dosync` for coordinated multi-state transactions
- Agents for async, queued state changes (logging, I/O)
- Futures for simple background computation
- core.async for complex coordination (pipelines, timeouts, select)
- Immutable data means most code doesn't need references at all
