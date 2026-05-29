# Chapter 10: Deployment

[prev: Testing](./chapter-09-testing.md) | [next: Overview](./chapter-00-overview.md)

## EAS Build

EAS (Expo Application Services) builds native binaries in the cloud.

```bash
npm install -g eas-cli
eas login
eas build:configure
```

This creates `eas.json`:

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  }
}
```

Build for platforms:

```bash
eas build --platform ios --profile production
eas build --platform android --profile production
```

## App Signing

### iOS Certificates

EAS manages certificates automatically. On first build it will:

1. Create a Distribution Certificate
2. Create a Provisioning Profile
3. Store them in your Expo account

Manual management:

```bash
eas credentials
```

### Android Keystore

EAS generates and stores your keystore automatically. To manage manually:

```bash
eas credentials --platform android
```

For existing keystores, add to `eas.json`:

```json
{
  "build": {
    "production": {
      "android": {
        "credentialsSource": "local"
      }
    }
  }
}
```

Then place `credentials.json` in project root:

```json
{
  "android": {
    "keystore": {
      "keystorePath": "./keystore.jks",
      "keystorePassword": "your-password",
      "keyAlias": "your-alias",
      "keyPassword": "your-key-password"
    }
  }
}
```

## OTA Updates (EAS Update)

Push JavaScript updates without going through app stores:

```bash
eas update:configure
eas update --branch production --message "Fix typo on home screen"
```

Configure update checking in `app.json`:

```json
{
  "expo": {
    "updates": {
      "url": "https://u.expo.dev/your-project-id",
      "fallbackToCacheTimeout": 0
    },
    "runtimeVersion": {
      "policy": "appVersion"
    }
  }
}
```

Check for updates programmatically:

```typescript
import * as Updates from "expo-updates";

async function checkForUpdate() {
  const update = await Updates.checkForUpdateAsync();
  if (update.isAvailable) {
    await Updates.fetchUpdateAsync();
    await Updates.reloadAsync();
  }
}
```

## App Store Submission (iOS)

1. Build production binary:

```bash
eas build --platform ios --profile production
```

2. Submit to App Store Connect:

```bash
eas submit --platform ios
```

3. In App Store Connect:
   - Add screenshots (6.7", 6.5", 5.5" iPhones + iPad)
   - Write description, keywords, support URL
   - Set pricing and availability
   - Submit for review

### Required `app.json` fields for iOS:

```json
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.yourname.myapp",
      "buildNumber": "1",
      "infoPlist": {
        "NSCameraUsageDescription": "Used to take profile photos",
        "NSLocationWhenInUseUsageDescription": "Used to show nearby places"
      }
    }
  }
}
```

## Google Play Submission (Android)

1. Build production AAB:

```bash
eas build --platform android --profile production
```

2. Submit to Google Play:

```bash
eas submit --platform android
```

3. In Google Play Console:
   - Create app listing with screenshots
   - Complete content rating questionnaire
   - Set up pricing and distribution
   - Upload to internal/closed/open testing track first
   - Promote to production

### Required `app.json` fields for Android:

```json
{
  "expo": {
    "android": {
      "package": "com.yourname.myapp",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "permissions": ["CAMERA", "ACCESS_FINE_LOCATION"]
    }
  }
}
```

## CI/CD with GitHub Actions

`.github/workflows/build.yml`:

```yaml
name: Build and Submit
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - run: npm test
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas build --platform all --profile production --non-interactive
      - run: eas submit --platform all --non-interactive
```

For OTA updates on every push:

```yaml
name: OTA Update
on:
  push:
    branches: [main]

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: eas update --branch production --message "${{ github.event.head_commit.message }}"
```

## App Versioning

In `app.json`:

```json
{
  "expo": {
    "version": "1.2.0",
    "ios": { "buildNumber": "5" },
    "android": { "versionCode": 5 }
  }
}
```

- `version` — user-facing version (semver)
- `buildNumber` / `versionCode` — must increment for each store submission

Automate with `eas build --auto-submit` and version bumping:

```bash
# Bump version before build
npm version patch
eas build --platform all --profile production --auto-submit
```

## Pre-Launch Checklist

- App icon and splash screen configured
- All permission descriptions filled in
- Privacy policy URL ready
- Screenshots for all required device sizes
- Test on real devices (not just simulators)
- Performance profiled (no jank on low-end devices)
- Error tracking set up (Sentry, Bugsnag)
- Analytics configured
- OTA update channel configured for hotfixes

## Summary

- EAS Build creates native binaries in the cloud
- EAS handles code signing automatically (or manually if needed)
- OTA updates push JS changes without store review
- `eas submit` automates store submission
- GitHub Actions for CI/CD: test, build, submit on every push
- Always increment `buildNumber`/`versionCode` for store submissions
