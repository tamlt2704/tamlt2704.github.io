# Chapter 31: Production Deployment

[prev: Building a DSL](chapter-30-dsl.md) | [next: Conclusion](chapter-32-conclusion.md)

## From REPL to Production

Your Clojure app works at the REPL. Now ship it. This chapter covers building, deploying, monitoring, and operating Clojure services in production.

## Building an Uberjar

`build.clj`:

```clojure
(ns build
  (:require [clojure.tools.build.api :as b]))

(def basis (delay (b/create-basis {:project "deps.edn"})))
(def class-dir "target/classes")
(def jar-file "target/app.jar")

(defn clean [_]
  (b/delete {:path "target"}))

(defn uberjar [_]
  (clean nil)
  (b/copy-dir {:src-dirs ["src" "resources"] :target-dir class-dir})
  (b/compile-clj {:basis @basis :src-dirs ["src"] :class-dir class-dir})
  (b/uber {:class-dir class-dir :uber-file jar-file :basis @basis
            :main 'myapp.core})
  (println "Built:" jar-file))
```

```bash
clj -T:build uberjar
java -jar target/app.jar
```

## Dockerfile

```dockerfile
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY target/app.jar app.jar
ENV JVM_OPTS="-Xms256m -Xmx512m -XX:+UseG1GC"
EXPOSE 8080
ENTRYPOINT ["sh", "-c", "java $JVM_OPTS -jar app.jar"]
```

```bash
docker build -t myapp .
docker run -p 8080:8080 -e DATABASE_URL=... myapp
```

## Configuration

```clojure
(ns myapp.config
  (:require [clojure.edn :as edn]
            [clojure.java.io :as io]))

(defn load-config []
  (let [defaults (-> (io/resource "config.edn") slurp edn/read-string)
        env-overrides {:port (some-> (System/getenv "PORT") parse-long)
                       :db-url (System/getenv "DATABASE_URL")
                       :log-level (some-> (System/getenv "LOG_LEVEL") keyword)}]
    (merge defaults (into {} (remove (comp nil? val) env-overrides)))))
```

## Graceful Shutdown

```clojure
(defn -main [& _]
  (let [config (load-config)
        server (start-server! config)
        db (connect-db! config)]
    ;; Register shutdown hook
    (.addShutdownHook (Runtime/getRuntime)
      (Thread. (fn []
                 (println "Shutting down...")
                 (.stop server)
                 (.close db)
                 (println "Goodbye."))))))
```

## Component Lifecycle (mount or integrant)

Using `mount`:

```clojure
(ns myapp.system
  (:require [mount.core :refer [defstate]]))

(defstate config
  :start (load-config))

(defstate db
  :start (connect-db! config)
  :stop (.close db))

(defstate server
  :start (start-server! config)
  :stop (.stop server))

;; Start everything:
(mount.core/start)
;; Stop everything in reverse order:
(mount.core/stop)
```

## Health Checks

```clojure
(defn health-handler [_]
  (let [db-ok (try (jdbc/execute-one! datasource ["SELECT 1"]) true
                   (catch Exception _ false))
        checks {:database db-ok
                :memory-ok (< (/ (.freeMemory (Runtime/getRuntime))
                                 (.maxMemory (Runtime/getRuntime))) 0.9)}]
    {:status (if (every? val (vals checks)) 200 503)
     :body checks}))
```

## Structured Logging

```clojure
;; deps: com.taoensso/timbre
(require '[taoensso.timbre :as log])

(log/info "Server started" {:port 8080 :env :production})
(log/error "Request failed" {:path "/api/users" :error (.getMessage e)})

;; JSON output for log aggregation:
(log/merge-config!
  {:output-fn (fn [data]
                (json/write-str {:level (:level data)
                                 :msg (:msg_ data)
                                 :ts (:timestamp_ data)}))})
```

## Metrics with Prometheus

```clojure
(def request-counter (atom {}))
(def request-duration (atom []))

(defn wrap-metrics [handler]
  (fn [request]
    (let [start (System/nanoTime)
          response (handler request)
          duration (/ (- (System/nanoTime) start) 1e6)]
      (swap! request-counter update
             [(:request-method request) (:uri request) (:status response)]
             (fnil inc 0))
      (swap! request-duration conj duration)
      response)))

(defn metrics-handler [_]
  {:status 200
   :headers {"Content-Type" "text/plain"}
   :body (str/join "\n"
           (for [[[method path status] count] @request-counter]
             (format "http_requests_total{method=\"%s\",path=\"%s\",status=\"%d\"} %d"
                     (name method) path status count)))})
```

## REPL in Production

Keep a socket REPL open for live debugging:

```clojure
;; In your -main:
(clojure.server/start-server
  {:name "repl"
   :port 5555
   :accept 'clojure.core.server/repl})
```

Connect remotely:

```bash
rlwrap nc production-host 5555
```

⚠️ Secure with SSH tunnels or network policies. Never expose to the internet.

## CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
      - uses: DeLaGuardo/setup-clojure@12.5
        with:
          cli: latest
      - run: clj -T:build uberjar
      - run: clj -M:test
      - run: docker build -t myapp .
      - run: docker push registry.example.com/myapp:${{ github.sha }}
```

## Key Takeaways

- Uberjars: single file deployment, `java -jar` anywhere
- Docker: Alpine + JRE image keeps size small (~100MB)
- Environment variables for config, EDN file for defaults
- Graceful shutdown hooks prevent request drops during deploys
- Socket REPL for live production debugging (secured!)
- Health checks + metrics for observability
- Component libraries (mount/integrant) manage startup/shutdown order
