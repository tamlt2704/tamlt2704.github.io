# Chapter 8: Authentication — Who Are You?

[← Chapter 7: Offline & Persistence](chapter-07-offline-persistence.md) | [Chapter 9: DAG Visualization →](chapter-09-dag-visualization.md)

---

## The Problem

Captain Deadline walks past Karen's desk. Her phone is unlocked, the job dashboard is open. He picks it up and cancels 47 jobs. "Oops."

The web dashboard has login (Chapter 8 of the frontend series). The mobile app has... nothing. Anyone who picks up the phone can see all jobs, cancel them, submit new ones. No login, no roles, no protection.

Mobile auth is harder than web auth:
- No cookies — mobile apps don't use browser cookies
- Token storage must be secure — not in plain AsyncStorage where any app can read it
- Biometric unlock — Face ID / fingerprint for quick re-auth
- Token refresh — the user shouldn't have to log in every hour
- Deep links — "shopzilla://jobs/abc-123" needs to check auth first

## The Auth Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Login   │────▶│  Token   │────▶│  Secure  │
│  Screen  │     │  from    │     │  Storage │
│          │     │  Backend │     │  (Keychain)│
└──────────┘     └──────────┘     └──────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │  Auto    │
                                  │  Attach  │
                                  │  to API  │
                                  └──────────┘
```

## Secure Token Storage

Never store tokens in AsyncStorage or MMKV — they're not encrypted at the OS level. Use the platform's secure enclave:

- **iOS**: Keychain Services
- **Android**: Android Keystore + EncryptedSharedPreferences

```bash
npx expo install expo-secure-store
```

```tsx
// src/services/secureStorage.ts
import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "auth_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "user_data";

export const secureStorage = {
  async setToken(token: string) {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  },

  async getToken(): Promise<string | null> {
    return SecureStore.getItemAsync(TOKEN_KEY);
  },

  async setRefreshToken(token: string) {
    await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, token);
  },

  async getRefreshToken(): Promise<string | null> {
    return SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
  },

  async setUser(user: { id: string; email: string; role: string }) {
    await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
  },

  async getUser() {
    const raw = await SecureStore.getItemAsync(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  },

  async clear() {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
    await SecureStore.deleteItemAsync(USER_KEY);
  },
};
```

## Auth Context & State

```tsx
// src/store/authContext.tsx
import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { secureStorage } from "../services/secureStorage";
import { API_URL } from "../services/config";

interface User {
  id: string;
  email: string;
  role: "ADMIN" | "OPERATOR" | "VIEWER";
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Restore session on app start
  useEffect(() => {
    async function restore() {
      try {
        const token = await secureStorage.getToken();
        const user = await secureStorage.getUser();

        if (token && user) {
          // Validate token is still valid
          const res = await fetch(`${API_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          if (res.ok) {
            setState({ user, token, isLoading: false, isAuthenticated: true });
          } else {
            // Token expired — try refresh
            await refreshSession();
          }
        } else {
          setState((s) => ({ ...s, isLoading: false }));
        }
      } catch {
        setState((s) => ({ ...s, isLoading: false }));
      }
    }
    restore();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({ message: "Login failed" }));
      throw new Error(body.message || `HTTP ${res.status}`);
    }

    const { token, refreshToken, user } = await res.json();

    await secureStorage.setToken(token);
    await secureStorage.setRefreshToken(refreshToken);
    await secureStorage.setUser(user);

    setState({ user, token, isLoading: false, isAuthenticated: true });
  }, []);

  const logout = useCallback(async () => {
    await secureStorage.clear();
    setState({ user: null, token: null, isLoading: false, isAuthenticated: false });
  }, []);

  const refreshSession = useCallback(async () => {
    const refreshToken = await secureStorage.getRefreshToken();
    if (!refreshToken) {
      await logout();
      return;
    }

    try {
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refreshToken }),
      });

      if (!res.ok) {
        await logout();
        return;
      }

      const { token, user } = await res.json();
      await secureStorage.setToken(token);
      await secureStorage.setUser(user);
      setState({ user, token, isLoading: false, isAuthenticated: true });
    } catch {
      await logout();
    }
  }, [logout]);

  return (
    <AuthContext.Provider value={{ ...state, login, logout, refreshSession }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
```

## Login Screen

```tsx
// src/screens/LoginScreen.tsx
import { View, Text, TextInput, Pressable, StyleSheet, Alert, KeyboardAvoidingView, Platform } from "react-native";
import { useState } from "react";
import { useAuth } from "../store/authContext";

export function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert("Missing fields", "Enter your email and password");
      return;
    }

    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch (err) {
      Alert.alert("Login failed", (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <View style={styles.form}>
        <Text style={styles.title}>ShopZilla</Text>
        <Text style={styles.subtitle}>Job Engine</Text>

        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          placeholder="Email"
          placeholderTextColor="#6b7280"
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          textContentType="emailAddress"
        />

        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          placeholder="Password"
          placeholderTextColor="#6b7280"
          secureTextEntry
          textContentType="password"
        />

        <Pressable
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={loading}
        >
          <Text style={styles.buttonText}>{loading ? "Signing in..." : "Sign In"}</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#111827", justifyContent: "center" },
  form: { paddingHorizontal: 32 },
  title: { color: "#f9fafb", fontSize: 32, fontWeight: "bold", textAlign: "center" },
  subtitle: { color: "#6b7280", fontSize: 16, textAlign: "center", marginBottom: 40 },
  input: {
    backgroundColor: "#1f2937",
    borderWidth: 1,
    borderColor: "#374151",
    borderRadius: 10,
    padding: 14,
    color: "#f9fafb",
    fontSize: 16,
    marginBottom: 12,
  },
  button: {
    backgroundColor: "#3b82f6",
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 12,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "bold" },
});
```

## Biometric Authentication

After the first login, let users unlock with Face ID / fingerprint:

```bash
npx expo install expo-local-authentication
```

```tsx
// src/services/biometrics.ts
import * as LocalAuthentication from "expo-local-authentication";
import { Platform } from "react-native";

export async function isBiometricAvailable(): Promise<boolean> {
  const compatible = await LocalAuthentication.hasHardwareAsync();
  const enrolled = await LocalAuthentication.isEnrolledAsync();
  return compatible && enrolled;
}

export async function authenticateWithBiometrics(): Promise<boolean> {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Unlock ShopZilla Jobs",
    cancelLabel: "Use Password",
    disableDeviceFallback: false,
    fallbackLabel: "Use Passcode",
  });

  return result.success;
}

export async function getBiometricType(): Promise<string> {
  const types = await LocalAuthentication.supportedAuthenticationTypesAsync();

  if (types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
    return Platform.OS === "ios" ? "Face ID" : "Face Unlock";
  }
  if (types.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
    return Platform.OS === "ios" ? "Touch ID" : "Fingerprint";
  }
  return "Biometrics";
}
```

```tsx
// src/hooks/useBiometricLogin.ts
import { useEffect, useState } from "react";
import { useAuth } from "../store/authContext";
import { isBiometricAvailable, authenticateWithBiometrics } from "../services/biometrics";
import { secureStorage } from "../services/secureStorage";

export function useBiometricLogin() {
  const { isAuthenticated } = useAuth();
  const [biometricReady, setBiometricReady] = useState(false);

  useEffect(() => {
    async function check() {
      const available = await isBiometricAvailable();
      const hasToken = await secureStorage.getToken();
      setBiometricReady(available && !!hasToken);
    }
    check();
  }, []);

  const loginWithBiometrics = async () => {
    const success = await authenticateWithBiometrics();
    if (success) {
      // Token is already in secure storage — restore session
      const token = await secureStorage.getToken();
      const user = await secureStorage.getUser();
      if (token && user) {
        // Trigger auth state update
        return true;
      }
    }
    return false;
  };

  return { biometricReady, loginWithBiometrics };
}
```

## Protected Navigation

Show login screen when not authenticated, main app when authenticated:

```tsx
// src/navigation/RootNavigator.tsx — updated
import { useAuth } from "../store/authContext";
import { LoginScreen } from "../screens/LoginScreen";
import { ActivityIndicator, View } from "react-native";

export function RootNavigator() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, backgroundColor: "#111827", justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  return (
    <NavigationContainer>
      {/* ... tabs and stacks from Chapter 1 */}
    </NavigationContainer>
  );
}
```

## Authenticated API Requests

Attach the token to every request:

```tsx
// src/services/api.ts — updated
import { secureStorage } from "./secureStorage";
import { API_URL } from "./config";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = await secureStorage.getToken();

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });

  if (res.status === 401) {
    // Token expired — trigger refresh
    const refreshToken = await secureStorage.getRefreshToken();
    if (refreshToken) {
      const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refreshToken }),
      });

      if (refreshRes.ok) {
        const { token: newToken } = await refreshRes.json();
        await secureStorage.setToken(newToken);
        // Retry original request with new token
        return request(path, options);
      }
    }
    // Refresh failed — force logout
    await secureStorage.clear();
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new Error(`${res.status}: ${body}`);
  }

  return res.json();
}
```

## Role-Based UI

Different users see different things:

```tsx
// src/components/RoleGate.tsx
import { useAuth } from "../store/authContext";

interface Props {
  roles: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGate({ roles, children, fallback = null }: Props) {
  const { user } = useAuth();

  if (!user || !roles.includes(user.role)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
```

Usage:

```tsx
<RoleGate roles={["ADMIN", "OPERATOR"]}>
  <SwipeableJobCard job={job} onPress={handlePress} />
</RoleGate>

<RoleGate roles={["VIEWER"]} fallback={<JobCard job={job} onPress={handlePress} />}>
  {/* Viewers get non-swipeable cards */}
</RoleGate>
```

## Deep Links

Handle `shopzilla://jobs/abc-123` URLs:

```json
// app.json — add scheme
{
  "expo": {
    "scheme": "shopzilla"
  }
}
```

```tsx
// src/navigation/linking.ts
import type { LinkingOptions } from "@react-navigation/native";

export const linking: LinkingOptions<any> = {
  prefixes: ["shopzilla://", "https://jobs.shopzilla.com"],
  config: {
    screens: {
      Jobs: {
        screens: {
          JobList: "jobs",
          JobDetail: "jobs/:jobId",
        },
      },
      Submit: "submit",
      Pipeline: "pipeline",
    },
  },
};
```

Deep links check auth first — if not logged in, the login screen shows, then navigates after successful auth.

## Session Timeout

Auto-lock after 5 minutes of inactivity:

```tsx
// src/hooks/useInactivityLock.ts
import { useEffect, useRef } from "react";
import { AppState } from "react-native";

const LOCK_TIMEOUT = 5 * 60 * 1000; // 5 minutes

export function useInactivityLock(onLock: () => void) {
  const backgroundTime = useRef<number>(0);

  useEffect(() => {
    const subscription = AppState.addEventListener("change", (state) => {
      if (state === "background") {
        backgroundTime.current = Date.now();
      } else if (state === "active") {
        const elapsed = Date.now() - backgroundTime.current;
        if (backgroundTime.current > 0 && elapsed > LOCK_TIMEOUT) {
          onLock(); // Require biometric re-auth
        }
      }
    });

    return () => subscription.remove();
  }, [onLock]);
}
```

## Verify

1. Open the app → login screen appears
2. Enter credentials → authenticated, job list shows
3. Kill the app → reopen → session restored from Keychain (no login needed)
4. Enable biometrics → lock phone → reopen app → Face ID prompt
5. Background for 5+ minutes → reopen → biometric prompt
6. Log in as VIEWER → swipe-to-cancel is disabled
7. Open `shopzilla://jobs/abc-123` → app opens to that job's detail
8. Token expires → next API call auto-refreshes → no interruption

Captain Deadline picks up Karen's phone. Face ID fails. "Access denied." He puts it down.

Karen picks it up. Face ID succeeds. Her jobs appear instantly. Secure and seamless.

"Show me the pipeline on my phone. The full DAG."

That's Chapter 9.

---

[← Chapter 7: Offline & Persistence](chapter-07-offline-persistence.md) | [Chapter 9: DAG Visualization →](chapter-09-dag-visualization.md)
