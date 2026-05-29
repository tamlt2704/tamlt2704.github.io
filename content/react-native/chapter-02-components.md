# Chapter 2: Core Components & Layout

[prev: Setup](./chapter-01-setup.md) | [next: Navigation](./chapter-03-navigation.md)

## Core Components

React Native provides platform-native components instead of HTML elements.

### View

The fundamental container — equivalent to `div`:

```typescript
import { View, StyleSheet } from "react-native";

function Card({ children }: { children: React.ReactNode }) {
  return <View style={styles.card}>{children}</View>;
}

const styles = StyleSheet.create({
  card: { padding: 16, borderRadius: 8, backgroundColor: "#f5f5f5" },
});
```

### Text

All text must be wrapped in `Text`. No raw strings allowed:

```typescript
import { Text, StyleSheet } from "react-native";

function Heading({ text }: { text: string }) {
  return <Text style={styles.heading}>{text}</Text>;
}

const styles = StyleSheet.create({
  heading: { fontSize: 24, fontWeight: "bold", color: "#333" },
});
```

### Image

```typescript
import { Image, StyleSheet } from "react-native";

// Local image
<Image source={require("./assets/logo.png")} style={styles.img} />

// Remote image (must specify dimensions)
<Image source={{ uri: "https://example.com/photo.jpg" }} style={styles.img} />

const styles = StyleSheet.create({
  img: { width: 200, height: 200, borderRadius: 8 },
});
```

### ScrollView

For scrollable content (use only for small lists):

```typescript
import { ScrollView, Text } from "react-native";

function Content() {
  return (
    <ScrollView contentContainerStyle={{ padding: 16 }}>
      <Text>Long content here...</Text>
    </ScrollView>
  );
}
```

### FlatList

For large lists — renders items lazily:

```typescript
import { FlatList, Text, View } from "react-native";

type Item = { id: string; title: string };

const data: Item[] = [
  { id: "1", title: "First" },
  { id: "2", title: "Second" },
];

function ItemList() {
  return (
    <FlatList
      data={data}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <View style={{ padding: 16 }}>
          <Text>{item.title}</Text>
        </View>
      )}
    />
  );
}
```

### TouchableOpacity & Pressable

```typescript
import { TouchableOpacity, Pressable, Text, StyleSheet } from "react-native";

// TouchableOpacity — fades on press
<TouchableOpacity onPress={() => console.log("tapped")} style={styles.btn}>
  <Text>Tap Me</Text>
</TouchableOpacity>

// Pressable — more control over press states
<Pressable
  onPress={() => console.log("pressed")}
  style={({ pressed }) => [styles.btn, pressed && { opacity: 0.7 }]}
>
  <Text>Press Me</Text>
</Pressable>

const styles = StyleSheet.create({
  btn: { padding: 12, backgroundColor: "#007AFF", borderRadius: 8 },
});
```

### TextInput

```typescript
import { TextInput, StyleSheet } from "react-native";
import { useState } from "react";

function SearchBar() {
  const [query, setQuery] = useState("");
  return (
    <TextInput
      style={styles.input}
      value={query}
      onChangeText={setQuery}
      placeholder="Search..."
      autoCapitalize="none"
    />
  );
}

const styles = StyleSheet.create({
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 12, fontSize: 16 },
});
```

### Switch

```typescript
import { Switch, View, Text } from "react-native";
import { useState } from "react";

function ToggleSetting() {
  const [enabled, setEnabled] = useState(false);
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
      <Text>Dark Mode</Text>
      <Switch value={enabled} onValueChange={setEnabled} />
    </View>
  );
}
```

### ActivityIndicator

```typescript
import { ActivityIndicator, View } from "react-native";

function LoadingScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <ActivityIndicator size="large" color="#007AFF" />
    </View>
  );
}
```

## StyleSheet.create

Always use `StyleSheet.create` — it validates at creation time and enables optimizations:

```typescript
const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
});
```

## Flexbox Layout

React Native uses flexbox by default. Key difference from web: `flexDirection` defaults to `"column"`.

### flex

```typescript
<View style={{ flex: 1 }}>
  <View style={{ flex: 1, backgroundColor: "red" }} />
  <View style={{ flex: 2, backgroundColor: "blue" }} />
</View>
// Red gets 1/3, blue gets 2/3
```

### flexDirection

```typescript
<View style={{ flexDirection: "row" }}>{/* children stack horizontally */}</View>
<View style={{ flexDirection: "column" }}>{/* default: children stack vertically */}</View>
```

### justifyContent

Controls alignment along the main axis. Values: `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `space-evenly`

### alignItems

Controls alignment along the cross axis. Values: `flex-start`, `flex-end`, `center`, `stretch`, `baseline`

```typescript
<View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
  <Text>Centered both ways</Text>
</View>
```

## Mini-Project: Profile Card

```typescript
import { View, Text, Image, StyleSheet } from "react-native";

type ProfileProps = { name: string; bio: string; avatar: string };

function ProfileCard({ name, bio, avatar }: ProfileProps) {
  return (
    <View style={styles.card}>
      <Image source={{ uri: avatar }} style={styles.avatar} />
      <View style={styles.info}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.bio}>{bio}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    padding: 16,
    backgroundColor: "#fff",
    borderRadius: 12,
    elevation: 3,
  },
  avatar: { width: 64, height: 64, borderRadius: 32 },
  info: { marginLeft: 12, flex: 1, justifyContent: "center" },
  name: { fontSize: 18, fontWeight: "bold" },
  bio: { fontSize: 14, color: "#666", marginTop: 4 },
});

export default ProfileCard;
```
