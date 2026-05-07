import BlogPost from "../components/BlogPost";
import { Code, Section, Paragraph } from "../components/Code";

export default function Page() {
    return (
        <BlogPost
            title="Authentication: Secure Storage & Biometrics"
            date="May 9, 2026"
            series="Job Engine Mobile"
            chapter={8}
            prevSlug="jobengine-mobile-07-offline-persistence"
            prevTitle="Offline & Persistence"
            nextSlug="jobengine-mobile-09-dag-visualization"
            nextTitle="DAG Visualization"
        >
            <Section title="The Problem">
                <Paragraph>
                    Captain Deadline walks past Karen&apos;s desk. Her phone is unlocked, the job dashboard is open. He picks it up and cancels 47 jobs. &quot;Oops.&quot; No login, no roles, no protection.
                </Paragraph>
                <Paragraph>
                    Mobile auth is harder than web: no cookies, token storage must be secure (not plain AsyncStorage), biometric unlock for quick re-auth, and token refresh so users don&apos;t log in every hour.
                </Paragraph>
            </Section>

            <Section title="Secure Token Storage">
                <Paragraph>
                    Never store tokens in AsyncStorage or MMKV — they&apos;re not encrypted at the OS level. Use the platform&apos;s secure enclave: iOS Keychain or Android Keystore.
                </Paragraph>
                <Code lang="bash">{`npx expo install expo-secure-store`}</Code>
                <Code lang="tsx" title="src/services/secureStorage.ts">{`import * as SecureStore from "expo-secure-store";

export const secureStorage = {
  async setToken(token: string) {
    await SecureStore.setItemAsync("auth_token", token);
  },
  async getToken(): Promise<string | null> {
    return SecureStore.getItemAsync("auth_token");
  },
  async clear() {
    await SecureStore.deleteItemAsync("auth_token");
    await SecureStore.deleteItemAsync("refresh_token");
  },
};`}</Code>
            </Section>

            <Section title="Biometric Authentication">
                <Paragraph>
                    After the first login, let users unlock with Face ID or fingerprint:
                </Paragraph>
                <Code lang="bash">{`npx expo install expo-local-authentication`}</Code>
                <Code lang="tsx">{`import * as LocalAuthentication from "expo-local-authentication";

export async function authenticateWithBiometrics(): Promise<boolean> {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Unlock ShopZilla Jobs",
    cancelLabel: "Use Password",
    disableDeviceFallback: false,
  });
  return result.success;
}`}</Code>
            </Section>

            <Section title="Auth Context">
                <Paragraph>
                    A context provider manages the auth state — login, logout, token refresh, session restore on app start:
                </Paragraph>
                <Code lang="tsx">{`const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }) {
  // On mount: restore token from Keychain, validate with /auth/me
  // login(): POST /auth/login → store tokens in SecureStore
  // logout(): clear SecureStore, reset state
  // refreshSession(): use refresh token to get new access token
}`}</Code>
            </Section>

            <Section title="Auto Token Refresh">
                <Paragraph>
                    When a request returns 401, automatically refresh the token and retry:
                </Paragraph>
                <Code lang="tsx">{`if (res.status === 401) {
  const refreshToken = await secureStorage.getRefreshToken();
  const refreshRes = await fetch(\`\${API_URL}/auth/refresh\`, {
    method: "POST",
    body: JSON.stringify({ refreshToken }),
  });
  if (refreshRes.ok) {
    const { token } = await refreshRes.json();
    await secureStorage.setToken(token);
    return request(path, options); // Retry original request
  }
  await secureStorage.clear(); // Force re-login
}`}</Code>
            </Section>

            <Section title="Role-Based UI">
                <Code lang="tsx">{`export function RoleGate({ roles, children, fallback = null }) {
  const { user } = useAuth();
  if (!user || !roles.includes(user.role)) return fallback;
  return children;
}

// Usage: only ADMIN and OPERATOR can swipe-to-cancel
<RoleGate roles={["ADMIN", "OPERATOR"]}>
  <SwipeableJobCard job={job} />
</RoleGate>`}</Code>
            </Section>

            <Section title="Session Timeout">
                <Paragraph>
                    Auto-lock after 5 minutes of inactivity. When the app comes back from background after the timeout, require biometric re-auth.
                </Paragraph>
            </Section>

            <Section title="Verify">
                <Paragraph>
                    Open the app → login screen. Enter credentials → authenticated. Kill and reopen → session restored from Keychain. Enable biometrics → lock phone → reopen → Face ID prompt. Log in as VIEWER → swipe-to-cancel is disabled.
                </Paragraph>
                <Paragraph>
                    Captain Deadline picks up Karen&apos;s phone. Face ID fails. &quot;Access denied.&quot; He puts it down. Karen picks it up. Face ID succeeds. Her jobs appear instantly. Secure and seamless.
                </Paragraph>
            </Section>
        </BlogPost>
    );
}
