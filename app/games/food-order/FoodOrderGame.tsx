"use client";

import { useState, useEffect, useCallback, useRef } from "react";

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
  // Singapore
  { id: "chickenrice", emoji: "🍚🐔", name: "Chicken Rice", country: "🇸🇬" },
  { id: "laksa", emoji: "🍜🌶️", name: "Laksa", country: "🇸🇬" },
  { id: "satay", emoji: "🍢🔥", name: "Satay", country: "🇸🇬" },
  { id: "rotiprata", emoji: "🫓🍛", name: "Roti Prata", country: "🇸🇬" },
  { id: "nasilemak", emoji: "🍚🥜", name: "Nasi Lemak", country: "🇸🇬" },
  { id: "chaркwayteow", emoji: "🍝🔥", name: "Char Kway Teow", country: "🇸🇬" },
  { id: "icekacang", emoji: "🍧🌈", name: "Ice Kacang", country: "🇸🇬" },
  { id: "kayatoast", emoji: "🍞🥚", name: "Kaya Toast", country: "🇸🇬" },
  // Vietnam
  { id: "pho", emoji: "🍲🌿", name: "Phở", country: "🇻🇳" },
  { id: "banhmi", emoji: "🥖🥩", name: "Bánh Mì", country: "🇻🇳" },
  { id: "buncha", emoji: "🍜🥬", name: "Bún Chả", country: "🇻🇳" },
  { id: "goicuon", emoji: "🌯🥒", name: "Gỏi Cuốn", country: "🇻🇳" },
  { id: "comtam", emoji: "🍚🍖", name: "Cơm Tấm", country: "🇻🇳" },
  { id: "banhxeo", emoji: "🥞🌱", name: "Bánh Xèo", country: "🇻🇳" },
  { id: "caphe", emoji: "☕🥛", name: "Cà Phê Sữa", country: "🇻🇳" },
  { id: "chebatmau", emoji: "🍨🌈", name: "Chè Ba Màu", country: "🇻🇳" },
];

export default function FoodOrderGame() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [cart, setCart] = useState<FoodItem[]>([]);
  const [isDesktop] = useState(() => typeof window !== "undefined" && window.innerWidth >= 768);
  const [orderCount, setOrderCount] = useState(0);
  const channelRef = useRef<BroadcastChannel | null>(null);

  useEffect(() => {
    const ch = new BroadcastChannel("food-order-game");
    channelRef.current = ch;

    ch.onmessage = (e) => {
      if (e.data.type === "new-order") {
        setOrders((prev) => [...prev, e.data.order]);
      }
      if (e.data.type === "order-update") {
        setOrders(e.data.orders);
      }
    };

    return () => ch.close();
  }, []);

  const addToCart = (item: FoodItem) => {
    setCart((prev) => [...prev, item]);
  };

  const removeFromCart = (idx: number) => {
    setCart((prev) => prev.filter((_, i) => i !== idx));
  };

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
    channelRef.current?.postMessage({ type: "new-order", order });
    setCart([]);
  };

  const updateOrder = useCallback((orderId: number, status: Order["status"]) => {
    setOrders((prev) => {
      const updated = prev.map((o) => (o.id === orderId ? { ...o, status } : o));
      channelRef.current?.postMessage({ type: "order-update", orders: updated });
      return updated;
    });
  }, []);

  const clearDone = () => {
    setOrders((prev) => {
      const updated = prev.filter((o) => o.status !== "done");
      channelRef.current?.postMessage({ type: "order-update", orders: updated });
      return updated;
    });
  };

  // Mobile: Order Screen
  if (!isDesktop) {
    return (
      <div className="min-h-screen bg-amber-50 p-4">
        <h1 className="text-center text-2xl font-bold text-amber-800">🍽️ Order Food!</h1>
        <p className="mb-4 text-center text-sm text-amber-600">Tap to add, then send to kitchen!</p>

        {/* Cart */}
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
              className="mt-3 w-full rounded-full bg-green-500 py-3 text-lg font-bold text-white shadow-lg active:scale-95"
            >
              🔔 Send to Kitchen! ({cart.length})
            </button>
          </div>
        )}

        {/* Menu */}
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

        {/* Order status */}
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
    );
  }

  // Desktop: Kitchen Screen
  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">👨‍🍳 Kitchen</h1>
        <button
          onClick={clearDone}
          className="rounded-lg bg-gray-700 px-4 py-2 text-sm text-white hover:bg-gray-600"
        >
          Clear Done ✓
        </button>
      </div>

      {orders.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-gray-500">
          <span className="mb-4 text-6xl">🍳</span>
          <p className="text-xl">Waiting for orders...</p>
          <p className="mt-2 text-sm">Open this page on a phone to order!</p>
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
  );
}
