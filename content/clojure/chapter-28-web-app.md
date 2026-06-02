# Chapter 28: Practical — A Web Application

[prev: An MP3 Database](chapter-27-mp3-database.md) | [next: HTML Generation](chapter-29-html-generation.md)

## What We're Building

A full web application combining the MP3 database (chapter 27) with a web UI: browse artists, albums, search tracks, and stream audio. Mirrors PCL chapters 26+29.

## Server with Ring + Reitit

```clojure
(ns mp3web.server
  (:require [ring.adapter.jetty :as jetty]
            [reitit.ring :as ring]
            [muuntaja.core :as m]
            [reitit.ring.middleware.muuntaja :as muuntaja]
            [mp3db.core :as db]
            [mp3web.views :as views]))

(def app
  (ring/ring-handler
    (ring/router
      [["/" {:get {:handler views/home}}]
       ["/artists" {:get {:handler views/artist-list}}]
       ["/artists/:name" {:get {:handler views/artist-detail}}]
       ["/albums/:name" {:get {:handler views/album-detail}}]
       ["/search" {:get {:handler views/search}}]
       ["/api"
        ["/tracks" {:get {:handler api/list-tracks}}]
        ["/search" {:get {:handler api/search-tracks}}]
        ["/stats" {:get {:handler api/stats}}]]
       ["/stream/:file" {:get {:handler views/stream-file}}]]
      {:data {:muuntaja m/instance
              :middleware [muuntaja/format-middleware]}})))

(defn -main [& args]
  (db/load-db! (or (first args) "./music"))
  (jetty/run-jetty app {:port 8080 :join? false})
  (println "MP3 Web running on http://localhost:8080"))
```

## HTML Views (Server-Side Rendering)

```clojure
(ns mp3web.views
  (:require [mp3db.core :as db]
            [hiccup2.core :refer [html]]
            [clojure.string :as str]))

(defn layout [title & body]
  {:status 200
   :headers {"Content-Type" "text/html"}
   :body (str (html
    [:html
     [:head [:title title]
      [:meta {:charset "utf-8"}]
      [:link {:rel "stylesheet" :href "https://cdn.simplecss.org/simple.min.css"}]]
     [:body
      [:header [:nav [:a {:href "/"} "Home"] " | "
                     [:a {:href "/artists"} "Artists"] " | "
                     [:a {:href "/search"} "Search"]]]
      [:main body]]]))})

(defn home [_]
  (let [{:keys [total-tracks artists albums]} (db/stats)]
    (layout "MP3 Library"
      [:h1 "🎵 My Music Library"]
      [:div.stats
       [:p (str total-tracks " tracks • " artists " artists • " albums " albums")]]
      [:h2 "Top Artists"]
      [:ul (for [{:keys [artist count]} (db/top-artists 10)]
             [:li [:a {:href (str "/artists/" (java.net.URLEncoder/encode artist "UTF-8"))}
                   artist] (str " (" count " tracks)")])])))

(defn artist-list [_]
  (layout "Artists"
    [:h1 "Artists"]
    [:ul (for [artist (db/artists)]
           [:li [:a {:href (str "/artists/" (java.net.URLEncoder/encode artist "UTF-8"))}
                 artist]])]))

(defn artist-detail [{{:keys [name]} :path-params}]
  (let [decoded (java.net.URLDecoder/decode name "UTF-8")
        tracks (db/by-artist decoded)
        albums (distinct (map :album tracks))]
    (layout decoded
      [:h1 decoded]
      [:p (str (count tracks) " tracks across " (count albums) " albums")]
      (for [album albums]
        [:div
         [:h2 album]
         [:ol (for [t (filter #(= (:album %) album) tracks)]
                [:li (:title t)])]]))))

(defn search [{{:keys [q]} :query-params :as req}]
  (layout "Search"
    [:h1 "Search"]
    [:form {:method "get" :action "/search"}
     [:input {:type "text" :name "q" :value (or q "") :placeholder "Artist, album, or title..."}]
     [:button {:type "submit"} "Search"]]
    (when q
      (let [results (db/search q)]
        [:div
         [:p (str (count results) " results for \"" q "\"")]
         [:table
          [:thead [:tr [:th "Title"] [:th "Artist"] [:th "Album"]]]
          [:tbody (for [{:keys [title artist album]} (take 50 results)]
                    [:tr [:td title] [:td artist] [:td album]])]]]))))
```

## Audio Streaming

```clojure
(defn stream-file [{{:keys [file]} :path-params}]
  (let [path (java.net.URLDecoder/decode file "UTF-8")
        f (clojure.java.io/file path)]
    (if (.exists f)
      {:status 200
       :headers {"Content-Type" "audio/mpeg"
                 "Content-Length" (str (.length f))
                 "Accept-Ranges" "bytes"}
       :body f}
      {:status 404 :body "Not found"})))
```

## JSON API

```clojure
(ns mp3web.api
  (:require [mp3db.core :as db]))

(defn list-tracks [{:keys [query-params]}]
  (let [limit (parse-long (get query-params "limit" "50"))
        offset (parse-long (get query-params "offset" "0"))]
    {:status 200
     :body {:tracks (->> (:tracks @db/db) (drop offset) (take limit))
            :total (count (:tracks @db/db))}}))

(defn search-tracks [{:keys [query-params]}]
  {:status 200
   :body {:results (take 50 (db/search (get query-params "q" "")))}})

(defn stats [_]
  {:status 200
   :body (db/stats)})
```

## Key Takeaways

- Ring handlers return maps; responses are data, not objects
- Hiccup generates HTML from Clojure data structures (vectors → HTML)
- Reitit routes are data (vectors of paths + handler maps)
- File streaming: just return a `java.io.File` as the response body
- Same database functions serve both HTML views and JSON API
- Server-side rendering is trivial — just functions returning strings
