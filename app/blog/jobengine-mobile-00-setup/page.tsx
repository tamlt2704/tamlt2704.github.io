import BlogPost from "../components/BlogPost";
import { Code, Section, SubSection, Paragraph, Note } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="React Native from Scratch: Setting Up Your Mobile Workbench"
            date="May 1, 2026"
            series="Job Engine Mobile"
            chapter={0}
            nextSlug="jobengine-mobile-01-first-screen"
            nextTitle="First Screen: Navigation"
        >
            <Section title="The Problem">
                <Paragraph>
                    Captain Deadline slides his phone across the table. &quot;Karen wants to check job status from her car. The web dashboard is too small. Build me an app.&quot;
                </Paragraph>
                <Paragraph>
                    You&apos;ve never built a mobile app. You don&apos;t have Xcode. You don&apos;t have Android Studio. Your terminal says <code>npx react-native: command not found</code>. Your phone is connected via USB and nothing happens.
                </Paragraph>
            </Section>

            <Section title="Expo vs Bare CLI">
                <Paragraph>
                    Two ways to start a React Native project. Expo gives you 5-minute setup with cloud builds. Bare CLI gives full native control but takes 30-60 minutes to configure. We start with Expo — it removes 90% of the setup pain. When we need native modules (push notifications, biometrics), we&apos;ll eject.
                </Paragraph>
            </Section>

            <Section title="Install the Toolchain">
                <SubSection title="Node.js">
                    <Code lang="bash">{`# macOS
brew install node

# Windows
winget install OpenJS.NodeJS.LTS

# Verify
node --version  # v20.x or higher`}</Code>
                </SubSection>

                <SubSection title="Create the Project">
                    <Code lang="bash">{`npx create-expo-app@latest jobengine-mobile --template blank-typescript
cd jobengine-mobile`}</Code>
                    <Paragraph>This gives you a TypeScript project with Expo configured. The structure:</Paragraph>
                    <Code lang="text">{`jobengine-mobile/
├── app.json             ← Expo config (name, icon, splash)
├── App.tsx              ← entry point
├── tsconfig.json        ← TypeScript config
├── package.json
├── assets/              ← icons, splash screens
└── node_modules/`}</Code>
                </SubSection>

                <SubSection title="iOS Setup (macOS only)">
                    <Code lang="bash">{`xcode-select --install
sudo gem install cocoapods`}</Code>
                    <Paragraph>Open Xcode → Settings → Platforms → Download iOS 17 Simulator.</Paragraph>
                </SubSection>

                <SubSection title="Android Setup">
                    <Paragraph>
                        Download Android Studio, install SDK Platform 34, Build-Tools 34, Android Emulator, and Platform-Tools. Create a Pixel 7 emulator with API 34.
                    </Paragraph>
                    <Code lang="bash">{`export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools`}</Code>
                </SubSection>
            </Section>

            <Section title="Run It">
                <Code lang="bash">{`npx expo start`}</Code>
                <Paragraph>
                    You&apos;ll see a QR code. Three options: scan with Expo Go on your phone, press <code>i</code> for iOS Simulator, or press <code>a</code> for Android Emulator.
                </Paragraph>
            </Section>

            <Section title="Project Configuration">
                <Code lang="json" title="app.json">{`{
  "expo": {
    "name": "ShopZilla Jobs",
    "slug": "shopzilla-jobs",
    "version": "1.0.0",
    "orientation": "portrait",
    "userInterfaceStyle": "dark",
    "splash": {
      "backgroundColor": "#111827"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.shopzilla.jobs"
    },
    "android": {
      "package": "com.shopzilla.jobs"
    }
  }
}`}</Code>
            </Section>

            <Section title="Core Dependencies">
                <Code lang="bash">{`npx expo install react-native-safe-area-context react-native-screens
npm install @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs`}</Code>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Replace App.tsx with a dark screen showing &quot;ShopZilla Job Engine&quot; in white text. Run <code>npx expo start</code>. If you see it on your simulator or phone — you&apos;re ready for Chapter 1.
                </Paragraph>
                <Code lang="tsx" title="App.tsx">{`import { StatusBar } from "expo-status-bar";
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
  container: { flex: 1, backgroundColor: "#111827", alignItems: "center", justifyContent: "center" },
  title: { color: "#f9fafb", fontSize: 24, fontWeight: "bold" },
  subtitle: { color: "#6b7280", fontSize: 16, marginTop: 8 },
});`}</Code>
            </Section>
        </BlogPost>
    );
}
