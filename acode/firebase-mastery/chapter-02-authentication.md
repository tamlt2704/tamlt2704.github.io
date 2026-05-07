# Chapter 2: Authentication — "Users Need to Sign In"

[← Chapter 1: Setup](chapter-01-setup-deploy.md) | [Chapter 3: Firestore CRUD →](chapter-03-firestore-crud.md)

---

## The Task

Lena: "We need user accounts. Email/password for the beta testers, Google sign-in for everyone else. And I need to know who's logged in so I can show their name."

Marco: "Same auth on web and mobile. One system."

---

## Enable Auth Providers

Firebase console → Authentication → Sign-in method:

1. **Email/Password** → Enable
2. **Google** → Enable → Set support email

That's the backend configuration. No OAuth callback URLs to manage. No token rotation to implement. No password hashing to choose.

---

## The Auth SDK

```typescript
// src/firebase.ts (add to existing file)
import {
  getAuth,
  connectAuthEmulator,
  onAuthStateChanged,
  User,
} from "firebase/auth";

export const auth = getAuth(app);

if (import.meta.env.DEV) {
  connectAuthEmulator(auth, "http://localhost:9099");
}
```

---

## Sign Up with Email/Password

```typescript
// src/auth.ts
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  GoogleAuthProvider,
  signInWithPopup,
  updateProfile,
} from "firebase/auth";
import { auth } from "./firebase";

export async function signUp(email: string, password: string, name: string) {
  const credential = await createUserWithEmailAndPassword(auth, email, password);
  await updateProfile(credential.user, { displayName: name });
  return credential.user;
}

export async function signIn(email: string, password: string) {
  const credential = await signInWithEmailAndPassword(auth, email, password);
  return credential.user;
}

export async function signInWithGoogle() {
  const provider = new GoogleAuthProvider();
  const credential = await signInWithPopup(auth, provider);
  return credential.user;
}

export async function logOut() {
  await signOut(auth);
}
```

That's the entire auth layer. No JWT management. No refresh token logic. No session storage. Firebase handles all of it.

---

## Listening to Auth State

The key pattern: `onAuthStateChanged`. This fires whenever the user signs in, signs out, or the page loads with an existing session.

```tsx
// src/hooks/useAuth.ts
import { useState, useEffect } from "react";
import { onAuthStateChanged, User } from "firebase/auth";
import { auth } from "../firebase";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return unsubscribe; // cleanup on unmount
  }, []);

  return { user, loading };
}
```

Use it in your app:

```tsx
// src/App.tsx
import { useAuth } from "./hooks/useAuth";
import { logOut } from "./auth";

function App() {
  const { user, loading } = useAuth();

  if (loading) return <p>Loading...</p>;

  if (!user) return <LoginPage />;

  return (
    <div>
      <p>Welcome, {user.displayName || user.email}</p>
      <button onClick={logOut}>Sign Out</button>
      <TaskBoard />
    </div>
  );
}
```

---

## The Login Page

```tsx
// src/components/LoginPage.tsx
import { useState } from "react";
import { signUp, signIn, signInWithGoogle } from "../auth";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      if (isSignUp) {
        await signUp(email, password, name);
      } else {
        await signIn(email, password);
      }
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "2rem auto" }}>
      <h1>SnapTask</h1>
      <form onSubmit={handleSubmit}>
        {isSignUp && (
          <input
            type="text"
            placeholder="Display name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password (min 6 chars)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
        />
        <button type="submit">{isSignUp ? "Sign Up" : "Sign In"}</button>
      </form>

      <button onClick={signInWithGoogle}>Sign in with Google</button>

      <p>
        {isSignUp ? "Already have an account?" : "Need an account?"}{" "}
        <button onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp ? "Sign In" : "Sign Up"}
        </button>
      </p>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
```

---

## What You Get from `user`

After authentication, `auth.currentUser` (or the `user` from `onAuthStateChanged`) gives you:

```typescript
user.uid;           // "abc123" — unique, stable identifier
user.email;         // "alex@example.com"
user.displayName;   // "Alex" (set during sign-up or from Google)
user.photoURL;      // Google profile photo (if Google sign-in)
user.emailVerified; // true/false
user.metadata.creationTime;    // when they signed up
user.metadata.lastSignInTime;  // last login
```

The `uid` is the key. Every security rule, every database query, every permission check uses this ID.

---

## The ID Token

Firebase Auth gives each signed-in user an **ID token** — a JWT that proves who they are. The SDK manages this automatically:

```typescript
// Get the current user's ID token (for calling your own APIs)
const token = await user.getIdToken();

// The token refreshes automatically every hour
// You almost never need to call this manually
```

When you write Security Rules (Chapter 5), Firebase automatically validates this token on every request. You don't pass it manually — the SDK handles it.

---

## Password Reset

```typescript
import { sendPasswordResetEmail } from "firebase/auth";

export async function resetPassword(email: string) {
  await sendPasswordResetEmail(auth, email);
  // Firebase sends the email. You don't manage email templates (yet).
}
```

---

## Error Handling

Firebase Auth errors have predictable codes:

```typescript
try {
  await signIn(email, password);
} catch (error: any) {
  switch (error.code) {
    case "auth/user-not-found":
      setError("No account with that email.");
      break;
    case "auth/wrong-password":
      setError("Incorrect password.");
      break;
    case "auth/email-already-in-use":
      setError("An account with that email already exists.");
      break;
    case "auth/weak-password":
      setError("Password must be at least 6 characters.");
      break;
    case "auth/too-many-requests":
      setError("Too many attempts. Try again later.");
      break;
    default:
      setError("Something went wrong. Try again.");
  }
}
```

---

## Testing with the Emulator

The Auth Emulator at `localhost:9099` lets you:

1. Create test users without real emails
2. Skip email verification
3. See all users in the Emulator UI (`localhost:4000` → Auth tab)
4. Clear all users between test runs

In the Emulator UI, you can manually add users, see their tokens, and even trigger password resets — all without sending real emails.

---

## The Auth State Flow

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  Page loads                                                  │
│      │                                                       │
│      ▼                                                       │
│  onAuthStateChanged fires                                    │
│      │                                                       │
│      ├── user exists (session persisted) → show app          │
│      │                                                       │
│      └── user is null → show login page                      │
│              │                                               │
│              ▼                                               │
│          User signs in (email or Google)                     │
│              │                                               │
│              ▼                                               │
│          onAuthStateChanged fires again → user exists        │
│              │                                               │
│              ▼                                               │
│          Show app                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

Firebase persists the session in IndexedDB by default. Users stay signed in across page refreshes and browser restarts. No cookies to manage.

---

## Session Persistence Options

```typescript
import { setPersistence, browserLocalPersistence, browserSessionPersistence, inMemoryPersistence } from "firebase/auth";

// Default: persists across browser restarts
await setPersistence(auth, browserLocalPersistence);

// Clears on tab close
await setPersistence(auth, browserSessionPersistence);

// Clears on page refresh (useful for sensitive apps)
await setPersistence(auth, inMemoryPersistence);
```

For SnapTask, the default (local persistence) is fine. Users don't want to sign in every time they open the app.

---

## Common Mistakes

### 1. Checking `auth.currentUser` on page load

```typescript
// ❌ WRONG — currentUser is null until auth initializes
const user = auth.currentUser; // null on first render!

// ✅ RIGHT — wait for onAuthStateChanged
onAuthStateChanged(auth, (user) => {
  // Now you know the real state
});
```

Auth initialization is async. `currentUser` is `null` until Firebase checks the persisted session. Always use `onAuthStateChanged`.

### 2. Not handling the loading state

If you render the login page before auth initializes, users see a flash of the login form before being redirected to the app. Always show a loading indicator until `onAuthStateChanged` fires.

### 3. Storing passwords or tokens yourself

Don't. Firebase manages tokens, refresh, and session persistence. You never see the password after sign-up. You never store tokens in localStorage manually.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Function                                │ What It Does
────────────────────────────────────────┼──────────────────────────────────────
createUserWithEmailAndPassword()        │ Create new account
signInWithEmailAndPassword()            │ Sign in existing user
signInWithPopup(provider)               │ OAuth popup (Google, GitHub, etc.)
signOut()                               │ Sign out
onAuthStateChanged(auth, callback)      │ Listen for auth state changes
updateProfile(user, { displayName })    │ Set display name / photo
sendPasswordResetEmail(auth, email)     │ Send reset email
user.getIdToken()                       │ Get JWT (for custom APIs)
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marco: "Great, users can sign in. But where do we store their tasks? We need a database."

Firestore. The real-time NoSQL database that makes Firebase powerful — and dangerous.

---

[← Chapter 1: Setup](chapter-01-setup-deploy.md) | [Chapter 3: Firestore CRUD →](chapter-03-firestore-crud.md)
