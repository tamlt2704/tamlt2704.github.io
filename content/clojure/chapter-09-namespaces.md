# Chapter 9: Namespaces and Project Structure

[prev: A Data Pipeline](chapter-08-data-pipeline.md) | [next: Destructuring](chapter-10-destructuring.md)

## Why Namespaces

As programs grow, you need to organize code into logical units and avoid name collisions. Namespaces are Clojure's module system.

## Defining a Namespace

```clojure
(ns myapp.users
  (:require [clojure.string :as str]
            [clojure.java.io :as io]
            [myapp.db :as db]
            [myapp.util :refer [now uuid]]))
```

The namespace `myapp.users` maps to file `src/myapp/users.clj`. Hyphens in names become underscores in filenames: `my-app.core` → `src/my_app/core.clj`.

## `:require` Options

```clojure
(ns myapp.core
  (:require
    ;; Alias — most common
    [clojure.string :as str]

    ;; Refer specific vars into current ns
    [clojure.set :refer [union intersection]]

    ;; Load without alias (use fully qualified)
    [clojure.pprint]

    ;; Refer all (avoid in production)
    [clojure.test :refer :all]))
```

## `:import` for Java Classes

```clojure
(ns myapp.core
  (:import [java.time LocalDate LocalDateTime Instant]
           [java.io File IOException]))

;; Now use without full path:
(LocalDate/now)
(Instant/now)
```

## Project Layout

```
my-project/
├── deps.edn
├── src/
│   └── myapp/
│       ├── core.clj        (ns myapp.core)
│       ├── db.clj          (ns myapp.db)
│       ├── api/
│       │   ├── routes.clj  (ns myapp.api.routes)
│       │   └── middleware.clj
│       └── domain/
│           ├── users.clj   (ns myapp.domain.users)
│           └── orders.clj  (ns myapp.domain.orders)
├── test/
│   └── myapp/
│       ├── core_test.clj
│       └── domain/
│           └── users_test.clj
└── resources/
    └── config.edn
```

## deps.edn

```clojure
{:paths ["src" "resources"]

 :deps {org.clojure/clojure {:mvn/version "1.12.0"}
        ring/ring-core {:mvn/version "1.12.1"}
        metosin/reitit {:mvn/version "0.7.2"}}

 :aliases
 {:dev {:extra-paths ["dev" "test"]
        :extra-deps {nrepl/nrepl {:mvn/version "1.1.1"}}}

  :test {:extra-paths ["test"]
         :extra-deps {lambdaisland/kaocha {:mvn/version "1.91.1392"}}
         :main-opts ["-m" "kaocha.runner"]}

  :build {:deps {io.github.clojure/tools.build {:mvn/version "0.10.5"}}
          :ns-default build}}}
```

Run with aliases:

```bash
clj -M:dev           # start with dev deps
clj -M:test          # run tests
clj -T:build uberjar # build fat JAR
```

## Accessing Other Namespaces at the REPL

```clojure
;; Load and switch to a namespace
(require '[myapp.db :as db])
(db/get-user 42)

;; Reload after editing
(require '[myapp.db :as db] :reload)

;; Switch namespace
(in-ns 'myapp.db)
```

## Private Vars

```clojure
(defn- internal-helper [x]
  (* x 2))

;; Or with metadata:
(def ^:private secret-key "abc123")
```

Private vars can't be accessed with `:refer` from other namespaces (though you can still access them with `#'myapp.core/secret` if you really need to).

## Organizing a Real App

```clojure
;; src/myapp/core.clj — entry point
(ns myapp.core
  (:require [myapp.config :as config]
            [myapp.db :as db]
            [myapp.api.server :as server]))

(defn -main [& args]
  (let [cfg (config/load!)]
    (db/connect! cfg)
    (server/start! cfg)
    (println "Started on port" (:port cfg))))
```

```clojure
;; src/myapp/config.clj
(ns myapp.config
  (:require [clojure.edn :as edn]
            [clojure.java.io :as io]))

(defn load! []
  (-> (io/resource "config.edn")
      slurp
      edn/read-string))
```

```clojure
;; src/myapp/db.clj
(ns myapp.db
  (:require [next.jdbc :as jdbc]))

(defonce datasource (atom nil))

(defn connect! [config]
  (reset! datasource (jdbc/get-datasource (:db config))))

(defn query [sql]
  (jdbc/execute! @datasource [sql]))
```

## Configuration with EDN

`resources/config.edn`:

```clojure
{:port 8080
 :db {:dbtype "postgresql"
      :host "localhost"
      :dbname "myapp"
      :user "dev"
      :password "dev123"}
 :redis {:host "localhost" :port 6379}}
```

EDN (Extensible Data Notation) is Clojure's data format — like JSON but with keywords, sets, and tagged literals.

## Key Takeaways

- One namespace per file, name maps to path (`my.ns` → `src/my/ns.clj`)
- Use `:require` with `:as` for aliases (most common pattern)
- `deps.edn` manages dependencies and aliases
- Organize by domain, not by layer (prefer `domain/users.clj` over `controllers/user_controller.clj`)
- EDN for configuration files — same syntax as Clojure data
- Use `defonce` for stateful things you don't want to reset on reload
