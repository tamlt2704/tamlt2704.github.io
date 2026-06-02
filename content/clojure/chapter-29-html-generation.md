# Chapter 29: Practical — An HTML Generation Library

[prev: A Web App](chapter-28-web-app.md) | [next: Building a DSL](chapter-30-dsl.md)

## What We're Building

Our own HTML generation library from scratch — turning Clojure data into HTML strings. This shows macro power and the "code as data" philosophy in action. Mirrors PCL chapters 30-31.

## The Idea

Represent HTML as Clojure vectors (Hiccup syntax):

```clojure
[:div {:class "container"}
 [:h1 "Hello"]
 [:p "World"]]
```

→ produces:

```html
<div class="container">
  <h1>Hello</h1>
  <p>World</p>
</div>
```

## The Interpreter (Runtime Rendering)

```clojure
(ns htmlgen.core
  (:require [clojure.string :as str]))

(def void-elements #{:area :base :br :col :embed :hr :img :input
                     :link :meta :param :source :track :wbr})

(defn escape-html [s]
  (-> (str s)
      (str/replace "&" "&amp;")
      (str/replace "<" "&lt;")
      (str/replace ">" "&gt;")
      (str/replace "\"" "&quot;")))

(defn render-attrs [attrs]
  (when (seq attrs)
    (str " " (str/join " "
               (map (fn [[k v]]
                      (cond
                        (true? v) (name k)
                        (false? v) nil
                        :else (str (name k) "=\"" (escape-html v) "\"")))
                    attrs)))))

(defn render
  "Convert hiccup to HTML string."
  [form]
  (cond
    (nil? form) ""
    (string? form) (escape-html form)
    (number? form) (str form)
    (keyword? form) (str "<" (name form) " />")
    (sequential? form)
    (let [[tag & rest] form
          [attrs children] (if (map? (first rest))
                             [(first rest) (rest rest)]
                             [nil rest])
          tag-name (name tag)
          attr-str (render-attrs attrs)]
      (if (void-elements tag)
        (str "<" tag-name attr-str " />")
        (str "<" tag-name attr-str ">"
             (str/join (map render children))
             "</" tag-name ">")))
    (seq? form) (str/join (map render form))
    :else (escape-html (str form))))
```

## Usage

```clojure
(render [:div {:class "card"}
         [:h2 "Title"]
         [:p {:style "color: red"} "Content"]
         [:img {:src "photo.jpg" :alt "A photo"}]])

;=> "<div class=\"card\"><h2>Title</h2><p style=\"color: red\">Content</p><img src=\"photo.jpg\" alt=\"A photo\" /></div>"
```

## Handling CSS Shorthand

Parse `[:div#main.container.flex]` into `{:id "main" :class "container flex"}`:

```clojure
(defn parse-tag [tag]
  (let [s (name tag)
        [_ tag-name id classes] (re-matches #"([^#.]+)?(?:#([^.]+))?((?:\.[^.]+)*)" s)]
    {:tag (or tag-name "div")
     :attrs (cond-> {}
              id (assoc :id id)
              (seq classes) (assoc :class (str/replace (subs classes 1) "." " ")))}))

(parse-tag :div#main.container.flex)
;=> {:tag "div", :attrs {:id "main", :class "container flex"}}
```

## The Compiler (Macro-Based, Zero Runtime Overhead)

For static templates, generate the HTML string at compile time:

```clojure
(defmacro html [& forms]
  (letfn [(compile-form [form]
            (cond
              (string? form) form
              (keyword? form) (str "<" (name form) " />")
              (vector? form)
              (let [[tag & rest] form
                    [attrs children] (if (map? (first rest))
                                      [(first rest) (rest rest)]
                                      [nil rest])
                    tag-name (name tag)]
                `(str ~(str "<" tag-name (render-attrs attrs) ">")
                      ~@(map compile-form children)
                      ~(str "</" tag-name ">")))
              :else `(escape-html (str ~form))))]
    `(str ~@(map compile-form forms))))
```

```clojure
;; At compile time, this becomes a simple string concatenation:
(html [:div {:class "greeting"}
       [:h1 "Hello!"]])
;; Expands to: (str "<div class=\"greeting\"><h1>" (escape-html (str "Hello!")) "</h1></div>")
```

## Component Pattern

```clojure
(defn card [{:keys [title body footer]}]
  [:div.card
   [:div.card-header [:h3 title]]
   [:div.card-body body]
   (when footer [:div.card-footer footer])])

(defn page [{:keys [title content]}]
  [:html
   [:head [:title title]
    [:link {:rel "stylesheet" :href "/css/style.css"}]]
   [:body
    [:header [:nav [:a {:href "/"} "Home"]]]
    [:main content]
    [:footer [:p "© 2024"]]]])

(render (page {:title "My Page"
               :content (card {:title "Hello" :body [:p "World"]})}))
```

## Streaming Output (Large Pages)

```clojure
(defn render-to-writer [form ^java.io.Writer writer]
  (cond
    (string? form) (.write writer (escape-html form))
    (vector? form)
    (let [[tag & rest] form
          [attrs children] (if (map? (first rest)) [(first rest) (rest rest)] [nil rest])]
      (.write writer (str "<" (name tag) (render-attrs attrs) ">"))
      (doseq [child children] (render-to-writer child writer))
      (.write writer (str "</" (name tag) ">")))
    (seq? form) (doseq [item form] (render-to-writer item writer))
    :else (.write writer (escape-html (str form)))))
```

## Key Takeaways

- HTML is just data — vectors and maps render to strings
- Interpreter: runtime flexibility, handles dynamic content
- Compiler (macro): zero-overhead for static templates
- CSS shorthand (`:div#id.class`) parsed at render time
- Components are just functions returning hiccup vectors
- Same pattern powers Reagent (ClojureScript), Hiccup, and our custom lib
