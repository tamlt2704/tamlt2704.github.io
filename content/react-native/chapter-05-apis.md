# Chapter 5: Working with APIs

[prev: State Management](./chapter-04-state.md) | [next: Forms & Input](./chapter-06-forms.md)

## fetch

React Native includes the Fetch API:

```typescript
type Post = { id: number; title: string; body: string };

async function getPosts(): Promise<Post[]> {
  const response = await fetch("https://jsonplaceholder.typicode.com/posts");
  if (!response.ok) throw new Error("Failed to fetch");
  return response.json();
}
```

## axios

```bash
npx expo install axios
```

```typescript
import axios from "axios";

const api = axios.create({
  baseURL: "https://api.example.com",
  timeout: 10000,
});

type User = { id: string; name: string; email: string };

async function getUser(id: string): Promise<User> {
  const { data } = await api.get<User>(`/users/${id}`);
  return data;
}
```

## Loading & Error States

```typescript
import { View, Text, ActivityIndicator, Pressable } from "react-native";
import { useQuery } from "@tanstack/react-query";

type Post = { id: number; title: string };

function PostList() {
  const { data, isLoading, error, refetch } = useQuery<Post[]>({
    queryKey: ["posts"],
    queryFn: () => fetch("https://jsonplaceholder.typicode.com/posts").then((r) => r.json()),
  });

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text>Something went wrong</Text>
        <Pressable onPress={() => refetch()}>
          <Text style={{ color: "#007AFF", marginTop: 8 }}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View>
      {data?.map((post) => <Text key={post.id}>{post.title}</Text>)}
    </View>
  );
}
```

## Pull-to-Refresh

```typescript
import { FlatList, Text, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";

function RefreshableList() {
  const { data, isLoading, refetch, isRefetching } = useQuery<Post[]>({
    queryKey: ["posts"],
    queryFn: () => fetch("https://jsonplaceholder.typicode.com/posts").then((r) => r.json()),
  });

  return (
    <FlatList
      data={data}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item }) => <Text style={{ padding: 16 }}>{item.title}</Text>}
      refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={refetch} />}
    />
  );
}
```

## Infinite Scroll

```typescript
import { FlatList, Text, ActivityIndicator } from "react-native";
import { useInfiniteQuery } from "@tanstack/react-query";

type Page = { data: Post[]; nextPage: number | null };

function InfiniteList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery<Page>({
    queryKey: ["posts-infinite"],
    queryFn: async ({ pageParam = 1 }) => {
      const res = await fetch(`https://api.example.com/posts?page=${pageParam}&limit=20`);
      return res.json();
    },
    getNextPageParam: (lastPage) => lastPage.nextPage,
    initialPageParam: 1,
  });

  const allPosts = data?.pages.flatMap((page) => page.data) ?? [];

  return (
    <FlatList
      data={allPosts}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item }) => <Text style={{ padding: 16 }}>{item.title}</Text>}
      onEndReached={() => { if (hasNextPage) fetchNextPage(); }}
      onEndReachedThreshold={0.5}
      ListFooterComponent={isFetchingNextPage ? <ActivityIndicator /> : null}
    />
  );
}
```

## Authentication Tokens

### axios interceptors

```typescript
import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

const api = axios.create({ baseURL: "https://api.example.com" });

// Request interceptor — attach token
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("auth_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem("auth_token");
      // Navigate to login screen
    }
    return Promise.reject(error);
  },
);

export default api;
```

## Mini-Project: Weather App

```typescript
import { View, Text, TextInput, Pressable, ActivityIndicator, StyleSheet } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

const API_KEY = "your_openweather_key";

type Weather = { main: { temp: number }; weather: [{ description: string }] };

function WeatherApp() {
  const [city, setCity] = useState("London");
  const [search, setSearch] = useState("London");

  const { data, isLoading, error } = useQuery<Weather>({
    queryKey: ["weather", search],
    queryFn: () =>
      fetch(`https://api.openweathermap.org/data/2.5/weather?q=${search}&appid=${API_KEY}&units=metric`)
        .then((r) => { if (!r.ok) throw new Error("City not found"); return r.json(); }),
  });

  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <TextInput style={styles.input} value={city} onChangeText={setCity} placeholder="City" />
        <Pressable onPress={() => setSearch(city)} style={styles.btn}>
          <Text style={styles.btnText}>Search</Text>
        </Pressable>
      </View>
      {isLoading && <ActivityIndicator size="large" />}
      {error && <Text style={styles.error}>City not found</Text>}
      {data && (
        <View style={styles.result}>
          <Text style={styles.temp}>{Math.round(data.main.temp)}C</Text>
          <Text style={styles.desc}>{data.weather[0].description}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, paddingTop: 60 },
  row: { flexDirection: "row", gap: 8 },
  input: { flex: 1, borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 12 },
  btn: { padding: 12, backgroundColor: "#007AFF", borderRadius: 8, justifyContent: "center" },
  btnText: { color: "#fff", fontWeight: "bold" },
  error: { color: "red", marginTop: 16 },
  result: { marginTop: 32, alignItems: "center" },
  temp: { fontSize: 64, fontWeight: "bold" },
  desc: { fontSize: 20, color: "#666", textTransform: "capitalize" },
});

export default WeatherApp;
```

## Summary

- Use `fetch` or `axios` for HTTP requests
- TanStack Query handles loading, error, caching, and refetching
- Pull-to-refresh with `RefreshControl` on FlatList
- Infinite scroll with `useInfiniteQuery` + `onEndReached`
- axios interceptors for auth tokens and error handling
