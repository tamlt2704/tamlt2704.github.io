# Chapter 9: Testing

[prev: Advanced Styling](./chapter-08-styling.md) | [next: Deployment](./chapter-10-deployment.md)

## Setup

```bash
npx expo install -- --save-dev jest @testing-library/react-native @testing-library/jest-native jest-expo
```

In `package.json`:

```json
{
  "scripts": {
    "test": "jest"
  },
  "jest": {
    "preset": "jest-expo",
    "setupFilesAfterFramework": ["@testing-library/jest-native/extend-expect"]
  }
}
```

## Component Tests

```typescript
// components/Counter.tsx
import { View, Text, Pressable, StyleSheet } from "react-native";
import { useState } from "react";

export function Counter() {
  const [count, setCount] = useState(0);
  return (
    <View style={styles.container}>
      <Text testID="count">{count}</Text>
      <Pressable onPress={() => setCount((c) => c + 1)} testID="increment">
        <Text>+</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: "center", gap: 8 },
});
```

```typescript
// components/__tests__/Counter.test.tsx
import { render, fireEvent, screen } from "@testing-library/react-native";
import { Counter } from "../Counter";

describe("Counter", () => {
  it("renders initial count of 0", () => {
    render(<Counter />);
    expect(screen.getByTestId("count")).toHaveTextContent("0");
  });

  it("increments on press", () => {
    render(<Counter />);
    fireEvent.press(screen.getByTestId("increment"));
    expect(screen.getByTestId("count")).toHaveTextContent("1");
  });
});
```

## Testing with async operations

```typescript
import { render, screen, waitFor } from "@testing-library/react-native";
import { PostList } from "../PostList";

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([{ id: 1, title: "Test Post" }]),
  })
) as jest.Mock;

describe("PostList", () => {
  it("displays posts after loading", async () => {
    render(<PostList />);
    await waitFor(() => {
      expect(screen.getByText("Test Post")).toBeTruthy();
    });
  });
});
```

## Mocking Native Modules

```typescript
// __mocks__/expo-location.ts
export const requestForegroundPermissionsAsync = jest.fn(() =>
  Promise.resolve({ status: "granted" }),
);

export const getCurrentPositionAsync = jest.fn(() =>
  Promise.resolve({ coords: { latitude: 51.5, longitude: -0.1 } }),
);
```

In `jest.config.js` or `package.json`:

```json
{
  "jest": {
    "moduleNameMapper": {
      "expo-location": "<rootDir>/__mocks__/expo-location.ts"
    }
  }
}
```

## Snapshot Testing

```typescript
import { render } from "@testing-library/react-native";
import ProfileCard from "../ProfileCard";

describe("ProfileCard", () => {
  it("matches snapshot", () => {
    const tree = render(
      <ProfileCard name="John" bio="Developer" avatar="https://example.com/avatar.jpg" />
    );
    expect(tree.toJSON()).toMatchSnapshot();
  });
});
```

Update snapshots when intentional changes are made:

```bash
npx jest --updateSnapshot
```

## E2E Testing with Detox

```bash
npm install --save-dev detox @types/detox
```

`detox.config.js`:

```javascript
module.exports = {
  testRunner: { args: { config: "e2e/jest.config.js" } },
  apps: {
    "ios.debug": {
      type: "ios.app",
      binaryPath: "ios/build/MyApp.app",
      build:
        "xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Debug -sdk iphonesimulator",
    },
    "android.debug": {
      type: "android.apk",
      binaryPath: "android/app/build/outputs/apk/debug/app-debug.apk",
      build: "cd android && ./gradlew assembleDebug",
    },
  },
  devices: {
    simulator: { type: "ios.simulator", device: { type: "iPhone 15" } },
    emulator: { type: "android.emulator", device: { avdName: "Pixel_7" } },
  },
  configurations: {
    "ios.sim.debug": { device: "simulator", app: "ios.debug" },
    "android.emu.debug": { device: "emulator", app: "android.debug" },
  },
};
```

E2E test:

```typescript
// e2e/login.test.ts
describe("Login Flow", () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  it("should login successfully", async () => {
    await element(by.id("email-input")).typeText("user@example.com");
    await element(by.id("password-input")).typeText("password123");
    await element(by.id("login-button")).tap();
    await expect(element(by.text("Welcome"))).toBeVisible();
  });
});
```

Run:

```bash
npx detox test --configuration ios.sim.debug
```

## Testing Best Practices

- Use `testID` props for reliable element selection
- Test behavior, not implementation details
- Mock external dependencies (APIs, native modules)
- Use `waitFor` for async operations
- Keep unit tests fast, E2E tests focused on critical paths

## Summary

- Jest + React Native Testing Library for unit/component tests
- Use `testID` for querying elements in tests
- Mock native modules with `moduleNameMapper`
- Snapshot tests catch unintended UI changes
- Detox for full E2E testing on real simulators
