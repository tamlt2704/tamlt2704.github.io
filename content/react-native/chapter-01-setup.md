# Chapter 1: Setup & Environment

[prev: Overview](./chapter-00-overview.md) | [next: Core Components](./chapter-02-components.md)

## Expo vs Bare Workflow

|                | Expo (Recommended)    | Bare Workflow              |
| -------------- | --------------------- | -------------------------- |
| Setup          | One command           | Manual native config       |
| Native modules | Expo SDK + dev client | Full control               |
| OTA updates    | Built-in (EAS Update) | Manual                     |
| Build          | EAS Build (cloud)     | Local Xcode/Android Studio |

**Recommendation:** Start with Expo. You get 90% of native capabilities without touching Xcode or Android Studio. You can always eject later if needed.

## Create a New Project

```bash
npx create-expo-app@latest my-app --template blank-typescript
cd my-app
```

## Project Structure

```
my-app/
├── app.json          # Expo config (name, icon, splash)
├── App.tsx           # Entry point
├── tsconfig.json     # TypeScript config
├── package.json
├── assets/           # Images, fonts
└── node_modules/
```

## Running the App

### Start the dev server

```bash
npx expo start
```

This opens the Expo CLI with options:

- Press `i` — open iOS simulator
- Press `a` — open Android emulator
- Scan QR code — open on physical device via Expo Go

### On a Physical Device

1. Install **Expo Go** from App Store or Google Play
2. Run `npx expo start`
3. Scan the QR code with your phone camera (iOS) or Expo Go app (Android)

### On Simulators

**iOS** (macOS only):

```bash
# Install Xcode from Mac App Store, then:
npx expo start --ios
```

**Android**:

```bash
# Install Android Studio, create an AVD, then:
npx expo start --android
```

## Hot Reload

React Native supports Fast Refresh out of the box. When you save a file:

- Component changes update instantly without losing state
- If state reset is needed (e.g., hooks changed), the component remounts automatically

No configuration required — it just works with Expo.

## Your First Edit

Open `App.tsx` and replace the content:

```typescript
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View } from "react-native";

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hello React Native!</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
  },
});
```

Save the file and watch it update on your device instantly.

## Expo Configuration (app.json)

Key fields:

```json
{
  "expo": {
    "name": "My App",
    "slug": "my-app",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "bundleIdentifier": "com.yourname.myapp"
    },
    "android": {
      "package": "com.yourname.myapp"
    }
  }
}
```

## Summary

- Use Expo for the fastest path from idea to app
- `npx create-expo-app` scaffolds a TypeScript project
- Test on physical devices with Expo Go or on simulators
- Fast Refresh keeps your feedback loop tight
