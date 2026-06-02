# Chapter 20: Practical — A Chat Server

[prev: A Web Scraper](chapter-19-web-scraper.md) | [next: A Build Tool](chapter-21-build-tool.md)

## What We're Building

A real-time chat server using WebSockets and core.async channels. Multiple clients connect, join rooms, and exchange messages — all managed with Clojure's concurrency primitives.

## Dependencies

```clojure
{:deps {org.clojure/clojure {:mvn/version "1.12.0"}
        org.clojure/core.async {:mvn/version "1.6.681"}
        ring/ring-core {:mvn/version "1.12.1"}
        ring/ring-jetty-adapter {:mvn/version "1.12.1"}
        info.sunng/ring-jetty9-adapter {:mvn/version "0.33.2"}}}
```

## Server State

```clojure
(ns chat.server
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! mult tap close!]]
            [ring.adapter.jetty9 :as jetty]))

;; Room -> {:clients #{ws-connections}, :history [messages]}
(def rooms (atom {}))

(defn join-room! [room-name ws username]
  (swap! rooms update room-name
         (fn [room]
           (-> (or room {:clients #{} :history []})
               (update :clients conj {:ws ws :username username})))))

(defn leave-room! [room-name ws]
  (swap! rooms update-in [room-name :clients]
         (fn [clients] (set (remove #(= (:ws %) ws) clients)))))

(defn add-message! [room-name message]
  (swap! rooms update-in [room-name :history]
         (fn [h] (take-last 100 (conj (or h []) message)))))
```

## WebSocket Handler

```clojure
(defn broadcast! [room-name message]
  (let [clients (get-in @rooms [room-name :clients])]
    (doseq [{:keys [ws]} clients]
      (try (jetty/send! ws (pr-str message))
           (catch Exception _ nil)))))

(defn ws-handler [upgrade-request]
  {:on-connect (fn [ws]
                 (println "Client connected"))

   :on-text (fn [ws text]
              (let [msg (read-string text)]
                (case (:type msg)
                  :join (do (join-room! (:room msg) ws (:username msg))
                            (broadcast! (:room msg)
                                        {:type :system
                                         :text (str (:username msg) " joined")
                                         :time (System/currentTimeMillis)})
                            ;; Send history
                            (doseq [m (get-in @rooms [(:room msg) :history])]
                              (jetty/send! ws (pr-str m))))

                  :message (let [full-msg {:type :message
                                           :username (:username msg)
                                           :text (:text msg)
                                           :room (:room msg)
                                           :time (System/currentTimeMillis)}]
                             (add-message! (:room msg) full-msg)
                             (broadcast! (:room msg) full-msg))

                  :leave (do (leave-room! (:room msg) ws)
                             (broadcast! (:room msg)
                                         {:type :system
                                          :text (str (:username msg) " left")
                                          :time (System/currentTimeMillis)})))))

   :on-close (fn [ws status-code reason]
               ;; Remove from all rooms
               (doseq [[room-name _] @rooms]
                 (leave-room! room-name ws)))

   :on-error (fn [ws e] (println "WebSocket error:" (.getMessage e)))})
```

## HTTP + WebSocket Server

```clojure
(defn app [request]
  (if (jetty/ws-upgrade-request? request)
    (jetty/ws-upgrade-response ws-handler)
    {:status 200
     :headers {"Content-Type" "text/html"}
     :body (slurp (clojure.java.io/resource "public/index.html"))}))

(defn -main [& _]
  (jetty/run-jetty app {:port 8080 :join? false})
  (println "Chat server running on http://localhost:8080"))
```

## core.async Version (Channel-Based)

```clojure
(def message-bus (chan 1000))
(def message-mult (mult message-bus))

(defn client-handler [ws username room]
  (let [client-ch (chan 100)]
    (tap message-mult client-ch)
    ;; Send filtered messages to this client
    (go-loop []
      (when-let [msg (<! client-ch)]
        (when (= (:room msg) room)
          (jetty/send! ws (pr-str msg)))
        (recur)))
    ;; Return channel for cleanup
    client-ch))

(defn publish-message! [msg]
  (async/>!! message-bus msg))
```

## CLI Chat Client

```clojure
(ns chat.client
  (:require [clojure.java.io :as io])
  (:import [java.net URI]
           [org.java_websocket.client WebSocketClient]))

(defn connect! [url username room]
  (let [client (proxy [WebSocketClient] [(URI. url)]
                 (onOpen [handshake]
                   (println "Connected!")
                   (.send this (pr-str {:type :join :username username :room room})))
                 (onMessage [message]
                   (let [{:keys [type username text]} (read-string message)]
                     (case type
                       :message (printf "[%s] %s%n" username text)
                       :system (printf "*** %s ***%n" text)
                       nil)))
                 (onClose [code reason remote]
                   (println "Disconnected:" reason))
                 (onError [ex]
                   (println "Error:" (.getMessage ex))))]
    (.connect client)
    client))
```

## Key Takeaways

- Atoms hold room state (clients + message history)
- WebSocket handlers are just maps of callback functions
- `broadcast!` iterates clients and sends to each
- core.async `mult`/`tap` for pub/sub message distribution
- EDN (`pr-str`/`read-string`) for message serialization — no JSON needed
- State is simple: maps of maps, updated atomically
