# Chapter 8: Advanced Styling

[prev: Native Features](./chapter-07-native-features.md) | [next: Testing](./chapter-09-testing.md)

## Responsive Design

### Dimensions

```typescript
import { Dimensions, StyleSheet } from "react-native";

const { width, height } = Dimensions.get("window");

const styles = StyleSheet.create({
  hero: { width: width, height: height * 0.4 },
  card: { width: width - 32, marginHorizontal: 16 },
});
```

### useWindowDimensions (reactive)

```typescript
import { useWindowDimensions, View, StyleSheet } from "react-native";

function ResponsiveGrid() {
  const { width } = useWindowDimensions();
  const columns = width > 768 ? 3 : 2;
  const itemWidth = (width - 48) / columns;

  return (
    <View style={styles.grid}>
      {items.map((item) => (
        <View key={item.id} style={[styles.item, { width: itemWidth }]} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  grid: { flexDirection: "row", flexWrap: "wrap", padding: 16, gap: 8 },
  item: { height: 120, backgroundColor: "#f0f0f0", borderRadius: 8 },
});
```

## Dark Mode

```typescript
import { useColorScheme, View, Text, StyleSheet } from "react-native";

function ThemedScreen() {
  const colorScheme = useColorScheme(); // "light" | "dark"
  const isDark = colorScheme === "dark";

  return (
    <View style={[styles.container, isDark && styles.containerDark]}>
      <Text style={[styles.text, isDark && styles.textDark]}>Hello</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  containerDark: { backgroundColor: "#1a1a1a" },
  text: { color: "#000", fontSize: 18 },
  textDark: { color: "#fff" },
});
```

### Theme context pattern

```typescript
import { createContext, useContext } from "react";
import { useColorScheme } from "react-native";

const colors = {
  light: { bg: "#fff", text: "#000", primary: "#007AFF", card: "#f5f5f5" },
  dark: { bg: "#1a1a1a", text: "#fff", primary: "#0A84FF", card: "#2c2c2c" },
};

const ThemeContext = createContext(colors.light);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const scheme = useColorScheme() ?? "light";
  return <ThemeContext.Provider value={colors[scheme]}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);
```

## Animations

### Animated API (built-in)

```typescript
import { Animated, Pressable, StyleSheet } from "react-native";
import { useRef } from "react";

function FadeInView({ children }: { children: React.ReactNode }) {
  const opacity = useRef(new Animated.Value(0)).current;

  const fadeIn = () => {
    Animated.timing(opacity, { toValue: 1, duration: 500, useNativeDriver: true }).start();
  };

  return (
    <Animated.View style={{ opacity }} onLayout={fadeIn}>
      {children}
    </Animated.View>
  );
}

function ScaleButton() {
  const scale = useRef(new Animated.Value(1)).current;

  const onPressIn = () => Animated.spring(scale, { toValue: 0.95, useNativeDriver: true }).start();
  const onPressOut = () => Animated.spring(scale, { toValue: 1, useNativeDriver: true }).start();

  return (
    <Pressable onPressIn={onPressIn} onPressOut={onPressOut}>
      <Animated.View style={[styles.btn, { transform: [{ scale }] }]}>
        {/* button content */}
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: { padding: 16, backgroundColor: "#007AFF", borderRadius: 8 },
});
```

### LayoutAnimation

Simple layout transitions with one line:

```typescript
import { LayoutAnimation, UIManager, Platform, View, Pressable, Text } from "react-native";
import { useState } from "react";

if (Platform.OS === "android") {
  UIManager.setLayoutAnimationEnabledExperimental?.(true);
}

function ExpandableCard() {
  const [expanded, setExpanded] = useState(false);

  const toggle = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpanded(!expanded);
  };

  return (
    <View style={{ padding: 16 }}>
      <Pressable onPress={toggle}>
        <Text>Toggle</Text>
      </Pressable>
      {expanded && <Text style={{ marginTop: 8 }}>Extra content here</Text>}
    </View>
  );
}
```

### Reanimated (high-performance)

```bash
npx expo install react-native-reanimated
```

Add to `babel.config.js`:

```javascript
module.exports = { presets: ["babel-preset-expo"], plugins: ["react-native-reanimated/plugin"] };
```

```typescript
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from "react-native-reanimated";
import { Pressable, View, StyleSheet } from "react-native";

function SpringBox() {
  const offset = useSharedValue(0);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: withSpring(offset.value) }],
  }));

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.box, animatedStyle]} />
      <Pressable onPress={() => { offset.value = offset.value === 0 ? 150 : 0; }}>
        <Animated.Text>Move</Animated.Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 16 },
  box: { width: 80, height: 80, backgroundColor: "#007AFF", borderRadius: 8 },
});
```

## Gestures (react-native-gesture-handler)

```bash
npx expo install react-native-gesture-handler
```

```typescript
import { GestureDetector, Gesture } from "react-native-gesture-handler";
import Animated, { useSharedValue, useAnimatedStyle } from "react-native-reanimated";

function DraggableBox() {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  const pan = Gesture.Pan().onUpdate((e) => {
    translateX.value = e.translationX;
    translateY.value = e.translationY;
  });

  const style = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }, { translateY: translateY.value }],
  }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={[{ width: 100, height: 100, backgroundColor: "#007AFF", borderRadius: 8 }, style]} />
    </GestureDetector>
  );
}
```

## NativeWind (Tailwind for RN)

```bash
npx expo install nativewind tailwindcss
```

Setup `tailwind.config.js`:

```javascript
module.exports = {
  content: ["./App.{js,tsx}", "./app/**/*.{js,tsx}", "./components/**/*.{js,tsx}"],
  theme: { extend: {} },
};
```

Usage:

```typescript
import { View, Text } from "react-native";

function Card() {
  return (
    <View className="flex-1 items-center justify-center bg-white dark:bg-gray-900 p-4">
      <Text className="text-2xl font-bold text-gray-900 dark:text-white">
        Styled with Tailwind
      </Text>
    </View>
  );
}
```

## Summary

- `useWindowDimensions` for reactive responsive layouts
- `useColorScheme` for system dark mode detection
- Built-in `Animated` API for simple animations, Reanimated for complex ones
- `LayoutAnimation` for effortless layout transitions
- react-native-gesture-handler for pan, pinch, swipe gestures
- NativeWind brings Tailwind utility classes to React Native
