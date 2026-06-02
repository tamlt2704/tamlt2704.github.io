# Chapter 25: core.async Patterns

[prev: ClojureScript](chapter-24-clojurescript.md) | [next: Parsing Binary Files](chapter-26-binary-parsing.md)

## Beyond Basic Channels

Chapter 13 introduced core.async. This chapter covers advanced patterns for building real systems: pipelines, fan-out, backpressure, and supervision.

## Pipeline Pattern

```clojure
(require '[clojure.core.async :as async
           :refer [chan go go-loop <! >! <!! >!! close! pipeline pipeline-async]])

;; Built-in pipeline: N parallel workers processing a channel
(let [in (chan 100)
      out (chan 100)]
  (pipeline 4 out (map #(* % %)) in)  ;; 4 workers squaring numbers
  (async/onto-chan! in (range 10))
  (<!! (async/into [] out)))
;=> [0 1 4 9 16 25 36 49 64 81]
```

## Fan-Out / Fan-In

```clojure
;; Fan-out: one source, multiple consumers
(defn fan-out [in-ch out-chs]
  (go-loop []
    (when-let [val (<! in-ch)]
      (doseq [ch out-chs]
        (>! ch val))
      (recur))))

;; Fan-in: multiple sources, one consumer
(defn fan-in [in-chs out-ch]
  (doseq [ch in-chs]
    (go-loop []
      (when-let [val (<! ch)]
        (>! out-ch val)
        (recur)))))

;; Usage: distribute work, collect results
(let [source (chan 100)
      workers (repeatedly 3 #(chan 100))
      results (chan 100)]
  (fan-out source workers)
  (fan-in workers results)
  ;; Each message goes to all workers, results merge
  )
```

## Pub/Sub

```clojure
(def event-bus (chan 1000))
(def pub (async/pub event-bus :topic))

;; Subscriber for :orders
(def order-ch (chan 50))
(async/sub pub :orders order-ch)

;; Subscriber for :users
(def user-ch (chan 50))
(async/sub pub :users user-ch)

;; Publish
(>!! event-bus {:topic :orders :data {:id 1 :amount 42}})
(>!! event-bus {:topic :users :data {:id 2 :action :login}})

;; Each subscriber only gets their topic
(<!! order-ch)  ;=> {:topic :orders, :data {:id 1, :amount 42}}
(<!! user-ch)   ;=> {:topic :users, :data {:id 2, :action :login}}
```

## Backpressure

Channels naturally provide backpressure. When a channel is full, producers block:

```clojure
(def work-queue (chan 10))  ;; only 10 items buffered

;; Producer blocks when queue is full — natural backpressure
(go-loop [i 0]
  (>! work-queue {:task i})
  (recur (inc i)))

;; Slow consumer controls the pace
(go-loop []
  (when-let [task (<! work-queue)]
    (<! (async/timeout 100))  ;; simulate work
    (println "Processed:" task)
    (recur)))
```

### Dropping/Sliding buffers (lossy)

```clojure
;; Drop newest when full
(def ch (chan (async/dropping-buffer 100)))

;; Drop oldest when full
(def ch (chan (async/sliding-buffer 100)))
```

## Rate Limiting

```clojure
(defn rate-limited-chan [source rate-ms]
  (let [out (chan)]
    (go-loop []
      (when-let [val (<! source)]
        (>! out val)
        (<! (async/timeout rate-ms))
        (recur)))
    out))

;; Process at most 1 per second
(def slow (rate-limited-chan fast-source 1000))
```

## Timeout and Retry

```clojure
(defn with-timeout [ch ms]
  (go
    (let [[val port] (async/alts! [ch (async/timeout ms)])]
      (if (= port ch)
        {:ok val}
        {:error :timeout}))))

(defn retry-async [f max-retries delay-ms]
  (go-loop [attempt 0]
    (let [result (<! (f))]
      (if (:error result)
        (if (< attempt max-retries)
          (do (<! (async/timeout (* delay-ms (Math/pow 2 attempt))))
              (recur (inc attempt)))
          result)
        result))))
```

## Worker Pool

```clojure
(defn worker-pool [n work-fn in-ch out-ch]
  (dotimes [_ n]
    (go-loop []
      (when-let [item (<! in-ch)]
        (let [result (work-fn item)]
          (>! out-ch result))
        (recur)))))

;; 10 workers processing HTTP requests
(def requests (chan 1000))
(def responses (chan 1000))
(worker-pool 10 fetch-url requests responses)
```

## Supervision (Error Recovery)

```clojure
(defn supervised-worker [name work-fn in-ch]
  (go-loop []
    (when-let [item (<! in-ch)]
      (try
        (work-fn item)
        (catch Exception e
          (println "Worker" name "error:" (.getMessage e))
          ;; Could retry, log, or put on dead-letter channel
          ))
      (recur))))
```

## Batching (Collect Then Process)

```clojure
(defn batch [in-ch size timeout-ms]
  (let [out (chan)]
    (go-loop [buf [] deadline (async/timeout timeout-ms)]
      (let [[val port] (async/alts! [in-ch deadline])]
        (cond
          ;; Channel closed
          (and (= port in-ch) (nil? val))
          (do (when (seq buf) (>! out buf))
              (close! out))

          ;; Got a value
          (= port in-ch)
          (let [new-buf (conj buf val)]
            (if (>= (count new-buf) size)
              (do (>! out new-buf) (recur [] (async/timeout timeout-ms)))
              (recur new-buf deadline)))

          ;; Timeout — flush partial batch
          :else
          (do (when (seq buf) (>! out buf))
              (recur [] (async/timeout timeout-ms))))))
    out))

;; Collect up to 100 items or flush every 5 seconds
(def batched (batch events 100 5000))
```

## Key Takeaways

- `pipeline` for parallel map/filter with bounded concurrency
- Pub/sub with `async/pub` and `async/sub` for topic-based routing
- Backpressure is automatic with bounded channels
- Rate limiting via `async/timeout` between takes
- Worker pools = N go-loops reading from shared channel
- Batching combines time-based and count-based flushing
