# Chapter 24: ClojureScript and the Browser

[prev: A Database Layer](chapter-23-database.md) | [next: core.async Patterns](chapter-25-async.md)

## Clojure in the Browser

ClojureScript compiles Clojure to JavaScript. Same language, same data structures, running in browsers and Node.js. Share code between frontend and backend.

## Setup with shadow-cljs

```bash
npx create-cljs-project my-app
cd my-app
```

`shadow-cljs.edn`:

```clojure
{:source-paths ["src"]
 :dependencies [[reagent "1.2.0"]]
 :builds {:app {:target :browser
                :output-dir "public/js"
                :asset-path "/js"
                :modules {:main {:init-fn app.core/init}}}}}
```

```bash
npx shadow-cljs watch app  ;; starts dev server with hot reload
```

## Hello World

```clojure
(ns app.core)

(defn init []
  (let [el (.getElementById js/document "app")]
    (set! (.-innerHTML el) "<h1>Hello from ClojureScript!</h1>")))
```

## Reagent (React Wrapper)

Reagent lets you write React components as plain Clojure functions:

```clojure
(ns app.core
  (:require [reagent.core :as r]
            [reagent.dom :as rdom]))

;; State
(def counter (r/atom 0))

;; Components are just functions returning hiccup
(defn counter-component []
  [:div.counter
   [:h2 "Count: " @counter]
   [:button {:on-click #(swap! counter inc)} "+"]
   [:button {:on-click #(swap! counter dec)} "-"]
   [:button {:on-click #(reset! counter 0)} "Reset"]])

(defn app []
  [:div.app
   [:h1 "My ClojureScript App"]
   [counter-component]])

(defn init []
  (rdom/render [app] (.getElementById js/document "app")))
```

## Hiccup Syntax

```clojure
;; HTML as data structures:
[:div {:class "container"}
 [:h1 "Title"]
 [:p "Paragraph"]
 [:ul
  (for [item ["A" "B" "C"]]
    ^{:key item} [:li item])]]

;; CSS shorthand:
[:div#main.container.flex "content"]
;; = <div id="main" class="container flex">content</div>
```

## Todo App

```clojure
(ns app.todo
  (:require [reagent.core :as r]))

(def todos (r/atom []))
(def input-text (r/atom ""))

(defn add-todo! []
  (when (seq @input-text)
    (swap! todos conj {:id (random-uuid) :text @input-text :done false})
    (reset! input-text "")))

(defn toggle-todo! [id]
  (swap! todos (fn [ts] (mapv #(if (= (:id %) id) (update % :done not) %) ts))))

(defn delete-todo! [id]
  (swap! todos (fn [ts] (vec (remove #(= (:id %) id) ts)))))

(defn todo-input []
  [:div.flex.gap-2
   [:input {:value @input-text
            :on-change #(reset! input-text (-> % .-target .-value))
            :on-key-down #(when (= "Enter" (.-key %)) (add-todo!))
            :placeholder "What needs to be done?"}]
   [:button {:on-click add-todo!} "Add"]])

(defn todo-item [{:keys [id text done]}]
  [:li {:class (when done "line-through opacity-50")}
   [:input {:type "checkbox" :checked done :on-change #(toggle-todo! id)}]
   [:span text]
   [:button {:on-click #(delete-todo! id)} "×"]])

(defn todo-app []
  [:div
   [:h1 "Todos (" (count (remove :done @todos)) " left)"]
   [todo-input]
   [:ul (for [todo @todos]
          ^{:key (:id todo)} [todo-item todo])]])
```

## Calling JavaScript

```clojure
;; Global objects
js/console
js/window
js/document

;; Methods
(.log js/console "hello")
(.getElementById js/document "app")
(.fetch js/window "/api/data")

;; Properties
(.-innerWidth js/window)
(.-href (.-location js/window))

;; JS interop
(js/setTimeout #(println "delayed!") 1000)
(js/JSON.stringify #js {:a 1 :b 2})
```

## HTTP Requests

```clojure
(ns app.api
  (:require [cljs.core.async :refer [go]]
            [cljs.core.async.interop :refer-macros [<p!]]))

(defn fetch-todos []
  (go
    (let [response (<p! (js/fetch "/api/todos"))
          data (<p! (.json response))]
      (js->clj data :keywordize-keys true))))
```

## Shared Code (`.cljc` files)

```clojure
;; src/shared/validation.cljc — runs on both JVM and browser
(ns shared.validation)

(defn valid-email? [email]
  (re-matches #".+@.+\..+" email))

(defn validate-user [{:keys [name email]}]
  (cond-> []
    (empty? name) (conj "Name is required")
    (not (valid-email? email)) (conj "Invalid email")))
```

## Key Takeaways

- ClojureScript = same language, compiles to JS instead of JVM bytecode
- Reagent wraps React with atoms for state and hiccup for templates
- Hot reload via shadow-cljs — instant feedback during development
- `.cljc` files share code between backend and frontend
- JS interop via `js/` prefix, `.-` for properties, `.` for methods
- Same immutable data structures, same functional patterns
