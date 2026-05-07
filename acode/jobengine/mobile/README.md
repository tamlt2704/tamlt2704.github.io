# Job Engine Mobile — React Native Learning Series

Karen checks the dashboard on her phone during meetings. The responsive web version works, but it's clunky — no push notifications, no haptic feedback when a job fails, no quick-glance widget on her home screen. Captain Deadline wants "a real app, not a website pretending to be one."

You're building the native mobile companion for the [Job Engine backend](../backend/chapter-00-prerequisites.md). Every chapter adds a feature by solving a real problem — from "I've never opened Xcode" to "we need offline support, push notifications, and it has to survive App Store review."

## The Roadmap

| Ch | The Problem | What You Build | What You Learn |
|---|---|---|---|
| 0 | "I don't have a simulator" | Dev environment setup | React Native CLI, Expo, Android Studio, Xcode, simulators |
| 1 | "Show me something on my phone" | Hello World + navigation | Core components, JSX on mobile, React Navigation, TypeScript |
| 2 | "It looks like a web page" | Native-feeling job list | StyleSheet, FlatList, platform-specific design, safe areas |
| 3 | "Where's the data?" | API integration + **data fetching** | TanStack Query, fetch on mobile, caching, retry, background refetch |
| 4 | "I have to reopen the app to see updates" | Real-time + **push notifications** | SSE on mobile, Expo Notifications, FCM/APNs, badge counts |
| 5 | "The list stutters when I scroll" | **Performance**-tuned list | React.memo, FlatList tuning, Hermes, pagination, Flipper profiling |
| 6 | "I want to cancel jobs with a swipe" | Gestures + animations | React Native Gesture Handler, Reanimated 3, swipe actions, haptics |
| 7 | "It crashes when I lose signal" | Offline + **persistence** | MMKV, NetInfo, optimistic updates, sync queue, cache persistence |
| 8 | "Who am I logged in as?" | **Authentication** flow | Secure storage, biometrics (Face ID/fingerprint), JWT, role-based UI, deep links |
| 9 | "Show me the pipeline on mobile" | DAG visualization | React Native SVG, pan/zoom gestures, layout algorithms |
| 10 | "It looks wrong on my iPad" | **Multiple screens** + responsive | Tablet/foldable layouts, master-detail, adaptive navigation, orientation |
| 11 | "Show me trends and numbers" | **Charts** & analytics dashboard | Line/bar/pie charts, KPI cards, animated data viz, interactive tooltips |
| 12 | "Ship it to the App Store" | Production release | EAS Build, OTA updates, Sentry crash reporting, CI/CD |

## Tech Stack

| Tool | Why |
|---|---|
| React Native 0.76+ | Native performance, shared JS knowledge from web dashboard |
| Expo (managed → bare) | Fast iteration early, eject when you need native modules |
| TypeScript | Same type safety as the web dashboard |
| React Navigation 7 | Native navigation patterns (stack, tabs, drawer) |
| TanStack Query (React Query) | Server state, caching, background refetch, offline persistence |
| React Native Reanimated 3 | 60fps animations on the UI thread |
| React Native Gesture Handler | Native touch handling (swipe, pinch, pan) |
| React Native Gifted Charts | Line, bar, pie charts with animations |
| MMKV | Persistent storage 30x faster than AsyncStorage |
| Expo Secure Store | Encrypted token storage (Keychain / Android Keystore) |
| Expo Notifications | Push notifications via FCM/APNs |
| Expo Local Authentication | Biometric auth (Face ID, fingerprint) |
| React Native SVG | DAG graph rendering |
| @react-navigation/drawer | Adaptive sidebar navigation for tablets |
| Sentry | Crash reporting and performance monitoring |
| EAS Build + Update | Cloud builds, OTA updates, App Store submission |

## Prerequisites

The backend should be running (Chapters 1-9 of the backend series). The web dashboard is helpful for comparison but not required.

```bash
# Backend should be at:
curl http://localhost:8080/jobs
# → [{"id":"abc-123","status":"COMPLETED",...}]
```

Start with [Chapter 0: Setting Up →](chapter-00-setup.md)
