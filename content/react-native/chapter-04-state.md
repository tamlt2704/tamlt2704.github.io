# Chapter 4: State Management

[prev: Navigation](./chapter-03-navigation.md) | [next: Working with APIs](./chapter-05-apis.md)

## Local State: useState

```typescript
import { useState } from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <View style={styles.container}>
      <Text style={styles.count}>{count}</Text>
      <Pressable onPress={() => setCount((c) => c + 1)} style={styles.btn}>
        <Text>Increment</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center" },
  count: { fontSize: 48, fontWeight: "bold" },
  btn: { marginTop: 16, padding: 12, backgroundColor: "#007AFF", borderRadius: 8 },
});
```

## Shared State: useContext

```typescript
import { createContext, useContext, useState, ReactNode } from "react";

type AuthState = { user: string | null; login: (name: string) => void; logout: () => void };

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null);
  return (
    <AuthContext.Provider value={{ user, login: setUser, logout: () => setUser(null) }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
```

## Complex Local State: useReducer

```typescript
import { useReducer } from "react";

type Todo = { id: number; text: string; done: boolean };
type Action =
  | { type: "add"; text: string }
  | { type: "toggle"; id: number }
  | { type: "remove"; id: number };

function todoReducer(state: Todo[], action: Action): Todo[] {
  switch (action.type) {
    case "add":
      return [...state, { id: Date.now(), text: action.text, done: false }];
    case "toggle":
      return state.map((t) => (t.id === action.id ? { ...t, done: !t.done } : t));
    case "remove":
      return state.filter((t) => t.id !== action.id);
  }
}

function useTodos() {
  const [todos, dispatch] = useReducer(todoReducer, []);
  return { todos, dispatch };
}
```

## Global State: Zustand

Zustand is lightweight and requires no providers:

```bash
npx expo install zustand
```

```typescript
import { create } from "zustand";

type CartItem = { id: string; name: string; qty: number };

type CartStore = {
  items: CartItem[];
  addItem: (item: Omit<CartItem, "qty">) => void;
  removeItem: (id: string) => void;
  clear: () => void;
};

export const useCartStore = create<CartStore>((set) => ({
  items: [],
  addItem: (item) =>
    set((state) => {
      const existing = state.items.find((i) => i.id === item.id);
      if (existing) {
        return { items: state.items.map((i) => (i.id === item.id ? { ...i, qty: i.qty + 1 } : i)) };
      }
      return { items: [...state.items, { ...item, qty: 1 }] };
    }),
  removeItem: (id) => set((state) => ({ items: state.items.filter((i) => i.id !== id) })),
  clear: () => set({ items: [] }),
}));

// Usage in any component — no provider needed:
function CartBadge() {
  const count = useCartStore((s) => s.items.length);
  return <Text>{count} items</Text>;
}
```

## Persistence: AsyncStorage

```bash
npx expo install @react-native-async-storage/async-storage
```

```typescript
import AsyncStorage from "@react-native-async-storage/async-storage";

async function saveToken(token: string) {
  await AsyncStorage.setItem("auth_token", token);
}

async function getToken(): Promise<string | null> {
  return AsyncStorage.getItem("auth_token");
}

async function clearToken() {
  await AsyncStorage.removeItem("auth_token");
}
```

### Zustand with persistence

```typescript
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";

type SettingsStore = {
  theme: "light" | "dark";
  setTheme: (theme: "light" | "dark") => void;
};

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      theme: "light",
      setTheme: (theme) => set({ theme }),
    }),
    { name: "settings", storage: createJSONStorage(() => AsyncStorage) },
  ),
);
```

## Server State: TanStack Query

```bash
npx expo install @tanstack/react-query
```

Setup provider:

```typescript
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainApp />
    </QueryClientProvider>
  );
}
```

Fetch data:

```typescript
import { useQuery } from "@tanstack/react-query";
import { View, Text, ActivityIndicator } from "react-native";

type Post = { id: number; title: string };

function PostList() {
  const { data, isLoading, error } = useQuery<Post[]>({
    queryKey: ["posts"],
    queryFn: () => fetch("https://jsonplaceholder.typicode.com/posts").then((r) => r.json()),
  });

  if (isLoading) return <ActivityIndicator />;
  if (error) return <Text>Error loading posts</Text>;

  return (
    <View>
      {data?.map((post) => (
        <Text key={post.id}>{post.title}</Text>
      ))}
    </View>
  );
}
```

## Mini-Project: Todo App with Zustand + AsyncStorage

```typescript
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { View, Text, TextInput, Pressable, FlatList, StyleSheet } from "react-native";
import { useState } from "react";

type Todo = { id: number; text: string; done: boolean };

const useTodoStore = create<{
  todos: Todo[];
  add: (text: string) => void;
  toggle: (id: number) => void;
}>()(
  persist(
    (set) => ({
      todos: [],
      add: (text) => set((s) => ({ todos: [...s.todos, { id: Date.now(), text, done: false }] })),
      toggle: (id) =>
        set((s) => ({ todos: s.todos.map((t) => (t.id === id ? { ...t, done: !t.done } : t)) })),
    }),
    { name: "todos", storage: createJSONStorage(() => AsyncStorage) }
  )
);

export default function TodoApp() {
  const [text, setText] = useState("");
  const { todos, add, toggle } = useTodoStore();

  const handleAdd = () => {
    if (text.trim()) { add(text.trim()); setText(""); }
  };

  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <TextInput style={styles.input} value={text} onChangeText={setText} placeholder="New todo" />
        <Pressable onPress={handleAdd} style={styles.addBtn}>
          <Text style={styles.addText}>Add</Text>
        </Pressable>
      </View>
      <FlatList
        data={todos}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <Pressable onPress={() => toggle(item.id)} style={styles.todo}>
            <Text style={item.done ? styles.done : undefined}>{item.text}</Text>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, paddingTop: 60 },
  row: { flexDirection: "row", gap: 8, marginBottom: 16 },
  input: { flex: 1, borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 12 },
  addBtn: { padding: 12, backgroundColor: "#007AFF", borderRadius: 8, justifyContent: "center" },
  addText: { color: "#fff", fontWeight: "bold" },
  todo: { padding: 16, borderBottomWidth: 1, borderBottomColor: "#eee" },
  done: { textDecorationLine: "line-through", color: "#999" },
});
```

## Summary

- `useState` for simple local state, `useReducer` for complex local logic
- `useContext` for sharing state across a subtree (auth, theme)
- Zustand for global state — no boilerplate, no providers
- AsyncStorage for persisting data across app restarts
- TanStack Query for server state — handles caching, refetching, loading/error states
