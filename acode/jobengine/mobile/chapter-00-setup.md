# Chapter 0: Setting Up — Your Mobile Workbench

[Chapter 1: First Screen →](chapter-01-first-screen.md)

---

## The Problem

Captain Deadline slides his phone across the table. "Karen wants to check job status from her car. The web dashboard is too small. Build me an app."

You've never built a mobile app. You don't have Xcode. You don't have Android Studio. Your terminal says `npx react-native: command not found`. Your phone is connected via USB and nothing happens.

Let's fix that.

## Choose Your Path: Expo vs Bare CLI

Two ways to start a React Native project:

| | Expo (Managed) | Bare CLI |
|---|---|---|
| Setup time | 5 minutes | 30-60 minutes |
| Native modules | Limited (until you eject) | Full access |
| Build | Cloud (EAS) or local | Local only |
| Best for | Learning, prototyping | Full native control |

We start with **Expo**. It removes 90% of the setup pain. When we need native modules (push notifications, biometrics), we'll eject to a bare workflow in Chapter 4.

## Install the Toolchain

### Node.js (if you don't have it from the web dashboard)

```bash
# macOS
brew install node

# Windows
winget install OpenJS.NodeJS.LTS

# Linux
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Verify:

```bash
node --version  # v20.x or higher
npm --version   # 10.x or higher
```

### Expo CLI

```bash
npm install -g expo-cli@latest
```

Actually — you don't even need this globally anymore. Modern Expo uses `npx`:

```bash
npx create-expo-app@latest --version
```

If that prints a version, you're good.

### Platform-Specific Setup

#### iOS (macOS only)

```bash
# Install Xcode from the App Store (it's 12GB, start now)
xcode-select --install

# Install CocoaPods
sudo gem install cocoapods

# Verify
xcodebuild -version  # Xcode 15.x+
pod --version         # 1.14+
```

Open Xcode → Settings → Platforms → Download iOS 17 Simulator.

#### Android (all platforms)

1. Download [Android Studio](https://developer.android.com/studio)
2. Open it → More Actions → SDK Manager
3. Install:
   - Android SDK Platform 34
   - Android SDK Build-Tools 34
   - Android Emulator
   - Android SDK Platform-Tools

4. Create an emulator: More Actions → Virtual Device Manager → Create Device → Pixel 7 → API 34

5. Set environment variables:

```bash
# ~/.bashrc or ~/.zshrc
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

Verify:

```bash
adb --version
emulator -list-avds  # Should show your Pixel 7
```

#### The Fast Path: Expo Go (No Simulator Needed)

Don't want to wait for Xcode to download? Install **Expo Go** on your physical phone (App Store / Play Store). You'll scan a QR code and see your app instantly.

## Create the Project

```bash
npx create-expo-app@latest jobengine-mobile --template blank-typescript
cd jobengine-mobile
```

This gives you:

```
jobengine-mobile/
├── app.json             ← Expo config (name, icon, splash)
├── App.tsx              ← entry point
├── tsconfig.json        ← TypeScript config
├── package.json
├── assets/              ← icons, splash screens
└── node_modules/
```

## Run It

```bash
npx expo start
```

You'll see a QR code in the terminal. Three options:

1. **Physical phone**: Scan the QR code with Expo Go
2. **iOS Simulator**: Press `i` (macOS only, requires Xcode)
3. **Android Emulator**: Press `a` (requires Android Studio emulator running)

You should see "Open up App.tsx to start working on your app!" on a white screen.

## Project Configuration

Update `app.json` for our project:

```json
{
  "expo": {
    "name": "ShopZilla Jobs",
    "slug": "shopzilla-jobs",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "dark",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#111827"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.shopzilla.jobs"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#111827"
      },
      "package": "com.shopzilla.jobs"
    }
  }
}
```

Dark background to match the web dashboard. We'll build on this config as we add features.

## Install Core Dependencies

These will be used across multiple chapters:

```bash
npx expo install react-native-safe-area-context react-native-screens
npm install @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs
```

## TypeScript Strict Mode

Update `tsconfig.json`:

```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

## Folder Structure

Create the structure we'll use throughout the series:

```
src/
├── components/      ← reusable UI components
├── screens/         ← full-page screens
├── hooks/           ← custom hooks
├── services/        ← API calls, storage, notifications
├── navigation/      ← React Navigation config
├── store/           ← state management
├── types/           ← TypeScript interfaces
└── utils/           ← helpers, constants
```

```bash
mkdir -p src/{components,screens,hooks,services,navigation,store,types,utils}
```

## Verify

Run `npx expo start`, press `i` or `a` or scan the QR code. You see the default screen. Replace `App.tsx`:

```tsx
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View } from "react-native";

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>ShopZilla Job Engine</Text>
      <Text style={styles.subtitle}>Mobile Dashboard</Text>
      <StatusBar style="light" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#111827",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    color: "#f9fafb",
    fontSize: 24,
    fontWeight: "bold",
  },
  subtitle: {
    color: "#6b7280",
    fontSize: 16,
    marginTop: 8,
  },
});
```

Dark screen. White text. "ShopZilla Job Engine." It's alive.

Tomorrow you'll add navigation and real screens. But today, the simulator works, the phone connects, and Captain Deadline can see progress.

---

[Chapter 1: First Screen →](chapter-01-first-screen.md)
