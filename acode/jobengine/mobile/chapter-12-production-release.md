# Chapter 12: Production Release — Ship It

[← Chapter 11: Charts & Analytics](chapter-11-charts-analytics.md)

---

## The Problem

Captain Deadline: "Ship it. I want this on the App Store by Friday."

You have a working app on your simulator. But between "works on my machine" and "available on the App Store" lies a minefield:

- Code signing (iOS certificates, Android keystores)
- App Store review guidelines
- Production API configuration
- Crash reporting
- Over-the-air updates (fix bugs without App Store review)
- CI/CD pipeline for automated builds

## EAS Build: Cloud Builds Without the Pain

Building locally requires Xcode (macOS only, 12GB), Android Studio, and hours of Gradle/CocoaPods configuration. EAS Build does it in the cloud:

```bash
npm install -g eas-cli
eas login
eas build:configure
```

This creates `eas.json`:

```json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": false }
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "1234567890",
        "appleTeamId": "ABCDE12345"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "production"
      }
    }
  }
}
```

## Environment Variables for Production

```bash
# Create environment-specific configs
eas secret:create --name API_URL --value "https://api.shopzilla.com" --scope project
eas secret:create --name SENTRY_DSN --value "https://xxx@sentry.io/123" --scope project
```

```tsx
// src/services/config.ts — updated for production
import Constants from "expo-constants";

const ENV = {
  development: {
    apiUrl: "http://localhost:8080",
    sentryDsn: "",
  },
  preview: {
    apiUrl: "https://staging-api.shopzilla.com",
    sentryDsn: "https://xxx@sentry.io/staging",
  },
  production: {
    apiUrl: "https://api.shopzilla.com",
    sentryDsn: "https://xxx@sentry.io/prod",
  },
};

const channel = Constants.expoConfig?.extra?.eas?.channel ?? "development";
export const config = ENV[channel as keyof typeof ENV] ?? ENV.development;
export const API_URL = config.apiUrl;
```

## Crash Reporting with Sentry

When the app crashes on Karen's phone, you need to know about it:

```bash
npx expo install sentry-expo @sentry/react-native
```

```tsx
// src/services/sentry.ts
import * as Sentry from "@sentry/react-native";
import { config } from "./config";

export function initSentry() {
  Sentry.init({
    dsn: config.sentryDsn,
    enableAutoSessionTracking: true,
    tracesSampleRate: 0.2, // 20% of transactions for performance monitoring
    environment: __DEV__ ? "development" : "production",
    beforeSend(event) {
      // Strip sensitive data
      if (event.request?.headers) {
        delete event.request.headers["Authorization"];
      }
      return event;
    },
  });
}

// Wrap your root component
export const SentryWrapper = Sentry.wrap;
```

```tsx
// App.tsx — wrap with Sentry
import { initSentry, SentryWrapper } from "./src/services/sentry";

initSentry();

function App() {
  // ... your app
}

export default SentryWrapper(App);
```

## Over-the-Air Updates (EAS Update)

Fix a bug without waiting 3 days for App Store review:

```bash
# Push a JS-only update to all users
eas update --branch production --message "Fix: job list crash on empty payload"
```

Configure in `app.json`:

```json
{
  "expo": {
    "updates": {
      "url": "https://u.expo.dev/your-project-id",
      "enabled": true,
      "fallbackToCacheTimeout": 5000,
      "checkAutomatically": "ON_LOAD"
    },
    "runtimeVersion": {
      "policy": "appVersion"
    }
  }
}
```

Handle updates in the app:

```tsx
// src/hooks/useOTAUpdate.ts
import { useEffect } from "react";
import * as Updates from "expo-updates";
import { Alert } from "react-native";

export function useOTAUpdate() {
  useEffect(() => {
    async function checkForUpdate() {
      if (__DEV__) return; // Skip in development

      try {
        const update = await Updates.checkForUpdateAsync();
        if (update.isAvailable) {
          await Updates.fetchUpdateAsync();
          Alert.alert(
            "Update Available",
            "A new version has been downloaded. Restart to apply?",
            [
              { text: "Later", style: "cancel" },
              { text: "Restart", onPress: () => Updates.reloadAsync() },
            ]
          );
        }
      } catch (e) {
        // Silent fail — don't bother the user
        console.warn("OTA update check failed:", e);
      }
    }

    checkForUpdate();
  }, []);
}
```

## App Store Assets

### iOS: App Store Connect

Required assets:
- 6.7" screenshots (1290 × 2796) — iPhone 15 Pro Max
- 6.5" screenshots (1284 × 2778) — iPhone 14 Plus
- 5.5" screenshots (1242 × 2208) — iPhone 8 Plus
- 12.9" iPad screenshots (2048 × 2732) — for tablet support
- App icon (1024 × 1024, no alpha)
- Privacy policy URL
- App description (4000 chars max)

### Android: Google Play Console

Required assets:
- Feature graphic (1024 × 500)
- Phone screenshots (min 2, 16:9 or 9:16)
- 7" tablet screenshots
- 10" tablet screenshots
- App icon (512 × 512)
- Short description (80 chars)
- Full description (4000 chars)

## Build & Submit

```bash
# Build for both platforms
eas build --platform all --profile production

# Submit to stores
eas submit --platform ios --profile production
eas submit --platform android --profile production
```

The build runs in the cloud. ~15 minutes for iOS, ~10 for Android. You get a URL to download the artifact or it submits directly to the stores.

## CI/CD with GitHub Actions

Automate builds on every merge to `main`:

```yaml
# .github/workflows/mobile-release.yml
name: Mobile Release

on:
  push:
    branches: [main]
    paths: ["mobile/**"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: mobile/package-lock.json

      - name: Install dependencies
        run: npm ci
        working-directory: mobile

      - name: Setup EAS
        uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - name: Build iOS
        run: eas build --platform ios --profile production --non-interactive
        working-directory: mobile

      - name: Build Android
        run: eas build --platform android --profile production --non-interactive
        working-directory: mobile

      - name: Submit to stores
        if: github.ref == 'refs/heads/main'
        run: |
          eas submit --platform ios --profile production --non-interactive
          eas submit --platform android --profile production --non-interactive
        working-directory: mobile
```

## App Performance Monitoring

Track real-world performance:

```tsx
// src/services/performanceTracking.ts
import * as Sentry from "@sentry/react-native";

export function trackScreenLoad(screenName: string, durationMs: number) {
  Sentry.addBreadcrumb({
    category: "navigation",
    message: `${screenName} loaded in ${durationMs}ms`,
    level: "info",
  });
}

export function trackApiCall(endpoint: string, durationMs: number, status: number) {
  Sentry.addBreadcrumb({
    category: "api",
    message: `${endpoint} → ${status} (${durationMs}ms)`,
    level: status >= 400 ? "warning" : "info",
  });
}
```

## App Store Review Checklist

Before submitting:

| Check | Status |
|---|---|
| App doesn't crash on launch | ✓ |
| Login works with test credentials | ✓ |
| All screens load without errors | ✓ |
| Offline mode shows cached data (not blank) | ✓ |
| Push notification permission is requested in context | ✓ |
| No placeholder text or "coming soon" screens | ✓ |
| Privacy policy URL is valid | ✓ |
| App icon meets guidelines (no alpha, no badges) | ✓ |
| Screenshots are accurate (not mockups) | ✓ |
| Minimum iOS 16 / Android API 28 | ✓ |
| No private API usage | ✓ |
| HTTPS only (no HTTP in production) | ✓ |
| Works on iPad (Split View, multitasking) | ✓ |
| Charts render correctly on all screen sizes | ✓ |

## Version Strategy

```json
// app.json
{
  "expo": {
    "version": "1.0.0",           // User-facing version
    "ios": { "buildNumber": "1" }, // Increment per submission
    "android": { "versionCode": 1 } // Increment per submission
  }
}
```

With `"autoIncrement": true` in `eas.json`, build numbers increment automatically.

## The Final Architecture

```
┌─────────────────────────────────────────────────────┐
│                    App Store / Play Store             │
├─────────────────────────────────────────────────────┤
│  EAS Build (cloud)  │  EAS Submit  │  EAS Update    │
├─────────────────────────────────────────────────────┤
│                    React Native App                   │
├──────────┬──────────┬──────────┬────────────────────┤
│ Auth     │ Data     │ Offline  │ Notifications      │
│(Keychain)│(React Q) │ (MMKV)  │ (FCM/APNs)         │
├──────────┼──────────┼──────────┼────────────────────┤
│ Charts   │ Adaptive │ Gestures │ DAG Viz            │
│(Gifted)  │ Layout   │(Reanimate)│(SVG)              │
├──────────┴──────────┴──────────┴────────────────────┤
│              Backend API (Spring Boot)                │
└─────────────────────────────────────────────────────┘
```

## Verify

1. `eas build --platform all --profile preview` → builds succeed
2. Install preview build on a physical device → app works end-to-end
3. `eas update --branch preview` → OTA update applies on next launch
4. Crash the app intentionally → Sentry captures the error with stack trace
5. `eas submit` → app appears in App Store Connect / Google Play Console
6. GitHub Actions triggers on push → automated build + submit

## What You've Built

Over 12 chapters, you went from "I don't have a simulator" to a production app on the App Store:

| Chapter | What You Learned |
|---|---|
| 0 | Expo, simulators, project setup |
| 1 | React Native components, navigation, TypeScript |
| 2 | StyleSheet, FlatList, platform-specific design |
| 3 | TanStack Query, API integration, error handling |
| 4 | SSE, push notifications, background updates |
| 5 | FlatList optimization, memo, Hermes, pagination |
| 6 | Gesture Handler, Reanimated, swipe actions |
| 7 | MMKV, offline queue, optimistic updates, sync |
| 8 | Secure storage, biometrics, JWT, role-based UI |
| 9 | SVG rendering, pan/zoom, DAG layout algorithms |
| 10 | Responsive layouts, tablet, foldable, master-detail |
| 11 | Charts, analytics dashboard, data visualization |
| 12 | EAS Build, OTA updates, crash reporting, CI/CD |

Karen opens the App Store on her phone. Searches "ShopZilla Jobs." Downloads it. Logs in with Face ID. Her jobs appear instantly from the cache. A push notification arrives: "CSV_IMPORT completed ✓." She swipes it to dismiss.

Captain Deadline opens the Analytics tab in a board meeting. The CEO sees charts — success rate trending up, failure rate trending down. He pinches to zoom the pipeline on his Galaxy Z Fold. The app adapts from phone to tablet layout seamlessly.

The app is live. The team is happy. Mrs. Jira already has 14 new tickets.

---

[← Chapter 11: Charts & Analytics](chapter-11-charts-analytics.md)
