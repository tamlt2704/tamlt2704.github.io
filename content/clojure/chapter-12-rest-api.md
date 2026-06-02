# Chapter 12: Practical — A REST API

[prev: Polymorphism](chapter-11-polymorphism.md) | [next: Concurrency](chapter-13-concurrency.md)

## What We're Building

A JSON REST API for a todo app using Ring (HTTP) and Reitit (routing). You'll see how Clojure's simplicity makes web services trivial.

## Setup

`deps.edn`:

```clojure
{:deps {org.clojure/clojure {:mvn/version "1.12.0"}
        ring/ring-core {:mvn/version "1.12.1"}
        ring/ring-jetty-adapter {:mvn/version "1.12.1"}
        metosin/reitit {:mvn/version "0.7.2"}
        metosin/muuntaja {:mvn/version "0.6.10"}}
 :paths ["src"]}
```

## Ring: The Foundation

Ring is Clojure's HTTP abstraction. A web app is just a function:

```clojure
;; Request → Response
(defn handler [request]
  {:status 200
   :headers {"Content-Type" "text/plain"}
   :body "Hello, World!"})
```

That's it. A map in, a map out.

## Building the API

```clojure
(ns todo.api
  (:require [reitit.ring :as ring]
            [reitit.coercion.spec]
            [reitit.ring.coercion :as coercion]
            [reitit.ring.middleware.muuntaja :as muuntaja]
            [muuntaja.core :as m]
            [ring.adapter.jetty :as jetty]))

;; In-memory "database"
(def todos (atom {}))
(def id-counter (atom 0))

;; Handlers
(defn list-todos [_]
  {:status 200
   :body (vals @todos)})

(defn create-todo [{:keys [body-params]}]
  (let [id (swap! id-counter inc)
        todo (assoc body-params :id id :done false :created-at (str (java.time.Instant/now)))]
    (swap! todos assoc id todo)
    {:status 201
     :body todo}))

(defn get-todo [{{:keys [id]} :path-params}]
  (if-let [todo (get @todos (parse-long id))]
    {:status 200 :body todo}
    {:status 404 :body {:error "Not found"}}))

(defn update-todo [{{:keys [id]} :path-params :keys [body-params]}]
  (let [id (parse-long id)]
    (if (contains? @todos id)
      (let [updated (swap! todos update id merge body-params)]
        {:status 200 :body (get updated id)})
      {:status 404 :body {:error "Not found"}})))

(defn delete-todo [{{:keys [id]} :path-params}]
  (let [id (parse-long id)]
    (swap! todos dissoc id)
    {:status 204 :body nil}))

(defn toggle-todo [{{:keys [id]} :path-params}]
  (let [id (parse-long id)]
    (if (contains? @todos id)
      (let [updated (swap! todos update-in [id :done] not)]
        {:status 200 :body (get updated id)})
      {:status 404 :body {:error "Not found"}})))
```

## Routes

```clojure
(def app
  (ring/ring-handler
    (ring/router
      [["/api"
        ["/todos" {:get list-todos
                   :post create-todo}]
        ["/todos/:id" {:get get-todo
                       :put update-todo
                       :delete delete-todo}]
        ["/todos/:id/toggle" {:post toggle-todo}]]]
      {:data {:muuntaja m/instance
              :middleware [muuntaja/format-middleware
                          coercion/coerce-exceptions-middleware
                          coercion/coerce-request-middleware
                          coercion/coerce-response-middleware]}})))
```

## Middleware

Middleware wraps handlers — like decorators:

```clojure
(defn wrap-logging [handler]
  (fn [request]
    (let [start (System/currentTimeMillis)
          response (handler request)
          duration (- (System/currentTimeMillis) start)]
      (printf "%s %s %d (%dms)%n"
              (:request-method request)
              (:uri request)
              (:status response)
              duration)
      response)))

(defn wrap-cors [handler]
  (fn [request]
    (let [response (handler request)]
      (update response :headers merge
              {"Access-Control-Allow-Origin" "*"
               "Access-Control-Allow-Methods" "GET,POST,PUT,DELETE"
               "Access-Control-Allow-Headers" "Content-Type"}))))
```

## Starting the Server

```clojure
(defn -main [& _]
  (let [port 3000]
    (jetty/run-jetty (-> app wrap-logging wrap-cors)
                     {:port port :join? false})
    (println (str "Server running on http://localhost:" port))))
```

## Testing with curl

```bash
# Create
curl -X POST http://localhost:3000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Clojure", "priority": "high"}'

# List
curl http://localhost:3000/api/todos

# Toggle done
curl -X POST http://localhost:3000/api/todos/1/toggle

# Update
curl -X PUT http://localhost:3000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Master Clojure"}'

# Delete
curl -X DELETE http://localhost:3000/api/todos/1
```

## REPL-Driven API Development

The killer feature: modify handlers while the server is running.

```clojure
;; In your REPL:
(def server (jetty/run-jetty app {:port 3000 :join? false}))

;; Edit a handler, re-evaluate it — instantly live!
;; No restart needed.

;; Stop:
(.stop server)
```

## Key Takeaways

- Ring: request map → response map. That's the whole web framework.
- Reitit: data-driven routing (routes are just vectors)
- Middleware: functions that wrap handlers (logging, CORS, auth)
- Muuntaja: automatic JSON encoding/decoding
- REPL-driven: change code, re-eval, instantly live — no restarts
