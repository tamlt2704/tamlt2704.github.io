import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Production Release: Ship It to the App Store"
            date="May 13, 2026"
            series="Job Engine Mobile"
            chapter={12}
            prevSlug="jobengine-mobile-11-charts-analytics"
            prevTitle="Charts & Analytics"
        >
            <Section title="The Problem">
                <Paragraph>
                    Captain Deadline: &quot;Ship it. I want this on the App Store by Friday.&quot; You have a working app on your simulator. But between &quot;works on my machine&quot; and &quot;available on the App Store&quot; lies code signing, review guidelines, crash reporting, and OTA updates.
                </Paragraph>
            </Section>

            <Section title="EAS Build: Cloud Builds">
                <Paragraph>
                    Building locally requires Xcode (12GB) and Android Studio. EAS Build does it in the cloud in ~15 minutes:
                </Paragraph>
                <Code lang="bash">{`npm install -g eas-cli
eas login
eas build:configure`}</Code>
                <Code lang="json" title="eas.json">{`{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": { "distribution": "internal" },
    "production": { "autoIncrement": true }
  },
  "submit": {
    "production": {
      "ios": { "appleId": "your@email.com", "ascAppId": "1234567890" },
      "android": { "serviceAccountKeyPath": "./google-service-account.json" }
    }
  }
}`}</Code>
            </Section>

            <Section title="Environment Configuration">
                <Code lang="tsx" title="src/services/config.ts">{`import Constants from "expo-constants";

const ENV = {
  development: { apiUrl: "http://localhost:8080" },
  preview: { apiUrl: "https://staging-api.shopzilla.com" },
  production: { apiUrl: "https://api.shopzilla.com" },
};

const channel = Constants.expoConfig?.extra?.eas?.channel ?? "development";
export const config = ENV[channel] ?? ENV.development;`}</Code>
            </Section>

            <Section title="Crash Reporting with Sentry">
                <Code lang="bash">{`npx expo install sentry-expo @sentry/react-native`}</Code>
                <Code lang="tsx">{`import * as Sentry from "@sentry/react-native";

Sentry.init({
  dsn: config.sentryDsn,
  tracesSampleRate: 0.2,
  beforeSend(event) {
    if (event.request?.headers) delete event.request.headers["Authorization"];
    return event;
  },
});

export default Sentry.wrap(App);`}</Code>
            </Section>

            <Section title="Over-the-Air Updates">
                <Paragraph>
                    Fix bugs without waiting for App Store review. EAS Update pushes JS-only changes directly to users:
                </Paragraph>
                <Code lang="bash">{`eas update --branch production --message "Fix: job list crash on empty payload"`}</Code>
                <Code lang="tsx">{`import * as Updates from "expo-updates";

async function checkForUpdate() {
  const update = await Updates.checkForUpdateAsync();
  if (update.isAvailable) {
    await Updates.fetchUpdateAsync();
    Alert.alert("Update Available", "Restart to apply?", [
      { text: "Later" },
      { text: "Restart", onPress: () => Updates.reloadAsync() },
    ]);
  }
}`}</Code>
            </Section>

            <Section title="CI/CD with GitHub Actions">
                <Code lang="yaml" title=".github/workflows/mobile-release.yml">{`name: Mobile Release
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
        with: { node-version: 20 }
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with: { eas-version: latest, token: \${{ secrets.EXPO_TOKEN }} }
      - run: eas build --platform all --profile production --non-interactive
      - run: eas submit --platform all --profile production --non-interactive`}</Code>
            </Section>

            <Section title="Build & Submit">
                <Code lang="bash">{`# Build for both platforms
eas build --platform all --profile production

# Submit to stores
eas submit --platform ios --profile production
eas submit --platform android --profile production`}</Code>
            </Section>

            <Section title="What You've Built">
                <Paragraph>
                    Over 12 chapters, you went from &quot;I don&apos;t have a simulator&quot; to a production app on the App Store: Expo setup, React Native components, navigation, data fetching with TanStack Query, SSE and push notifications, FlatList performance tuning, gesture handling with Reanimated, offline persistence with MMKV, secure authentication with biometrics, DAG visualization with SVG, responsive tablet/foldable layouts, charts and analytics, and finally cloud builds with CI/CD.
                </Paragraph>
                <Paragraph>
                    Karen opens the App Store. Downloads &quot;ShopZilla Jobs.&quot; Logs in with Face ID. Her jobs appear instantly from cache. A push notification arrives: &quot;CSV_IMPORT completed ✓.&quot; Captain Deadline opens the Analytics tab in a board meeting. The CEO sees charts trending up. The app is live. Mrs. Jira already has 14 new tickets.
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
