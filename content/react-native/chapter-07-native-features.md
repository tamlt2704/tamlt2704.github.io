# Chapter 7: Native Features

[prev: Forms & Input](./chapter-06-forms.md) | [next: Advanced Styling](./chapter-08-styling.md)

## Permissions

Expo provides a unified permissions API:

```typescript
import * as Location from "expo-location";

async function requestLocationPermission() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== "granted") {
    alert("Permission denied");
    return false;
  }
  return true;
}
```

## Push Notifications (Expo Notifications)

```bash
npx expo install expo-notifications expo-device expo-constants
```

```typescript
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import Constants from "expo-constants";
import { Platform } from "react-native";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    alert("Physical device required");
    return null;
  }

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;
  if (existing !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== "granted") return null;

  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
    });
  }

  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const token = await Notifications.getExpoPushTokenAsync({ projectId });
  return token.data;
}
```

Schedule a local notification:

```typescript
async function scheduleReminder(title: string, body: string, seconds: number) {
  await Notifications.scheduleNotificationAsync({
    content: { title, body },
    trigger: { seconds },
  });
}
```

## Location (expo-location)

```bash
npx expo install expo-location
```

```typescript
import * as Location from "expo-location";
import { useEffect, useState } from "react";
import { View, Text } from "react-native";

type Coords = { latitude: number; longitude: number };

function LocationDisplay() {
  const [coords, setCoords] = useState<Coords | null>(null);

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") return;
      const location = await Location.getCurrentPositionAsync({});
      setCoords(location.coords);
    })();
  }, []);

  if (!coords) return <Text>Getting location...</Text>;
  return <Text>Lat: {coords.latitude.toFixed(4)}, Lon: {coords.longitude.toFixed(4)}</Text>;
}
```

## File System

```bash
npx expo install expo-file-system
```

```typescript
import * as FileSystem from "expo-file-system";

async function saveData(filename: string, content: string) {
  const path = FileSystem.documentDirectory + filename;
  await FileSystem.writeAsStringAsync(path, content);
  return path;
}

async function readData(filename: string): Promise<string> {
  const path = FileSystem.documentDirectory + filename;
  return FileSystem.readAsStringAsync(path);
}

async function downloadFile(url: string, filename: string) {
  const path = FileSystem.documentDirectory + filename;
  const { uri } = await FileSystem.downloadAsync(url, path);
  return uri;
}
```

## Biometrics (expo-local-authentication)

```bash
npx expo install expo-local-authentication
```

```typescript
import * as LocalAuthentication from "expo-local-authentication";
import { Alert } from "react-native";

async function authenticate(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  if (!hasHardware) {
    Alert.alert("Biometrics not available");
    return false;
  }

  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  if (!isEnrolled) {
    Alert.alert("No biometrics enrolled");
    return false;
  }

  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Authenticate to continue",
    fallbackLabel: "Use passcode",
  });

  return result.success;
}
```

## Haptics

```bash
npx expo install expo-haptics
```

```typescript
import * as Haptics from "expo-haptics";

// Light tap feedback
function onButtonPress() {
  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
}

// Success feedback
function onSuccess() {
  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
}
```

## Device Info

```bash
npx expo install expo-device
```

```typescript
import * as Device from "expo-device";

function getDeviceInfo() {
  return {
    brand: Device.brand,
    modelName: Device.modelName,
    osName: Device.osName,
    osVersion: Device.osVersion,
    isDevice: Device.isDevice, // false on simulator
  };
}
```

## Mini-Project: Location Tracker

```typescript
import * as Location from "expo-location";
import { useEffect, useState } from "react";
import { View, Text, FlatList, Pressable, StyleSheet } from "react-native";

type LocationEntry = { id: number; latitude: number; longitude: number; timestamp: number };

export default function LocationTracker() {
  const [entries, setEntries] = useState<LocationEntry[]>([]);
  const [tracking, setTracking] = useState(false);

  useEffect(() => {
    if (!tracking) return;
    let sub: Location.LocationSubscription;
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") return;
      sub = await Location.watchPositionAsync(
        { accuracy: Location.Accuracy.High, distanceInterval: 10 },
        (loc) => {
          setEntries((prev) => [
            { id: Date.now(), latitude: loc.coords.latitude, longitude: loc.coords.longitude, timestamp: loc.timestamp },
            ...prev,
          ]);
        }
      );
    })();
    return () => { sub?.remove(); };
  }, [tracking]);

  return (
    <View style={styles.container}>
      <Pressable onPress={() => setTracking(!tracking)} style={styles.btn}>
        <Text style={styles.btnText}>{tracking ? "Stop" : "Start"} Tracking</Text>
      </Pressable>
      <FlatList
        data={entries}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <Text style={styles.entry}>
            {item.latitude.toFixed(4)}, {item.longitude.toFixed(4)}
          </Text>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, paddingTop: 60 },
  btn: { padding: 14, backgroundColor: "#007AFF", borderRadius: 8, alignItems: "center", marginBottom: 16 },
  btnText: { color: "#fff", fontWeight: "bold" },
  entry: { padding: 8, borderBottomWidth: 1, borderBottomColor: "#eee" },
});
```

## Summary

- Always request permissions before accessing native features
- Expo Notifications handles both push and local notifications
- expo-location for GPS, expo-file-system for local storage
- expo-local-authentication for Face ID / fingerprint
- expo-haptics for tactile feedback
