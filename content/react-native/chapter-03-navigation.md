# Chapter 3: Navigation

[prev: Core Components](./chapter-02-components.md) | [next: State Management](./chapter-04-state.md)

## Setup

```bash
npx expo install @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs @react-navigation/drawer react-native-screens react-native-safe-area-context
```

## Stack Navigator

Screens push/pop like a deck of cards:

```typescript
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { View, Text, Pressable } from "react-native";

type RootStackParams = {
  Home: undefined;
  Detail: { id: string; title: string };
};

const Stack = createNativeStackNavigator<RootStackParams>();

function HomeScreen({ navigation }: any) {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Pressable onPress={() => navigation.navigate("Detail", { id: "1", title: "Item 1" })}>
        <Text>Go to Detail</Text>
      </Pressable>
    </View>
  );
}

function DetailScreen({ route }: any) {
  const { id, title } = route.params;
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text>Detail: {title} (ID: {id})</Text>
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Detail" component={DetailScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## Type-Safe Params

```typescript
import { NativeStackScreenProps } from "@react-navigation/native-stack";

type DetailProps = NativeStackScreenProps<RootStackParams, "Detail">;

function DetailScreen({ route, navigation }: DetailProps) {
  const { id, title } = route.params;
  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text>{title}</Text>
      <Pressable onPress={() => navigation.goBack()}>
        <Text>Go Back</Text>
      </Pressable>
    </View>
  );
}
```

## Tab Navigator

```typescript
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";

type TabParams = { Feed: undefined; Search: undefined; Profile: undefined };
const Tab = createBottomTabNavigator<TabParams>();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color, size }) => {
          const icons: Record<keyof TabParams, keyof typeof Ionicons.glyphMap> = {
            Feed: "home",
            Search: "search",
            Profile: "person",
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Feed" component={FeedScreen} />
      <Tab.Screen name="Search" component={SearchScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
```

## Drawer Navigator

```typescript
import { createDrawerNavigator } from "@react-navigation/drawer";

const Drawer = createDrawerNavigator();

function DrawerNavigator() {
  return (
    <Drawer.Navigator>
      <Drawer.Screen name="Home" component={HomeScreen} />
      <Drawer.Screen name="Settings" component={SettingsScreen} />
    </Drawer.Navigator>
  );
}
```

## Nested Navigators

Combine tabs with stacks:

```typescript
const HomeStack = createNativeStackNavigator();

function HomeStackNavigator() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="HomeList" component={HomeListScreen} />
      <HomeStack.Screen name="HomeDetail" component={HomeDetailScreen} />
    </HomeStack.Navigator>
  );
}

// Use inside tabs:
<Tab.Screen name="Home" component={HomeStackNavigator} />
```

## Header Customization

```typescript
<Stack.Screen
  name="Detail"
  component={DetailScreen}
  options={{
    title: "Item Detail",
    headerStyle: { backgroundColor: "#007AFF" },
    headerTintColor: "#fff",
    headerRight: () => (
      <Pressable onPress={() => alert("Menu")}>
        <Ionicons name="ellipsis-horizontal" size={24} color="#fff" />
      </Pressable>
    ),
  }}
/>
```

Dynamic header from within a screen:

```typescript
function DetailScreen({ navigation, route }: DetailProps) {
  React.useLayoutEffect(() => {
    navigation.setOptions({ title: route.params.title });
  }, [navigation, route.params.title]);
  return <View />;
}
```

## Deep Linking

```typescript
const linking = {
  prefixes: ["myapp://", "https://myapp.com"],
  config: {
    screens: {
      Home: "",
      Detail: "detail/:id",
    },
  },
};

<NavigationContainer linking={linking}>
  <Stack.Navigator>...</Stack.Navigator>
</NavigationContainer>
```

Test with:

```bash
npx uri-scheme open "myapp://detail/123" --expo
```

## Summary

- Stack for push/pop flows, Tabs for top-level sections, Drawer for side menus
- Define param types for type-safe navigation
- Nest navigators to combine patterns (tabs containing stacks)
- Use `linking` config for deep linking support
