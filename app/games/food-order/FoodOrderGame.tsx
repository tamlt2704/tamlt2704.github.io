"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Script from "next/script";

interface FoodItem {
  id: string;
  emoji: string;
  name: string;
  country: "🇸🇬" | "🇻🇳";
}

interface Order {
  id: number;
  items: FoodItem[];
  status: "pending" | "cooking" | "done";
  time: number;
}

const MENU: FoodItem[] = [
  { id: "chickenrice", emoji: "🍚🐔", name: "Chicken Rice", country: "🇸🇬" },
  { id: "laksa", emoji: "🍜🌶️", name: "Laksa", country: "🇸🇬" },
  { id: "satay", emoji: "🍢🔥", name: "Satay", country: "🇸🇬" },
  { id: "rotiprata", emoji: "🫓🍛", name: "Roti Prata", country: "🇸🇬" },
  { id: "nasilemak", emoji: "🍚🥜", name: "Nasi Lemak", country: "🇸🇬" },
  { id: "charkwayteow", emoji: "🍝🔥", name: "Char Kway Teow", country: "🇸🇬" },
  { id: "icekacang", emoji: "🍧🌈", name: "Ice Kacang", country: "🇸🇬" },
  { id: "kayatoast", emoji: "🍞🥚", name: "Kaya Toast", country: "🇸🇬" },
  { id: "pho", emoji: "🍲🌿", name: "Phở", country: "🇻🇳" },
  { id: "banhmi", emoji: "🥖🥩", name: "Bánh Mì", country: "🇻🇳" },
  { id: "buncha", emoji: "🍜🥬", name: "Bún Chả", country: "🇻🇳" },
  { id: "goicuon", emoji: "🌯🥒", name: "Gỏi Cuốn", country: "🇻🇳" },
  { id: "comtam", emoji: "🍚🍖", name: "Cơm Tấm", country: "🇻🇳" },
  { id: "banhxeo", emoji: "🥞🌱", name: "Bánh Xèo", country: "🇻🇳" },
  { id: "caphe", emoji: "☕🥛", name: "Cà Phê Sữa", country: "🇻🇳" },
  { id: "chebatmau", emoji: "🍨🌈", name: "Chè Ba Màu", country: "🇻🇳" },
];

function generateRoomCode() {
  return Math.random().toString(36).substring(2, 6).toUpperCase();
}

export default function FoodOrderGame() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [cart, setCart] = useState<FoodItem[]>([]);
  const [role, setRole] = useState<"choose" | "kitchen" | "customer">("choose");
  const [roomCode, setRoomCode] = useState("");
  const [inputCode, setInputCode] = useState("");
  const [connected, setConnected] = useState(false);
  const [orderCount, setOrderCount] = useState(0);
  const [peerReady, setPeerReady] = useState(false);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const peerRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const connRef = useRef<any>(null);

  // Load PeerJS from CDN
  const onPeerScriptLoad = () => setPeerReady(true);

  const sendMessage = useCallback((msg: Record<string, unknown>) => {
    if (connRef.current && connRef.current.open) {
      connRef.current.send(JSON.stringify(msg));
    }
  }, []);

  const handleMessageRef = useRef<(data: string) => void>(() => {});
  useEffect(() => {
    handleMessageRef.current = (data: string) => {
      const msg = JSON.parse(data);
      if (msg.type === "new-order") {
        setOrders((prev) => [...prev, msg.order]);
      } else if (msg.type === "order-update") {
        setOrders(msg.orders);
      }
    };
  });

  // Kitchen: create peer and wait for connection
  const startKitchen = () => {
    if (!peerReady) return;
    const code = generateRoomCode();
    setRoomCode(code);
    setRole("kitchen");

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const Peer = (window as any).Peer;
    const peer = new Peer("foodorder-" + code, {
      config: { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] },
    });
    peerRef.current = peer;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    peer.on("connection", (conn: any) => {
      connRef.current = conn;
      conn.on("open", () => setConnected(true));
      conn.on("data", (data: string) => handleMessageRef.current(data));
      conn.on("close", () => setConnected(false));
    });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    peer.on("error", (err: any) => {
      console.error("Peer error:", err);
      if (err.type === "unavailable-id") {
        peer.destroy();
      }
    });
  };

  // Customer: connect to kitchen peer
  const joinKitchen = () => {
    if (!peerReady || !inputCode.trim()) return;
    setRole("customer");
    setRoomCode(inputCode.toUpperCase());

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const Peer = (window as any).Peer;
    const peer = new Peer(undefined, {
      config: { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] },
    });
    peerRef.current = peer;

    peer.on("open", () => {
      const conn = peer.connect("foodorder-" + inputCode.toUpperCase());
      connRef.current = conn;
      conn.on("open", () => setConnected(true));
      conn.on("data", (data: string) => handleMessageRef.current(data));
      conn.on("close", () => setConnected(false));
    });
  };

  // Cleanup
  useEffect(() => {
    return () => {
      connRef.current?.close();
      peerRef.current?.destroy();
    };
  }, []);

  const addToCart = (item: FoodItem) => setCart((prev) => [...prev, item]);
  const removeFromCart = (idx: number) => setCart((prev) => prev.filter((_, i) => i !== idx));

  const submitOrder = () => {
    if (cart.length === 0) return;
    const order: Order = {
      id: orderCount + 1,
      items: [...cart],
      status: "pending",
      time: Date.now(),
    };
    setOrderCount((c) => c + 1);
    setOrders((prev) => [...prev, order]);
    sendMessage({ type: "new-order", order });
    setCart([]);
  };

  const updateOrder = (orderId: number, status: Order["status"]) => {
    setOrders((prev) => {
      const updated = prev.map((o) => (o.id === orderId ? { ...o, status } : o));
      sendMessage({ type: "order-update", orders: updated });
      return updated;
    });
  };

  const clearDone = () => {
    setOrders((prev) => {
      const updated = prev.filter((o) => o.status !== "done");
      sendMessage({ type: "order-update", orders: updated });
      return updated;
    });
  };

  // Role selection screen
  if (role === "choose") {
    return (
      <>
        <Script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js" onLoad={onPeerScriptLoad} />
        <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-amber-50 p-6">
          <h1 className="text-3xl font-bold text-amber-800">🍽️ Food Order Game</h1>
          <p className="text-center text-amber-600">
            Play across devices! One is the kitchen, others order food.
          </p>

          <button
            onClick={startKitchen}
            disabled={!peerReady}
            className="w-64 rounded-2xl bg-gray-800 py-5 text-xl font-bold text-white shadow-lg active:scale-95 disabled:opacity-50"
          >
            👨‍🍳 I&apos;m the Kitchen
          </button>

          <div className="font-medium text-amber-600">— or —</div>

          <div className="flex flex-col items-center gap-3">
            <input
              type="text"
              placeholder="Enter room code"
              value={inputCode}
              onChange={(e) => setInputCode(e.target.value.toUpperCase())}
              maxLength={4}
              className="w-48 rounded-xl border-2 border-amber-300 px-4 py-3 text-center text-2xl font-bold tracking-widest uppercase focus:border-amber-500 focus:outline-none"
            />
            <button
              onClick={joinKitchen}
              disabled={!peerReady || inputCode.length < 4}
              className="w-64 rounded-2xl bg-green-500 py-5 text-xl font-bold text-white shadow-lg active:scale-95 disabled:opacity-50"
            >
              📱 Join as Customer
            </button>
          </div>
        </div>
      </>
    );
  }

  // Customer view (mobile)
  if (role === "customer") {
    return (
      <>
        <Script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js" onLoad={onPeerScriptLoad} />
        <div className="min-h-screen bg-amber-50 p-4">
          <div className="mb-4 flex items-center justify-between">
            <h1 className="text-2xl font-bold text-amber-800">🍽️ Order Food!</h1>
            <div
              className={`rounded-full px-3 py-1 text-xs font-bold ${connected ? "bg-green-200 text-green-800" : "bg-red-200 text-red-800"}`}
            >
              {connected ? "🟢 Connected" : "🔴 Connecting..."}
            </div>
          </div>
          <p className="mb-4 text-center text-sm text-amber-600">
            Room: <span className="font-bold">{roomCode}</span>
          </p>

          {cart.length > 0 && (
            <div className="mb-4 rounded-2xl bg-white p-3 shadow">
              <div className="flex flex-wrap gap-1">
                {cart.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => removeFromCart(i)}
                    className="rounded-full bg-amber-100 px-2 py-1 text-lg active:scale-90"
                  >
                    {item.emoji} ✕
                  </button>
                ))}
              </div>
              <button
                onClick={submitOrder}
                disabled={!connected}
                className="mt-3 w-full rounded-full bg-green-500 py-3 text-lg font-bold text-white shadow-lg active:scale-95 disabled:opacity-50"
              >
                🔔 Send to Kitchen! ({cart.length})
              </button>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            {MENU.map((item) => (
              <button
                key={item.id}
                onClick={() => addToCart(item)}
                className="flex flex-col items-center rounded-2xl bg-white p-4 shadow-md transition-transform active:scale-95 active:bg-amber-50"
              >
                <span className="text-4xl">{item.emoji}</span>
                <span className="mt-2 text-sm font-semibold text-gray-700">{item.name}</span>
                <span className="text-xs text-gray-400">{item.country}</span>
              </button>
            ))}
          </div>

          {orders.length > 0 && (
            <div className="mt-4">
              <h2 className="mb-2 font-bold text-amber-800">My Orders:</h2>
              {orders.map((o) => (
                <div
                  key={o.id}
                  className={`mb-2 rounded-xl p-3 ${
                    o.status === "done"
                      ? "bg-green-100"
                      : o.status === "cooking"
                        ? "bg-orange-100"
                        : "bg-gray-100"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">
                      {o.status === "done" ? "✅" : o.status === "cooking" ? "👨‍🍳" : "⏳"}
                    </span>
                    <span className="text-sm font-medium">Order #{o.id}</span>
                  </div>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {o.items.map((item, i) => (
                      <span key={i} className="text-lg">
                        {item.emoji}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </>
    );
  }

  // Kitchen view (desktop)
  return (
    <>
      <Script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js" onLoad={onPeerScriptLoad} />
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-white">👨‍🍳 Kitchen</h1>
          <div className="flex items-center gap-4">
            <div className="rounded-xl bg-gray-800 px-4 py-2 text-center">
              <div className="text-xs text-gray-400">Room Code</div>
              <div className="text-2xl font-bold tracking-widest text-amber-400">{roomCode}</div>
            </div>
            <div
              className={`rounded-full px-3 py-1 text-xs font-bold ${connected ? "bg-green-900 text-green-300" : "bg-yellow-900 text-yellow-300"}`}
            >
              {connected ? "🟢 Customer connected" : "⏳ Waiting for customer..."}
            </div>
            <button
              onClick={clearDone}
              className="rounded-lg bg-gray-700 px-4 py-2 text-sm text-white hover:bg-gray-600"
            >
              Clear Done ✓
            </button>
          </div>
        </div>

        {orders.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-gray-500">
            <span className="mb-4 text-6xl">🍳</span>
            <p className="text-xl">Waiting for orders...</p>
            <p className="mt-2 text-sm">
              Enter code <span className="font-bold text-amber-400">{roomCode}</span> on your phone
              to order!
            </p>
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {orders.map((order) => (
            <div
              key={order.id}
              className={`rounded-2xl p-5 shadow-lg transition-all ${
                order.status === "done"
                  ? "border-2 border-green-500 bg-green-900/50"
                  : order.status === "cooking"
                    ? "animate-pulse border-2 border-orange-500 bg-orange-900/50"
                    : "border-2 border-gray-600 bg-gray-800"
              }`}
            >
              <div className="mb-3 flex items-center justify-between">
                <span className="text-lg font-bold text-white">Order #{order.id}</span>
                <span className="text-2xl">
                  {order.status === "done" ? "✅" : order.status === "cooking" ? "🔥" : "🆕"}
                </span>
              </div>
              <div className="mb-4 flex flex-wrap gap-2">
                {order.items.map((item, i) => (
                  <div key={i} className="flex flex-col items-center rounded-xl bg-black/30 p-3">
                    <span className="text-3xl">{item.emoji}</span>
                    <span className="mt-1 text-xs text-gray-300">{item.name}</span>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                {order.status === "pending" && (
                  <button
                    onClick={() => updateOrder(order.id, "cooking")}
                    className="flex-1 rounded-full bg-orange-500 py-2 text-sm font-bold text-white active:scale-95"
                  >
                    🍳 Start Cooking
                  </button>
                )}
                {order.status === "cooking" && (
                  <button
                    onClick={() => updateOrder(order.id, "done")}
                    className="flex-1 rounded-full bg-green-500 py-2 text-sm font-bold text-white active:scale-95"
                  >
                    ✅ Done!
                  </button>
                )}
                {order.status === "done" && (
                  <span className="flex-1 py-2 text-center font-bold text-green-400">
                    Ready to serve! 🎉
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
